#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-22 18:58:59"
# Author: Yusuke Watanabe (ywata1989@gmail.com)

"""
This script does XYZ.
"""

# Functions
# Imports
import inspect
import subprocess


# # Config
# CONFIG = scitex.gen.load_configs()


def src(obj):
    """
    Returns the source code of a given object using `less`.
    Handles functions, classes, class instances, methods, and built-in functions.
    """
    # If obj is an instance of a class, get the class of the instance.
    if (
        not inspect.isclass(obj)
        and not inspect.isfunction(obj)
        and not inspect.ismethod(obj)
    ):
        obj = obj.__class__

    try:
        # Attempt to retrieve the source code
        source_code = inspect.getsource(obj)

        # Assuming scitex.gen.less is a placeholder for displaying text with `less`
        # This part of the code is commented out as it seems to be a placeholder
        # scitex.gen.less(source_code)

        # Open a subprocess to use `less` for displaying the source code
        process = subprocess.Popen(["less"], stdin=subprocess.PIPE, encoding="utf8")
        process.communicate(input=source_code)
        if process.returncode != 0:
            print(f"Process exited with return code {process.returncode}")
    except OSError as e:
        # Handle cases where the source code cannot be retrieved (e.g., built-in functions)
        print(f"Cannot retrieve source code: {e}")
    except TypeError as e:
        # Handle cases where the object type is not supported
        print(f"TypeError: {e}")
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Error: {e}")


# def src(obj):
#     """
#     Returns the source code of a given object using `less`.
#     Handles functions, classes, class instances, and methods.
#     """
#     # If obj is an instance of a class, get the class of the instance.
#     if (
#         not inspect.isclass(obj)
#         and not inspect.isfunction(obj)
#         and not inspect.ismethod(obj)
#     ):
#         obj = obj.__class__

#     try:
#         # Attempt to retrieve the source code
#         source_code = inspect.getsource(obj)
#         scitex.gen.less(source_code)

#         # # Open a subprocess to use `less` for displaying the source code
#         # process = subprocess.Popen(
#         #     ["less"], stdin=subprocess.PIPE, encoding="utf8"
#         # )
#         # process.communicate(input=source_code)
#         if process.returncode != 0:
#             print(f"Process exited with return code {process.returncode}")
#     except TypeError as e:
#         # Handle cases where the object type is not supported
#         print(f"TypeError: {e}")
#     except Exception as e:
#         # Handle any other unexpected errors
#         print(f"Error: {e}")


# (YOUR AWESOME CODE)

if __name__ == "__main__":
    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)

    # (YOUR AWESOME CODE)

    # Close
    scitex.gen.close(CONFIG, verbose=False, notify=False)

# EOF

"""
/ssh:ywatanabe@444:/home/ywatanabe/proj/entrance/scitex/gen/_def.py
"""
