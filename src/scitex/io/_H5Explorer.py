#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-13 21:00:00 (ywatanabe)"
# File: src/scitex/io/_H5Explorer.py

"""HDF5 file explorer for interactive data inspection."""

import h5py
import numpy as np
from typing import Any, Dict, List, Optional, Union


class H5Explorer:
    """Interactive HDF5 file explorer.
    
    This class provides convenient methods to explore HDF5 files,
    inspect their structure, and load data.
    
    Example:
        >>> explorer = H5Explorer('data.h5')
        >>> explorer.show()  # Display file structure
        >>> data = explorer.load('group1/dataset1')  # Load specific dataset
        >>> explorer.close()
    """
    
    def __init__(self, filepath: str, mode: str = 'r'):
        """Initialize H5Explorer.
        
        Args:
            filepath: Path to HDF5 file
            mode: File opening mode ('r' for read, 'r+' for read/write)
        """
        self.filepath = filepath
        self.mode = mode
        self.file = h5py.File(filepath, mode)
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def close(self):
        """Close the HDF5 file."""
        if hasattr(self, 'file') and self.file:
            self.file.close()
            
    def show(self, path: str = '/', max_depth: Optional[int] = None, 
             indent: str = '', _current_depth: int = 0) -> None:
        """Display HDF5 file structure.
        
        Args:
            path: Starting path in HDF5 file
            max_depth: Maximum depth to explore (None for unlimited)
            indent: Indentation string (used internally)
            _current_depth: Current depth (used internally)
        """
        if max_depth is not None and _current_depth > max_depth:
            return
            
        item = self.file[path] if path != '/' else self.file
        
        if isinstance(item, h5py.Group):
            if path != '/':
                print(f"{indent}[{path.split('/')[-1]}]")
            for key in sorted(item.keys()):
                subpath = f"{path}/{key}".replace('//', '/')
                self.show(subpath, max_depth, indent + '  ', _current_depth + 1)
        elif isinstance(item, h5py.Dataset):
            name = path.split('/')[-1]
            shape = item.shape
            dtype = item.dtype
            size = item.size
            print(f"{indent}{name}: shape={shape}, dtype={dtype}, size={size}")
            
    def keys(self, path: str = '/') -> List[str]:
        """Get keys at specified path.
        
        Args:
            path: Path in HDF5 file
            
        Returns:
            List of keys at the specified path
        """
        item = self.file[path] if path != '/' else self.file
        if isinstance(item, h5py.Group):
            return list(item.keys())
        return []
        
    def load(self, path: str) -> Any:
        """Load data from specified path.
        
        Args:
            path: Path to dataset or group in HDF5 file
            
        Returns:
            Data from the specified path
        """
        item = self.file[path]
        
        if isinstance(item, h5py.Dataset):
            return item[()]
        elif isinstance(item, h5py.Group):
            # Load group as dictionary
            result = {}
            for key in item.keys():
                result[key] = self.load(f"{path}/{key}".replace('//', '/'))
            # Also load attributes
            for key in item.attrs.keys():
                result[f"_attr_{key}"] = item.attrs[key]
            return result
        else:
            return item
            
    def get(self, path: str) -> Any:
        """Alias for load() method for compatibility.
        
        Args:
            path: Path to dataset or group in HDF5 file
            
        Returns:
            Data from the specified path
        """
        return self.load(path)
            
    def get_info(self, path: str = '/') -> Dict[str, Any]:
        """Get information about an item.
        
        Args:
            path: Path to item in HDF5 file
            
        Returns:
            Dictionary with item information
        """
        item = self.file[path] if path != '/' else self.file
        
        info = {
            'path': path,
            'type': type(item).__name__,
        }
        
        if isinstance(item, h5py.Dataset):
            info.update({
                'shape': item.shape,
                'dtype': str(item.dtype),
                'size': item.size,
                'compression': item.compression,
                'chunks': item.chunks,
            })
        elif isinstance(item, h5py.Group):
            info['n_items'] = len(item.keys())
            info['keys'] = list(item.keys())
            
        # Add attributes
        if hasattr(item, 'attrs') and len(item.attrs) > 0:
            info['attributes'] = dict(item.attrs)
            
        return info
        
    def find(self, pattern: str, path: str = '/') -> List[str]:
        """Find items matching pattern.
        
        Args:
            pattern: Pattern to search for in item names
            path: Starting path for search
            
        Returns:
            List of paths matching the pattern
        """
        matches = []
        
        def _search(current_path):
            item = self.file[current_path] if current_path != '/' else self.file
            
            if isinstance(item, h5py.Group):
                for key in item.keys():
                    subpath = f"{current_path}/{key}".replace('//', '/')
                    if pattern.lower() in key.lower():
                        matches.append(subpath)
                    _search(subpath)
            elif pattern.lower() in current_path.split('/')[-1].lower():
                matches.append(current_path)
                
        _search(path)
        return matches
        
    def get_shape(self, path: str) -> Optional[tuple]:
        """Get shape of a dataset.
        
        Args:
            path: Path to dataset
            
        Returns:
            Shape tuple or None if not a dataset
        """
        item = self.file[path]
        if isinstance(item, h5py.Dataset):
            return item.shape
        return None
        
    def get_dtype(self, path: str) -> Optional[np.dtype]:
        """Get dtype of a dataset.
        
        Args:
            path: Path to dataset
            
        Returns:
            Numpy dtype or None if not a dataset
        """
        item = self.file[path]
        if isinstance(item, h5py.Dataset):
            return item.dtype
        return None


# Convenience function
def explore_h5(filepath: str) -> H5Explorer:
    """Create an H5Explorer instance.
    
    Args:
        filepath: Path to HDF5 file
        
    Returns:
        H5Explorer instance
    """
    return H5Explorer(filepath)


# EOF