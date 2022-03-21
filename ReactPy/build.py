import os
import shutil
from subprocess import run
from argparse import ArgumentParser
import futils

REACT_FOLDER = "./react/"
PUBLIC_FOLDER = "./data/templates/public/"
parser = ArgumentParser()
parser.add_argument(
    "--build-react",
    help="Build Brython module of ReactPy and write it to data",
    action="store_true",
)

if __name__ == "__main__":
    args = parser.parse_args()

    if args.build_react:
        # make package of ReactPy using brython
        cmd_output = run(
            ["brython-cli", "--make_package", "ReactPy"],
            cwd=REACT_FOLDER,
            capture_output=True,
        )
        print(cmd_output.stdout.decode("utf-8"), end="")
        print(cmd_output.stderr.decode("utf-8"), end="")

        # move file from REACT_FOLDER to data folder
        shutil.move(
            futils.join(REACT_FOLDER, "ReactPy.brython.js"),
            futils.join(PUBLIC_FOLDER, "ReactPy.brython.js"),
        )
