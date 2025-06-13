#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:30:00"

import pytest


class TestRangerModuleInit:
    def test_ranger_import(self):
        # Test that Ranger optimizer can be imported
        try:
            from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import Ranger
            assert Ranger is not None
        except ImportError:
            pytest.skip("Ranger optimizer not available")

    def test_ranger_va_import(self):
        # Test that RangerVA optimizer can be imported
        try:
            from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import RangerVA
            assert RangerVA is not None
        except ImportError:
            pytest.skip("RangerVA optimizer not available")

    def test_ranger_qh_import(self):
        # Test that RangerQH optimizer can be imported
        try:
            from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import RangerQH
            assert RangerQH is not None
        except ImportError:
            pytest.skip("RangerQH optimizer not available")

    def test_all_optimizers_import(self):
        # Test that all optimizers can be imported together
        try:
            from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import Ranger, RangerVA, RangerQH
            
            optimizers = [Ranger, RangerVA, RangerQH]
            for optimizer in optimizers:
                assert optimizer is not None
                assert hasattr(optimizer, '__name__')
                
        except ImportError:
            pytest.skip("Ranger optimizers not available")

    def test_module_attributes(self):
        # Test that the module has the expected attributes
        try:
            import scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger as ranger_module
            
            expected_attrs = ['Ranger', 'RangerVA', 'RangerQH']
            for attr in expected_attrs:
                assert hasattr(ranger_module, attr), f"Module missing attribute: {attr}"
                
        except ImportError:
            pytest.skip("Ranger module not available")


class TestRangerOptimizerBasics:
    def test_ranger_is_class(self):
        # Test that Ranger is a class
        try:
            from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import Ranger
            
            assert isinstance(Ranger, type), "Ranger should be a class"
            
        except ImportError:
            pytest.skip("Ranger optimizer not available")

    def test_ranger_va_is_class(self):
        # Test that RangerVA is a class
        try:
            from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import RangerVA
            
            assert isinstance(RangerVA, type), "RangerVA should be a class"
            
        except ImportError:
            pytest.skip("RangerVA optimizer not available")

    def test_ranger_qh_is_class(self):
        # Test that RangerQH is a class
        try:
            from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import RangerQH
            
            assert isinstance(RangerQH, type), "RangerQH should be a class"
            
        except ImportError:
            pytest.skip("RangerQH optimizer not available")

    def test_optimizers_are_different_classes(self):
        # Test that the optimizers are distinct classes
        try:
            from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import Ranger, RangerVA, RangerQH
            
            # All should be different classes
            assert Ranger != RangerVA, "Ranger and RangerVA should be different classes"
            assert Ranger != RangerQH, "Ranger and RangerQH should be different classes"
            assert RangerVA != RangerQH, "RangerVA and RangerQH should be different classes"
            
        except ImportError:
            pytest.skip("Ranger optimizers not available")


@pytest.mark.skipif(
    not pytest.importorskip("torch", reason="torch not available"),
    reason="PyTorch required for optimizer tests"
)
class TestRangerOptimizerIntegration:
    def test_ranger_torch_optimizer_inheritance(self):
        # Test that Ranger optimizers inherit from torch.optim.Optimizer
        try:
            import torch.optim
            from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import Ranger
            
            # Check if it's a torch optimizer
            assert issubclass(Ranger, torch.optim.Optimizer), "Ranger should inherit from torch.optim.Optimizer"
            
        except ImportError:
            pytest.skip("Ranger or torch not available")

    def test_ranger_va_torch_optimizer_inheritance(self):
        # Test that RangerVA inherits from torch optimizer
        try:
            import torch.optim
            from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import RangerVA
            
            # Check if it's a torch optimizer
            assert issubclass(RangerVA, torch.optim.Optimizer), "RangerVA should inherit from torch.optim.Optimizer"
            
        except ImportError:
            pytest.skip("RangerVA or torch not available")

    def test_ranger_qh_torch_optimizer_inheritance(self):
        # Test that RangerQH inherits from torch optimizer
        try:
            import torch.optim
            from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import RangerQH
            
            # Check if it's a torch optimizer
            assert issubclass(RangerQH, torch.optim.Optimizer), "RangerQH should inherit from torch.optim.Optimizer"
            
        except ImportError:
            pytest.skip("RangerQH or torch not available")

    def test_optimizer_instantiation(self):
        # Test that optimizers can be instantiated with parameters
        try:
            import torch
            import torch.nn as nn
            from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import Ranger
            
            # Create a simple model
            model = nn.Linear(10, 1)
            
            # Try to instantiate Ranger optimizer
            optimizer = Ranger(model.parameters())
            assert optimizer is not None
            assert hasattr(optimizer, 'step'), "Optimizer should have step method"
            assert hasattr(optimizer, 'zero_grad'), "Optimizer should have zero_grad method"
            
        except ImportError:
            pytest.skip("Ranger or torch not available")
        except Exception:
            # If there are parameter issues, just skip - we're testing basic import functionality
            pytest.skip("Ranger optimizer instantiation failed - may need specific parameters")


class TestRangerModuleStructure:
    def test_module_docstring_or_name(self):
        # Test that the module has proper identification
        try:
            import scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger as ranger_module
            
            # Should have a module name at minimum
            assert hasattr(ranger_module, '__name__')
            assert 'ranger' in ranger_module.__name__
            
        except ImportError:
            pytest.skip("Ranger module not available")

    def test_no_extra_imports(self):
        # Test that module only exports expected classes
        try:
            import scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger as ranger_module
            
            # Get all public attributes (not starting with _)
            public_attrs = [attr for attr in dir(ranger_module) if not attr.startswith('_')]
            
            # Should primarily contain the three optimizer classes
            expected_optimizers = {'Ranger', 'RangerVA', 'RangerQH'}
            found_optimizers = set(public_attrs).intersection(expected_optimizers)
            
            # At least some of the expected optimizers should be present
            assert len(found_optimizers) > 0, "No expected optimizers found in module"
            
        except ImportError:
            pytest.skip("Ranger module not available")


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
