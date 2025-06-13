#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-27 21:36:51 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/feature_extraction/vit.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/feature_extraction/vit.py"

"""
Functionality:
    Extracts features from images using Vision Transformer (ViT) models
Input:
    Image arrays of arbitrary dimensions
Output:
    Feature vectors (1000-dimensional embeddings)
Prerequisites:
    torch, PIL, torchvision
"""

import os as _os
from typing import Tuple, Union

import torch
import torch as _torch
from pytorch_pretrained_vit import ViT
from torchvision import transforms as _transforms

# from ...decorators import batch_torch_fn


def _setup_device(device: Union[str, None]) -> str:
    if device is None:
        device = "cuda" if _torch.cuda.is_available() else "cpu"
    return device


class VitFeatureExtractor:
    def __init__(
        self,
        model_name="B_16",
        torch_home="./models",
        device=None,
    ):
        self.valid_models = [
            "B_16",
            "B_32",
            "L_16",
            "L_32",
            "B_16_imagenet1k",
            "B_32_imagenet1k",
            "L_16_imagenet1k",
            "L_32_imagenet1k",
        ]
        self.model_name = model_name
        self.torch_home = torch_home
        self.device = _setup_device(device)

        _os.environ["TORCH_HOME"] = torch_home
        self._validate_inputs()
        self.model = ViT(model_name, pretrained=True).to(self.device).eval()
        self.transform = _transforms.Compose(
            [
                _transforms.ToPILImage(),
                _transforms.Resize(self.model.image_size),
                _transforms.ToTensor(),
                _transforms.Normalize(0.5, 0.5),
            ]
        )

    def _validate_inputs(self):
        if self.model_name not in self.valid_models:
            raise ValueError(f"Invalid model name. Choose from: {self.valid_models}")
        if not _os.path.exists(self.torch_home):
            raise FileNotFoundError(f"Model directory not found: {self.torch_home}")

    def _preprocess_array(
        self,
        arr: _torch.Tensor,
        dim: Tuple[int, int],
        channel_dim: Union[int, None],
    ) -> _torch.Tensor:
        # print(f"Input array shape: {arr.shape}")

        orig_shape = arr.shape
        dim = tuple(d if d >= 0 else len(orig_shape) + d for d in dim)

        perm = list(range(len(orig_shape)))
        for d in sorted(dim):
            perm.remove(d)
            perm.append(d)
        arr = arr.permute(perm)

        # Flatten all dimensions except the last two (spatial dimensions)
        batch_shape = arr.shape[:-2]
        spatial_shape = arr.shape[-2:]
        arr = arr.reshape(-1, *spatial_shape)

        # Process each image
        transformed = []
        for img in arr:
            img = img.unsqueeze(0)
            img = img.repeat(3, 1, 1)
            transformed.append(self.transform(img))
        result = _torch.stack(transformed)
        return result, batch_shape

    # @batch_method
    # @torch_method
    # @batch_torch_fn
    def extract_features(
        self,
        arr,
        axis=(-2, -1),
        dim=None,
        channel_dim=None,
        batch_size=None,
        device="cuda",
    ):

        processed_arr, batch_shape = self._preprocess_array(
            arr,
            axis,
            channel_dim,
        )
        # print(f"Processed shape: {processed_arr.shape}")

        processed_arr = processed_arr.to(self.device)
        with _torch.no_grad():
            features = self.model(processed_arr).cpu()

        return features.reshape(*batch_shape, -1)


if __name__ == "__main__":
    import scitex

    extractor = scitex.ai.feature_extraction.VitFeatureExtractor(
        model_name="B_16_imagenet1k"
    )
    tensor = torch.randn(3, 2, 4, 5, 32, 32)
    processed = extractor.extract_features(tensor, (-2, -1), None)
    print(processed.shape)

    arr = np.random.rand(3, 2, 4, 5, 32, 32)
    processed = extractor.extract_features(arr, (-2, -1), None)
    print(processed.shape)
    # torch.Size([3, 2, 4, 5, 32, 32])

# EOF
