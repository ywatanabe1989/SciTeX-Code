#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test for scitex.plt.close() function

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import matplotlib.pyplot as plt
import scitex.plt as mplt

def test_close_no_args():
    """Test scitex.plt.close() without arguments."""
    print("Testing scitex.plt.close() without arguments...")
    
    # Create some figures to close
    fig1 = mplt.figure()
    fig2 = mplt.figure()
    
    # Check how many figures are open
    num_figs_before = len(plt.get_fignums())
    print(f"Number of figures before close(): {num_figs_before}")
    
    # Close all figures
    mplt.close()
    
    # Check how many figures are open after close
    num_figs_after = len(plt.get_fignums())
    print(f"Number of figures after close(): {num_figs_after}")
    
    return num_figs_after == 0

def test_close_with_arg():
    """Test scitex.plt.close() with a specific figure argument."""
    print("\nTesting scitex.plt.close() with a specific figure argument...")
    
    # Create some figures to close
    fig1 = mplt.figure()
    fig2 = mplt.figure()
    
    # Check how many figures are open
    num_figs_before = len(plt.get_fignums())
    print(f"Number of figures before close(): {num_figs_before}")
    
    # Close just one figure
    mplt.close(fig1)
    
    # Check how many figures are open after closing one
    num_figs_after_one = len(plt.get_fignums())
    print(f"Number of figures after closing one: {num_figs_after_one}")
    
    # Close the remaining figure
    mplt.close(fig2)
    
    # Check how many figures are open after closing all
    num_figs_after_all = len(plt.get_fignums())
    print(f"Number of figures after closing all: {num_figs_after_all}")
    
    return num_figs_after_one == (num_figs_before - 1) and num_figs_after_all == 0

def test_close_all_string():
    """Test scitex.plt.close('all')."""
    print("\nTesting scitex.plt.close('all')...")
    
    # Create some figures to close
    fig1 = mplt.figure()
    fig2 = mplt.figure()
    fig3 = mplt.figure()
    
    # Check how many figures are open
    num_figs_before = len(plt.get_fignums())
    print(f"Number of figures before close('all'): {num_figs_before}")
    
    # Close all figures using 'all' string
    mplt.close('all')
    
    # Check how many figures are open after close
    num_figs_after = len(plt.get_fignums())
    print(f"Number of figures after close('all'): {num_figs_after}")
    
    return num_figs_after == 0

if __name__ == "__main__":
    no_args_success = test_close_no_args()
    with_arg_success = test_close_with_arg()
    all_string_success = test_close_all_string()
    
    print("\nTest Results:")
    print(f"close() test (no args): {'PASSED' if no_args_success else 'FAILED'}")
    print(f"close(fig) test: {'PASSED' if with_arg_success else 'FAILED'}")
    print(f"close('all') test: {'PASSED' if all_string_success else 'FAILED'}")
    print(f"Overall test: {'PASSED' if all([no_args_success, with_arg_success, all_string_success]) else 'FAILED'}")