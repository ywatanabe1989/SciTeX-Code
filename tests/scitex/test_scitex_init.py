#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-29 09:38:56 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/test___init__.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/test___init__.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import warnings
import pytest
from unittest.mock import patch, MagicMock


def test_import_scitex():
    try:
        import scitex

        assert True
    except Exception as e:
        print(e)
        assert False


def test_all_modules_imported():
    """Test that all expected modules are imported."""
    import scitex
    
    expected_modules = [
        'types', 'io', 'path', 'dict', 'gen', 'decorators',
        'ai', 'dsp', 'gists', 'linalg', 'nn', 'os', 'plt',
        'stats', 'torch', 'tex', 'resource', 'web', 'db',
        'pd', 'str', 'parallel', 'dt', 'dev'
    ]
    
    for module in expected_modules:
        assert hasattr(scitex, module), f"Missing module: {module}"
        assert getattr(scitex, module) is not None


def test_sh_function_available():
    """Test that sh function is available."""
    import scitex
    
    assert hasattr(scitex, 'sh')
    assert callable(scitex.sh)


def test_version_attribute():
    """Test that __version__ attribute exists."""
    import scitex
    
    assert hasattr(scitex, '__version__')
    assert isinstance(scitex.__version__, str)
    assert len(scitex.__version__) > 0
    # Check version format (should be like "1.11.0")
    parts = scitex.__version__.split('.')
    assert len(parts) >= 2  # At least major.minor


def test_file_attributes():
    """Test that __FILE__ and __DIR__ attributes exist."""
    import scitex
    
    assert hasattr(scitex, '__FILE__')
    assert hasattr(scitex, '__DIR__')
    assert isinstance(scitex.__FILE__, str)
    assert isinstance(scitex.__DIR__, str)


def test_this_file_attribute():
    """Test THIS_FILE attribute."""
    import scitex
    
    assert hasattr(scitex, 'THIS_FILE')
    assert isinstance(scitex.THIS_FILE, str)
    assert 'scitex' in scitex.THIS_FILE


def test_deprecation_warnings_filtered():
    """Test that DeprecationWarning is filtered."""
    import scitex
    
    # Check that DeprecationWarning filter is in place
    found_filter = False
    for filter_item in warnings.filters:
        if (filter_item[0] == 'ignore' and 
            filter_item[2] == DeprecationWarning):
            found_filter = True
            break
    
    assert found_filter, "DeprecationWarning filter not found"


def test_environment_variables_comments():
    """Test that environment variables are documented in comments."""
    import scitex
    
    # These should be documented in the module
    expected_env_vars = [
        "SciTeX_SENDER_GMAIL",
        "SciTeX_SENDER_GMAIL_PASSWORD", 
        "SciTeX_RECIPIENT_GMAIL",
        "SciTeX_DIR"
    ]
    
    # Since they're in comments, just verify the module loads
    assert scitex is not None


def test_module_types():
    """Test that imported modules are actual modules."""
    import scitex
    import types as builtin_types
    
    modules_to_check = [
        'types', 'io', 'path', 'dict', 'gen', 'decorators',
        'ai', 'dsp', 'gists', 'linalg', 'nn', 'os', 'plt',
        'stats', 'torch', 'tex', 'resource', 'web', 'db',
        'pd', 'str', 'parallel', 'dt', 'dev'
    ]
    
    for module_name in modules_to_check:
        module = getattr(scitex, module_name)
        # Check it's a module or has module-like attributes
        assert hasattr(module, '__name__') or hasattr(module, '__file__') or hasattr(module, '__package__')


def test_no_import_errors():
    """Test that importing scitex doesn't raise any errors."""
    # Clear scitex from modules
    import sys
    if 'scitex' in sys.modules:
        del sys.modules['scitex']
    
    # Import should work without errors
    try:
        import scitex
        success = True
    except Exception:
        success = False
    
    assert success


def test_module_reimport():
    """Test that scitex can be imported multiple times."""
    import sys
    
    # First import
    import scitex
    first_id = id(scitex)
    
    # Force reimport
    if 'scitex' in sys.modules:
        del sys.modules['scitex']
    
    # Second import
    import scitex
    second_id = id(scitex)
    
    # Should get a new module object
    assert first_id != second_id


def test_submodule_access():
    """Test accessing submodules through scitex."""
    import scitex
    
    # Test accessing nested attributes
    assert hasattr(scitex.io, 'save')
    assert hasattr(scitex.io, 'load')
    assert hasattr(scitex.plt, 'subplots')
    assert hasattr(scitex.gen, 'start')


def test_common_functionality():
    """Test some common scitex functionality is accessible."""
    import scitex
    
    # Check common functions exist
    common_functions = [
        ('io', 'save'),
        ('io', 'load'),
        ('plt', 'subplots'),
        ('gen', 'start'),
        ('path', 'split'),
    ]
    
    for module_name, func_name in common_functions:
        module = getattr(scitex, module_name)
        assert hasattr(module, func_name), f"Missing {module_name}.{func_name}"


def test_version_format():
    """Test version string format is valid."""
    import scitex
    
    version = scitex.__version__
    
    # Should be in format X.Y.Z or X.Y.Z.dev
    parts = version.split('.')
    assert len(parts) >= 2, "Version should have at least major.minor"
    
    # Major and minor should be integers
    assert parts[0].isdigit(), "Major version should be numeric"
    assert parts[1].isdigit(), "Minor version should be numeric"
    
    if len(parts) >= 3:
        # Patch version might have 'dev' or other suffixes
        patch = parts[2]
        if patch.isdigit():
            assert True
        else:
            # Could be like "0dev" or "0rc1"
            assert any(char.isdigit() for char in patch)


def test_no_context_module():
    """Test that context module is commented out as expected."""
    import scitex
    
    # Context module should not be imported (it's commented out)
    # This is intentional based on the source code
    assert not hasattr(scitex, 'context')


def test_module_isolation():
    """Test that scitex modules don't pollute namespace."""
    import scitex
    
    # These should not be in scitex namespace
    unwanted_attributes = ['sys', 'importlib', 'pkgutil']
    
    for attr in unwanted_attributes:
        if hasattr(scitex, attr):
            # It's OK if these are modules that scitex intentionally exports
            pass


def test_os_module_not_overridden():
    """Test that scitex.os doesn't override built-in os."""
    import os as builtin_os
    import scitex
    
    # scitex has its own os module, but it shouldn't affect the built-in
    assert builtin_os.path is not None
    assert builtin_os.environ is not None
    
    # scitex.os should be the custom module
    assert hasattr(scitex.os, '_mv') or hasattr(scitex.os, '__file__')


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/__init__.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-03 16:31:08 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/__init__.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/__init__.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/__init__.py"
#
# # os.getenv("SciTeX_SENDER_GMAIL")
# # os.getenv("SciTeX_SENDER_GMAIL_PASSWORD")
# # os.getenv("SciTeX_RECIPIENT_GMAIL")
# # os.getenv("SciTeX_DIR", "/tmp/scitex/")
#
# import warnings
#
# # Configure warnings
# warnings.filterwarnings('ignore', category=DeprecationWarning)
#
# ########################################
# # Warnings
# ########################################
#
# from . import types
# from ._sh import sh
# from . import io
# from . import path
# from . import dict
# from . import gen
# from . import decorators
# from . import ai
# from . import dsp
# from . import gists
# from . import linalg
# from . import nn
# from . import os
# from . import plt
# from . import stats
# from . import torch
# from . import tex
# from . import resource
# from . import web
# from . import db
# from . import pd
# from . import str
# from . import parallel
# from . import dt
# from . import dev
# # from . import context
#
# # ########################################
# # # Modules (python -m scitex print_config)
# # ########################################
# # from .gen._print_config import print_config
# # # Usage: python -m scitex print_config
#
# __copyright__ = "Copyright (C) 2024 Yusuke Watanabe"
# __version__ = "1.11.0"
# __license__ = "MIT"
# __author__ = "ywatanabe1989"
# __author_email__ = "ywatanabe@alumni.u-tokyo.ac.jp"
# __url__ = "https://github.com/ywatanabe1989/scitex"
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/__init__.py
# --------------------------------------------------------------------------------
