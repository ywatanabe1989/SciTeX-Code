#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:49:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__torch.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__torch.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for PyTorch saving functionality
"""

import os
import tempfile
import pytest
import numpy as np
from pathlib import Path

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

    from scitex.io._save_modules import save_torch


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch not installed")
class TestSaveTorch:
    """Test suite for save_torch function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.pth")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_tensor(self):
        """Test saving single tensor"""
        tensor = torch.randn(10, 20)
        save_torch(tensor, self.test_file)
        
        assert os.path.exists(self.test_file)
        loaded = torch.load(self.test_file)
        torch.testing.assert_close(tensor, loaded)

    def test_save_multiple_tensors(self):
        """Test saving dictionary of tensors"""
        tensors = {
            "tensor1": torch.randn(5, 5),
            "tensor2": torch.randn(10, 10),
            "tensor3": torch.randn(3, 4, 5)
        }
        save_torch(tensors, self.test_file)
        
        loaded = torch.load(self.test_file)
        for key in tensors:
            torch.testing.assert_close(tensors[key], loaded[key])

    def test_save_model_state_dict(self):
        """Test saving model state dict"""
        class SimpleModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc1 = nn.Linear(10, 20)
                self.fc2 = nn.Linear(20, 5)
                self.relu = nn.ReLU()
            
            def forward(self, x):
                x = self.relu(self.fc1(x))
                return self.fc2(x)
        
        model = SimpleModel()
        save_torch(model.state_dict(), self.test_file)
        
        # Load into new model
        new_model = SimpleModel()
        new_model.load_state_dict(torch.load(self.test_file))
        
        # Check that parameters match
        for (name1, param1), (name2, param2) in zip(
            model.named_parameters(), 
            new_model.named_parameters()
        ):
            assert name1 == name2
            torch.testing.assert_close(param1, param2)

    def test_save_full_model(self):
        """Test saving entire model"""
        model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 5)
        )
        save_torch(model, self.test_file)
        
        loaded_model = torch.load(self.test_file)
        
        # Test with same input
        x = torch.randn(2, 10)
        torch.testing.assert_close(model(x), loaded_model(x))

    def test_save_optimizer_state(self):
        """Test saving optimizer state"""
        model = nn.Linear(10, 5)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        # Do some optimization steps
        for _ in range(5):
            loss = model(torch.randn(2, 10)).sum()
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        
        save_torch(optimizer.state_dict(), self.test_file)
        
        # Load into new optimizer
        new_optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        new_optimizer.load_state_dict(torch.load(self.test_file))
        
        # Check states match
        assert len(optimizer.state_dict()["state"]) == len(new_optimizer.state_dict()["state"])

    def test_save_training_checkpoint(self):
        """Test saving complete training checkpoint"""
        model = nn.Linear(10, 5)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        
        checkpoint = {
            "epoch": 10,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "loss": 0.123,
            "best_accuracy": 0.95
        }
        save_torch(checkpoint, self.test_file)
        
        loaded = torch.load(self.test_file)
        assert loaded["epoch"] == 10
        assert loaded["loss"] == pytest.approx(0.123)
        assert loaded["best_accuracy"] == pytest.approx(0.95)

    def test_save_different_tensor_types(self):
        """Test saving tensors of different types"""
        tensors = {
            "float32": torch.randn(5, 5, dtype=torch.float32),
            "float64": torch.randn(5, 5, dtype=torch.float64),
            "int32": torch.randint(0, 10, (5, 5), dtype=torch.int32),
            "int64": torch.randint(0, 10, (5, 5), dtype=torch.int64),
            "bool": torch.rand(5, 5) > 0.5,
            "complex": torch.randn(5, 5, dtype=torch.complex64)
        }
        save_torch(tensors, self.test_file)
        
        loaded = torch.load(self.test_file)
        for key, tensor in tensors.items():
            torch.testing.assert_close(tensor, loaded[key])
            assert tensor.dtype == loaded[key].dtype

    def test_save_cuda_tensor(self):
        """Test saving CUDA tensor (if available)"""
        if torch.cuda.is_available():
            tensor = torch.randn(10, 10).cuda()
            save_torch(tensor, self.test_file)
            
            loaded = torch.load(self.test_file)
            # Loaded tensor should be on CPU by default
            assert loaded.device.type == "cpu"
            torch.testing.assert_close(tensor.cpu(), loaded)
        else:
            pytest.skip("CUDA not available")

    def test_save_sparse_tensor(self):
        """Test saving sparse tensor"""
        indices = torch.LongTensor([[0, 1, 1], [2, 0, 2]])
        values = torch.FloatTensor([3, 4, 5])
        size = (2, 3)
        sparse_tensor = torch.sparse.FloatTensor(indices, values, size)
        
        save_torch(sparse_tensor, self.test_file)
        
        loaded = torch.load(self.test_file)
        torch.testing.assert_close(sparse_tensor.to_dense(), loaded.to_dense())

    def test_save_quantized_model(self):
        """Test saving quantized model"""
        try:
            import torch.quantization as quantization
            
            model = nn.Sequential(
                quantization.QuantStub(),
                nn.Linear(10, 5),
                quantization.DeQuantStub()
            )
            model.qconfig = quantization.default_qconfig
            quantization.prepare(model, inplace=True)
            quantization.convert(model, inplace=True)
            
            save_torch(model.state_dict(), self.test_file)
            assert os.path.exists(self.test_file)
        except (ImportError, AttributeError):
            pytest.skip("Quantization not available")

    def test_save_with_custom_pickle(self):
        """Test saving with custom pickle module"""
        import pickle
        tensor = torch.randn(5, 5)
        save_torch(tensor, self.test_file, pickle_module=pickle)
        
        loaded = torch.load(self.test_file)
        torch.testing.assert_close(tensor, loaded)

    def test_save_empty_tensor(self):
        """Test saving empty tensor"""
        empty_tensor = torch.empty(0)
        save_torch(empty_tensor, self.test_file)
        
        loaded = torch.load(self.test_file)
        assert loaded.numel() == 0

    def test_save_gradient_tensor(self):
        """Test saving tensor with gradient"""
        tensor = torch.randn(5, 5, requires_grad=True)
        # Compute some gradient
        loss = tensor.sum()
        loss.backward()
        
        # Save tensor with gradient
        save_torch({"tensor": tensor, "grad": tensor.grad}, self.test_file)
        
        loaded = torch.load(self.test_file)
        torch.testing.assert_close(tensor, loaded["tensor"])
        torch.testing.assert_close(tensor.grad, loaded["grad"])

    def test_save_list_of_tensors(self):
        """Test saving list of tensors"""
        tensors = [torch.randn(i, i) for i in range(1, 6)]
        save_torch(tensors, self.test_file)
        
        loaded = torch.load(self.test_file)
        assert len(loaded) == len(tensors)
        for original, loaded_tensor in zip(tensors, loaded):
            torch.testing.assert_close(original, loaded_tensor)

    def test_save_numpy_array_as_tensor(self):
        """Test saving numpy array converted to tensor"""
        arr = np.random.randn(10, 10)
        tensor = torch.from_numpy(arr)
        save_torch(tensor, self.test_file)
        
        loaded = torch.load(self.test_file)
        torch.testing.assert_close(tensor, loaded)


# EOF
