#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-02-14 21:12:25 (ywatanabe)"
# File: ./src/scitex/gen/_close.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_close.py"

import os
import re
import shutil
import time
from datetime import datetime
from glob import glob as _glob

from ..io import flush as scitex_io_flush
from ..io import save as scitex_io_save
from ..str._printc import printc
from ..utils._notify import notify as scitex_utils_notify


def _format_diff_time(diff_time):
    # Get total seconds from the timedelta object
    total_seconds = int(diff_time.total_seconds())

    # Calculate hours, minutes and seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Format the time difference as a string
    diff_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return diff_time_str


def _process_timestamp(CONFIG, verbose=True):
    try:
        CONFIG["END_TIME"] = datetime.now()
        CONFIG["RUN_TIME"] = _format_diff_time(
            CONFIG["END_TIME"] - CONFIG["START_TIME"]
        )
        if verbose:
            print()
            print(f"START TIME: {CONFIG['START_TIME']}")
            print(f"END TIME: {CONFIG['END_TIME']}")
            print(f"RUN TIME: {CONFIG['RUN_TIME']}")
            print()

    except Exception as e:
        print(e)

    return CONFIG


def _save_configs(CONFIG):
    scitex_io_save(CONFIG, CONFIG["SDIR"] + "CONFIGS/CONFIG.pkl", verbose=False)
    scitex_io_save(CONFIG, CONFIG["SDIR"] + "CONFIGS/CONFIG.yaml", verbose=False)


def _escape_ansi_from_log_files(log_files):
    """Remove ANSI escape sequences from log files.
    
    Parameters
    ----------
    log_files : list
        List of log file paths to clean
    """
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    # ANSI code escape
    for f in log_files:
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
        cleaned_content = ansi_escape.sub("", content)
        with open(f, "w", encoding="utf-8") as file:
            file.write(cleaned_content)


def _args_to_str(args_dict):
    """Convert args dictionary to formatted string."""
    if args_dict:
        max_key_length = max(len(str(k)) for k in args_dict.keys())
        return "\n".join(
            f"{str(k):<{max_key_length}} : {str(v)}"
            for k, v in sorted(args_dict.items())
        )
    else:
        return ""


def close(CONFIG, message=":)", notify=False, verbose=True, exit_status=None):
    sys = None  # Initialize sys outside try block
    try:
        CONFIG.EXIT_STATUS = exit_status
        CONFIG = CONFIG.to_dict()
        CONFIG = _process_timestamp(CONFIG, verbose=verbose)
        sys = CONFIG.pop("sys")
        _save_configs(CONFIG)
        # scitex_io_flush(sys=sys)

        # RUNNING to RUNNING2FINISHEDED
        CONFIG = running2finished(CONFIG, exit_status=exit_status)
        # scitex_io_flush(sys=sys)

        # ANSI code escape
        log_files = _glob(CONFIG["SDIR"] + "logs/*.log")
        _escape_ansi_from_log_files(log_files)
        # scitex_io_flush(sys=sys)

        if CONFIG.get("ARGS"):
            message += f"\n{_args_to_str(CONFIG.get('ARGS'))}"

        if notify:
            try:
                message = (
                    f"[DEBUG]\n" + str(message)
                    if CONFIG.get("DEBUG", False)
                    else str(message)
                )
                scitex_utils_notify(
                    message=message,
                    ID=CONFIG["ID"],
                    file=CONFIG.get("FILE"),
                    attachment_paths=log_files,
                    verbose=verbose,
                )
                # scitex_io_flush(sys=sys)
            except Exception as e:
                print(e)

    finally:
        # Only close if they're custom file objects (Tee objects)
        if sys:
            try:
                # First, flush all outputs
                if hasattr(sys, "stdout") and hasattr(sys.stdout, "flush"):
                    sys.stdout.flush()
                if hasattr(sys, "stderr") and hasattr(sys.stderr, "flush"):
                    sys.stderr.flush()

                # Then close Tee objects
                if hasattr(sys, "stdout") and hasattr(sys.stdout, "_log_file"):
                    sys.stdout.close()
                if hasattr(sys, "stderr") and hasattr(sys.stderr, "_log_file"):
                    sys.stderr.close()
            except Exception:
                # Silent fail to ensure logs are saved even if there's an error
                pass
    # finally:
    #     # Ensure file handles are closed
    #     if hasattr(sys, 'stdout') and hasattr(sys.stdout, 'close'):
    #         sys.stdout.close()
    #     if hasattr(sys, 'stderr') and hasattr(sys.stderr, 'close'):
    #         sys.stderr.close()
    # # try:
    # #     sys.stdout.close()
    # #     sys.stderr.close()
    # # except Exception as e:
    # #     print(e)


def running2finished(CONFIG, exit_status=None, remove_src_dir=True, max_wait=60):
    if exit_status == 0:
        dest_dir = CONFIG["SDIR"].replace("RUNNING/", "FINISHED_SUCCESS/")
    elif exit_status == 1:
        dest_dir = CONFIG["SDIR"].replace("RUNNING/", "FINISHED_ERROR/")
    else:  # exit_status is None:
        dest_dir = CONFIG["SDIR"].replace("RUNNING/", "FINISHED/")

    src_dir = CONFIG["SDIR"]
    # if dest_dir is None:
    #     dest_dir = src_dir.replace("RUNNING/", "FINISHED/")

    os.makedirs(dest_dir, exist_ok=True)
    try:

        # Copy files individually
        for item in os.listdir(src_dir):
            s = os.path.join(src_dir, item)
            d = os.path.join(dest_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        start_time = time.time()
        while not os.path.exists(dest_dir) and time.time() - start_time < max_wait:
            time.sleep(0.1)
        if os.path.exists(dest_dir):
            printc(
                f"Congratulations! The script completed.\n\n{dest_dir}",
                c="yellow",
            )
            if remove_src_dir:
                shutil.rmtree(src_dir)
        else:
            print(f"Copy operation timed out after {max_wait} seconds")

        CONFIG["SDIR"] = dest_dir
    except Exception as e:
        print(e)

    finally:
        return CONFIG


if __name__ == "__main__":
    import sys

    import matplotlib.pyplot as plt
    from icecream import ic

    from .._start import start

    CONFIG, sys.stdout, sys.stderr, plt, CC = start(sys, plt, verbose=False)

    ic("aaa")
    ic("bbb")
    ic("ccc")

    close(CONFIG)

# EOF
