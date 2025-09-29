#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 20:57:29 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_deprecated.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/decorators/_deprecated.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import functools
import importlib
import warnings


def deprecated(reason=None, forward_to=None):
    """
    A decorator to mark functions as deprecated. It will result in a warning being emitted
    when the function is used.

    Args:
        reason (str): A human-readable string explaining why this function was deprecated.
        forward_to (str): Optional module path to forward calls to (e.g., "..session.start").
                         If provided, calls will be forwarded to the new function instead of
                         executing the original deprecated function.
    """

    def decorator(func):
        if forward_to:
            # Create a forwarding wrapper with auto-generated docstring
            @functools.wraps(func)
            def new_func(*args, **kwargs):
                warnings.warn(
                    f"{func.__name__} is deprecated: {reason}",
                    DeprecationWarning,
                    stacklevel=2,
                )
                # Dynamic import and call forwarding
                module_path, function_name = forward_to.rsplit(".", 1)
                
                # Handle relative imports
                if module_path.startswith(".."):
                    # Get the module where the function was defined (not the calling module)
                    func_module = func.__module__
                    
                    if func_module:
                        # Convert relative import to absolute based on the function's module
                        package_parts = func_module.split('.')
                        # Count the number of dots to determine how many levels to go up
                        level_count = 0
                        for char in module_path:
                            if char == '.':
                                level_count += 1
                            else:
                                break
                        
                        # Remove the relative part and create absolute path
                        if level_count > 0:
                            base_package_parts = package_parts[:-level_count]
                            if base_package_parts:
                                base_package = '.'.join(base_package_parts)
                                relative_part = module_path.lstrip('.')
                                module_path = base_package + '.' + relative_part if relative_part else base_package
                            else:
                                # Can't go up that many levels, fallback to absolute
                                module_path = module_path.lstrip('.')
                
                try:
                    target_module = importlib.import_module(module_path)
                    target_function = getattr(target_module, function_name)
                    return target_function(*args, **kwargs)
                except (ImportError, AttributeError) as e:
                    # Fallback to original function if forwarding fails
                    warnings.warn(
                        f"Failed to forward {func.__name__} to {forward_to}: {e}. "
                        f"Using original deprecated implementation.",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                    return func(*args, **kwargs)
            
            # Auto-generate docstring for forwarding wrapper with target function's docstring
            original_name = func.__name__
            new_location = forward_to.replace("..", "scitex.").lstrip(".")
            
            # Try to get the target function's docstring
            target_docstring = ""
            try:
                # Get the same target we'll forward to
                target_module_path, target_function_name = forward_to.rsplit(".", 1)
                
                # Handle relative imports for docstring retrieval
                if target_module_path.startswith(".."):
                    func_module = func.__module__
                    if func_module:
                        package_parts = func_module.split('.')
                        level_count = 0
                        for char in target_module_path:
                            if char == '.':
                                level_count += 1
                            else:
                                break
                        
                        if level_count > 0:
                            base_package_parts = package_parts[:-level_count]
                            if base_package_parts:
                                base_package = '.'.join(base_package_parts)
                                relative_part = target_module_path.lstrip('.')
                                target_module_path = base_package + '.' + relative_part if relative_part else base_package
                            else:
                                target_module_path = target_module_path.lstrip('.')
                
                target_module = importlib.import_module(target_module_path)
                target_function = getattr(target_module, target_function_name)
                if target_function.__doc__:
                    target_docstring = target_function.__doc__.strip()
            except (ImportError, AttributeError):
                pass  # Fall back to basic docstring if target can't be imported
            
            # Create comprehensive docstring combining deprecation notice with target docs
            if target_docstring:
                forwarding_docstring = f"""**DEPRECATED: Use {new_location} instead**

{target_docstring}

Deprecation Notice
------------------
This function is deprecated and will be removed in a future version.
Use `{new_location}` instead. This wrapper forwards all calls to the new function
while displaying a deprecation warning.

Parameters
----------
*args : tuple
    Positional arguments passed to {new_location}
**kwargs : dict 
    Keyword arguments passed to {new_location}
    
Returns
-------
Any
    Same return value as {new_location}
    
Warns
-----
DeprecationWarning
    Always warns that this function is deprecated
"""
            else:
                # Fallback if target docstring unavailable
                forwarding_docstring = f"""**DEPRECATED: Use {new_location} instead**
    
This function provides backward compatibility for existing code that uses
{original_name}(). It forwards all calls to the new {new_location}
function while displaying a deprecation warning.

Parameters
----------
*args : tuple
    Positional arguments passed to {new_location}
**kwargs : dict 
    Keyword arguments passed to {new_location}
    
Returns
-------
Any
    Same return value as {new_location}
    
Warns
-----
DeprecationWarning
    Always warns that this function is deprecated
"""
            new_func.__doc__ = forwarding_docstring
            return new_func
        else:
            # Original behavior for non-forwarding deprecation
            @functools.wraps(func)
            def new_func(*args, **kwargs):
                warnings.warn(
                    f"{func.__name__} is deprecated: {reason}",
                    DeprecationWarning,
                    stacklevel=2,
                )
                return func(*args, **kwargs)

            return new_func

    return decorator

# EOF
