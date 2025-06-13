# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/decorators/_converters.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-30 14:58:43 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_converters.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/decorators/_converters.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import functools
# import warnings
# from typing import Any as _Any
# from typing import Callable, Dict, Tuple, Union
#
# import numpy as np
# import pandas as pd
# import torch
# import xarray
#
# """
# Core conversion utilities for handling data type transformations.
# Provides consistent conversion between NumPy, PyTorch, Pandas, and other formats.
# """
#
#
# class ConversionWarning(UserWarning):
#     pass
#
#
# # Configure warnings
# warnings.simplefilter("always", ConversionWarning)
#
#
# @functools.lru_cache(maxsize=None)
# def _cached_warning(message: str) -> None:
#     """Cache warnings to avoid repetition."""
#     warnings.warn(message, category=ConversionWarning)
#
#
# def _conversion_warning(old: _Any, new: torch.Tensor) -> None:
#     """Generate standardized type conversion warning."""
#     message = (
#         f"Converted from {type(old).__name__} to {type(new).__name__} ({new.device}). "
#         f"Consider using {type(new).__name__} ({new.device}) as input for faster computation."
#     )
#     _cached_warning(message)
#
#
# def _try_device(tensor: torch.Tensor, device: str) -> torch.Tensor:
#     """Try to move tensor to specified device with graceful fallback."""
#     if not isinstance(tensor, torch.Tensor):
#         return tensor
#
#     if tensor.device.type == device:
#         return tensor
#
#     try:
#         return tensor.to(device)
#     except RuntimeError as error:
#         if "cuda" in str(error).lower() and device == "cuda":
#             warnings.warn(
#                 "CUDA memory insufficient, falling back to CPU.", UserWarning
#             )
#             return tensor.cpu()
#         raise error
#
#
# def is_torch(*args: _Any, **kwargs: _Any) -> bool:
#     """Check if any input is a PyTorch tensor."""
#     return any(isinstance(arg, torch.Tensor) for arg in args) or any(
#         isinstance(val, torch.Tensor) for val in kwargs.values()
#     )
#
#
# def is_cuda(*args: _Any, **kwargs: _Any) -> bool:
#     """Check if any input is a CUDA tensor."""
#     return any(
#         (isinstance(arg, torch.Tensor) and arg.is_cuda) for arg in args
#     ) or any(
#         (isinstance(val, torch.Tensor) and val.is_cuda)
#         for val in kwargs.values()
#     )
#
#
# def _return_always(*args: _Any, **kwargs: _Any) -> Tuple[Tuple, Dict]:
#     """Always return args and kwargs as a tuple of (args, kwargs)."""
#     return args, kwargs
#
#
# def _return_if(*args: _Any, **kwargs: _Any) -> Union[Tuple, Dict, None]:
#     """Return args and/or kwargs depending on what's provided."""
#     if args and kwargs:
#         return args, kwargs
#     elif args:
#         return args
#     elif kwargs:
#         return kwargs
#     else:
#         return None
#
#
# def to_torch(
#     *args: _Any,
#     return_fn: Callable = _return_if,
#     device: str = None,
#     **kwargs: _Any,
# ) -> _Any:
#     """Convert various data types to PyTorch tensors."""
#     if device is None:
#         device = kwargs.get(
#             "device", "cuda" if torch.cuda.is_available() else "cpu"
#         )
#
#     def _to_torch(data: _Any) -> _Any:
#         """Internal conversion function for various data types."""
#         # Check for None
#         if data is None:
#             return None
#
#         # Handle collections
#         if isinstance(data, (tuple, list)):
#             return [_to_torch(item) for item in data if item is not None]
#
#         # Handle pandas types
#         if isinstance(data, (pd.Series, pd.DataFrame)):
#             new_data = torch.tensor(data.to_numpy()).squeeze().float()
#             new_data = _try_device(new_data, device)
#             if device == "cuda":
#                 _conversion_warning(data, new_data)
#             return new_data
#
#         # Handle arrays and lists
#         if isinstance(data, (np.ndarray, list)):
#             new_data = torch.tensor(data).float()
#             new_data = _try_device(new_data, device)
#             if device == "cuda":
#                 _conversion_warning(data, new_data)
#             return new_data
#
#         # Handle xarray
#         if isinstance(data, xarray.core.dataarray.DataArray):
#             new_data = torch.tensor(np.array(data)).float()
#             new_data = _try_device(new_data, device)
#             if device == "cuda":
#                 _conversion_warning(data, new_data)
#             return new_data
#
#         # Return as is for other types
#         return data
#
#     # Process args and kwargs
#     converted_args = [_to_torch(arg) for arg in args if arg is not None]
#     converted_kwargs = {
#         key: _to_torch(val) for key, val in kwargs.items() if val is not None
#     }
#
#     # Handle axis/dim parameter conversion
#     if "axis" in converted_kwargs:
#         converted_kwargs["dim"] = converted_kwargs.pop("axis")
#
#     # Return in the specified format
#     return return_fn(*converted_args, **converted_kwargs)
#
#
# def to_numpy(
#     *args: _Any, return_fn: Callable = _return_if, **kwargs: _Any
# ) -> _Any:
#     """Convert various data types to NumPy arrays."""
#
#     def _to_numpy(data: _Any) -> _Any:
#         """Internal conversion function for various data types."""
#         # Handle pandas types
#         if isinstance(data, (pd.Series, pd.DataFrame)):
#             return data.to_numpy().squeeze()
#
#         # Handle torch tensors
#         if isinstance(data, torch.Tensor):
#             return data.detach().cpu().numpy()
#
#         # Handle lists
#         if isinstance(data, list):
#             return np.array(data)
#
#         # Handle tuples (recursively)
#         if isinstance(data, tuple):
#             return [_to_numpy(item) for item in data if item is not None]
#
#         # Return as is for other types
#         return data
#
#     # Process args and kwargs
#     converted_args = [_to_numpy(arg) for arg in args if arg is not None]
#     converted_kwargs = {
#         key: _to_numpy(val) for key, val in kwargs.items() if val is not None
#     }
#
#     # Handle dim/axis parameter conversion
#     if "dim" in converted_kwargs:
#         converted_kwargs["axis"] = converted_kwargs.pop("dim")
#
#     # Return in the specified format
#     return return_fn(*converted_args, **converted_kwargs)
#
#
# def is_nested_decorator():
#     """Check if we're in a nested decorator context."""
#     import inspect
#
#     frame = inspect.currentframe()
#     current_decorator = None
#     decorator_chain = []
#
#     # Walk up the call stack
#     while frame:
#         if frame.f_code.co_name == "wrapper":
#             # Check if this frame has local variables
#             if frame.f_locals:
#                 # Try to get the self reference if it's a method
#                 if "self" in frame.f_locals:
#                     decorator_chain.append(frame.f_locals["self"])
#
#                 # Check if the wrapper has marked itself with decorator info
#                 if "_current_decorator" in frame.f_locals:
#                     decorator_type = frame.f_locals["_current_decorator"]
#                     if current_decorator is None:
#                         current_decorator = decorator_type
#                     elif current_decorator != decorator_type:
#                         # Found a different decorator in the chain
#                         return True
#
#         frame = frame.f_back
#
#     # If we found more than one decorator in the chain
#     return len(decorator_chain) > 1
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/decorators/_converters.py
# --------------------------------------------------------------------------------
