#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-06-30 12:11:01 (ywatanabe)"
# /mnt/ssd/ripple-wm-code/scripts/externals/scitex/src/scitex/dsp/_time.py


import numpy as np


def time(start_sec, end_sec, fs):
    # return np.linspace(start_sec, end_sec, (end_sec - start_sec) * fs)
    return scitex.gen.float_linspace(start_sec, end_sec, (end_sec - start_sec) * fs)


def main():
    out = time(10, 15, 256)
    print(out)


if __name__ == "__main__":
    import sys

    import matplotlib.pyplot as plt

    # # Argument Parser
    # import argparse
    # parser = argparse.ArgumentParser(description='')
    # parser.add_argument('--var', '-v', type=int, default=1, help='')
    # parser.add_argument('--flag', '-f', action='store_true', default=False, help='')
    # args = parser.parse_args()
    # Main
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)
    main()
    scitex.gen.close(CONFIG, verbose=False, notify=False)

# EOF
