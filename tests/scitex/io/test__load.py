#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-30 01:00:00 (Claude)"
# File: /tests/scitex/io/test__load.py

import os
import json
import tempfile
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

import scitex.io


class TestLoad:
    """Test cases for scitex.io.load function."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_load_json(self, temp_dir):
        """Test loading JSON files."""
        # Arrange
        test_data = {"name": "test", "value": 42, "array": [1, 2, 3]}
        json_path = os.path.join(temp_dir, "test.json")
        with open(json_path, "w") as f:
            json.dump(test_data, f)

        # Act
        loaded_data = scitex.io.load(json_path)

        # Assert
        assert loaded_data == test_data
        assert isinstance(loaded_data, dict)

    def test_load_yaml(self, temp_dir):
        """Test loading YAML files."""
        # Arrange
        yaml_content = """
name: test
value: 42
array:
  - 1
  - 2
  - 3
"""
        yaml_path = os.path.join(temp_dir, "test.yaml")
        with open(yaml_path, "w") as f:
            f.write(yaml_content)

        # Act
        loaded_data = scitex.io.load(yaml_path)

        # Assert
        assert loaded_data["name"] == "test"
        assert loaded_data["value"] == 42
        assert loaded_data["array"] == [1, 2, 3]

    def test_load_csv(self, temp_dir):
        """Test loading CSV files."""
        # Arrange
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"], "C": [1.1, 2.2, 3.3]})
        csv_path = os.path.join(temp_dir, "test.csv")
        df.to_csv(csv_path, index=False)

        # Act
        loaded_df = scitex.io.load(csv_path)

        # Assert
        assert isinstance(loaded_df, pd.DataFrame)
        pd.testing.assert_frame_equal(loaded_df, df)

    def test_load_numpy(self, temp_dir):
        """Test loading NumPy array files."""
        # Arrange
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        npy_path = os.path.join(temp_dir, "test.npy")
        np.save(npy_path, arr)

        # Act
        loaded_arr = scitex.io.load(npy_path)

        # Assert
        assert isinstance(loaded_arr, np.ndarray)
        np.testing.assert_array_equal(loaded_arr, arr)

    def test_load_txt(self, temp_dir):
        """Test loading text files."""
        # Arrange
        text_content = "Hello\nWorld\nTest"
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, "w") as f:
            f.write(text_content)

        # Act
        loaded_text = scitex.io.load(txt_path)

        # Assert
        assert loaded_text == text_content

    def test_load_markdown(self, temp_dir):
        """Test loading markdown files."""
        # Arrange
        md_content = "# Header\n\nThis is a **test** markdown file."
        md_path = os.path.join(temp_dir, "test.md")
        with open(md_path, "w") as f:
            f.write(md_content)

        # Act
        loaded_md = scitex.io.load(md_path)

        # Assert
        assert "Header" in loaded_md
        assert "test" in loaded_md

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        # Arrange
        fake_path = "/path/to/nonexistent/file.txt"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            scitex.io.load(fake_path)

    def test_load_with_extension_no_dot(self, temp_dir):
        """Test loading a file without extension."""
        # Arrange
        text_content = "File without extension"
        no_ext_path = os.path.join(temp_dir, "testfile")
        with open(no_ext_path, "w") as f:
            f.write(text_content)

        # Act
        loaded_text = scitex.io.load(no_ext_path)

        # Assert
        assert loaded_text == text_content

    def test_load_pickle(self, temp_dir):
        """Test loading pickle files."""
        # Arrange
        import pickle

        test_obj = {"key": "value", "list": [1, 2, 3], "nested": {"a": 1}}
        pkl_path = os.path.join(temp_dir, "test.pkl")
        with open(pkl_path, "wb") as f:
            pickle.dump(test_obj, f)

        # Act
        loaded_obj = scitex.io.load(pkl_path)

        # Assert
        assert loaded_obj == test_obj

    def test_load_excel(self, temp_dir):
        """Test loading Excel files."""
        # Arrange
        df = pd.DataFrame({"Col1": [1, 2, 3], "Col2": ["x", "y", "z"]})
        excel_path = os.path.join(temp_dir, "test.xlsx")
        df.to_excel(excel_path, index=False)

        # Act
        loaded_df = scitex.io.load(excel_path)

        # Assert
        assert isinstance(loaded_df, pd.DataFrame)
        pd.testing.assert_frame_equal(loaded_df, df)

    def test_load_tsv(self, temp_dir):
        """Test loading TSV files."""
        # Arrange
        df = pd.DataFrame({"A": [10, 20, 30], "B": ["foo", "bar", "baz"]})
        tsv_path = os.path.join(temp_dir, "test.tsv")
        df.to_csv(tsv_path, sep="\t", index=False)

        # Act
        loaded_df = scitex.io.load(tsv_path)

        # Assert
        assert isinstance(loaded_df, pd.DataFrame)
        pd.testing.assert_frame_equal(loaded_df, df)

    def test_load_clean_path(self, temp_dir):
        """Test that paths are cleaned properly."""
        # Arrange
        text_content = "Path cleaning test"
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, "w") as f:
            f.write(text_content)

        # Create path with extra slashes
        messy_path = txt_path.replace("/", "//")

        # Act
        loaded_text = scitex.io.load(messy_path)

        # Assert
        assert loaded_text == text_content


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_load.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-10 08:05:53 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "/ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# from typing import Any
# from ..decorators import preserve_doc
# from ..str._clean_path import clean_path
# # from ._load_modules._catboost import _load_catboost
# from ._load_modules._con import _load_con
# from ._load_modules._db import _load_sqlite3db
# from ._load_modules._docx import _load_docx
# from ._load_modules._eeg import _load_eeg_data
# from ._load_modules._hdf5 import _load_hdf5
# from ._load_modules._image import _load_image
# from ._load_modules._joblib import _load_joblib
# from ._load_modules._json import _load_json
# from ._load_modules._markdown import _load_markdown
# from ._load_modules._numpy import _load_npy
# from ._load_modules._matlab import _load_matlab
# from ._load_modules._pandas import _load_csv, _load_excel, _load_tsv
# from ._load_modules._pdf import _load_pdf
# from ._load_modules._pickle import _load_pickle
# from ._load_modules._torch import _load_torch
# from ._load_modules._txt import _load_txt
# from ._load_modules._xml import _load_xml
# from ._load_modules._yaml import _load_yaml
# from ._load_modules._matlab import _load_matlab
#
# def load(
#     lpath: str, show: bool = False, verbose: bool = False, **kwargs
# ) -> Any:
#     """
#     Load data from various file formats.
#
#     This function supports loading data from multiple file formats.
#
#     Parameters
#     ----------
#     lpath : str
#         The path to the file to be loaded.
#     show : bool, optional
#         If True, display additional information during loading. Default is False.
#     verbose : bool, optional
#         If True, print verbose output during loading. Default is False.
#     **kwargs : dict
#         Additional keyword arguments to be passed to the specific loading function.
#
#     Returns
#     -------
#     object
#         The loaded data object, which can be of various types depending on the input file format.
#
#     Raises
#     ------
#     ValueError
#         If the file extension is not supported.
#     FileNotFoundError
#         If the specified file does not exist.
#
#     Supported Extensions
#     -------------------
#     - Data formats: .csv, .tsv, .xls, .xlsx, .xlsm, .xlsb, .json, .yaml, .yml
#     - Scientific: .npy, .npz, .mat, .hdf5, .con
#     - ML/DL: .pth, .pt, .cbm, .joblib, .pkl
#     - Documents: .txt, .log, .event, .md, .docx, .pdf, .xml
#     - Images: .jpg, .png, .tiff, .tif
#     - EEG data: .vhdr, .vmrk, .edf, .bdf, .gdf, .cnt, .egi, .eeg, .set
#     - Database: .db
#
#     Examples
#     --------
#     >>> data = load('data.csv')
#     >>> image = load('image.png')
#     >>> model = load('model.pth')
#     """
#     lpath = clean_path(lpath)
#
#     if not os.path.exists(lpath):
#         raise FileNotFoundError(f"{lpath} not found.")
#
#     loaders_dict = {
#         # Default
#         "": _load_txt,
#         # Config/Settings
#         "yaml": _load_yaml,
#         "yml": _load_yaml,
#         "json": _load_json,
#         "xml": _load_xml,
#         # ML/DL Models
#         "pth": _load_torch,
#         "pt": _load_torch,
#         # "cbm": _load_catboost,
#         "joblib": _load_joblib,
#         "pkl": _load_pickle,
#         # Tabular Data
#         "csv": _load_csv,
#         "tsv": _load_tsv,
#         "xls": _load_excel,
#         "xlsx": _load_excel,
#         "xlsm": _load_excel,
#         "xlsb": _load_excel,
#         "db": _load_sqlite3db,
#         # Scientific Data
#         "npy": _load_npy,
#         "npz": _load_npy,
#         "mat": _load_matlab,
#         "hdf5": _load_hdf5,
#         "mat": _load_matlab,
#         "con": _load_con,
#         # Documents
#         "txt": _load_txt,
#         "tex": _load_txt,
#         "log": _load_txt,
#         "event": _load_txt,
#         "py": _load_txt,
#         "sh": _load_txt,
#         "md": _load_markdown,
#         "docx": _load_docx,
#         "pdf": _load_pdf,
#         # Images
#         "jpg": _load_image,
#         "png": _load_image,
#         "tiff": _load_image,
#         "tif": _load_image,
#         # EEG Data
#         "vhdr": _load_eeg_data,
#         "vmrk": _load_eeg_data,
#         "edf": _load_eeg_data,
#         "bdf": _load_eeg_data,
#         "gdf": _load_eeg_data,
#         "cnt": _load_eeg_data,
#         "egi": _load_eeg_data,
#         "eeg": _load_eeg_data,
#         "set": _load_eeg_data,
#     }
#
#     ext = lpath.split(".")[-1] if "." in lpath else ""
#     loader = preserve_doc(loaders_dict.get(ext, _load_txt))
#
#     try:
#         return loader(lpath, **kwargs)
#     except (ValueError, FileNotFoundError) as e:
#         raise ValueError(f"Error loading file {lpath}: {str(e)}")
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_load.py
# --------------------------------------------------------------------------------


def test_load_hdf5_with_h5explorer():
    """Test loading HDF5 files using H5Explorer integration."""
    try:
        import h5py
    except ImportError:
        pytest.skip("h5py not installed")
    
    from scitex.io import save, load
    from scitex.io._H5Explorer import H5Explorer
    
    with tempfile.TemporaryDirectory() as tmpdir:
        h5_path = os.path.join(tmpdir, "test_load.h5")
        
        # Create test data with nested structure
        test_data = {
            'arrays': {
                'data1': np.random.rand(10, 10),
                'data2': np.arange(50).reshape(5, 10)
            },
            'metadata': {
                'experiment': 'test',
                'date': '2025-01-01',
                'params': {'learning_rate': 0.01, 'epochs': 100}
            }
        }
        
        # Save using the new key parameter
        save(test_data['arrays'], h5_path, key='arrays', verbose=False)
        save(test_data['metadata'], h5_path, key='metadata', verbose=False)
        
        # Test 1: Load entire HDF5 file
        loaded_all = load(h5_path)
        assert isinstance(loaded_all, dict) or hasattr(loaded_all, 'file')
        
        # Test 2: Use H5Explorer to load specific keys
        with H5Explorer(h5_path) as explorer:
            # Load arrays group
            arrays = explorer.load('/arrays')
            np.testing.assert_array_equal(arrays['data1'], test_data['arrays']['data1'])
            np.testing.assert_array_equal(arrays['data2'], test_data['arrays']['data2'])
            
            # Load metadata group
            metadata = explorer.load('/metadata')
            assert metadata['experiment'] == test_data['metadata']['experiment']
            assert metadata['date'] == test_data['metadata']['date']
        
        # Test 3: Save and load single array (not dict)
        single_array = np.random.rand(20, 20)
        h5_path2 = os.path.join(tmpdir, "single_array.h5")
        save(single_array, h5_path2, verbose=False)
        
        # When loading single array saved to HDF5, it should be in 'data' key
        with H5Explorer(h5_path2) as explorer:
            loaded_single = explorer.load('/data')
            np.testing.assert_array_equal(loaded_single, single_array)
