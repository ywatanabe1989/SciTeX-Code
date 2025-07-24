#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:17:12 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_text.py


def _save_text(obj, spath):
    """
    Save text content to a file.
    
    Parameters
    ----------
    obj : str
        The text content to save.
    spath : str
        Path where the text file will be saved.
        
    Returns
    -------
    None
    """
    with open(spath, "w") as file:
        file.write(obj)
