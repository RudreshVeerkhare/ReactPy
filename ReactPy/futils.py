import os
from urllib.request import urlopen
import zipfile
import shutil


def writefile(filepath, content, mode="w"):
    with open(filepath, mode) as file:
        file.write(content)


def readfile(filepath, mode="r"):
    content = None
    with open(filepath, mode) as file:
        content = file.read()
    return content


def makedirs(pathname, exist_ok=True, dir_from_path=False):
    if dir_from_path:
        pathname = os.path.dirname(pathname)
    os.makedirs(pathname, exist_ok=exist_ok)


def download_file(url, save_location):
    try:
        print("Downloading Data...")
        with open(save_location, "wb") as f:
            u = urlopen(url)
            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                file_size_dl += len(buffer)
                f.write(buffer)
        print("Download Complete!")
        return True

    except Exception as e:
        print(f"Download Failed Due to: {e}")
        if os.path.isfile(save_location):
            os.remove(save_location)
        return False


def copy_from_zip(source_zip, source_path, target_path):
    with zipfile.ZipFile(source_zip) as z:
        with z.open(source_path) as zf, open(join(target_path), "wb") as f:
            shutil.copyfileobj(zf, f)


def join(*paths, ignore_terminal_slash=True):

    # Check https://stackoverflow.com/questions/1945920/why-doesnt-os-path-join-work-in-this-case
    if not ignore_terminal_slash:
        return os.path.join(*paths)

    return os.path.normpath("/".join(paths))
    # final_path = ""
    # # replace \\ -> /
    # temp = []
    # for path in paths:
    #     temp.append(path.replace("\\", "/").strip("/"))

    # return "/".join(temp)
