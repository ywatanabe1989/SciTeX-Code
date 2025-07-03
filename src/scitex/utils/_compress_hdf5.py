#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-10 08:26:28 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/utils/_compress_hdf5.py
# ----------------------------------------
import os

__FILE__ = "/ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/utils/_compress_hdf5.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import numpy as np

# h5py and tqdm imported in functions that need them


def compress_hdf5(input_file, output_file=None, compression_level=4):
    """
    Compress an existing HDF5 file by reading all datasets and rewriting them with compression.

    Parameters:
    -----------
    input_file : str
        Path to the input HDF5 file
    output_file : str, optional
        Path to the output compressed HDF5 file. If None, will use input_file + '.compressed.h5'
    compression_level : int, optional
        Compression level (1-9), higher means more compression but slower processing
    """
    # Import h5py when actually needed
    try:
        import h5py
    except ImportError:
        raise ImportError("h5py is required for HDF5 compression but not installed")
    
    # Import tqdm if available
    try:
        from tqdm import tqdm
    except ImportError:
        tqdm = None
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}.compressed{ext}"

    print(f"Compressing {input_file} to {output_file}")

    with h5py.File(input_file, "r") as src, h5py.File(output_file, "w") as dst:
        # Copy file attributes
        for key, value in src.attrs.items():
            dst.attrs[key] = value

        def copy_dataset(name, obj):
            if isinstance(obj, h5py.Dataset):
                # Print progress for large datasets
                if len(obj.shape) > 0 and obj.shape[0] > 1000000:
                    print(f"Processing large dataset {name} with shape {obj.shape}")

                # Get original dataset attributes
                chunks = True  # Let h5py choose chunking
                if obj.chunks is not None:
                    chunks = obj.chunks

                # Create the compressed dataset
                compressed_data = dst.create_dataset(
                    name,
                    shape=obj.shape,
                    dtype=obj.dtype,
                    compression="gzip",
                    compression_opts=compression_level,
                    chunks=chunks,
                )

                # Copy data and attributes
                if len(obj.shape) > 0 and obj.shape[0] > 10000000:
                    # Process large datasets in chunks to avoid memory issues
                    chunk_size = 5000000  # Adjust based on your available RAM
                    for i in tqdm(
                        range(0, obj.shape[0], chunk_size), desc=f"Copying {name}"
                    ):
                        end = min(i + chunk_size, obj.shape[0])
                        if len(obj.shape) == 1:
                            compressed_data[i:end] = obj[i:end]
                        else:
                            compressed_data[i:end, ...] = obj[i:end, ...]
                else:
                    # Small enough to copy at once
                    compressed_data[()] = obj[()]

                # Copy dataset attributes
                for key, value in obj.attrs.items():
                    compressed_data.attrs[key] = value

            elif isinstance(obj, h5py.Group):
                # Create group in destination file
                group = dst.create_group(name)
                # Copy group attributes
                for key, value in obj.attrs.items():
                    group.attrs[key] = value

        # Process all objects in the file
        src.visititems(copy_dataset)

    print(
        f"Compression complete. Original size: {os.path.getsize(input_file)/1e9:.2f} GB, "
        f"New size: {os.path.getsize(output_file)/1e9:.2f} GB"
    )

    return output_file


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Compress existing HDF5 files with gzip compression"
    )
    parser.add_argument("input_file", help="Path to the input HDF5 file")
    parser.add_argument(
        "--output_file", help="Path to the output compressed HDF5 file", default=None
    )
    parser.add_argument(
        "--compression", type=int, help="Compression level (1-9)", default=4
    )

    args = parser.parse_args()
    compress_hdf5(args.input_file, args.output_file, args.compression)

# EOF
