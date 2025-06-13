#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 15:15:00 (ywatanabe)"
# File: ./tests/scitex/ai/feature_extraction/test_vit.py

"""Tests for scitex.ai.feature_extraction.vit module."""

import pytest
import torch
import numpy as np
import os
from unittest.mock import patch, MagicMock, Mock
from scitex.ai.feature_extraction.vit import VitFeatureExtractor, _setup_device


class TestSetupDevice:
    """Test suite for _setup_device function."""

    def test_setup_device_none_cuda_available(self):
        """Test device setup when None is passed and CUDA is available."""
        with patch('torch.cuda.is_available', return_value=True):
            device = _setup_device(None)
            assert device == "cuda"

    def test_setup_device_none_cuda_not_available(self):
        """Test device setup when None is passed and CUDA is not available."""
        with patch('torch.cuda.is_available', return_value=False):
            device = _setup_device(None)
            assert device == "cpu"

    def test_setup_device_explicit_cpu(self):
        """Test device setup with explicit CPU."""
        device = _setup_device("cpu")
        assert device == "cpu"

    def test_setup_device_explicit_cuda(self):
        """Test device setup with explicit CUDA."""
        device = _setup_device("cuda")
        assert device == "cuda"


class TestVitFeatureExtractor:
    """Test suite for VitFeatureExtractor class."""

    @pytest.fixture
    def mock_vit_model(self):
        """Create a mock ViT model."""
        mock_model = MagicMock()
        mock_model.image_size = 224
        mock_model.eval.return_value = mock_model
        mock_model.to.return_value = mock_model
        # Mock forward pass to return 1000-dim features
        mock_model.return_value = torch.randn(1, 1000)
        return mock_model

    @pytest.fixture
    def mock_environment(self, tmp_path, mock_vit_model):
        """Set up mock environment for testing."""
        # Create temporary model directory
        model_dir = tmp_path / "models"
        model_dir.mkdir()
        
        with patch('scitex.ai.feature_extraction.vit.ViT', return_value=mock_vit_model):
            with patch('os.path.exists', return_value=True):
                yield model_dir

    def test_initialization_default_params(self, mock_environment):
        """Test initialization with default parameters."""
        extractor = VitFeatureExtractor()
        assert extractor.model_name == "B_16"
        assert extractor.torch_home == "./models"
        assert extractor.device in ["cpu", "cuda"]

    def test_initialization_custom_params(self, mock_environment):
        """Test initialization with custom parameters."""
        extractor = VitFeatureExtractor(
            model_name="L_32",
            torch_home=str(mock_environment),
            device="cpu"
        )
        assert extractor.model_name == "L_32"
        assert extractor.torch_home == str(mock_environment)
        assert extractor.device == "cpu"

    def test_initialization_sets_torch_home(self, mock_environment):
        """Test that initialization sets TORCH_HOME environment variable."""
        torch_home = str(mock_environment)
        with patch.dict(os.environ, {}, clear=True):
            _ = VitFeatureExtractor(torch_home=torch_home)
            assert os.environ["TORCH_HOME"] == torch_home

    def test_valid_model_names(self, mock_environment):
        """Test all valid model names."""
        valid_models = [
            "B_16", "B_32", "L_16", "L_32",
            "B_16_imagenet1k", "B_32_imagenet1k", 
            "L_16_imagenet1k", "L_32_imagenet1k",
        ]
        
        for model_name in valid_models:
            extractor = VitFeatureExtractor(model_name=model_name)
            assert extractor.model_name == model_name

    def test_invalid_model_name_raises_error(self, mock_environment):
        """Test that invalid model name raises ValueError."""
        with pytest.raises(ValueError, match="Invalid model name"):
            VitFeatureExtractor(model_name="invalid_model")

    def test_nonexistent_model_directory_raises_error(self):
        """Test that non-existent model directory raises FileNotFoundError."""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(FileNotFoundError, match="Model directory not found"):
                VitFeatureExtractor(torch_home="/nonexistent/path")

    def test_transform_pipeline_setup(self, mock_environment):
        """Test that transform pipeline is properly set up."""
        extractor = VitFeatureExtractor()
        
        # Check that transform is a Compose object
        from torchvision.transforms import Compose
        assert isinstance(extractor.transform, Compose)
        
        # Check transform steps
        transforms = extractor.transform.transforms
        assert len(transforms) == 4  # ToPILImage, Resize, ToTensor, Normalize

    def test_preprocess_array_2d_input(self, mock_environment):
        """Test preprocessing of 2D array."""
        extractor = VitFeatureExtractor()
        
        # Create 2D test tensor (H, W)
        arr = torch.randn(32, 32)
        processed, batch_shape = extractor._preprocess_array(
            arr, dim=(-2, -1), channel_dim=None
        )
        
        assert processed.shape == (1, 3, 224, 224)  # 1 image, 3 channels, resized
        assert batch_shape == ()

    def test_preprocess_array_3d_input(self, mock_environment):
        """Test preprocessing of 3D array with batch dimension."""
        extractor = VitFeatureExtractor()
        
        # Create 3D test tensor (B, H, W)
        batch_size = 4
        arr = torch.randn(batch_size, 32, 32)
        processed, batch_shape = extractor._preprocess_array(
            arr, dim=(-2, -1), channel_dim=None
        )
        
        assert processed.shape == (batch_size, 3, 224, 224)
        assert batch_shape == (batch_size,)

    def test_preprocess_array_high_dimensional(self, mock_environment):
        """Test preprocessing of high-dimensional array."""
        extractor = VitFeatureExtractor()
        
        # Create 6D test tensor
        arr = torch.randn(2, 3, 4, 5, 32, 32)
        processed, batch_shape = extractor._preprocess_array(
            arr, dim=(-2, -1), channel_dim=None
        )
        
        # Should flatten all but spatial dims
        assert processed.shape == (2*3*4*5, 3, 224, 224)
        assert batch_shape == (2, 3, 4, 5)

    def test_extract_features_simple(self, mock_environment, mock_vit_model):
        """Test feature extraction with simple input."""
        extractor = VitFeatureExtractor()
        
        # Create test input
        arr = torch.randn(32, 32)
        
        # Mock model to return features
        mock_vit_model.return_value = torch.randn(1, 1000)
        
        features = extractor.extract_features(arr, axis=(-2, -1))
        
        assert features.shape == (1000,)
        assert isinstance(features, torch.Tensor)

    def test_extract_features_batch(self, mock_environment, mock_vit_model):
        """Test feature extraction with batch input."""
        extractor = VitFeatureExtractor()
        
        # Create batch test input
        batch_size = 4
        arr = torch.randn(batch_size, 32, 32)
        
        # Mock model to return batch features
        mock_vit_model.return_value = torch.randn(batch_size, 1000)
        
        features = extractor.extract_features(arr, axis=(-2, -1))
        
        assert features.shape == (batch_size, 1000)

    def test_extract_features_high_dimensional(self, mock_environment, mock_vit_model):
        """Test feature extraction preserves non-spatial dimensions."""
        extractor = VitFeatureExtractor()
        
        # Create high-dimensional input
        arr = torch.randn(2, 3, 4, 32, 32)
        
        # Mock model to return appropriate number of features
        mock_vit_model.return_value = torch.randn(2*3*4, 1000)
        
        features = extractor.extract_features(arr, axis=(-2, -1))
        
        assert features.shape == (2, 3, 4, 1000)

    def test_extract_features_no_grad(self, mock_environment, mock_vit_model):
        """Test that feature extraction runs in no_grad mode."""
        extractor = VitFeatureExtractor()
        
        arr = torch.randn(32, 32, requires_grad=True)
        
        # Track if no_grad was used
        no_grad_called = False
        original_no_grad = torch.no_grad
        
        def mock_no_grad():
            nonlocal no_grad_called
            no_grad_called = True
            return original_no_grad()
        
        with patch('torch.no_grad', side_effect=mock_no_grad):
            _ = extractor.extract_features(arr, axis=(-2, -1))
        
        assert no_grad_called

    def test_extract_features_device_handling(self, mock_environment, mock_vit_model):
        """Test proper device handling during feature extraction."""
        extractor = VitFeatureExtractor(device="cpu")
        
        arr = torch.randn(32, 32)
        
        # Track tensor movements
        to_device_called = False
        
        def mock_to(device):
            nonlocal to_device_called
            to_device_called = True
            assert device == "cpu"
            return arr
        
        with patch.object(torch.Tensor, 'to', side_effect=mock_to):
            _ = extractor.extract_features(arr, axis=(-2, -1))
        
        assert to_device_called

    def test_extract_features_cpu_output(self, mock_environment, mock_vit_model):
        """Test that output is always on CPU."""
        extractor = VitFeatureExtractor(device="cuda" if torch.cuda.is_available() else "cpu")
        
        arr = torch.randn(32, 32)
        
        # Mock model output
        mock_output = torch.randn(1, 1000)
        mock_output.cpu = Mock(return_value=mock_output)
        mock_vit_model.return_value = mock_output
        
        features = extractor.extract_features(arr, axis=(-2, -1))
        
        # Check that .cpu() was called
        mock_output.cpu.assert_called_once()

    def test_model_eval_mode(self, mock_environment, mock_vit_model):
        """Test that model is set to eval mode."""
        extractor = VitFeatureExtractor()
        
        # Check that eval was called during initialization
        mock_vit_model.eval.assert_called_once()

    @pytest.mark.parametrize("axis", [
        (-2, -1),  # Last two dimensions
        (-3, -2),  # Different dimensions
        (0, 1),    # First two dimensions
    ])
    def test_different_axis_specifications(self, mock_environment, mock_vit_model, axis):
        """Test feature extraction with different axis specifications."""
        extractor = VitFeatureExtractor()
        
        # Create appropriate tensor for axis
        if axis == (0, 1):
            arr = torch.randn(32, 32, 3, 4)
        else:
            arr = torch.randn(3, 4, 32, 32)
        
        mock_vit_model.return_value = torch.randn(12, 1000)  # 3*4 = 12
        
        features = extractor.extract_features(arr, axis=axis)
        
        # Features should have correct shape
        assert features.ndim == 3  # Original 4D - 2 spatial + 1 feature
        assert features.shape[-1] == 1000

    def test_negative_axis_handling(self, mock_environment):
        """Test that negative axis indices are handled correctly."""
        extractor = VitFeatureExtractor()
        
        arr = torch.randn(2, 3, 32, 32)
        
        # Test internal preprocessing
        processed, batch_shape = extractor._preprocess_array(
            arr, dim=(-2, -1), channel_dim=None
        )
        
        # Should correctly identify spatial dimensions
        assert processed.shape[0] == 2 * 3  # Batch flattened
        assert processed.shape[2:] == (224, 224)  # Resized spatial

    def test_transform_grayscale_to_rgb(self, mock_environment):
        """Test that grayscale images are converted to RGB."""
        extractor = VitFeatureExtractor()
        
        # Single channel input
        arr = torch.randn(1, 32, 32)
        processed, _ = extractor._preprocess_array(
            arr, dim=(-2, -1), channel_dim=None
        )
        
        # Should have 3 channels after processing
        assert processed.shape[1] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
