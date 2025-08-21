#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-10 15:57:54 (ywatanabe)"


# FUnctions

if __name__ == "__main__":
    import scitex
    import sys

    import matplotlib.pyplot as plt

    import torch

    # Start
    CONFIG, sys.stdout, sys.stderr, plt, cc = scitex.session.start(sys, plt)

    # Close
    scitex.session.close(CONFIG)

    """
    /home/ywatanabe/proj/scitex/src/scitex/dsp/template.py
    """

    # EOF
