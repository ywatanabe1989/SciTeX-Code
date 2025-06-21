#!/usr/bin/env python3
"""
Example showing the fixed HDF5 save functionality with key and override parameters.

The key improvements:
1. Use 'key' parameter instead of 'path' or 'group_path'
2. Skip existing keys by default (unless override=True)
3. Proper handling of nested groups/keys
"""

import numpy as np
import scitex as stx

# Example for your PAC script:
# This is how the save call should look now:

pac_results_with_metadata = {
    'pac_values': np.random.rand(10, 10),
    'metadata': {'seizure_id': 'test_001', 'duration': 60}
}

lpath_pac_h5 = './pac_data.h5'
h5_key = 'patient_23/seizure_001/pac'

# Save with the new syntax
stx.io.save(
    pac_results_with_metadata,
    lpath_pac_h5,
    key=h5_key,  # Now using 'key' instead of 'path'
    override=False,  # Skip if key exists (default behavior)
    symlink_from_cwd=True,
)

# If you want to override existing data:
# stx.io.save(
#     pac_results_with_metadata,
#     lpath_pac_h5,
#     key=h5_key,
#     override=True,  # This will overwrite existing data
#     symlink_from_cwd=True,
# )