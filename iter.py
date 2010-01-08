# Copyright (c) 2009 J-Pascal Mercier
#
# vim: ts=4 sw=4 sts=0 noexpandtab:

import itertools, os


def reclist(fct, first_arg, n):
    """
    This function create a list composed of the first argument
    and the calculated functions with the previous result.
    """
    return_value = [first_arg] * n
    for i in range(1,n):
        return_value[i] = fct(return_value[i - 1])
    return return_value


def file_series(path, first = 0, last = -1):
		files = os.listdir(path)
		files.sort()
		for fname in files:
				yield os.path.join(path, fname)

__colors__ = [(0,0,1), (0, 1, 0), (1, 0, 0), (1, 1, 0), (0, 1, 1), (1, 0, 1)]


