#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:26:16 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_yaml.py

from ruamel.yaml import YAML


def _save_yaml(obj, spath):
    """
    Save a Python object as a YAML file.
    
    Parameters
    ----------
    obj : dict
        The object to serialize to YAML.
    spath : str
        Path where the YAML file will be saved.
        
    Returns
    -------
    None
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=4, sequence=4, offset=4)

    with open(spath, "w") as f:
        yaml.dump(obj, f)
