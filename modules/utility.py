#!/usr/bin/env python3

def _map(x, l, r, lt=None, rt=None, fl=None, fr=None):
    '''map(x, l, r, lt=None, rt=None, fl=None, fr=None)
    Return x in left and right
    Can map to_left and to_right
    Can set default value far_left and far_right
    '''
    # TODO lt rt
    if x < l:
        return l if fl is None else fl
    if x > r:
        return r if fr is None else fr
    return x
