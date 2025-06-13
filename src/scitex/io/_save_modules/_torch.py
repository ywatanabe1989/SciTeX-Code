#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:25:14 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_torch.py

import torch


def _save_torch(obj, spath, **kwargs):
    """
    Save a PyTorch model or tensor.
    
    Parameters
    ----------
    obj : torch.nn.Module or torch.Tensor
        The PyTorch model or tensor to save.
    spath : str
        Path where the PyTorch file will be saved.
    **kwargs : dict
        Additional keyword arguments to pass to torch.save.
        
    Returns
    -------
    None
    """
    torch.save(obj, spath, **kwargs)
