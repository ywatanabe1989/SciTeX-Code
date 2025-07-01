#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 00:18:00 (ywatanabe)"
# File: ./tests/scitex/scholar/test_init.py

"""Test module initialization and imports for scitex.scholar."""

import pytest


def test_scholar_module_imports():
    """Test that the scholar module can be imported."""
    import scitex.scholar
    assert scitex.scholar is not None


def test_core_legacy_imports():
    """Test core legacy imports are available."""
    from scitex.scholar import (
        LocalSearchEngine,
        Paper,
        PDFDownloader,
        build_index,
        get_scholar_dir,
        search_sync,
        VectorSearchEngine
    )
    
    assert LocalSearchEngine is not None
    assert Paper is not None
    assert PDFDownloader is not None
    assert callable(build_index)
    assert callable(get_scholar_dir)
    assert callable(search_sync)
    assert VectorSearchEngine is not None


def test_all_exports():
    """Test that __all__ exports are accessible."""
    import scitex.scholar
    
    for export in scitex.scholar.__all__:
        assert hasattr(scitex.scholar, export), f"Missing export: {export}"


if __name__ == "__main__":
    pytest.main([__file__])