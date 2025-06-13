import numpy as np
import pandas as pd

BANDS = pd.DataFrame(
    data=np.array([[0.5, 4], [4, 8], [8, 10], [10, 13], [13, 32], [32, 75]]).T,
    index=["low_hz", "high_hz"],
    columns=["delta", "theta", "lalpha", "halpha", "beta", "gamma"],
)

EEG_MONTAGE_1020 = [
    "FP1",
    "F3",
    "C3",
    "P3",
    "O1",
    "FP2",
    "F4",
    "C4",
    "P4",
    "O2",
    "F7",
    "T7",
    "P7",
    "F8",
    "T8",
    "P8",
    "FZ",
    "CZ",
    "PZ",
]

EEG_MONTAGE_BIPOLAR_TRANVERSE = [
    # Frontal
    "FP1-FP2",
    "F7-F3",
    "F3-FZ",
    "FZ-F4",
    "F4-F8",
    # Central
    "T7-C3",
    "C3-CZ",
    "CZ-C4",
    "C4-T8",
    # Parietal
    "P7-P3",
    "P3-PZ",
    "PZ-P4",
    "P4-P8",
    # Occipital
    "O1-O2",
]
