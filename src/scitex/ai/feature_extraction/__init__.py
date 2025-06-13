#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-20 10:53:22 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/feature_extraction/__init__.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/feature_extraction/__init__.py"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-22 19:51:47 (ywatanabe)"
# File: __init__.py

import os as __os
import importlib as __importlib
import inspect as __inspect
import warnings as __warnings

# Get the current directory
current_dir = __os.path.dirname(__file__)

# Iterate through all Python files in the current directory
for filename in __os.listdir(current_dir):
    if filename.endswith(".py") and not filename.startswith("__"):
        module_name = filename[:-3]  # Remove .py extension
        try:
            module = __importlib.import_module(f".{module_name}", package=__name__)
            
            # Import only functions and classes from the module
            for name, obj in __inspect.getmembers(module):
                if __inspect.isfunction(obj) or __inspect.isclass(obj):
                    if not name.startswith("_"):
                        globals()[name] = obj
        except ImportError as e:
            # Warn about modules that couldn't be imported due to missing dependencies
            __warnings.warn(
                f"Could not import {module_name} from mngs.ai.feature_extraction: {str(e)}. "
                f"Some functionality may be unavailable. "
                f"Consider installing missing dependencies if you need this module.",
                ImportWarning,
                stacklevel=2
            )

# Clean up temporary variables
del __os, __importlib, __inspect, __warnings, current_dir
if 'filename' in locals():
    del filename
if 'module_name' in locals():
    del module_name
if 'module' in locals():
    del module
if 'name' in locals():
    del name
if 'obj' in locals():
    del obj

# EOF
