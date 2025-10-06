#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-14 11:29:19 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/_sh.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import subprocess
from typing import Union, List, Dict, Literal

import scitex


def sh(
    command_str_or_list: Union[str, List[str]], 
    verbose: bool = True, 
    return_as: Literal["dict", "str"] = "dict"
) -> Union[str, Dict[str, Union[str, int, bool]]]:
    """
    Executes a shell command from Python.

    Parameters:
    - command_str_or_list (str or list): Command to execute. 
        - str: Shell command string (uses shell=True)
        - list: Command and arguments (safer, uses shell=False)
    - verbose (bool): Whether to print command and output.
    - return_as ("dict" or "str"): Return format.
        - "dict": Returns dict with stdout, stderr, exit_code
        - "str": Returns string output for backward compatibility

    Returns:
    - If return_as="str": output (str) - stdout if success, stderr if failure
    - If return_as="dict": dict with keys:
        - 'stdout' (str): Standard output
        - 'stderr' (str): Standard error
        - 'exit_code' (int): Exit code (0 for success)
        - 'success' (bool): True if exit_code == 0
        
    Examples:
    --------
    >>> # String command (uses shell)
    >>> sh("ls -la | grep .py")
    
    >>> # List command (safer, no shell)
    >>> sh(["ls", "-la", "/home"])
    
    >>> # Command with environment variable expansion
    >>> sh(["echo", "$HOME"])  # Won't expand $HOME
    >>> sh("echo $HOME")  # Will expand $HOME
    """
    # Display command
    if verbose:
        if isinstance(command_str_or_list, list):
            cmd_display = " ".join(command_str_or_list)
        else:
            cmd_display = command_str_or_list
        print(scitex.str.color_text(f"{cmd_display}", "yellow"))

    # Execute based on command type
    if isinstance(command_str_or_list, list):
        # List mode: safer, no shell injection
        process = subprocess.Popen(
            command_str_or_list, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    else:
        # String mode: uses shell, supports pipes and redirects
        process = subprocess.Popen(
            command_str_or_list, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    
    stdout_bytes, stderr_bytes = process.communicate()

    # Decode outputs
    stdout = stdout_bytes.decode("utf-8").strip()
    stderr = stderr_bytes.decode("utf-8").strip()
    exit_code = process.returncode

    if return_as == "dict":
        result = {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "success": exit_code == 0,
        }

        if verbose:
            if stdout:
                print(stdout)
            if stderr:
                print(scitex.str.color_text(stderr, "red"))

        return result
    else:
        # Backward compatibility mode
        if exit_code == 0:
            out = stdout
        else:
            out = stderr

        if verbose:
            print(out)

        return out


def sh_run(command, verbose=True):
    """
    Executes a shell command and returns detailed results.
    
    This is a convenience function that always returns a dictionary
    with complete execution information.
    
    Parameters:
    - command (str or list): Command to execute.
        - str: Shell command string (uses shell=True)
        - list: Command and arguments (safer, uses shell=False)
    - verbose (bool): Whether to print command and output.
    
    Returns:
    - dict with keys:
        - 'stdout' (str): Standard output
        - 'stderr' (str): Standard error  
        - 'exit_code' (int): Exit code (0 for success)
        - 'success' (bool): True if exit_code == 0
    
    Examples:
    --------
    >>> # String command with pipe
    >>> result = sh_run("ls -la | grep .py")
    >>> if result['success']:
    ...     print(result['stdout'])
    
    >>> # List command (safer)
    >>> result = sh_run(["ls", "-la", "/home"])
    >>> print(f"Exit code: {result['exit_code']}")
    
    >>> # Command with spaces in arguments
    >>> result = sh_run(["mkdir", "-p", "/tmp/my folder"])  # Handles spaces correctly
    """
    return sh(command, verbose=verbose, return_dict=True)


if __name__ == "__main__":
    import sys

    import matplotlib.pyplot as plt
    import scitex

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(
        sys, plt, verbose=False
    )
    
    # Test backward compatibility
    print("Test 1: Backward compatibility mode")
    output = sh("echo 'Hello World'", verbose=True)
    print(f"Output: {output}\n")
    
    # Test new dict mode
    print("Test 2: Dictionary return mode")
    result = sh("echo 'Hello' && echo 'Error message' >&2", verbose=True, return_dict=True)
    print(f"Result dict: {result}\n")
    
    # Test sh_run convenience function
    print("Test 3: sh_run convenience function")
    result = sh_run("ls -la | head -5")
    print(f"Success: {result['success']}, Exit code: {result['exit_code']}\n")
    
    # Test error handling
    print("Test 4: Error handling")
    result = sh_run("cat /nonexistent/file", verbose=False)
    print(f"Success: {result['success']}")
    print(f"Exit code: {result['exit_code']}")
    print(f"Stderr: {result['stderr']}\n")
    
    scitex.session.close(CONFIG, verbose=False, notify=False)

# EOF
