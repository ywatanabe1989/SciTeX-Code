#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 00:00:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/ai/loss/test___init__.py
# ----------------------------------------
"""Tests for loss module initialization and exports."""

import pytest
import torch
import torch.nn as nn


class TestLossModuleInit:
    """Test loss module initialization and imports."""

    def test_module_imports(self):
        """Test that loss module can be imported."""
        import scitex.ai.loss
        assert hasattr(scitex.ai.loss, "__name__")

    def test_multi_task_loss_export(self):
        """Test MultiTaskLoss is exported."""
        from scitex.ai.loss import MultiTaskLoss
        assert MultiTaskLoss is not None
        assert issubclass(MultiTaskLoss, nn.Module)

    def test_l1_function_export(self):
        """Test l1 function is exported."""
        from scitex.ai.loss import l1
        assert callable(l1)

    def test_l2_function_export(self):
        """Test l2 function is exported."""
        from scitex.ai.loss import l2
        assert callable(l2)

    def test_elastic_function_export(self):
        """Test elastic function is exported."""
        from scitex.ai.loss import elastic
        assert callable(elastic)

    def test_all_exports(self):
        """Test __all__ exports are correct."""
        import scitex.ai.loss
        assert "MultiTaskLoss" in scitex.ai.loss.__all__

    def test_module_namespace(self):
        """Test module namespace contains expected items."""
        import scitex.ai.loss as loss_module
        expected_attrs = ["MultiTaskLoss", "l1", "l2", "elastic"]
        for attr in expected_attrs:
            assert hasattr(loss_module, attr)

    def test_import_from_parent(self):
        """Test imports work from parent module."""
        from scitex.ai import loss
        assert hasattr(loss, "MultiTaskLoss")
        assert hasattr(loss, "l1")
        assert hasattr(loss, "l2")
        assert hasattr(loss, "elastic")

    def test_direct_import_paths(self):
        """Test direct import paths work correctly."""
        # Test MultiTaskLoss
        from scitex.ai.loss.multi_task_loss import MultiTaskLoss as MTL1
        from scitex.ai.loss import MultiTaskLoss as MTL2
        assert MTL1 is MTL2

    def test_module_documentation(self):
        """Test module has proper documentation."""
        import scitex.ai.loss
        assert scitex.ai.loss.__doc__ is not None
        assert "Loss functions" in scitex.ai.loss.__doc__

    def test_no_unexpected_exports(self):
        """Test no unexpected items are exported."""
        import scitex.ai.loss
        # Get public exports (not starting with _)
        public_attrs = [attr for attr in dir(scitex.ai.loss) if not attr.startswith("_")]
        expected_public = ["MultiTaskLoss", "l1", "l2", "elastic"]
        # Check that all public attrs are expected
        for attr in public_attrs:
            if attr not in ["__builtins__", "__cached__", "__file__", "__loader__", 
                          "__name__", "__package__", "__path__", "__spec__"]:
                assert attr in expected_public, f"Unexpected export: {attr}"

    def test_submodule_structure(self):
        """Test submodule structure is correct."""
        import scitex.ai.loss
        import os
        loss_dir = os.path.dirname(scitex.ai.loss.__file__)
        expected_files = ["__init__.py", "_L1L2Losses.py", "multi_task_loss.py"]
        for file in expected_files:
            assert os.path.exists(os.path.join(loss_dir, file))

    def test_import_performance(self):
        """Test module imports quickly."""
        import time
        import importlib
        import sys
        
        # Remove from cache if already imported
        if "scitex.ai.loss" in sys.modules:
            del sys.modules["scitex.ai.loss"]
        
        start = time.time()
        importlib.import_module("scitex.ai.loss")
        duration = time.time() - start
        
        # Should import in less than 1 second
        assert duration < 1.0, f"Import took too long: {duration:.2f}s"

    def test_circular_imports(self):
        """Test no circular imports exist."""
        # This should not raise ImportError
        import scitex.ai.loss
        from scitex.ai.loss import MultiTaskLoss
        from scitex.ai.loss import l1, l2, elastic
        
        # Should be able to instantiate without issues
        mtl = MultiTaskLoss()
        assert mtl is not None

    def test_version_compatibility(self):
        """Test module works with required PyTorch version."""
        import torch
        import scitex.ai.loss
        
        # Check PyTorch is available
        assert torch.__version__ is not None
        
        # Test basic functionality works
        from scitex.ai.loss import MultiTaskLoss
        mtl = MultiTaskLoss([True, False])
        assert isinstance(mtl, nn.Module)


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
    
    pytest.main([os.path.abspath(__file__), "-v"])
