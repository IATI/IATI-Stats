from collections import OrderedDict
from decimal import Decimal


# From http://bugs.python.org/issue16535
class NumberStr(float):
    def __init__(self, o):
        # We don't call the parent here, since we're deliberately altering it's functionality
        # pylint: disable=W0231
        self.o = o

    def __repr__(self):
        return str(self.o)

    # This is needed for this trick to work in python 3.4
    def __float__(self):
        return self


def decimal_default(o):
    if isinstance(o, Decimal):
        return NumberStr(o)
    raise TypeError(repr(o) + " is not JSON serializable")


def sort_keys(o):
    def key(k):
        if isinstance(k, tuple):
            k = k[0]
        if isinstance(k, type(None)):
            return (0, 0, "")
        try:
            return (1, float(k), "")
        except ValueError:
            pass
        return (2, 0, str(k))

    if isinstance(o, list):
        return sorted(o, key=key)
    if isinstance(o, dict):
        return OrderedDict(sorted(o.items(), key=key))
    return o


def get_git_file_contents(repo, path, commit):
    out = repo.git.ls_tree(commit, path)
    if out == "":
        return None
    blob = out.split()[2]
    return repo.git.cat_file("blob", blob)
