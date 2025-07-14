#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-12 10:14:46 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/suggestions.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/suggestions.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Enhanced HDF5 save with SWMR support for HPC

import time


def _load_hdf5_swmr(lpath, key=None, swmr=True, max_retries=10, **kwargs):
    """Load HDF5 file with SWMR support."""
    for attempt in range(max_retries):
        try:
            with SWMRFile(lpath, "r", swmr=swmr) as h5_file:
                if key:
                    if key not in h5_file:
                        return None
                    target = h5_file[key]
                else:
                    target = h5_file

                # Load data recursively
                return _load_h5_object(target)

        except (OSError, IOError) as e:
            if attempt < max_retries - 1:
                time.sleep(0.1 * (2**attempt))
            else:
                raise

    return None


# Example usage for your PAC calculation
def save_pac_results_hpc(pac_results, h5_path, key, metadata):
    """Save PAC results in HPC environment with proper concurrency handling."""

    # Combine results and metadata
    data_to_save = pac_results.copy()
    data_to_save.update(metadata)

    # Save with SWMR and retries
    _save_hdf5_swmr(
        data_to_save,
        h5_path,
        key=key,
        override=False,  # Don't override existing
        swmr=True,
        compression="gzip",
        compression_opts=4,
        max_retries=20,
    )

# EOF
