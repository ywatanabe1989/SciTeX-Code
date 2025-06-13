#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-01-29 07:36:39 (ywatanabe)"

import os
import subprocess


def run_shellscript(lpath_sh, *args):
    # Check if the script is executable, if not, make it executable
    if not os.access(lpath_sh, os.X_OK):
        subprocess.run(["chmod", "+x", lpath_sh])

    # Prepare the command with script path and arguments
    command = [lpath_sh] + list(args)

    # Run the shell script with arguments using run_shellcommand
    return run_shellcommand(*command)
    # return stdout, stderr, exit_code


def run_shellcommand(command, *args):
    # Prepare the command with additional arguments
    full_command = [command] + list(args)

    # Run the command
    result = subprocess.run(
        full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # Get the standard output and error
    stdout = result.stdout
    stderr = result.stderr
    exit_code = result.returncode

    # Check if the command ran successfully
    if exit_code == 0:
        print("Command executed successfully")
        print("Output:", stdout)
    else:
        print("Command failed with error code:", exit_code)
        print("Error:", stderr)

    return {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
    }
