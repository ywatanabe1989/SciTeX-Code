#!/usr/bin/env python3

from torch.utils.data import Dataset
import numpy as np


class DefaultDataset(Dataset):
    """
    Apply transform for the first element of arrs_list

    Example:
        n = 1024
        n_chs = 19
        X = np.random.rand(n, n_chs, 1000)
        T = np.random.randint(0, 4, size=(n, 1))
        S = np.random.randint(0, 999, size=(n, 1))
        Sr = np.random.randint(0, 4, size=(n, 1))

        arrs_list = [X, T, S, Sr]
        transform = None
        ds = _DefaultDataset(arrs_list, transform=transform)
        len(ds) # 1024
    """

    def __init__(self, arrs_list, transform=None):
        self.arrs_list = arrs_list
        self.arrs = arrs_list  # alias

        assert np.all([len(arr) for arr in arrs_list])

        self.length = len(arrs_list[0])
        self.transform = transform

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        arrs_list_idx = [arr[idx] for arr in self.arrs_list]

        # Here, you might want to transform, or apply DA on X as a numpy array
        if self.transform:
            dtype_orig = arrs_list_idx[0].dtype
            arrs_list_idx[0] = self.transform(
                arrs_list_idx[0].astype(np.float64)
            ).astype(dtype_orig)
        return arrs_list_idx
