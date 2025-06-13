import pytest
import numpy as np
import pandas as pd
import scitex


class TestBands:
    """Test BANDS parameter."""

    def test_import(self):
        """Test BANDS can be imported."""
        assert hasattr(scitex.dsp.params, "BANDS")

    def test_bands_structure(self):
        """Test BANDS is a DataFrame with correct structure."""
        bands = scitex.dsp.params.BANDS
        
        # Check type
        assert isinstance(bands, pd.DataFrame)
        
        # Check shape
        assert bands.shape == (2, 6)
        
        # Check index
        assert list(bands.index) == ["low_hz", "high_hz"]
        
        # Check columns
        expected_cols = ["delta", "theta", "lalpha", "halpha", "beta", "gamma"]
        assert list(bands.columns) == expected_cols

    def test_band_values(self):
        """Test BANDS contains correct frequency values."""
        bands = scitex.dsp.params.BANDS
        
        # Expected values
        expected = {
            "delta": [0.5, 4],
            "theta": [4, 8],
            "lalpha": [8, 10],
            "halpha": [10, 13],
            "beta": [13, 32],
            "gamma": [32, 75]
        }
        
        for band, (low, high) in expected.items():
            assert bands[band]["low_hz"] == low
            assert bands[band]["high_hz"] == high

    def test_band_ordering(self):
        """Test bands are in increasing frequency order."""
        bands = scitex.dsp.params.BANDS
        
        # Check that low < high for each band
        for col in bands.columns:
            assert bands[col]["low_hz"] < bands[col]["high_hz"]
        
        # Check that bands don't overlap (each starts where previous ends)
        cols = list(bands.columns)
        for i in range(len(cols) - 1):
            assert bands[cols[i]]["high_hz"] == bands[cols[i+1]]["low_hz"]

    def test_band_coverage(self):
        """Test frequency bands cover typical EEG range."""
        bands = scitex.dsp.params.BANDS
        
        # Check minimum frequency
        assert bands.iloc[0].min() == 0.5  # Starts at 0.5 Hz
        
        # Check maximum frequency
        assert bands.iloc[1].max() == 75  # Ends at 75 Hz
        
        # Check continuous coverage
        all_lows = bands.loc["low_hz"].values
        all_highs = bands.loc["high_hz"].values
        
        # Sort to ensure continuity
        all_freqs = np.sort(np.concatenate([all_lows, all_highs]))
        
        # Check no gaps (each value appears twice except first and last)
        unique, counts = np.unique(all_freqs, return_counts=True)
        assert counts[0] == 1  # First frequency appears once
        assert counts[-1] == 1  # Last frequency appears once
        assert all(c == 2 for c in counts[1:-1])  # Middle frequencies appear twice

    def test_band_access(self):
        """Test different ways to access band information."""
        bands = scitex.dsp.params.BANDS
        
        # Access by band name
        assert bands["delta"]["low_hz"] == 0.5
        assert bands["gamma"]["high_hz"] == 75
        
        # Access by frequency type
        assert bands.loc["low_hz", "theta"] == 4
        assert bands.loc["high_hz", "beta"] == 32
        
        # Get all low frequencies
        low_freqs = bands.loc["low_hz"]
        assert len(low_freqs) == 6
        assert all(isinstance(f, (int, float)) for f in low_freqs)


class TestEEGMontage1020:
    """Test EEG_MONTAGE_1020 parameter."""

    def test_import(self):
        """Test EEG_MONTAGE_1020 can be imported."""
        assert hasattr(scitex.dsp.params, "EEG_MONTAGE_1020")

    def test_montage_structure(self):
        """Test EEG_MONTAGE_1020 is a list of strings."""
        montage = scitex.dsp.params.EEG_MONTAGE_1020
        
        # Check type
        assert isinstance(montage, list)
        
        # Check all elements are strings
        assert all(isinstance(ch, str) for ch in montage)
        
        # Check length (standard 10-20 without reference/ground)
        assert len(montage) == 19

    def test_channel_names(self):
        """Test channel names follow 10-20 convention."""
        montage = scitex.dsp.params.EEG_MONTAGE_1020
        
        expected_channels = [
            "FP1", "F3", "C3", "P3", "O1",  # Left hemisphere
            "FP2", "F4", "C4", "P4", "O2",  # Right hemisphere
            "F7", "T7", "P7",  # Left lateral
            "F8", "T8", "P8",  # Right lateral
            "FZ", "CZ", "PZ"   # Midline
        ]
        
        assert montage == expected_channels

    def test_channel_symmetry(self):
        """Test channels have proper left-right symmetry."""
        montage = scitex.dsp.params.EEG_MONTAGE_1020
        
        # Pairs that should exist
        pairs = [
            ("FP1", "FP2"), ("F3", "F4"), ("C3", "C4"), 
            ("P3", "P4"), ("O1", "O2"), ("F7", "F8"),
            ("T7", "T8"), ("P7", "P8")
        ]
        
        for left, right in pairs:
            assert left in montage
            assert right in montage

    def test_midline_channels(self):
        """Test midline channels are present."""
        montage = scitex.dsp.params.EEG_MONTAGE_1020
        
        midline = ["FZ", "CZ", "PZ"]
        for ch in midline:
            assert ch in montage

    def test_channel_grouping(self):
        """Test channels can be grouped by region."""
        montage = scitex.dsp.params.EEG_MONTAGE_1020
        
        # Frontal channels
        frontal = [ch for ch in montage if ch.startswith("F")]
        assert len(frontal) == 7  # FP1, FP2, F3, F4, F7, F8, FZ
        
        # Central channels
        central = [ch for ch in montage if ch.startswith("C")]
        assert len(central) == 3  # C3, C4, CZ
        
        # Parietal channels
        parietal = [ch for ch in montage if ch.startswith("P")]
        assert len(parietal) == 5  # P3, P4, P7, P8, PZ
        
        # Temporal channels
        temporal = [ch for ch in montage if ch.startswith("T")]
        assert len(temporal) == 2  # T7, T8
        
        # Occipital channels
        occipital = [ch for ch in montage if ch.startswith("O")]
        assert len(occipital) == 2  # O1, O2


class TestEEGMontageBipolarTransverse:
    """Test EEG_MONTAGE_BIPOLAR_TRANVERSE parameter."""

    def test_import(self):
        """Test EEG_MONTAGE_BIPOLAR_TRANVERSE can be imported."""
        assert hasattr(scitex.dsp.params, "EEG_MONTAGE_BIPOLAR_TRANVERSE")

    def test_montage_structure(self):
        """Test bipolar montage is a list of strings."""
        montage = scitex.dsp.params.EEG_MONTAGE_BIPOLAR_TRANVERSE
        
        # Check type
        assert isinstance(montage, list)
        
        # Check all elements are strings
        assert all(isinstance(ch, str) for ch in montage)
        
        # Check all are bipolar pairs (contain hyphen)
        assert all("-" in ch for ch in montage)

    def test_bipolar_pairs(self):
        """Test bipolar pairs are properly formatted."""
        montage = scitex.dsp.params.EEG_MONTAGE_BIPOLAR_TRANVERSE
        
        expected_pairs = [
            # Frontal
            "FP1-FP2", "F7-F3", "F3-FZ", "FZ-F4", "F4-F8",
            # Central
            "T7-C3", "C3-CZ", "CZ-C4", "C4-T8",
            # Parietal
            "P7-P3", "P3-PZ", "PZ-P4", "P4-P8",
            # Occipital
            "O1-O2"
        ]
        
        assert montage == expected_pairs

    def test_transverse_chains(self):
        """Test transverse chains are continuous."""
        montage = scitex.dsp.params.EEG_MONTAGE_BIPOLAR_TRANVERSE
        
        # Frontal chain
        frontal = ["FP1-FP2", "F7-F3", "F3-FZ", "FZ-F4", "F4-F8"]
        assert montage[:5] == frontal
        
        # Central chain
        central = ["T7-C3", "C3-CZ", "CZ-C4", "C4-T8"]
        assert montage[5:9] == central
        
        # Parietal chain
        parietal = ["P7-P3", "P3-PZ", "PZ-P4", "P4-P8"]
        assert montage[9:13] == parietal
        
        # Occipital chain
        occipital = ["O1-O2"]
        assert montage[13:14] == occipital

    def test_channel_consistency(self):
        """Test all channels in pairs exist in standard 10-20."""
        montage = scitex.dsp.params.EEG_MONTAGE_BIPOLAR_TRANVERSE
        standard = scitex.dsp.params.EEG_MONTAGE_1020
        
        for pair in montage:
            ch1, ch2 = pair.split("-")
            assert ch1 in standard, f"{ch1} not in standard 10-20"
            assert ch2 in standard, f"{ch2} not in standard 10-20"

    def test_no_duplicate_pairs(self):
        """Test no duplicate bipolar pairs."""
        montage = scitex.dsp.params.EEG_MONTAGE_BIPOLAR_TRANVERSE
        
        # Check no duplicates
        assert len(montage) == len(set(montage))
        
        # Check no reversed duplicates (e.g., "F3-FZ" and "FZ-F3")
        normalized = []
        for pair in montage:
            ch1, ch2 = pair.split("-")
            normalized.append(tuple(sorted([ch1, ch2])))
        
        assert len(normalized) == len(set(normalized))


class TestParamsUsage:
    """Test practical usage of DSP parameters."""

    def test_bands_for_filtering(self):
        """Test bands can be used for filtering operations."""
        bands = scitex.dsp.params.BANDS
        
        # Simulate getting filter parameters
        for band_name in bands.columns:
            low_freq = bands[band_name]["low_hz"]
            high_freq = bands[band_name]["high_hz"]
            
            # Check values are numeric and valid
            assert isinstance(low_freq, (int, float))
            assert isinstance(high_freq, (int, float))
            assert 0 < low_freq < high_freq < 100

    def test_montage_indexing(self):
        """Test montages can be used for channel indexing."""
        montage = scitex.dsp.params.EEG_MONTAGE_1020
        
        # Create channel index mapping
        ch_to_idx = {ch: i for i, ch in enumerate(montage)}
        
        # Test indexing
        assert ch_to_idx["FP1"] == 0
        assert ch_to_idx["O2"] == 9
        assert ch_to_idx["PZ"] == 18
        
        # Test reverse mapping
        idx_to_ch = {i: ch for i, ch in enumerate(montage)}
        assert idx_to_ch[0] == "FP1"
        assert idx_to_ch[18] == "PZ"


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/dsp/params.py
# --------------------------------------------------------------------------------
# import numpy as np
# import pandas as pd
#
# BANDS = pd.DataFrame(
#     data=np.array([[0.5, 4], [4, 8], [8, 10], [10, 13], [13, 32], [32, 75]]).T,
#     index=["low_hz", "high_hz"],
#     columns=["delta", "theta", "lalpha", "halpha", "beta", "gamma"],
# )
#
# EEG_MONTAGE_1020 = [
#     "FP1",
#     "F3",
#     "C3",
#     "P3",
#     "O1",
#     "FP2",
#     "F4",
#     "C4",
#     "P4",
#     "O2",
#     "F7",
#     "T7",
#     "P7",
#     "F8",
#     "T8",
#     "P8",
#     "FZ",
#     "CZ",
#     "PZ",
# ]
#
# EEG_MONTAGE_BIPOLAR_TRANVERSE = [
#     # Frontal
#     "FP1-FP2",
#     "F7-F3",
#     "F3-FZ",
#     "FZ-F4",
#     "F4-F8",
#     # Central
#     "T7-C3",
#     "C3-CZ",
#     "CZ-C4",
#     "C4-T8",
#     # Parietal
#     "P7-P3",
#     "P3-PZ",
#     "PZ-P4",
#     "P4-P8",
#     # Occipital
#     "O1-O2",
# ]

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/dsp/params.py
# --------------------------------------------------------------------------------
