#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 05:58:41 (ywatanabe)"
# File: ./scitex_repo/src/scitex/decorators/_timeout.py

#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-23 19:11:33"
# Author: Yusuke Watanabe (ywatanabe@scitex.ai)

"""
This script does XYZ.
"""

"""
Imports
"""


"""
Config
"""
# CONFIG = scitex.gen.load_configs()

"""
Functions & Classes
"""
from multiprocessing import Process, Queue


def timeout(seconds=10, error_message="Timeout"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            def queue_wrapper(queue, args, kwargs):
                result = func(*args, **kwargs)
                queue.put(result)

            queue = Queue()
            args_for_process = (queue, args, kwargs)
            process = Process(target=queue_wrapper, args=args_for_process)
            process.start()
            process.join(timeout=seconds)

            if process.is_alive():
                process.terminate()
                raise TimeoutError(error_message)
            else:
                return queue.get()

        return wrapper

    return decorator


# EOF
