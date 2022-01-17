def lmap(func, iterable):
    """
    returns list after applying map
    :: list(map(func, iterable))
    """
    return list(map(func, iterable))


def flatten(list_iterable):
    """
    Flatten out multidim list
    """
    res = []
    for item in list_iterable:
        if isinstance(item, list):
            res += flatten(item)
        else:
            res.append(item)
    return res


def transform_attr(name):
    """
    Transform camel case attributes to CSS style
    """
    res = ""
    for ch in name:
        if ch.isupper():
            res += "-" + ch.lower()
        else:
            res += ch
    return res
