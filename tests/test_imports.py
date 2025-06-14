"""Test that imports are coming from the correct location."""

import sys
import pytest

def test_import_paths():
    """Verify imports are from the current project, not mngs_repo."""
    # Check that mngs_repo is not in sys.path
    for path in sys.path:
        assert "mngs_repo" not in path, f"mngs_repo found in sys.path: {path}"
    
    # Import scitex and check its location
    import scitex
    scitex_path = scitex.__file__
    assert "SciTeX-Code" in scitex_path, f"scitex imported from wrong location: {scitex_path}"
    assert "mngs_repo" not in scitex_path, f"scitex imported from mngs_repo: {scitex_path}"

def test_basic_imports():
    """Test that basic imports work."""
    try:
        import scitex
        import scitex.gen
        import scitex.io
        import scitex.plt
        import scitex.str
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import basic modules: {e}")

def test_sh_module():
    """Test that _sh module can be imported."""
    try:
        from scitex import _sh
        from scitex._sh import sh
        assert hasattr(_sh, 'sh')
        assert callable(sh)
    except ImportError as e:
        pytest.fail(f"Failed to import _sh module: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])