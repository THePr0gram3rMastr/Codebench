# Copyright (c) 2009 J-Pascal Mercier
#
#

import itertools

def reclist(fct, first_arg, n):
    """
    This function create a list composed of the first argument
    and the calculated functions with the previous result.
    """
    return_value = [first_arg] * n
    for i in range(1,n):
        return_value[i] = fct(return_value[i - 1])
    return return_value

__colors__ = [(0,0,1), (0, 1, 0), (1, 0, 0), (1, 1, 0), (0, 1, 1), (1, 0, 1)]


