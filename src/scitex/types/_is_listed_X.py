#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 17:10:53 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/types/_is_listed_X.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/types/_is_listed_X.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


def is_listed_X(obj, types):
    """
    Check if obj is a list where all elements are of one of the specified types.

    Args:
        obj: Object to check
        types: Type or list of types to check against

    Example:
        obj = [3, 2, 1, 5]
        is_listed_X(obj, int)  # Returns True
        is_listed_X(obj, (int, float))  # Returns True
        is_listed_X(obj, str)  # Returns False

    Returns:
        bool: True if obj is a list and all elements are of one of the specified types
    """
    import numpy as np

    try:
        condition_list = isinstance(obj, list)

        if not (isinstance(types, list) or isinstance(types, tuple)):
            types = [types]

        _conditions_susp = []
        for typ in types:
            _conditions_susp.append(
                (np.array([isinstance(o, typ) for o in obj]) == True).all()
            )

        condition_susp = np.any(_conditions_susp)

        _is_listed_X = np.all([condition_list, condition_susp])
        return _is_listed_X

    except:
        return False


# More conventional alias
def is_list_of_type(obj, types):
    """
    Check if obj is a list where all elements are of one of the specified types.
    
    This is an alias for is_listed_X with a more conventional name.
    
    Args:
        obj: Object to check
        types: Type or list of types to check against
        
    Returns:
        bool: True if obj is a list and all elements are of one of the specified types
    """
    return is_listed_X(obj, types)


# EOF
