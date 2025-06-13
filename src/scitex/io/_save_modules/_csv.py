#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:12:18 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_csv.py

import os
import pandas as pd
import numpy as np


def _save_csv(obj, spath: str, **kwargs) -> None:
    """
    Save data to a CSV file, handling various input types appropriately.
    
    Parameters
    ----------
    obj : Any
        The object to save. Can be DataFrame, Series, ndarray, list, tuple, dict, or scalar.
    spath : str
        Path where the CSV file will be saved.
    **kwargs : dict
        Additional keyword arguments to pass to the pandas to_csv method.
        
    Returns
    -------
    None
    
    Raises
    ------
    ValueError
        If the object type cannot be converted to CSV format.
    """
    # Check if path already exists
    if os.path.exists(spath):
        # Calculate hash of new data
        data_hash = None

        # Process based on type
        if isinstance(obj, (pd.Series, pd.DataFrame)):
            data_hash = hash(obj.to_string())
        elif isinstance(obj, np.ndarray):
            data_hash = hash(pd.DataFrame(obj).to_string())
        else:
            # For other types, create a string representation and hash it
            try:
                data_str = str(obj)
                data_hash = hash(data_str)
            except:
                # If we can't hash it, proceed with saving
                pass

        # Compare with existing file if hash calculation was successful
        if data_hash is not None:
            try:
                existing_df = pd.read_csv(spath)
                existing_hash = hash(existing_df.to_string())

                # Skip if hashes match
                if existing_hash == data_hash:
                    return
            except:
                # If reading fails, proceed with saving
                pass

    # Set default index=False if not explicitly specified in kwargs
    if 'index' not in kwargs:
        kwargs['index'] = False
        
    # Save the file based on type
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        obj.to_csv(spath, **kwargs)
    elif isinstance(obj, np.ndarray):
        pd.DataFrame(obj).to_csv(spath, **kwargs)
    elif isinstance(obj, (int, float)):
        pd.DataFrame([obj]).to_csv(spath, **kwargs)
    elif isinstance(obj, (list, tuple)):
        if all(isinstance(x, (int, float)) for x in obj):
            pd.DataFrame(obj).to_csv(spath, **kwargs)
        elif all(isinstance(x, pd.DataFrame) for x in obj):
            pd.concat(obj).to_csv(spath, **kwargs)
        else:
            pd.DataFrame({"data": obj}).to_csv(spath, **kwargs)
    elif isinstance(obj, dict):
        pd.DataFrame.from_dict(obj).to_csv(spath, **kwargs)
    else:
        try:
            pd.DataFrame({"data": [obj]}).to_csv(spath, **kwargs)
        except:
            raise ValueError(f"Unable to save type {type(obj)} as CSV")
