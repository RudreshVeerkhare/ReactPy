import os


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
