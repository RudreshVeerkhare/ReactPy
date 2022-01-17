import os
import shutil
from argparse import ArgumentParser
from glob import glob

# from . import __version__, BRYTHON_DEFAULT_VERSION

SERVE_FOLDER = "temp"
BUILD_FOLDER = "build"

__version__ = "1.0.0"
BRYTHON_DEFAULT_VERSION = "3.10.4"


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
        print(f"Installing Brython {args.init}")

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
        for path in glob(os.path.join(data_path, "**\\**"), recursive=True):
            if os.path.isdir(path):
                if path[len(data_path) :] != "\\":
                    os.makedirs(CWD + path[len(data_path) :], exist_ok=True)
                continue
            try:
                # TODO: Find out why os.path.join is not working
                shutil.copy(path, CWD + path[len(data_path) :])
            except shutil.SameFileError:
                print(f"{path} has not been moved. Are the same file.")

        print("done")

    if args.build:
        # TODO: Parse .pyx files to .py files
        parse_pyx(output_folder=BUILD_FOLDER)

        # TODO: make module using brython

        # TODO: write all to build folder

        pass

    if args.serve != "absent":
        from livereload import Server

        # TODO: create a live server
        server = Server()

        def _setup_dev_server():
            # parse all .pyx files
            parse_pyx(output_folder=SERVE_FOLDER)
            CWD = os.getcwd()

            # move .html files from public folder to SERVE_FOLDER
            for filepath in glob(os.path.join(CWD, "public/**"), recursive=True):
                if os.path.isdir(filepath):
                    continue

                try:
                    shutil.copyfile(
                        filepath,
                        SERVE_FOLDER + filepath[len(os.path.join(CWD, "public")) :],
                    )
                except shutil.SameFileError:
                    print(f"{filepath} has not been moved. Are the same file.")

        _setup_dev_server()
        # TODO: watch .pyx files
        server.watch("src/*.pyx", _setup_dev_server)
        server.watch("public/", _setup_dev_server)

        server.serve(root=os.path.join(os.getcwd(), SERVE_FOLDER))

    if args.version:
        print("ReactPy version:", __version__)
        print("Brython version:", BRYTHON_DEFAULT_VERSION)


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
        path = os.path.join(cwd, output_folder, filename[:-1])

        os.makedirs(
            os.path.dirname(os.path.join(cwd, output_folder, filename[:-1])),
            exist_ok=True,
        )
        with open(path, "w") as wf:
            wf.write(transformed_code)


if __name__ == "__main__":
    main()
