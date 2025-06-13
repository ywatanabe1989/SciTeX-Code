#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test suite for check_params function.

This test module verifies:
- Parameter inspection for neural network models
- Correct shape and status reporting
- Filtering by parameter name
- Display functionality
- Edge cases and error handling
"""

import pytest
import torch
import torch.nn as nn
from io import StringIO
import sys
from scitex.ai.utils import check_params


class SimpleModel(nn.Module):
    """Simple test model with various parameter types."""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3)
        self.bn1 = nn.BatchNorm2d(16)
        self.fc1 = nn.Linear(16 * 28 * 28, 128)
        self.fc2 = nn.Linear(128, 10)
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        return x


class TestCheckParams:
    """Test cases for check_params function."""
    
    @pytest.fixture
    def simple_model(self):
        """Create a simple model for testing."""
        return SimpleModel()
    
    @pytest.fixture
    def complex_model(self):
        """Create a more complex model with frozen layers."""
        model = SimpleModel()
        # Freeze first conv layer
        for param in model.conv1.parameters():
            param.requires_grad = False
        return model
    
    def test_basic_functionality(self, simple_model):
        """Test basic parameter checking functionality."""
        result = check_params(simple_model)
        assert isinstance(result, dict)
        assert len(result) > 0
        
        # Check that all model parameters are included
        expected_params = dict(simple_model.named_parameters())
        assert len(result) == len(expected_params)
    
    def test_parameter_shapes(self, simple_model):
        """Test that parameter shapes are correctly reported."""
        result = check_params(simple_model)
        
        # Check conv1 weight shape
        assert 'conv1.weight' in result
        shape, status = result['conv1.weight']
        assert shape == torch.Size([16, 3, 3, 3])
        assert status == "Learnable"
        
        # Check fc1 weight shape
        assert 'fc1.weight' in result
        shape, status = result['fc1.weight']
        assert shape == torch.Size([128, 16 * 28 * 28])
    
    def test_parameter_status(self, complex_model):
        """Test that frozen/learnable status is correctly reported."""
        result = check_params(complex_model)
        
        # Conv1 should be frozen
        assert 'conv1.weight' in result
        _, status = result['conv1.weight']
        assert status == "Freezed"
        
        # FC layers should be learnable
        assert 'fc1.weight' in result
        _, status = result['fc1.weight']
        assert status == "Learnable"
    
    def test_target_parameter_filtering(self, simple_model):
        """Test filtering by specific parameter name."""
        # Test getting specific parameter
        result = check_params(simple_model, tgt_name='fc1.weight')
        assert len(result) == 1
        assert 'fc1.weight' in result
        
        # Test with non-existent parameter
        result = check_params(simple_model, tgt_name='nonexistent.weight')
        assert len(result) == 0
    
    def test_show_parameter(self, simple_model, capsys):
        """Test the show parameter functionality."""
        # Test with show=True
        result = check_params(simple_model, show=True)
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert 'conv1.weight' in captured.out
        assert 'fc1.weight' in captured.out
    
    def test_show_specific_parameter(self, simple_model, capsys):
        """Test showing specific parameter only."""
        result = check_params(simple_model, tgt_name='fc2.bias', show=True)
        captured = capsys.readouterr()
        assert 'fc2.bias' in captured.out
        assert 'fc1.weight' not in captured.out  # Should not show other params
    
    def test_empty_model(self):
        """Test with a model that has no parameters."""
        class EmptyModel(nn.Module):
            def forward(self, x):
                return x
        
        model = EmptyModel()
        result = check_params(model)
        assert isinstance(result, dict)
        assert len(result) == 0
    
    def test_nested_modules(self):
        """Test with nested module structures."""
        class NestedModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(10, 20),
                    nn.ReLU(),
                    nn.Linear(20, 30)
                )
                self.decoder = nn.Sequential(
                    nn.Linear(30, 20),
                    nn.ReLU(),
                    nn.Linear(20, 10)
                )
        
        model = NestedModel()
        result = check_params(model)
        
        # Check nested parameter names
        assert 'encoder.0.weight' in result
        assert 'encoder.2.weight' in result
        assert 'decoder.0.weight' in result
        assert 'decoder.2.weight' in result
    
    def test_batchnorm_parameters(self, simple_model):
        """Test that BatchNorm parameters are correctly identified."""
        result = check_params(simple_model)
        
        # BatchNorm has weight and bias
        assert 'bn1.weight' in result
        assert 'bn1.bias' in result
        
        # Check shapes
        shape, _ = result['bn1.weight']
        assert shape == torch.Size([16])
    
    def test_no_grad_context(self, simple_model):
        """Test behavior within no_grad context."""
        with torch.no_grad():
            result = check_params(simple_model)
            # Should still report correct requires_grad status
            _, status = result['fc1.weight']
            assert status == "Learnable"
    
    def test_cuda_model(self):
        """Test with CUDA model if available."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
        
        model = SimpleModel().cuda()
        result = check_params(model)
        
        # Should work the same way
        assert 'conv1.weight' in result
        assert 'fc1.weight' in result
    
    def test_parameter_ordering(self, simple_model):
        """Test that parameters maintain consistent ordering."""
        result1 = check_params(simple_model)
        result2 = check_params(simple_model)
        
        # Keys should be in same order
        assert list(result1.keys()) == list(result2.keys())
    
    def test_large_model_performance(self):
        """Test performance with a model having many parameters."""
        class LargeModel(nn.Module):
            def __init__(self):
                super().__init__()
                for i in range(100):
                    setattr(self, f'layer_{i}', nn.Linear(10, 10))
        
        model = LargeModel()
        import time
        start = time.time()
        result = check_params(model)
        elapsed = time.time() - start
        
        assert len(result) == 200  # 100 layers * 2 params each
        assert elapsed < 1.0  # Should be fast
    
    def test_shared_parameters(self):
        """Test model with shared parameters."""
        class SharedParamModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.shared_layer = nn.Linear(10, 10)
                self.layer1 = self.shared_layer
                self.layer2 = self.shared_layer
        
        model = SharedParamModel()
        result = check_params(model)
        
        # Should only show unique parameters
        assert len(result) == 2  # weight and bias
    
    def test_custom_parameter_registration(self):
        """Test with custom registered parameters."""
        class CustomModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.custom_param = nn.Parameter(torch.randn(5, 5))
                self.register_parameter('named_param', nn.Parameter(torch.randn(3, 3)))
        
        model = CustomModel()
        result = check_params(model)
        
        assert 'custom_param' in result
        assert 'named_param' in result
        assert result['custom_param'][0] == torch.Size([5, 5])
        assert result['named_param'][0] == torch.Size([3, 3])
    
    def test_buffer_not_included(self):
        """Test that buffers are not included in parameters."""
        class BufferModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc = nn.Linear(10, 10)
                self.register_buffer('buffer', torch.randn(5, 5))
        
        model = BufferModel()
        result = check_params(model)
        
        assert 'fc.weight' in result
        assert 'fc.bias' in result
        assert 'buffer' not in result  # Buffers should not be included
    
    def test_model_with_no_show_default(self, simple_model):
        """Test that show defaults to False."""
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            result = check_params(simple_model)  # show not specified
            output = sys.stdout.getvalue()
            assert output == ""  # Nothing should be printed
        finally:
            sys.stdout = old_stdout


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/utils/_check_params.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # Time-stamp: "2024-02-17 12:38:40 (ywatanabe)"
#
# from pprint import pprint as _pprint
# from time import sleep
#
# # def get_params(model, tgt_name=None, sleep_sec=2, show=False):
#
# #     name_shape_dict = {}
# #     for name, param in model.named_parameters():
# #         learnable = "Learnable" if param.requires_grad else "Freezed"
#
# #         if (tgt_name is not None) & (name == tgt_name):
# #             return param
# #         if tgt_name is None:
# #             # print(f"\n{param}\n{param.shape}\nname: {name}\n")
# #             if show is True:
# #                 print(
# #                     f"\n{param}: {param.shape}\nname: {name}\nStatus: {learnable}\n"
# #                 )
# #                 sleep(sleep_sec)
# #             name_shape_dict[name] = list(param.shape)
#
# #     if tgt_name is None:
# #         print()
# #         _pprint(name_shape_dict)
# #         print()
#
#
# def check_params(model, tgt_name=None, show=False):
#
#     out_dict = {}
#
#     for name, param in model.named_parameters():
#         learnable = "Learnable" if param.requires_grad else "Freezed"
#
#         if tgt_name is None:
#             out_dict[name] = (param.shape, learnable)
#
#         elif (tgt_name is not None) & (name == tgt_name):
#             out_dict[name] = (param.shape, learnable)
#
#         elif (tgt_name is not None) & (name != tgt_name):
#             continue
#
#     if show:
#         for k, v in out_dict.items():
#             print(f"\n{k}\n{v}")
#
#     return out_dict

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/utils/_check_params.py
# --------------------------------------------------------------------------------
