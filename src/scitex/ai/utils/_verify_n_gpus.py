import torch
import warnings


def verify_n_gpus(n_gpus):
    if torch.cuda.device_count() < n_gpus:
        warnings.warn(
            f"N_GPUS ({n_gpus}) is larger "
            f"than n_gpus torch can acesses (= {torch.cuda.device_count()})"
            f"Please check $CUDA_VISIBLE_DEVICES and your setting in this script.",
            UserWarning,
        )
        return torch.cuda.device_count()

    else:
        return n_gpus
