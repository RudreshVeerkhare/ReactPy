import os
import shutil
from argparse import ArgumentParser
from glob import glob
from subprocess import run

from . import __version__, BRYTHON_DEFAULT_VERSION

SERVE_FOLDER = "temp"
BUILD_FOLDER = "build"


def main():
    parser = ArgumentParser()

    parser.add_argument(
        "--init",
        help="Initialize ReactPy in an empty directory with given Brython version",
        action="store_true",
    )

    parser.add_argument("--build", help="Build a ReactPy project", action="store_true")

    parser.add_argument(
        "--serve", help="Start development server", nargs="?", default="absent"
    )

    parser.add_argument("--version", help="ReactPy version", action="store_true")

    args = parser.parse_args()

    if args.init:

        print(f"Installing ReactPy {__version__}")
        print(f"Installing Brython {BRYTHON_DEFAULT_VERSION}")

        data_path = os.path.join(os.path.dirname(__file__), "data")
        current_path_files = os.listdir(os.getcwd())

        if current_path_files and "brython.js" in current_path_files:
            override = input(
                "brython.js is already present in this directory." " Override ? (Y/N)"
            )
            if override.lower() != "y":
                import sys

                print("exiting")
                sys.exit()

        CWD = os.getcwd()

        for path in glob(os.path.join(data_path, "**/**"), recursive=True):
            if os.path.isdir(path):
                continue
            try:
                target_path = path[len(data_path) + 1 :]
                os.makedirs(
                    os.path.dirname(target_path),
                    exist_ok=True,
                )
                shutil.copy(path, target_path)
            except shutil.SameFileError:
                print(f"{path} has not been moved. Are the same file.")

        print("done")

    if args.build:
        parse_pyx(output_folder=BUILD_FOLDER)
        move_public_files(output_folder=BUILD_FOLDER)

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
            move_public_files(output_folder=SERVE_FOLDER)

        reload_files()

        # watch .pyx files
        server.watch("src/**", reload_files)
        server.watch("public/", reload_files)

        server.serve(root=os.path.join(os.getcwd(), SERVE_FOLDER))

    if args.version:
        print("ReactPy version:", __version__)
        print("Brython version:", BRYTHON_DEFAULT_VERSION)


def move_public_files(output_folder=SERVE_FOLDER, exclude_list=[]):
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


def parse_pyx(output_folder=SERVE_FOLDER):
    from pyx import parser

    # get current path
    cwd = os.getcwd()

    # iterate through .pyx files and parse them
    for filename in glob("src/**", recursive=True):

        if filename[-3:] != "pyx":
            continue

        # read file content
        with open(filename, "r") as rf:
            transformed_code = parser.transform(rf.read())

        # write to the file within SERVE_FOLDER folder
        path = os.path.join(cwd, output_folder, filename[4:][:-1])

        os.makedirs(
            os.path.dirname(path),
            exist_ok=True,
        )
        with open(path, "w") as wf:
            wf.write(transformed_code)


if __name__ == "__main__":
    main()
