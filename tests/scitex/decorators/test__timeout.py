#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-28 15:45:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/decorators/test__timeout.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/decorators/test__timeout.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import time

import pytest
from scitex.decorators import timeout


def test_timeout_decorator_success():
    """Test that timeout decorator allows functions to complete within time limit."""

    @timeout(seconds=2, error_message="Test timed out")
    def quick_function():
        time.sleep(0.5)
        return "Success"

    result = quick_function()
    assert result == "Success"


def test_timeout_decorator_raises_exception():
    """Test that timeout decorator raises TimeoutError for functions exceeding time limit."""

    @timeout(seconds=0.5, error_message="Custom timeout message")
    def slow_function():
        time.sleep(1)
        return "This should not be returned"

    with pytest.raises(TimeoutError) as excinfo:
        slow_function()

    assert "Custom timeout message" in str(excinfo.value)


def test_timeout_with_arguments():
    """Test timeout decorator with functions that take arguments."""

    @timeout(seconds=1)
    def function_with_args(xx, yy):
        time.sleep(0.2)
        return xx + yy

    result = function_with_args(2, 3)
    assert result == 5


def test_timeout_with_keyword_arguments():
    """Test timeout decorator with functions that take keyword arguments."""

    @timeout(seconds=1)
    def function_with_kwargs(xx=0, yy=0):
        time.sleep(0.2)
        return xx * yy

    result = function_with_kwargs(xx=5, yy=4)
    assert result == 20


# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:58:41 (ywatanabe)"
#
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-23 19:11:33"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
#
# """
# This script does XYZ.
# """
#
# """
# Imports
# """
#
#
# """
# Config
# """
# # CONFIG = scitex.gen.load_configs()
#
# """
# Functions & Classes
# """
# from multiprocessing import Process, Queue
#
#
# def timeout(seconds=10, error_message="Timeout"):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             def queue_wrapper(queue, args, kwargs):
#                 result = func(*args, **kwargs)
#                 queue.put(result)
#
#             queue = Queue()
#             args_for_process = (queue, args, kwargs)
#             process = Process(target=queue_wrapper, args=args_for_process)
#             process.start()
#             process.join(timeout=seconds)
#
#             if process.is_alive():
#                 process.terminate()
#                 raise TimeoutError(error_message)
#             else:
#                 return queue.get()
#
#         return wrapper
#
#     return decorator
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:58:41 (ywatanabe)"
#
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-23 19:11:33"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
#
# """
# This script does XYZ.
# """
#
# """
# Imports
# """
#
#
# """
# Config
# """
# # CONFIG = scitex.gen.load_configs()
#
# """
# Functions & Classes
# """
# from multiprocessing import Process, Queue
#
#
# def timeout(seconds=10, error_message="Timeout"):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             def queue_wrapper(queue, args, kwargs):
#                 result = func(*args, **kwargs)
#                 queue.put(result)
#
#             queue = Queue()
#             args_for_process = (queue, args, kwargs)
#             process = Process(target=queue_wrapper, args=args_for_process)
#             process.start()
#             process.join(timeout=seconds)
#
#             if process.is_alive():
#                 process.terminate()
#                 raise TimeoutError(error_message)
#             else:
#                 return queue.get()
#
#         return wrapper
#
#     return decorator
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:58:41 (ywatanabe)"
#
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-23 19:11:33"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
#
# """
# This script does XYZ.
# """
#
# """
# Imports
# """
#
#
# """
# Config
# """
# # CONFIG = scitex.gen.load_configs()
#
# """
# Functions & Classes
# """
# from multiprocessing import Process, Queue
#
#
# def timeout(seconds=10, error_message="Timeout"):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             def queue_wrapper(queue, args, kwargs):
#                 result = func(*args, **kwargs)
#                 queue.put(result)
#
#             queue = Queue()
#             args_for_process = (queue, args, kwargs)
#             process = Process(target=queue_wrapper, args=args_for_process)
#             process.start()
#             process.join(timeout=seconds)
#
#             if process.is_alive():
#                 process.terminate()
#                 raise TimeoutError(error_message)
#             else:
#                 return queue.get()
#
#         return wrapper
#
#     return decorator
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:58:41 (ywatanabe)"
#
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-23 19:11:33"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
#
# """
# This script does XYZ.
# """
#
# """
# Imports
# """
#
#
# """
# Config
# """
# # CONFIG = scitex.gen.load_configs()
#
# """
# Functions & Classes
# """
# from multiprocessing import Process, Queue
#
#
# def timeout(seconds=10, error_message="Timeout"):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             def queue_wrapper(queue, args, kwargs):
#                 result = func(*args, **kwargs)
#                 queue.put(result)
#
#             queue = Queue()
#             args_for_process = (queue, args, kwargs)
#             process = Process(target=queue_wrapper, args=args_for_process)
#             process.start()
#             process.join(timeout=seconds)
#
#             if process.is_alive():
#                 process.terminate()
#                 raise TimeoutError(error_message)
#             else:
#                 return queue.get()
#
#         return wrapper
#
#     return decorator
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:58:41 (ywatanabe)"
#
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-23 19:11:33"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
#
# """
# This script does XYZ.
# """
#
# """
# Imports
# """
#
#
# """
# Config
# """
# # CONFIG = scitex.gen.load_configs()
#
# """
# Functions & Classes
# """
# from multiprocessing import Process, Queue
#
#
# def timeout(seconds=10, error_message="Timeout"):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             def queue_wrapper(queue, args, kwargs):
#                 result = func(*args, **kwargs)
#                 queue.put(result)
#
#             queue = Queue()
#             args_for_process = (queue, args, kwargs)
#             process = Process(target=queue_wrapper, args=args_for_process)
#             process.start()
#             process.join(timeout=seconds)
#
#             if process.is_alive():
#                 process.terminate()
#                 raise TimeoutError(error_message)
#             else:
#                 return queue.get()
#
#         return wrapper
#
#     return decorator
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:58:41 (ywatanabe)"
#
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-23 19:11:33"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
#
# """
# This script does XYZ.
# """
#
# """
# Imports
# """
#
#
# """
# Config
# """
# # CONFIG = scitex.gen.load_configs()
#
# """
# Functions & Classes
# """
# from multiprocessing import Process, Queue
#
#
# def timeout(seconds=10, error_message="Timeout"):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             def queue_wrapper(queue, args, kwargs):
#                 result = func(*args, **kwargs)
#                 queue.put(result)
#
#             queue = Queue()
#             args_for_process = (queue, args, kwargs)
#             process = Process(target=queue_wrapper, args=args_for_process)
#             process.start()
#             process.join(timeout=seconds)
#
#             if process.is_alive():
#                 process.terminate()
#                 raise TimeoutError(error_message)
#             else:
#                 return queue.get()
#
#         return wrapper
#
#     return decorator
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:58:41 (ywatanabe)"
#
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-23 19:11:33"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
#
# """
# This script does XYZ.
# """
#
# """
# Imports
# """
#
#
# """
# Config
# """
# # CONFIG = scitex.gen.load_configs()
#
# """
# Functions & Classes
# """
# from multiprocessing import Process, Queue
#
#
# def timeout(seconds=10, error_message="Timeout"):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             def queue_wrapper(queue, args, kwargs):
#                 result = func(*args, **kwargs)
#                 queue.put(result)
#
#             queue = Queue()
#             args_for_process = (queue, args, kwargs)
#             process = Process(target=queue_wrapper, args=args_for_process)
#             process.start()
#             process.join(timeout=seconds)
#
#             if process.is_alive():
#                 process.terminate()
#                 raise TimeoutError(error_message)
#             else:
#                 return queue.get()
#
#         return wrapper
#
#     return decorator
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------


def test_timeout_decorator_success():
    """Test that timeout decorator allows functions to complete within time limit."""

    @timeout(seconds=2, error_message="Test timed out")
    def quick_function():
        time.sleep(0.5)
        return "Success"

    result = quick_function()
    assert result == "Success"


def test_timeout_decorator_raises_exception():
    """Test that timeout decorator raises TimeoutError for functions exceeding time limit."""

    @timeout(seconds=0.5, error_message="Custom timeout message")
    def slow_function():
        time.sleep(1)
        return "This should not be returned"

    with pytest.raises(TimeoutError) as excinfo:
        slow_function()

    assert "Custom timeout message" in str(excinfo.value)


def test_timeout_with_arguments():
    """Test timeout decorator with functions that take arguments."""

    @timeout(seconds=1)
    def function_with_args(xx, yy):
        time.sleep(0.2)
        return xx + yy

    result = function_with_args(2, 3)
    assert result == 5


def test_timeout_with_keyword_arguments():
    """Test timeout decorator with functions that take keyword arguments."""

    @timeout(seconds=1)
    def function_with_kwargs(xx=0, yy=0):
        time.sleep(0.2)
        return xx * yy

    result = function_with_kwargs(xx=5, yy=4)
    assert result == 20


# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:58:41 (ywatanabe)"
#
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-23 19:11:33"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
#
# """
# This script does XYZ.
# """
#
# """
# Imports
# """
#
#
# """
# Config
# """
# # CONFIG = scitex.gen.load_configs()
#
# """
# Functions & Classes
# """
# from multiprocessing import Process, Queue
#
#
# def timeout(seconds=10, error_message="Timeout"):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             def queue_wrapper(queue, args, kwargs):
#                 result = func(*args, **kwargs)
#                 queue.put(result)
#
#             queue = Queue()
#             args_for_process = (queue, args, kwargs)
#             process = Process(target=queue_wrapper, args=args_for_process)
#             process.start()
#             process.join(timeout=seconds)
#
#             if process.is_alive():
#                 process.terminate()
#                 raise TimeoutError(error_message)
#             else:
#                 return queue.get()
#
#         return wrapper
#
#     return decorator
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/decorators/_timeout.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:58:41 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/decorators/_timeout.py
#
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-23 19:11:33"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
#
# """
# This script does XYZ.
# """
#
# """
# Imports
# """
#
#
# """
# Config
# """
# # CONFIG = scitex.gen.load_configs()
#
# """
# Functions & Classes
# """
# from multiprocessing import Process, Queue
#
#
# def timeout(seconds=10, error_message="Timeout"):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             def queue_wrapper(queue, args, kwargs):
#                 result = func(*args, **kwargs)
#                 queue.put(result)
#
#             queue = Queue()
#             args_for_process = (queue, args, kwargs)
#             process = Process(target=queue_wrapper, args=args_for_process)
#             process.start()
#             process.join(timeout=seconds)
#
#             if process.is_alive():
#                 process.terminate()
#                 raise TimeoutError(error_message)
#             else:
#                 return queue.get()
#
#         return wrapper
#
#     return decorator
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/decorators/_timeout.py
# --------------------------------------------------------------------------------
