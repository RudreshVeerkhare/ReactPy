import os
import sys
import shutil
import os.path as pt
from argparse import ArgumentParser
from glob import glob
from subprocess import run
from . import futils, pyx, html_parser
from . import __version__, BRYTHON_DEFAULT_VERSION

SERVE_FOLDER = "temp"
BUILD_FOLDER = "build"
PUBLIC_FOLDER = "public"


def main():
    parser = ArgumentParser()

    parser.add_argument(
        "--init",
        help="Initialize ReactPy in an empty directory with given Brython version",
        type=str,
        const=BRYTHON_DEFAULT_VERSION,
        nargs="?",
    )

    parser.add_argument("--build", help="Build a ReactPy project", action="store_true")

    parser.add_argument(
        "--refresh",
        help="Refresh Brython files with latest ReactPy installation",
        action="store_true",
    )

    parser.add_argument(
        "--serve", help="Start development server", nargs="?", default="absent"
    )

    parser.add_argument("--version", help="ReactPy version", action="store_true")

    args = parser.parse_args()

    if args.init:
        brython_version = args.init
        print(f"Installing ReactPy {__version__}")
        print(f"Installing Brython {brython_version}")

        template_path = os.path.join(os.path.dirname(__file__), "data/templates")
        brython_bundle_path = os.path.join(
            os.path.dirname(__file__), "data/brython_bundles"
        )

        current_path = os.getcwd()
        source_zip = futils.join(brython_bundle_path, f"Brython-{brython_version}.zip")

        # download Brython if required version does not exists in data folder
        if not os.path.isfile(source_zip):
            status = futils.download_file(
                f"https://github.com/brython-dev/brython/releases/download/{brython_version}/Brython-{brython_version}.zip",
                source_zip,
            )
            if not status:
                print("Failed to Install!")
                sys.exit()

        for path in glob(os.path.join(template_path, "**/**"), recursive=True):
            if os.path.isdir(path):
                continue
            try:
                target_path = path[len(template_path) + 1 :]
                os.makedirs(
                    os.path.dirname(target_path),
                    exist_ok=True,
                )
                shutil.copy(path, target_path)
            except shutil.SameFileError:
                print(f"{path} has not been moved. Are the same file.")

        # extract brython.js and brython_stdlib.js from zip
        futils.copy_from_zip(
            source_zip,
            f"Brython-{brython_version}/brython.js",
            futils.join(current_path, "public", "brython.js"),
        )
        futils.copy_from_zip(
            source_zip,
            f"Brython-{brython_version}/brython_stdlib.js",
            futils.join(current_path, "public", "brython_stdlib.js"),
        )

        print("done")

    if args.refresh:

        print(f"Installing ReactPy {__version__}")
        print(f"Installing Brython {BRYTHON_DEFAULT_VERSION}")

        template_path = os.path.join(
            os.path.dirname(__file__), "data", "templates", "public"
        )

        for path in glob(os.path.join(template_path, "**"), recursive=True):
            if os.path.isdir(path):
                continue
            try:
                target_path = PUBLIC_FOLDER
                shutil.copy(path, target_path)
            except shutil.SameFileError:
                print(f"{path} has not been moved. Are the same file.")

        print("done")

    if args.build:
        parse_pyx(output_folder=BUILD_FOLDER)
        move_public_files(
            output_folder=BUILD_FOLDER, brython_module="brython_modules.js"
        )

        # make module using brython
        project_name = os.path.basename(os.getcwd())
        cmd_output = run(
            ["brython-cli", "--modules"],
            cwd=BUILD_FOLDER,
            capture_output=True,
        )
        print(cmd_output.stdout.decode("utf-8"), end="")
        print(cmd_output.stderr.decode("utf-8"), end="")
        os.remove(os.path.join(BUILD_FOLDER, "brython_stdlib.js"))
        print("done")

    if args.serve != "absent":
        from livereload import Server

        # create a live server
        server = Server()

        def reload_files():
            # parse all .pyx files
            parse_pyx(output_folder=SERVE_FOLDER)
            move_public_files(
                output_folder=SERVE_FOLDER, brython_module="brython_stdlib.js"
            )

        reload_files()

        # watch .pyx files
        server.watch("src/**", reload_files)
        server.watch("public/", reload_files)

        server.serve(root=os.path.join(os.getcwd(), SERVE_FOLDER))

    if args.version:
        print("ReactPy version:", __version__)
        print("Brython version:", BRYTHON_DEFAULT_VERSION)


def move_public_files(
    output_folder=SERVE_FOLDER, exclude_list=[], brython_module="brython_stdlib.js"
):
    # move .html files from public folder to SERVE_FOLDER
    for filepath in glob("public/**", recursive=True):
        if os.path.isdir(filepath) or os.path.basename(filepath) in exclude_list:
            continue

        try:
            shutil.copyfile(
                filepath,
                output_folder + filepath[len("public") :],
            )
        except shutil.SameFileError:
            print(f"{filepath} has not been moved. Are the same file.")

    # edit index.html to include custom_style.css
    html_filepath = futils.join(output_folder, "index.html")
    html_content = futils.readfile(html_filepath)
    futils.writefile(
        html_filepath,
        html_parser.add_brython_modules(
            html_parser.link_css_file(html_content, ["custom_style.css"]),
            brython_module,
        ),
    )


def parse_pyx(output_folder=SERVE_FOLDER):
    # get current path
    cwd = os.getcwd()

    # iterate through .pyx files and parse them
    for filename in glob("src/**", recursive=True):

        if filename[-3:] != "pyx":
            continue

        # read file content
        pyx_code = futils.readfile(filename)
        transformed_code, css_files = pyx.transform(pyx_code)

        # write to the file within SERVE_FOLDER folder
        # path = os.path.join(cwd, output_folder, filename[4:][:-1])
        py_filename = filename[4:][:-1]  # src/xyz.pyx -> xyz.py
        path = futils.join(output_folder, py_filename)

        futils.makedirs(path, dir_from_path=True)
        futils.writefile(path, transformed_code)

        # append app css to single file -> custom_style.css
        # append css content to custom_style.css in output_folder
        # clear file to avoid appending same thing again
        futils.writefile(futils.join(output_folder, "custom_style.css"), "", mode="w")
        for css_path in css_files:
            # normalize path
            normalized_path = pt.normpath(futils.join("src", css_path))
            css_content = futils.readfile(normalized_path)

            # append css content to custom_style.css in output_folder
            futils.writefile(
                futils.join(output_folder, "custom_style.css"), css_content, mode="a"
            )


if __name__ == "__main__":
    main()
