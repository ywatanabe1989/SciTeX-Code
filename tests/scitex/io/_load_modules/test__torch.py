#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:45:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__torch.py

"""Tests for PyTorch file loading functionality.

This module tests the _load_torch function from scitex.io._load_modules._torch,
which handles loading PyTorch model and checkpoint files.
"""

import os
import tempfile
import pytest
import torch
import torch.nn as nn


def test_load_torch_tensor():
    """Test loading a PyTorch tensor."""
    from scitex.io._load_modules import _load_torch
    
    # Create various tensors
    tensor_1d = torch.tensor([1, 2, 3, 4, 5])
    tensor_2d = torch.randn(10, 20)
    tensor_3d = torch.ones(5, 10, 15)
    
    with tempfile.NamedTemporaryFile(suffix='.pth', delete=False) as f:
        torch.save(tensor_2d, f.name)
        temp_path = f.name
    
    try:
        loaded_tensor = _load_torch(temp_path)
        assert torch.allclose(loaded_tensor, tensor_2d)
        assert loaded_tensor.shape == (10, 20)
    finally:
        os.unlink(temp_path)


def test_load_torch_state_dict():
    """Test loading a model state dict."""
    from scitex.io._load_modules import _load_torch
    
    # Create a simple model
    class SimpleModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc1 = nn.Linear(10, 20)
            self.fc2 = nn.Linear(20, 10)
            self.relu = nn.ReLU()
        
        def forward(self, x):
            x = self.relu(self.fc1(x))
            return self.fc2(x)
    
    model = SimpleModel()
    state_dict = model.state_dict()
    
    with tempfile.NamedTemporaryFile(suffix='.pth', delete=False) as f:
        torch.save(state_dict, f.name)
        temp_path = f.name
    
    try:
        loaded_state_dict = _load_torch(temp_path)
        
        # Verify all keys are present
        assert set(loaded_state_dict.keys()) == set(state_dict.keys())
        
        # Verify tensors are equal
        for key in state_dict:
            assert torch.allclose(loaded_state_dict[key], state_dict[key])
    finally:
        os.unlink(temp_path)


def test_load_torch_checkpoint():
    """Test loading a training checkpoint."""
    from scitex.io._load_modules import _load_torch
    
    # Create a typical checkpoint dictionary
    checkpoint = {
        'epoch': 10,
        'model_state_dict': {
            'layer1.weight': torch.randn(10, 5),
            'layer1.bias': torch.randn(10),
            'layer2.weight': torch.randn(3, 10),
            'layer2.bias': torch.randn(3)
        },
        'optimizer_state_dict': {
            'state': {},
            'param_groups': [{'lr': 0.001, 'momentum': 0.9}]
        },
        'loss': 0.123,
        'accuracy': 0.95
    }
    
    with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as f:
        torch.save(checkpoint, f.name)
        temp_path = f.name
    
    try:
        loaded_checkpoint = _load_torch(temp_path)
        
        assert loaded_checkpoint['epoch'] == 10
        assert loaded_checkpoint['loss'] == 0.123
        assert loaded_checkpoint['accuracy'] == 0.95
        assert 'model_state_dict' in loaded_checkpoint
        assert 'optimizer_state_dict' in loaded_checkpoint
    finally:
        os.unlink(temp_path)


def test_load_torch_with_pt_extension():
    """Test loading with .pt extension."""
    from scitex.io._load_modules import _load_torch
    
    data = {'test': torch.tensor([1, 2, 3])}
    
    with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as f:
        torch.save(data, f.name)
        temp_path = f.name
    
    try:
        loaded_data = _load_torch(temp_path)
        assert torch.equal(loaded_data['test'], data['test'])
    finally:
        os.unlink(temp_path)


def test_load_torch_invalid_extension():
    """Test that loading non-torch file raises ValueError."""
    from scitex.io._load_modules import _load_torch
    
    with pytest.raises(ValueError, match="File must have .pth or .pt extension"):
        _load_torch("model.pkl")
    
    with pytest.raises(ValueError, match="File must have .pth or .pt extension"):
        _load_torch("/path/to/file.json")


def test_load_torch_map_location():
    """Test loading with map_location parameter."""
    from scitex.io._load_modules import _load_torch
    
    # Create tensor on CPU
    tensor = torch.randn(5, 5)
    
    with tempfile.NamedTemporaryFile(suffix='.pth', delete=False) as f:
        torch.save(tensor, f.name)
        temp_path = f.name
    
    try:
        # Load with explicit CPU mapping
        loaded_tensor = _load_torch(temp_path, map_location='cpu')
        assert loaded_tensor.device.type == 'cpu'
        assert torch.allclose(loaded_tensor, tensor)
        
        # Load with device mapping function
        loaded_tensor2 = _load_torch(temp_path, map_location=torch.device('cpu'))
        assert loaded_tensor2.device.type == 'cpu'
    finally:
        os.unlink(temp_path)


def test_load_torch_nonexistent_file():
    """Test loading a nonexistent file."""
    from scitex.io._load_modules import _load_torch
    
    with pytest.raises(FileNotFoundError):
        _load_torch("/nonexistent/path/model.pth")


def test_load_torch_multiple_objects():
    """Test loading multiple objects saved together."""
    from scitex.io._load_modules import _load_torch
    
    # Save multiple objects
    objects = {
        'tensors': [torch.randn(3, 3) for _ in range(5)],
        'model_config': {
            'hidden_size': 256,
            'num_layers': 3,
            'dropout': 0.1
        },
        'training_history': {
            'losses': [0.5, 0.3, 0.2, 0.15],
            'accuracies': [0.7, 0.8, 0.85, 0.9]
        }
    }
    
    with tempfile.NamedTemporaryFile(suffix='.pth', delete=False) as f:
        torch.save(objects, f.name)
        temp_path = f.name
    
    try:
        loaded_objects = _load_torch(temp_path)
        
        assert len(loaded_objects['tensors']) == 5
        assert loaded_objects['model_config']['hidden_size'] == 256
        assert loaded_objects['training_history']['losses'] == [0.5, 0.3, 0.2, 0.15]
        
        # Verify tensors
        for i, tensor in enumerate(loaded_objects['tensors']):
            assert torch.allclose(tensor, objects['tensors'][i])
    finally:
        os.unlink(temp_path)


def test_load_torch_cuda_tensor_to_cpu():
    """Test loading CUDA tensor to CPU (if CUDA available)."""
    from scitex.io._load_modules import _load_torch
    
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    
    # Create tensor on CUDA
    cuda_tensor = torch.randn(5, 5).cuda()
    
    with tempfile.NamedTemporaryFile(suffix='.pth', delete=False) as f:
        torch.save(cuda_tensor, f.name)
        temp_path = f.name
    
    try:
        # Load to CPU
        loaded_tensor = _load_torch(temp_path, map_location='cpu')
        assert loaded_tensor.device.type == 'cpu'
        assert torch.allclose(loaded_tensor, cuda_tensor.cpu())
    finally:
        os.unlink(temp_path)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_torch.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-14 07:41:34 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/io/_load_modules/_torch.py
# 
# import torch
# 
# 
# def _load_torch(lpath, **kwargs):
#     """Load PyTorch model/checkpoint file."""
#     if not lpath.endswith((".pth", ".pt")):
#         raise ValueError("File must have .pth or .pt extension")
#     return torch.load(lpath, **kwargs)
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_torch.py
# --------------------------------------------------------------------------------
