"""
This script does XYZ.
"""

# import os
# import sys

# import matplotlib.pyplot as plt

# # Imports
#
# import numpy as np
# import pandas as pd
# import torch
# import torch.nn as nn
# import torch.nn.functional as F

# # Config
# CONFIG = scitex.gen.load_configs()

# Functions
# from IPython import embed as _embed
# import pyperclip

# def embed_with_clipboard_exec():
#     # Try to get text from the clipboard
#     try:
#         clipboard_content = pyperclip.paste()
#     except pyperclip.PyperclipException as e:
#         clipboard_content = ""
#         print("Could not access the clipboard:", e)

#     # Start IPython session with the clipboard content preloaded
#     ipython_shell = embed(header='IPython is now running with the following clipboard content executed:', compile_flags=None)

#     # Optionally, execute the clipboard content automatically
#     if clipboard_content:
#         # Execute the content as if it was typed in directly
#         ipython_shell.run_cell(clipboard_content)


def embed():
    import pyperclip
    from IPython import embed as _embed

    try:
        clipboard_content = pyperclip.paste()
    except pyperclip.PyperclipException as e:
        clipboard_content = ""
        print("Could not access the clipboard:", e)

    print("Clipboard content loaded. Do you want to execute it? [y/n]")
    execute_clipboard = input().strip().lower() == "y"

    # Start IPython shell
    ipython_shell = _embed(
        header="IPython is now running. Clipboard content will be executed if confirmed."
    )

    # Execute if confirmed
    if clipboard_content and execute_clipboard:
        ipython_shell.run_cell(clipboard_content)


if __name__ == "__main__":
    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)

    embed()

    # Close
    scitex.gen.close(CONFIG)

# EOF

"""
/ssh:ywatanabe@444:/home/ywatanabe/proj/entrance/scitex/gen/_embed.py
"""
