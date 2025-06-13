#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-06-04 19:10:36 (ywatanabe)"


def reload(module_or_func, verbose=False):
    """
    Reload a module or the module containing a given function.

    This function attempts to reload a module directly if a module is passed,
    or reloads the module containing the function if a function is passed.
    This is useful during development to reflect changes without restarting the Python interpreter.

    Parameters:
    -----------
    module_or_func : module or function
        The module to reload, or a function whose containing module should be reloaded.
    verbose : bool, optional
        If True, print additional information during the reload process. Default is False.

    Returns:
    --------
    None

    Raises:
    -------
    Exception
        If the module cannot be found or if there's an error during the reload process.

    Notes:
    ------
    - Reloading modules can have unexpected side effects, especially for modules that
      maintain state or have complex imports. Use with caution.
    - This function modifies sys.modules, which affects the global state of the Python interpreter.

    Examples:
    ---------
    >>> import my_module
    >>> reload(my_module)

    >>> from my_module import my_function
    >>> reload(my_function)
    """
    import importlib
    import sys

    if module_or_func in sys.modules:
        del sys.modules[module_or_func]
        importlib.reload(module_or_func)

    if hasattr(module_or_func, "__module__"):
        # If the object has a __module__ attribute, it's likely a function or class.
        # Attempt to reload its module.
        module_name = module_or_func.__module__
        if module_name not in sys.modules:
            print(f"Module {module_name} not found in sys.modules. Cannot reload.")
            return
    elif hasattr(module_or_func, "__name__") and module_or_func.__name__ in sys.modules:
        # Otherwise, assume it's a module and try to get its name directly.
        module_name = module_or_func.__name__
    else:
        print(
            f"Provided object is neither a recognized module nor a function/class with a __module__ attribute."
        )
        return

    try:
        # Attempt to reload the module by name.
        importlib.reload(sys.modules[module_name])
        if verbose:
            print(f"Successfully reloaded module: {module_name}")

    except KeyError:
        # The module is not found in sys.modules, likely due to it not being imported.
        print(f"Module {module_name} not found in sys.modules. Cannot reload.")
    except Exception as e:
        # Catch any other exceptions and print an error message.
        print(f"Failed to reload module {module_name}. Error: {e}")
