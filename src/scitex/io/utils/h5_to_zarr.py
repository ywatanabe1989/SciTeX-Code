#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-12 05:30:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/utils/h5_to_zarr.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/io/utils/h5_to_zarr.py"

"""
1. Functionality:
   - Migrates HDF5 files to Zarr format
   - Preserves hierarchical structure and attributes
   - Supports batch migration of multiple files
2. Input:
   - HDF5 file path(s)
   - Optional Zarr output path(s)
   - Migration options (compression, chunking)
3. Output:
   - Zarr store(s) with migrated data
4. Prerequisites:
   - h5py, zarr, numpy
"""

"""Imports"""
import h5py
import zarr
import numpy as np
import os
from pathlib import Path
from typing import Optional, Union, Dict, Any, List, Tuple
import warnings
from tqdm import tqdm

from ...errors import (
    IOError as SciTeXIOError,
    FileFormatError,
    PathNotFoundError,
    check_file_exists,
    check_path,
    warn_data_loss,
    warn_performance
)


def _get_zarr_compressor(compressor: Optional[Union[str, Any]] = "zstd") -> Optional[Any]:
    """Get Zarr compressor object from string name."""
    if compressor is None:
        return None
    
    if not isinstance(compressor, str):
        return compressor
    
    from numcodecs import Zstd, LZ4, GZip, Blosc
    
    compressor_map = {
        "zstd": Zstd(level=3),
        "lz4": LZ4(acceleration=1),
        "gzip": GZip(level=5),
        "blosc": Blosc(cname='zstd', clevel=3, shuffle=Blosc.BITSHUFFLE)
    }
    
    return compressor_map.get(compressor.lower(), Zstd(level=3))


def _infer_chunks(shape: Tuple[int, ...], dtype: np.dtype, 
                  target_chunk_mb: float = 10.0) -> Tuple[int, ...]:
    """Infer reasonable chunk sizes based on array shape and dtype."""
    if len(shape) == 0:  # Scalar
        return None
    
    # Calculate bytes per element
    bytes_per_element = dtype.itemsize
    
    # Target chunk size in elements
    target_elements = (target_chunk_mb * 1024 * 1024) / bytes_per_element
    
    # Calculate chunk shape
    chunks = []
    remaining_elements = target_elements
    
    for dim_size in shape:
        if remaining_elements <= 1:
            chunks.append(1)
        else:
            chunk_dim = min(dim_size, int(remaining_elements))
            chunks.append(chunk_dim)
            remaining_elements = remaining_elements / chunk_dim
    
    return tuple(chunks)


def _copy_h5_attributes(h5_obj: Union[h5py.Group, h5py.Dataset], 
                       zarr_obj: Union[zarr.Group, zarr.Array]) -> None:
    """Copy attributes from HDF5 object to Zarr object."""
    for key, value in h5_obj.attrs.items():
        try:
            # Handle special cases
            if isinstance(value, bytes):
                value = value.decode('utf-8', errors='replace')
            elif isinstance(value, np.ndarray) and value.dtype.kind == 'S':
                # Byte string array
                value = [v.decode('utf-8', errors='replace') for v in value]
            elif isinstance(value, (np.integer, np.floating)):
                value = value.item()  # Convert to Python type
            
            zarr_obj.attrs[key] = value
        except Exception as e:
            warnings.warn(f"Could not copy attribute '{key}': {e}")


def _migrate_dataset(h5_dataset: h5py.Dataset, 
                    zarr_parent: zarr.Group,
                    name: str,
                    compressor: Optional[Any],
                    chunks: Optional[Union[bool, Tuple[int, ...]]] = True,
                    show_progress: bool = False) -> zarr.Array:
    """Migrate a single HDF5 dataset to Zarr."""
    try:
        # Try to access the dataset to check if it's corrupted
        test_access = h5_dataset.shape
        if hasattr(h5_dataset, 'dtype'):
            test_dtype = h5_dataset.dtype
    except Exception as e:
        warnings.warn(f"Skipping corrupted dataset '{name}': {e}")
        return None
    
    # Get dataset info
    shape = h5_dataset.shape
    dtype = h5_dataset.dtype
    
    # Handle chunking
    if chunks is True:
        # Auto-infer chunks
        dataset_chunks = _infer_chunks(shape, dtype)
    elif chunks is False:
        dataset_chunks = None
    else:
        dataset_chunks = chunks
    
    # Handle special dtypes
    if dtype.kind == 'O':  # Object dtype
        warn_data_loss(
            f"Dataset '{name}'",
            "Object dtype will be converted to string or pickled"
        )
        # Try to convert to string array
        try:
            # Check if scalar or array
            if not h5_dataset.shape:  # Scalar dataset
                value = h5_dataset[()]
                if isinstance(value, (bytes, str)):
                    # String scalar - store as 0-d string array
                    zarr_array = zarr_parent.create_dataset(
                        name,
                        data=str(value) if isinstance(value, str) else value.decode('utf-8', errors='replace'),
                        dtype=str,
                        compressor=None
                    )
                else:
                    # Complex object scalar - pickle
                    import pickle
                    pickled_data = pickle.dumps(value)
                    zarr_array = zarr_parent.create_dataset(
                        name,
                        data=np.frombuffer(pickled_data, dtype=np.uint8),
                        compressor=compressor
                    )
                    zarr_array.attrs["_type"] = "pickled_scalar"
            elif len(h5_dataset) > 0:  # Non-empty array
                first_elem = h5_dataset[0]
                if isinstance(first_elem, (bytes, str)):
                    # String data - convert to string array
                    data = np.array([
                        str(item) if isinstance(item, str) else item.decode('utf-8', errors='replace')
                        for item in h5_dataset[:]
                    ])
                    zarr_array = zarr_parent.create_dataset(
                        name,
                        data=data,
                        dtype=data.dtype,  # Will be string dtype
                        compressor=None
                    )
                else:
                    # Complex object - pickle
                    import pickle
                    pickled_data = pickle.dumps(h5_dataset[:])
                    zarr_array = zarr_parent.create_dataset(
                        name,
                        data=np.frombuffer(pickled_data, dtype=np.uint8),
                        compressor=compressor
                    )
                    zarr_array.attrs["_type"] = "pickled"
            else:
                # Empty dataset - use empty string array
                zarr_array = zarr_parent.create_dataset(
                    name,
                    shape=shape,
                    dtype='U1',  # Unicode string dtype
                    fill_value=''
                )
        except Exception as e:
            raise SciTeXIOError(
                f"Failed to migrate object dtype dataset '{name}'",
                context={"error": str(e)},
                suggestion="Consider converting object arrays before migration"
            )
    else:
        # Regular array
        if show_progress and shape and np.prod(shape) > 1e6:
            # Large array - show progress
            print(f"  Migrating large dataset '{name}' {shape} {dtype}...")
        
        # Create Zarr array
        zarr_array = zarr_parent.create_dataset(
            name,
            shape=shape,
            dtype=dtype,
            chunks=dataset_chunks,
            compressor=compressor
        )
        
        # Copy data
        try:
            if shape:  # Non-scalar
                if len(shape) > 0 and np.prod(shape) > 0:
                    zarr_array[:] = h5_dataset[:]
            else:  # Scalar
                zarr_array[()] = h5_dataset[()]
        except Exception as e:
            warnings.warn(f"Error copying data for dataset '{name}': {e}. Leaving empty.")
            # The array structure is created but data might be zeros/empty
    
    # Copy attributes
    _copy_h5_attributes(h5_dataset, zarr_array)
    
    return zarr_array


def _migrate_group(h5_group: h5py.Group,
                  zarr_parent: zarr.Group,
                  compressor: Optional[Any],
                  chunks: Optional[Union[bool, Tuple[int, ...]]] = True,
                  show_progress: bool = False,
                  _level: int = 0) -> None:
    """Recursively migrate HDF5 group to Zarr."""
    # Copy group attributes
    _copy_h5_attributes(h5_group, zarr_parent)
    
    # Iterate through group items
    try:
        keys = list(h5_group.keys())
    except Exception as e:
        warnings.warn(f"Cannot access group keys: {e}")
        return
    
    for key in keys:
        try:
            item = h5_group[key]
        except Exception as e:
            warnings.warn(f"Cannot access item '{key}': {e}")
            continue
        
        if isinstance(item, h5py.Dataset):
            # Migrate dataset
            result = _migrate_dataset(item, zarr_parent, key, compressor, chunks, show_progress)
            if result is None:
                print(f"  Warning: Skipped corrupted dataset '{key}'")
        
        elif isinstance(item, h5py.Group):
            # Create subgroup and migrate recursively
            if show_progress and _level < 2:
                print(f"{'  ' * _level}Migrating group '{key}'...")
            
            zarr_subgroup = zarr_parent.create_group(key)
            _migrate_group(item, zarr_subgroup, compressor, chunks, 
                          show_progress, _level + 1)
        
        else:
            warnings.warn(f"Unknown HDF5 object type for '{key}': {type(item)}")


def migrate_h5_to_zarr(h5_path: Union[str, Path],
                      zarr_path: Optional[Union[str, Path]] = None,
                      compressor: Optional[Union[str, Any]] = "zstd",
                      chunks: Optional[Union[bool, Tuple[int, ...]]] = True,
                      overwrite: bool = False,
                      show_progress: bool = True,
                      validate: bool = True) -> str:
    """
    Migrate HDF5 file to Zarr format.
    
    Parameters
    ----------
    h5_path : str or Path
        Path to input HDF5 file
    zarr_path : str or Path, optional
        Path for output Zarr store. If None, uses h5_path with .zarr extension
    compressor : str or compressor object, optional
        Compression to use: 'zstd', 'lz4', 'gzip', 'blosc', or None
    chunks : bool or tuple, optional
        Chunking strategy. True for auto, False for no chunks, or specific shape
    overwrite : bool, optional
        Whether to overwrite existing Zarr store
    show_progress : bool, optional
        Whether to show migration progress
    validate : bool, optional
        Whether to validate the migration by comparing shapes
        
    Returns
    -------
    str
        Path to created Zarr store
        
    Raises
    ------
    PathNotFoundError
        If HDF5 file doesn't exist
    FileFormatError
        If input is not a valid HDF5 file
    SciTeXIOError
        If migration fails
        
    Examples
    --------
    >>> # Basic migration
    >>> migrate_h5_to_zarr("data.h5")
    
    >>> # Custom output and compression
    >>> migrate_h5_to_zarr("data.h5", "output.zarr", compressor="lz4")
    
    >>> # Specific chunking
    >>> migrate_h5_to_zarr("large_data.h5", chunks=(100, 100, 10))
    """
    # Validate input path
    h5_path = Path(h5_path)
    # Allow absolute paths
    if not h5_path.is_absolute():
        check_file_exists(str(h5_path))
    else:
        # For absolute paths, just check existence
        if not h5_path.exists():
            raise PathNotFoundError(str(h5_path))
    
    # Determine output path
    if zarr_path is None:
        zarr_path = h5_path.with_suffix('.zarr')
    else:
        zarr_path = Path(zarr_path)
        # Allow absolute paths if explicitly provided
        if not zarr_path.is_absolute():
            check_path(str(zarr_path))
    
    # Check if output exists
    if zarr_path.exists() and not overwrite:
        raise SciTeXIOError(
            f"Zarr store already exists: {zarr_path}",
            suggestion="Use overwrite=True to replace existing store"
        )
    
    # Get compressor
    compressor_obj = _get_zarr_compressor(compressor)
    
    if show_progress:
        print(f"Migrating HDF5 to Zarr:")
        print(f"  Source: {h5_path}")
        print(f"  Target: {zarr_path}")
        print(f"  Compressor: {compressor}")
    
    try:
        # Open HDF5 file
        with h5py.File(str(h5_path), 'r') as h5_file:
            # Create or open Zarr store
            if zarr_path.exists() and overwrite:
                import shutil
                shutil.rmtree(zarr_path)
            
            zarr_store = zarr.open(str(zarr_path), mode='w')
            
            # Migrate root attributes
            _copy_h5_attributes(h5_file, zarr_store)
            
            # Migrate all groups and datasets
            _migrate_group(h5_file, zarr_store, compressor_obj, chunks, show_progress)
            
            if show_progress:
                print("Migration complete!")
            
            # Validation
            if validate:
                if show_progress:
                    print("Validating migration...")
                _validate_migration(h5_file, zarr_store, show_progress)
    
    except OSError as e:
        if "Unable to open file" in str(e) or "bad symbol table" in str(e):
            # File is corrupted
            warnings.warn(f"HDF5 file appears to be corrupted: {h5_path}")
            raise FileFormatError(
                str(h5_path),
                expected_format="HDF5",
                actual_format="corrupted HDF5"
            )
        else:
            raise SciTeXIOError(
                f"Failed to open HDF5 file: {h5_path}",
                context={"error": str(e)}
            )
    except Exception as e:
        raise SciTeXIOError(
            f"Migration failed: {str(e)}",
            context={"h5_path": str(h5_path), "zarr_path": str(zarr_path)},
            suggestion="Check file permissions and disk space"
        )
    
    return str(zarr_path)


def _validate_migration(h5_file: h5py.File, zarr_store: zarr.Group, 
                       show_progress: bool = False) -> None:
    """Validate that migration preserved data structure."""
    def validate_item(h5_item, zarr_item, path=""):
        if isinstance(h5_item, h5py.Dataset) and isinstance(zarr_item, zarr.Array):
            # Compare shapes
            if h5_item.shape != zarr_item.shape:
                raise SciTeXIOError(
                    f"Shape mismatch at {path}",
                    context={
                        "h5_shape": h5_item.shape,
                        "zarr_shape": zarr_item.shape
                    }
                )
            # Compare dtypes (approximately)
            if h5_item.dtype.kind != 'O' and zarr_item.dtype.kind != 'O':
                if h5_item.dtype != zarr_item.dtype:
                    warnings.warn(
                        f"Dtype mismatch at {path}: "
                        f"HDF5={h5_item.dtype}, Zarr={zarr_item.dtype}"
                    )
        
        elif isinstance(h5_item, h5py.Group) and isinstance(zarr_item, zarr.Group):
            # Compare keys
            h5_keys = set(h5_item.keys())
            zarr_keys = set(zarr_item.keys())
            
            if h5_keys != zarr_keys:
                raise SciTeXIOError(
                    f"Key mismatch at {path}",
                    context={
                        "h5_only": h5_keys - zarr_keys,
                        "zarr_only": zarr_keys - h5_keys
                    }
                )
            
            # Validate recursively
            for key in h5_keys:
                validate_item(h5_item[key], zarr_item[key], f"{path}/{key}")
    
    validate_item(h5_file, zarr_store)
    
    if show_progress:
        print("  Validation passed ✓")


def migrate_h5_to_zarr_batch(h5_paths: List[Union[str, Path]],
                           output_dir: Optional[Union[str, Path]] = None,
                           compressor: Optional[Union[str, Any]] = "zstd",
                           chunks: Optional[Union[bool, Tuple[int, ...]]] = True,
                           overwrite: bool = False,
                           parallel: bool = False,
                           n_workers: Optional[int] = None) -> List[str]:
    """
    Migrate multiple HDF5 files to Zarr format.
    
    Parameters
    ----------
    h5_paths : list of str or Path
        List of HDF5 files to migrate
    output_dir : str or Path, optional
        Directory for output Zarr stores. If None, creates alongside HDF5 files
    compressor : str or compressor object, optional
        Compression to use
    chunks : bool or tuple, optional
        Chunking strategy
    overwrite : bool, optional
        Whether to overwrite existing Zarr stores
    parallel : bool, optional
        Whether to process files in parallel
    n_workers : int, optional
        Number of parallel workers (defaults to CPU count)
        
    Returns
    -------
    list of str
        Paths to created Zarr stores
        
    Examples
    --------
    >>> # Migrate all HDF5 files in directory
    >>> import glob
    >>> h5_files = glob.glob("data/*.h5")
    >>> zarr_paths = migrate_h5_to_zarr_batch(h5_files)
    
    >>> # Parallel migration to specific directory
    >>> zarr_paths = migrate_h5_to_zarr_batch(
    ...     h5_files, 
    ...     output_dir="zarr_data/",
    ...     parallel=True
    ... )
    """
    h5_paths = [Path(p) for p in h5_paths]
    
    # Determine output paths
    zarr_paths = []
    for h5_path in h5_paths:
        if output_dir is None:
            zarr_path = h5_path.with_suffix('.zarr')
        else:
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)
            zarr_path = output_dir_path / h5_path.with_suffix('.zarr').name
        zarr_paths.append(zarr_path)
    
    print(f"Migrating {len(h5_paths)} HDF5 files to Zarr format...")
    
    if parallel and len(h5_paths) > 1:
        # Parallel processing
        from concurrent.futures import ProcessPoolExecutor, as_completed
        
        if n_workers is None:
            n_workers = min(os.cpu_count() or 4, len(h5_paths))
        
        print(f"Using {n_workers} parallel workers...")
        
        # Define a module-level function to avoid pickling issues
        import functools
        migrate_func = functools.partial(
            migrate_h5_to_zarr,
            compressor=compressor,
            chunks=chunks,
            overwrite=overwrite,
            show_progress=False,
            validate=True
        )
        
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            futures = {
                executor.submit(migrate_func, h5_path, zarr_path): i
                for i, (h5_path, zarr_path) in enumerate(zip(h5_paths, zarr_paths))
            }
            
            results = []
            with tqdm(total=len(h5_paths), desc="Migrating") as pbar:
                for future in as_completed(futures):
                    idx = futures[future]
                    try:
                        result = future.result()
                        results.append((idx, result))
                        pbar.update(1)
                    except Exception as e:
                        print(f"\nError migrating {h5_paths[idx]}: {e}")
                        results.append((idx, None))
                        pbar.update(1)
            
            # Sort results by original order
            results.sort(key=lambda x: x[0])
            migrated_paths = [r[1] for r in results if r[1] is not None]
    
    else:
        # Sequential processing
        migrated_paths = []
        for h5_path, zarr_path in tqdm(
            zip(h5_paths, zarr_paths), 
            total=len(h5_paths),
            desc="Migrating"
        ):
            try:
                result = migrate_h5_to_zarr(
                    h5_path, zarr_path,
                    compressor=compressor,
                    chunks=chunks,
                    overwrite=overwrite,
                    show_progress=False,
                    validate=True
                )
                migrated_paths.append(result)
            except Exception as e:
                print(f"\nError migrating {h5_path}: {e}")
    
    print(f"\nSuccessfully migrated {len(migrated_paths)}/{len(h5_paths)} files")
    
    return migrated_paths


# Example usage in docstring
if __name__ == "__main__":
    # Example 1: Basic migration
    # migrate_h5_to_zarr("data.h5")
    
    # Example 2: Custom settings
    # migrate_h5_to_zarr(
    #     "large_data.h5",
    #     "compressed_data.zarr",
    #     compressor="blosc",
    #     chunks=(100, 100, 10)
    # )
    
    # Example 3: Batch migration
    # import glob
    # h5_files = glob.glob("*.h5")
    # migrate_h5_to_zarr_batch(h5_files, parallel=True)
    
    pass