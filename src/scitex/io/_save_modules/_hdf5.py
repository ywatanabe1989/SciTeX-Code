#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 19:06:19 (ywatanabe)"
# File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/.claude-worktree/mngs_repo/src/scitex/io/_save_modules/_hdf5.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/_save_modules/_hdf5.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import h5py


def _save_hdf5(obj, spath, group_path=None, **kwargs):
    """
    Save a dictionary of arrays or a single array to an HDF5 file.

    Parameters
    ----------
    obj : dict or array-like
        Dictionary of arrays to save (keys will be dataset names) or 
        a single array/data to save (will be saved as 'data').
    spath : str
        Path where the HDF5 file will be saved.
    group_path : str, optional
        Path to the group within the HDF5 file. If None, saves to root.
    **kwargs : dict
        Additional keyword arguments passed to create_dataset.
        Common: compression='gzip', compression_opts=9, shuffle=True

    Returns
    -------
    None
    """
    import numpy as np

    # Convert single array to dict
    if not isinstance(obj, dict):
        obj = {'data': obj}

    # Set default compression if not specified
    if "compression" not in kwargs:
        kwargs["compression"] = "gzip"

    mode = "a" if group_path else "w"

    with h5py.File(spath, mode) as hf:
        if group_path:
            if group_path in hf:
                del hf[group_path]
            group = hf.create_group(group_path)
        else:
            group = hf

        for name, data in obj.items():
            try:
                # Check if data is scalar and remove incompatible options
                if np.isscalar(data) or (isinstance(data, np.ndarray) and data.ndim == 0):
                    # Remove chunk/compression options for scalars
                    scalar_kwargs = {k: v for k, v in kwargs.items() 
                                   if k not in ['chunks', 'compression', 'compression_opts', 
                                               'shuffle', 'fletcher32', 'maxshape']}
                    group.create_dataset(name, data=data, **scalar_kwargs)
                else:
                    group.create_dataset(name, data=data, **kwargs)
            except TypeError as e:
                if "Object dtype" in str(
                    e
                ) or "has no native HDF5 equivalent" in str(e):
                    if isinstance(data, np.ndarray) and data.dtype == object:
                        if all(isinstance(item, str) for item in data.flat):
                            dt = h5py.string_dtype(encoding="utf-8")
                            group.create_dataset(
                                name, data=data.astype(dt), **kwargs
                            )
                        else:
                            str_data = np.array(
                                [str(item) for item in data.flat]
                            ).reshape(data.shape)
                            dt = h5py.string_dtype(encoding="utf-8")
                            group.create_dataset(
                                name, data=str_data, dtype=dt, **kwargs
                            )
                    else:
                        group.attrs[name] = str(data)
                else:
                    raise


# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-16 12:24:04 (ywatanabe)"
# # File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_hdf5.py

# import h5py


# def _save_hdf5(obj, spath, group_path=None, **kwargs):
#     """
#     Save a dictionary of arrays to an HDF5 file.

#     Parameters
#     ----------
#     obj : dict
#         Dictionary of arrays to save. Keys will be dataset names.
#     spath : str
#         Path where the HDF5 file will be saved.
#     group_path : str, optional
#         Path to the group within the HDF5 file. If None, saves to root.
#     **kwargs : dict
#         Additional keyword arguments passed to create_dataset.

#     Returns
#     -------
#     None
#     """
#     import numpy as np

#     name_list, obj_list = [], []
#     for k, v in obj.items():
#         name_list.append(k)
#         obj_list.append(v)

#     with h5py.File(spath, "w") as hf:
#         # If group_path is specified, create/get the group
#         if group_path:
#             group = hf.require_group(group_path)
#         else:
#             group = hf

#         for name, data in zip(name_list, obj_list):
#             try:
#                 # Try to save directly
#                 group.create_dataset(name, data=data, **kwargs)
#             except TypeError as e:
#                 if "Object dtype" in str(e) or "has no native HDF5 equivalent" in str(e):
#                     # Handle object dtype by converting to appropriate format
#                     if isinstance(data, np.ndarray) and data.dtype == object:
#                         # Try to convert to string array
#                         try:
#                             # Check if all elements are strings
#                             if all(isinstance(item, str) for item in data.flat):
#                                 # Save as variable-length string
#                                 dt = h5py.string_dtype(encoding='utf-8')
#                                 group.create_dataset(name, data=data.astype(dt), **kwargs)
#                             else:
#                                 # Convert to string representation
#                                 str_data = np.array([str(item) for item in data.flat]).reshape(data.shape)
#                                 dt = h5py.string_dtype(encoding='utf-8')
#                                 group.create_dataset(name, data=str_data, dtype=dt, **kwargs)
#                         except Exception:
#                             # If conversion fails, save as attributes or skip
#                             group.attrs[name] = str(data)
#                             print(f"Warning: Dataset '{name}' saved as attribute due to incompatible dtype")
#                     else:
#                         # For non-array objects, save as attribute
#                         group.attrs[name] = str(data)
#                         print(f"Warning: Dataset '{name}' saved as attribute due to incompatible type")
#                 else:
#                     raise  # Re-raise if it's a different error

# EOF
