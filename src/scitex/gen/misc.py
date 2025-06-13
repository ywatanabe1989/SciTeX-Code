#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-16 16:26:59 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/misc.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/misc.py"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 12:50:29 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/misc.py

import math
import os
import shutil
import threading
import time
import warnings
from bisect import bisect_left
from functools import wraps


import numpy as np
import pandas as pd
import readchar
import torch


def find_closest(list_obj, num_insert):
    """Find the closest value in a sorted list to a given number.

    Parameters
    ----------
    list_obj : list
        A sorted list of numbers.
    num_insert : float or int
        The number to find the closest value to.

    Returns
    -------
    tuple
        A tuple containing (closest_value, index_of_closest_value).

    Example
    -------
    >>> find_closest([1, 3, 5, 7, 9], 6)
    (5, 2)
    >>> find_closest([1, 3, 5, 7, 9], 8)
    (7, 3)
    """
    """
    Assumes list_obj is sorted. Returns the closest value to num.
    If the same number is included in list_obj, the smaller number is returned.

    Example:
        list_obj = np.array([0, 1, 1, 2, 3, 3])
        num = 1.2
        closest_num, closest_pos = take_the_closest(list_obj, num)
        print(closest_num, closest_pos)
        # 1 2

        list_obj = np.array([0, 1, 1, 2, 3, 3])
        num = 1
        closest_num, closest_pos = take_the_closest(list_obj, num)
        print(closest_num, closest_pos)
        # 1 1
    """
    if math.isnan(num_insert):
        closest_num = np.nan
        closest_pos = np.nan

    pos_num_insert = bisect_left(list_obj, num_insert)

    if pos_num_insert == 0:
        closest_num = list_obj[0]
        closest_pos = pos_num_insert

    if pos_num_insert == len(list_obj):
        closest_num = list_obj[-1]
        closest_pos = pos_num_insert

    else:
        pos_before = pos_num_insert - 1

        before_num = list_obj[pos_before]
        after_num = list_obj[pos_num_insert]

        delta_after = abs(after_num - num_insert)
        delta_before = abs(before_num - num_insert)

        if np.abs(delta_after) < np.abs(delta_before):
            closest_num = after_num
            closest_pos = pos_num_insert

        else:
            closest_num = before_num
            closest_pos = pos_before

    return closest_num, closest_pos


################################################################################
## mutable
################################################################################
def isclose(mutable_a, mutable_b):
    """Check if two mutable objects are close to each other.

    This function compares two mutable objects (e.g., lists, numpy arrays) element-wise
    to determine if they are close to each other.

    Parameters
    ----------
    mutable_a : list or numpy.ndarray
        The first mutable object to compare.
    mutable_b : list or numpy.ndarray
        The second mutable object to compare.

    Returns
    -------
    bool
        True if the objects are close to each other, False otherwise.

    Example
    -------
    >>> isclose([1.0, 2.0, 3.0], [1.0, 2.0001, 3.0])
    True
    >>> isclose([1.0, 2.0, 3.0], [1.0, 2.1, 3.0])
    False
    """
    return [math.isclose(a, b) for a, b in zip(mutable_a, mutable_b)]


################################################################################
## dictionary
################################################################################


################################################################################
## variables
################################################################################
def is_defined_global(x_str):
    """
    Example:
        print(is_defined('a'))
        # False

        a = 5
        print(is_defined('a'))
        # True
    """
    return x_str in globals()


def is_defined_local(x_str):
    """
    Example:
        print(is_defined('a'))
        # False

        a = 5
        print(is_defined('a'))
        # True
    """
    return x_str in locals()


################################################################################
## versioning
################################################################################
def is_later_or_equal(package, tgt_version, format="MAJOR.MINOR.PATCH"):
    """Check if the installed version of a package is later than or equal to a target version.

    Parameters
    ----------
    package : str
        The name of the package to check.
    tgt_version : str
        The target version to compare against.
    format : str, optional
        The version format (default is "MAJOR.MINOR.PATCH").

    Returns
    -------
    bool
        True if the installed version is later than or equal to the target version, False otherwise.

    Example
    -------
    >>> is_later_or_equal('numpy', '1.18.0')
    True
    >>> is_later_or_equal('pandas', '2.0.0')
    False
    """

    import numpy as np

    indi, matched = scitex.gen.search(["MAJOR", "MINOR", "PATCH"], format.split("."))
    imp_major, imp_minor, imp_patch = [
        int(v) for v in np.array(package.__version__.split("."))[indi]
    ]
    tgt_major, tgt_minor, tgt_patch = [
        int(v) for v in np.array(tgt_version.split("."))[indi]
    ]

    print(
        f"\npackage: {package.__name__}\n"
        f"target_version: {tgt_version}\n"
        f"imported_version: {imp_major}.{imp_minor}.{imp_patch}\n"
    )

    ## Mjorr
    if imp_major > tgt_major:
        return True

    if imp_major < tgt_major:
        return False

    if imp_major == tgt_major:

        ## Minor
        if imp_minor > tgt_minor:
            return True

        if imp_minor < tgt_minor:
            return False

        if imp_minor == tgt_minor:

            ## Patch
            if imp_patch > tgt_patch:
                return True
            if imp_patch < tgt_patch:
                return False
            if imp_patch == tgt_patch:
                return True


################################################################################
## File
################################################################################
def _copy_a_file(src, dst, allow_overwrite=False):
    """Copy a single file from source to destination.

    Parameters
    ----------
    src : str
        The path to the source file.
    dst : str
        The path to the destination file.
    allow_overwrite : bool, optional
        If True, allows overwriting existing files (default is False).

    Raises
    ------
    FileExistsError
        If the destination file already exists and allow_overwrite is False.

    Example
    -------
    >>> _copy_a_file('/path/to/source.txt', '/path/to/destination.txt')
    >>> _copy_a_file('/path/to/source.txt', '/path/to/existing.txt', allow_overwrite=True)
    """
    if src == "/dev/null":
        print(f"\n/dev/null was not copied.\n")

    else:

        if dst.endswith("/"):
            _, src_fname, src_ext = scitex.path.split(src)
            # src_fname = src + src_ext
            dst = dst + src_fname + src_ext

        if not os.path.exists(dst):
            shutil.copyfile(src, dst)
            print(f'\nCopied "{src}" to "{dst}".\n')

        else:
            if allow_overwrite:
                shutil.copyfile(src, dst)
                print(f'\nCopied "{src}" to "{dst}" (overwritten).\n')

            if not allow_overwrite:
                print(f'\n"{dst}" exists and copying from "{src}" was aborted.\n')


def copy_files(src_files, dists, allow_overwrite=False):
    """Copy multiple files from source(s) to destination(s).

    Parameters
    ----------
    src_files : str or list of str
        The path(s) to the source file(s).
    dists : str or list of str
        The path(s) to the destination file(s) or directory(ies).
    allow_overwrite : bool, optional
        If True, allows overwriting existing files (default is False).

    Example
    -------
    >>> copy_files('/path/to/source.txt', '/path/to/destination/')
    >>> copy_files(['/path/to/file1.txt', '/path/to/file2.txt'], ['/path/to/dest1/', '/path/to/dest2/'])
    >>> copy_files('/path/to/source.txt', '/path/to/existing.txt', allow_overwrite=True)
    """
    if isinstance(src_files, str):
        src_files = [src_files]

    if isinstance(dists, str):
        dists = [dists]

    for sf in src_files:
        for dst in dists:
            _copy_a_file(sf, dst, allow_overwrite=allow_overwrite)


def copy_the_file(sdir):
    """Copy the current script file to a specified directory.

    This function copies the script file that called it to a specified directory.
    It uses the calling script's filename and copies it to the given directory.

    Parameters
    ----------
    sdir : str
        The destination directory where the file should be copied.

    Note
    ----
    This function will not copy the file if it's run in an IPython environment.

    Example
    -------
    >>> copy_the_file('/path/to/destination/')
    """
    THIS_FILE = inspect.stack()[1].filename
    _, fname, ext = scitex.path.split(__file__)

    #     dst = sdir + fname + ext

    if "ipython" not in __file__:
        _copy_a_file(__file__, dst)


def is_nan(X):
    """Check if the input contains any NaN values and raise an error if found.

    This function checks for NaN values in various data types including pandas DataFrames,
    numpy arrays, PyTorch tensors, and scalar values.

    Parameters
    ----------
    X : pandas.DataFrame, numpy.ndarray, torch.Tensor, float, or int
        The input data to check for NaN values.

    Raises
    ------
    ValueError
        If any NaN value is found in the input.

    Example
    -------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import torch
    >>> is_nan(pd.DataFrame({'a': [1, 2, np.nan]}))
    ValueError: NaN was found in X
    >>> is_nan(np.array([1, 2, 3]))
    # No error raised
    >>> is_nan(torch.tensor([1.0, float('nan'), 3.0]))
    ValueError: NaN was found in X
    >>> is_nan(float('nan'))
    ValueError: X was NaN
    """
    if isinstance(X, pd.DataFrame):
        if X.isna().any().any():
            raise ValueError("NaN was found in X")
    elif isinstance(X, np.ndarray):
        if np.isnan(X).any():
            raise ValueError("NaN was found in X")
    elif torch.is_tensor(X):
        if X.isnan().any():
            raise ValueError("NaN was found in X")
    elif isinstance(X, (float, int)):
        if math.isnan(X):
            raise ValueError("X was NaN")


def partial_at(func, index, value):
    """Create a partial function with a fixed argument at a specific position.

    This function creates a new function that calls the original function with a
    fixed argument inserted at the specified index position.

    Parameters
    ----------
    func : callable
        The original function to be partially applied.
    index : int
        The position at which to insert the fixed argument.
    value : any
        The fixed argument value to be inserted.

    Returns
    -------
    callable
        A new function that calls the original function with the fixed argument.

    Example
    -------
    >>> def greet(greeting, name):
    ...     return f"{greeting}, {name}!"
    >>> hello = partial_at(greet, 0, "Hello")
    >>> hello("Alice")
    'Hello, Alice!'
    >>> hello("Bob")
    'Hello, Bob!'
    """

    @wraps(func)
    def result(*rest, **kwargs):
        args = []
        args.extend(rest[:index])
        args.append(value)
        args.extend(rest[index:])
        return func(*args, **kwargs)

    return result


# def describe(df, method="mean", round_factor=1, axis=0):
# assert method in ["mean_std", "mean_ci", "median_iqr"]
#     df = pd.DataFrame(df)
#     with warnings.catch_warnings():
#         warnings.simplefilter("ignore", RuntimeWarning)
#         if method == "mean":
#             return round(np.nanmean(df, axis=axis), 3), round(
#                 np.nanstd(df, axis=axis) / round_factor, 3
#             )
#         if method == "median":
#             med = df.median(axis=axis)
#             IQR = df.quantile(0.75, axis=axis) - df.quantile(0.25, axis=axis)
#             return round(med, 3), round(IQR / round_factor, 3)


def describe(df, method="mean_std", round_factor=3, axis=0):
    """
    Compute descriptive statistics for a DataFrame.

    Example
    -------
    import pandas as pd
    import numpy as np
    data = pd.DataFrame({'A': [1, 2, 3, 4, 5], 'B': [10, 20, 30, 40, 50]})
    result = describe(data, method='mean_std')
    print(f"n={result['n']}, mean={result['mean']}, std={result['std']}")

    Parameters
    ----------
    df : pandas.DataFrame or array-like
        Input data.
    method : str, optional
        Statistical method to use. Options are 'mean_std', 'mean_ci', 'median_iqr'.
        Default is 'mean_std'.
    round_factor : int, optional
        Factor to divide the spread statistic by. Default is 3.
    axis : int, optional
        Axis along which to compute statistics. Default is 0.

    Returns
    -------
    dict
        Dictionary containing statistics based on the method chosen.
    """
    assert method in ["mean_std", "mean_ci", "median_iqr"]
    df = pd.DataFrame(df)
    nn = df.notna().sum(axis=axis)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        if method in ["mean_std", "mean_ci"]:
            mm = np.nanmean(df, axis=axis)
            if method == "mean_std":
                ss = np.nanstd(df, axis=axis)
                key = "std"
            else:  # mean_ci
                ss = 1.96 * np.nanstd(df, axis=axis) / np.sqrt(nn)
                key = "ci"
            return {
                "n": np.round(nn, 3),
                "mean": np.round(mm, 3),
                key: np.round(ss, 3),
            }
        else:  # median_iqr
            med = df.median(axis=axis)
            iqr = df.quantile(0.75, axis=axis) - df.quantile(0.25, axis=axis)
            return {
                "n": np.round(nn, round_factor),
                "median": np.round(med, round_factor),
                "iqr": np.round(iqr, round_factor),
            }


def _return_counting_process():
    import multiprocessing

    def _count():
        counter = 0
        while True:
            print(counter)
            time.sleep(1)
            counter += 1

    p1 = multiprocessing.Process(target=_count)
    p1.start()
    return p1


def wait_key(process, tgt_key="q"):
    """Wait for a specific key press while a process is running.

    This function waits for a specific key to be pressed while a given process
    is running. It's typically used to provide a way to interrupt or terminate
    a long-running process.

    Parameters
    ----------
    process : multiprocessing.Process
        The process to monitor while waiting for the key press.
    tgt_key : str, optional
        The target key to wait for (default is "q" for quit).

    Returns
    -------
    None

    Note
    ----
    This function will block until either the target key is pressed or the
    monitored process terminates.

    Example
    -------
    >>> import multiprocessing
    >>> def long_running_task():
    ...     while True:
    ...         pass
    >>> p = multiprocessing.Process(target=long_running_task)
    >>> p.start()
    >>> wait_key(p)  # This will wait until 'q' is pressed or the process ends
    """
    """
    Example:

        p1 = scitex.gen._return_counting_process()
        scitex.gen.wait_key(p1)
        # press q
    """
    pressed_key = None
    while pressed_key != tgt_key:
        pressed_key = readchar.readchar()
        print(pressed_key)
    process.terminate()


class ThreadWithReturnValue(threading.Thread):
    """
    Example:
        t = ThreadWithReturnValue(
            target=func, args=(,), kwargs={key: val}
        )
        t.start()
        out = t.join()

    """

    def __init__(
        self,
        group=None,
        target=None,
        name=None,
        args=(),
        kwargs={},
        Verbose=None,
    ):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        ### fixme
        Thread.join(self, *args)
        return self._return


def unique(data, axis=None):
    """
    Identifies unique elements in the data along the specified axis and their counts, returning a DataFrame.

    Parameters:
    - data (array-like): The input data to analyze for unique elements.
    - axis (int, optional): The axis along which to find the unique elements. Defaults to None.

    Returns:
    - df (pandas.DataFrame): DataFrame with unique elements and their counts.
    """
    if axis is None:
        uqs, counts = np.unique(data, return_counts=True)
    else:
        uqs, counts = np.unique(data, axis=axis, return_counts=True)

    if axis is None:
        df = pd.DataFrame({"uq": uqs, "n": counts})
    else:
        df = pd.DataFrame(uqs, columns=[f"axis_{i}" for i in range(uqs.shape[1])])
        df["n"] = counts

    df["n"] = df["n"].apply(lambda x: f"{int(x):,}")

    return df


def unique(data, axis=None):
    """
    Identifies unique elements in the data along the specified axis and their counts, returning a DataFrame.

    Parameters:
    - data (array-like): The input data to analyze for unique elements.
    - axis (int, optional): The axis along which to find the unique elements. Defaults to None.

    Returns:
    - df (pandas.DataFrame): DataFrame with unique elements and their counts.
    """
    # Find unique elements and their counts
    if axis is None:
        uqs, counts = np.unique(data, return_counts=True)
        df = pd.DataFrame({"Unique Elements": uqs, "Counts": counts})
    else:
        uqs, counts = np.unique(data, axis=axis, return_counts=True)
        # Create a DataFrame with unique elements
        df = pd.DataFrame(
            uqs,
            columns=[f"Unique Elements Axis {i}" for i in range(uqs.shape[1])],
        )
        # Add a column for counts
        df["Counts"] = counts

    # Format the 'Counts' column with commas for thousands
    df["Counts"] = df["Counts"].apply(lambda x: f"{x:,}")

    return df


def uq(*args, **kwargs):
    """Alias for the unique function.

    This function is a wrapper around the unique function, providing the same
    functionality with a shorter name.

    Parameters
    ----------
    *args : positional arguments
        Positional arguments to be passed to the unique function.
    **kwargs : keyword arguments
        Keyword arguments to be passed to the unique function.

    Returns
    -------
    array_like
        The result of calling the unique function with the given arguments.

    See Also
    --------
    unique : The main function for finding unique elements.

    Example
    -------
    >>> uq([1, 2, 2, 3, 3, 3])
    array([1, 2, 3])
    """
    return unique(*args, **kwargs)


# def mv_col(dataframe, column_name, position):
#     temp_col = dataframe[column_name]
#     dataframe.drop(labels=[column_name], axis=1, inplace=True)
#     dataframe.insert(loc=position, column=column_name, value=temp_col)
#     return dataframe


def float_linspace(start, stop, num_points):
    """Generate evenly spaced floating-point numbers over a specified interval.

    This function is similar to numpy's linspace, but ensures that the output
    consists of floating-point numbers with a specified number of decimal places.

    Parameters
    ----------
    start : float
        The starting value of the sequence.
    stop : float
        The end value of the sequence.
    num_points : int
        Number of points to generate.

    Returns
    -------
    numpy.ndarray
        Array of evenly spaced floating-point values.

    Example
    -------
    >>> float_linspace(0, 1, 5)
    array([0.  , 0.25, 0.5 , 0.75, 1.  ])
    >>> float_linspace(1, 2, 3)
    array([1. , 1.5, 2. ])
    """
    num_points = int(num_points)  # Ensure num_points is an integer

    if num_points < 2:
        return np.array([start, stop]) if num_points == 2 else np.array([start])

    step = (stop - start) / (num_points - 1)
    values = [start + i * step for i in range(num_points)]

    return np.array(values)


# EOF
