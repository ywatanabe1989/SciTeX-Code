#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:26:16 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_yaml.py

from pathlib import Path
from ruamel.yaml import YAML


def _convert_paths_to_strings(obj):
    """
    Recursively convert pathlib.Path objects to strings and DotDict objects to regular dicts in a data structure.
    
    Parameters
    ----------
    obj : any
        The object to process. Can be dict, list, tuple, DotDict, Path, or any other type.
        
    Returns
    -------
    any
        Copy of the object with all Path objects converted to strings and DotDict objects converted to regular dicts.
    """
    if isinstance(obj, Path):
        return str(obj)
    elif hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
        # Handle DotDict or similar objects with to_dict() method
        dict_obj = obj.to_dict()
        return _convert_paths_to_strings(dict_obj)
    elif isinstance(obj, dict):
        return {key: _convert_paths_to_strings(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        converted_list = [_convert_paths_to_strings(item) for item in obj]
        return tuple(converted_list) if isinstance(obj, tuple) else converted_list
    else:
        return obj


def _save_yaml(obj, spath):
    """
    Save a Python object as a YAML file.
    
    Automatically converts any pathlib.Path objects and DotDict objects within 
    the data structure before serialization, as YAML cannot directly serialize 
    these complex objects.
    
    Parameters
    ----------
    obj : dict or DotDict
        The object to serialize to YAML. Can contain pathlib.Path objects and
        DotDict objects, which will be automatically converted to strings and
        regular dicts respectively.
    spath : str
        Path where the YAML file will be saved.
        
    Returns
    -------
    None
    """
    # Convert any Path objects to strings before YAML serialization
    obj_with_strings = _convert_paths_to_strings(obj)
    
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=4, sequence=4, offset=4)

    with open(spath, "w") as f:
        yaml.dump(obj_with_strings, f)
