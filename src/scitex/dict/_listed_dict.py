#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 12:40:01 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dict/_listed_dict.py

from collections import defaultdict


def listed_dict(keys=None):
    """
    Example 1:
        import random
        random.seed(42)
        d = listed_dict()
        for _ in range(10):
            d['a'].append(random.randint(0, 10))
        print(d)
        # defaultdict(<class 'list'>, {'a': [10, 1, 0, 4, 3, 3, 2, 1, 10, 8]})

    Example 2:
        import random
        random.seed(42)
        keys = ['a', 'b', 'c']
        d = listed_dict(keys)
        for _ in range(10):
            d['a'].append(random.randint(0, 10))
            d['b'].append(random.randint(0, 10))
            d['c'].append(random.randint(0, 10))
        print(d)
        # defaultdict(<class 'list'>, {'a': [10, 4, 2, 8, 6, 1, 8, 8, 8, 7],
        #                              'b': [1, 3, 1, 1, 0, 3, 9, 3, 6, 9],
        #                              'c': [0, 3, 10, 9, 0, 3, 0, 10, 3, 4]})
    """
    dict_list = defaultdict(list)
    # initialize with keys if possible
    if keys is not None:
        for k in keys:
            dict_list[k] = []
    return dict_list


# EOF
