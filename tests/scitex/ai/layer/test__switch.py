#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 21:55:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/ai/layer/test__switch.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/ai/layer/test__switch.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pytest
import torch
import torch.nn as nn
from scitex.ai.layer import switch, Pass


class TestSwitchFunction:
    """Comprehensive test suite for the switch function."""
    
    def test_switch_returns_layer_when_true(self):
        """Test that switch returns the original layer when is_used=True."""
        layer = nn.Linear(10, 5)
        result = switch(layer, True)
        assert result is layer
        assert isinstance(result, nn.Linear)
    
    def test_switch_returns_pass_when_false(self):
        """Test that switch returns Pass layer when is_used=False."""
        layer = nn.Linear(10, 5)
        result = switch(layer, False)
        assert isinstance(result, Pass)
        assert result is not layer
    
    def test_switch_with_different_layer_types(self):
        """Test switch with various layer types."""
        layers = [
            nn.Linear(10, 5),
            nn.Conv2d(3, 16, 3),
            nn.LSTM(10, 20),
            nn.BatchNorm1d(10),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.MaxPool2d(2),
            nn.Sequential(nn.Linear(10, 5), nn.ReLU())
        ]
        
        for layer in layers:
            # Test with is_used=True
            result_true = switch(layer, True)
            assert result_true is layer
            
            # Test with is_used=False
            result_false = switch(layer, False)
            assert isinstance(result_false, Pass)
            assert result_false is not layer
    
    def test_switch_functionality_preservation(self):
        """Test that switched layer preserves functionality when is_used=True."""
        layer = nn.Linear(10, 5)
        switched_layer = switch(layer, True)
        
        x = torch.randn(32, 10)
        output1 = layer(x)
        output2 = switched_layer(x)
        
        assert torch.equal(output1, output2)
    
    def test_switch_pass_behavior(self):
        """Test that switched-off layer acts as identity."""
        layer = nn.Linear(10, 5)
        switched_layer = switch(layer, False)
        
        x = torch.randn(32, 10)
        output = switched_layer(x)
        
        assert torch.equal(output, x)
    
    def test_switch_with_custom_module(self):
        """Test switch with custom nn.Module."""
        class CustomLayer(nn.Module):
            def __init__(self):
                super().__init__()
                self.weight = nn.Parameter(torch.randn(5, 10))
            
            def forward(self, x):
                return x @ self.weight.T
        
        custom_layer = CustomLayer()
        
        # Test with is_used=True
        result_true = switch(custom_layer, True)
        assert result_true is custom_layer
        
        # Test with is_used=False
        result_false = switch(custom_layer, False)
        assert isinstance(result_false, Pass)
    
    def test_switch_in_sequential_true(self):
        """Test switch in nn.Sequential when is_used=True."""
        model = nn.Sequential(
            nn.Linear(10, 20),
            switch(nn.ReLU(), True),
            nn.Linear(20, 5)
        )
        
        x = torch.randn(32, 10)
        output = model(x)
        assert output.shape == (32, 5)
        
        # Verify ReLU is active
        assert any(isinstance(m, nn.ReLU) for m in model.modules())
    
    def test_switch_in_sequential_false(self):
        """Test switch in nn.Sequential when is_used=False."""
        model = nn.Sequential(
            nn.Linear(10, 20),
            switch(nn.ReLU(), False),
            nn.Linear(20, 5)
        )
        
        x = torch.randn(32, 10)
        output = model(x)
        assert output.shape == (32, 5)
        
        # Verify Pass is used instead of ReLU
        assert any(isinstance(m, Pass) for m in model.modules())
        assert not any(isinstance(m, nn.ReLU) for m in model.modules())
    
    def test_switch_gradient_flow_enabled(self):
        """Test gradient flow when layer is enabled."""
        layer = nn.Linear(10, 5)
        switched_layer = switch(layer, True)
        
        x = torch.randn(32, 10, requires_grad=True)
        output = switched_layer(x)
        loss = output.sum()
        loss.backward()
        
        assert x.grad is not None
        assert layer.weight.grad is not None
        assert layer.bias.grad is not None
    
    def test_switch_gradient_flow_disabled(self):
        """Test gradient flow when layer is disabled (Pass)."""
        layer = nn.Linear(10, 5)
        switched_layer = switch(layer, False)
        
        x = torch.randn(32, 10, requires_grad=True)
        output = switched_layer(x)
        loss = output.sum()
        loss.backward()
        
        assert x.grad is not None
        # Original layer should not have gradients
        assert layer.weight.grad is None
        assert layer.bias.grad is None
    
    def test_switch_with_none_layer(self):
        """Test switch behavior with None as layer."""
        # This might raise an error or return Pass - test the behavior
        result = switch(None, True)
        assert result is None
        
        result = switch(None, False)
        assert isinstance(result, Pass)
    
    def test_switch_with_pass_layer(self):
        """Test switch with Pass layer as input."""
        pass_layer = Pass()
        
        # When True, should return the same Pass instance
        result_true = switch(pass_layer, True)
        assert result_true is pass_layer
        
        # When False, should return a new Pass instance
        result_false = switch(pass_layer, False)
        assert isinstance(result_false, Pass)
        # Note: might be different instance
    
    def test_switch_boolean_variations(self):
        """Test switch with various boolean-like values."""
        layer = nn.Linear(10, 5)
        
        # Truthy values
        for truthy in [True, 1, "yes", [1], {"a": 1}]:
            result = switch(layer, truthy)
            assert result is layer
        
        # Falsy values
        for falsy in [False, 0, "", [], {}, None]:
            result = switch(layer, falsy)
            assert isinstance(result, Pass)
    
    def test_switch_memory_efficiency(self):
        """Test that switch doesn't create unnecessary copies."""
        layer = nn.Linear(1000, 1000)
        
        # Get memory of original layer
        original_id = id(layer)
        
        # Switch with True should return same object
        result_true = switch(layer, True)
        assert id(result_true) == original_id
        
        # Switch with False creates new Pass (lightweight)
        result_false = switch(layer, False)
        assert isinstance(result_false, Pass)
        assert id(result_false) != original_id
    
    def test_switch_with_complex_model(self):
        """Test switch with complex model architectures."""
        class ComplexModel(nn.Module):
            def __init__(self, use_dropout=True, use_batchnorm=True):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 64, 3)
                self.bn1 = switch(nn.BatchNorm2d(64), use_batchnorm)
                self.relu = nn.ReLU()
                self.dropout = switch(nn.Dropout2d(0.5), use_dropout)
                self.conv2 = nn.Conv2d(64, 128, 3)
                self.bn2 = switch(nn.BatchNorm2d(128), use_batchnorm)
            
            def forward(self, x):
                x = self.conv1(x)
                x = self.bn1(x)
                x = self.relu(x)
                x = self.dropout(x)
                x = self.conv2(x)
                x = self.bn2(x)
                return x
        
        # Test different configurations
        model1 = ComplexModel(use_dropout=True, use_batchnorm=True)
        model2 = ComplexModel(use_dropout=False, use_batchnorm=True)
        model3 = ComplexModel(use_dropout=True, use_batchnorm=False)
        model4 = ComplexModel(use_dropout=False, use_batchnorm=False)
        
        x = torch.randn(1, 3, 32, 32)
        
        # All models should produce output
        for model in [model1, model2, model3, model4]:
            output = model(x)
            assert output.shape[0] == 1
            assert output.shape[1] == 128
    
    def test_switch_state_dict_handling(self):
        """Test state dict handling with switched layers."""
        class ModelWithSwitch(nn.Module):
            def __init__(self, use_extra=True):
                super().__init__()
                self.main = nn.Linear(10, 20)
                self.extra = switch(nn.Linear(20, 20), use_extra)
                self.output = nn.Linear(20, 5)
            
            def forward(self, x):
                x = self.main(x)
                x = self.extra(x)
                x = self.output(x)
                return x
        
        # Model with extra layer
        model1 = ModelWithSwitch(use_extra=True)
        state1 = model1.state_dict()
        
        # Model without extra layer
        model2 = ModelWithSwitch(use_extra=False)
        state2 = model2.state_dict()
        
        # State dict sizes should be different
        assert len(state1) > len(state2)
        assert "extra.weight" in state1
        assert "extra.weight" not in state2
    
    def test_switch_multiple_times(self):
        """Test applying switch multiple times."""
        layer = nn.Linear(10, 5)
        
        # Multiple True switches
        result = layer
        for _ in range(5):
            result = switch(result, True)
        assert result is layer
        
        # Switch to Pass then back
        result = switch(layer, False)
        assert isinstance(result, Pass)
        result = switch(result, True)
        assert isinstance(result, Pass)  # Pass stays Pass
    
    def test_switch_with_requires_grad(self):
        """Test switch preserves requires_grad property."""
        layer = nn.Linear(10, 5)
        layer.requires_grad_(False)
        
        # When enabled
        result = switch(layer, True)
        assert not any(p.requires_grad for p in result.parameters())
        
        # Enable gradients
        layer.requires_grad_(True)
        result = switch(layer, True)
        assert all(p.requires_grad for p in result.parameters())


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/layer/_switch.py
# --------------------------------------------------------------------------------
# from ._Pass import Pass
# 
# 
# def switch(layer, is_used):
#     if is_used:
#         return layer
#     else:
#         return Pass()

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/layer/_switch.py
# --------------------------------------------------------------------------------
