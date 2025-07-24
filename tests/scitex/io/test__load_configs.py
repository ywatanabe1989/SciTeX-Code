#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 20:00:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/io/test__load_configs.py

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, MagicMock
from scitex.io import load_configs
from scitex.dict import DotDict


class TestLoadConfigs:
    """Test cases for load_configs function."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary config directory with test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "config")
            os.makedirs(config_dir)

            # Create test config files
            config1 = {
                "param1": "value1",
                "param2": 123,
                "nested": {"key1": "val1", "DEBUG_key2": "debug_val2"},
            }
            with open(os.path.join(config_dir, "config1.yaml"), "w") as f:
                yaml.dump(config1, f)

            config2 = {
                "param3": "value3",
                "DEBUG_param4": "debug_value4",
                "debug_param5": "debug_value5",
            }
            with open(os.path.join(config_dir, "config2.yaml"), "w") as f:
                yaml.dump(config2, f)

            # Create IS_DEBUG.yaml
            with open(os.path.join(config_dir, "IS_DEBUG.yaml"), "w") as f:
                yaml.dump({"IS_DEBUG": False}, f)

            yield tmpdir

    @patch("scitex.io._load_configs.glob")
    @patch("scitex.io._load_configs.load")
    def test_load_configs_basic(self, mock_load, mock_glob):
        """Test basic loading of config files."""
        # Setup mocks
        mock_glob.return_value = ["./config/config1.yaml", "./config/config2.yaml"]
        mock_load.side_effect = [
            {"IS_DEBUG": False},  # IS_DEBUG.yaml
            {"param1": "value1", "param2": 123},  # config1.yaml
            {"param3": "value3"},  # config2.yaml
        ]

        result = load_configs(IS_DEBUG=False)

        assert isinstance(result, DotDict)
        assert result.param1 == "value1"
        assert result.param2 == 123
        assert result.param3 == "value3"

    @patch("scitex.io._load_configs.glob")
    @patch("scitex.io._load_configs.load")
    def test_load_configs_debug_mode(self, mock_load, mock_glob):
        """Test loading configs with debug mode enabled."""
        # Setup mocks
        mock_glob.return_value = ["./config/config1.yaml"]
        mock_load.return_value = {
            "param1": "normal_value",
            "DEBUG_param1": "debug_value",
            "debug_param2": "another_debug_value",
        }

        result = load_configs(IS_DEBUG=True)

        # Debug values should override normal values
        assert result.param1 == "debug_value"
        assert result.param2 == "another_debug_value"

    @patch("scitex.io._load_configs.glob")
    @patch("scitex.io._load_configs.load")
    def test_load_configs_nested_debug(self, mock_load, mock_glob):
        """Test debug value replacement in nested structures."""
        # Setup mocks
        mock_glob.return_value = ["./config/config1.yaml"]
        mock_load.return_value = {
            "top_level": {
                "normal_key": "normal_value",
                "DEBUG_special_key": "debug_special_value",
                "nested": {"debug_nested_key": "debug_nested_value"},
            }
        }

        result = load_configs(IS_DEBUG=True)

        # Check nested debug value replacement
        assert result.top_level.special_key == "debug_special_value"
        assert result.top_level.nested.nested_key == "debug_nested_value"
        assert result.top_level.normal_key == "normal_value"

    @patch("scitex.io._load_configs.os.getenv")
    @patch("scitex.io._load_configs.glob")
    @patch("scitex.io._load_configs.load")
    def test_load_configs_ci_environment(self, mock_load, mock_glob, mock_getenv):
        """Test that CI environment variable enables debug mode."""
        mock_getenv.return_value = "True"
        mock_glob.return_value = ["./config/config1.yaml"]
        mock_load.return_value = {"param": "normal", "DEBUG_param": "debug"}

        result = load_configs(IS_DEBUG=None)

        # CI should enable debug mode
        assert result.param == "debug"

    @patch("scitex.io._load_configs.glob")
    @patch("scitex.io._load_configs.load")
    @patch("scitex.io._load_configs.os.path.exists")
    def test_load_configs_from_is_debug_file(self, mock_exists, mock_load, mock_glob):
        """Test loading debug mode from IS_DEBUG.yaml file."""
        mock_exists.return_value = True
        mock_glob.return_value = ["./config/config1.yaml"]
        mock_load.side_effect = [
            {"IS_DEBUG": True},  # IS_DEBUG.yaml
            {"param": "normal", "DEBUG_param": "debug"},  # config1.yaml
        ]

        result = load_configs(IS_DEBUG=None)

        # Should read debug mode from file
        assert result.param == "debug"

    @patch("scitex.io._load_configs.glob")
    @patch("scitex.io._load_configs.load")
    def test_load_configs_show_output(self, mock_load, mock_glob, capsys):
        """Test verbose output during debug value replacement."""
        mock_glob.return_value = ["./config/config1.yaml"]
        mock_load.return_value = {"DEBUG_param": "debug_value"}

        load_configs(IS_DEBUG=True, show=True)

        captured = capsys.readouterr()
        assert "DEBUG_param -> param" in captured.out

    @patch("scitex.io._load_configs.glob")
    @patch("scitex.io._load_configs.load")
    def test_load_configs_empty_config(self, mock_load, mock_glob):
        """Test loading empty config files."""
        mock_glob.return_value = ["./config/empty.yaml"]
        mock_load.return_value = None

        result = load_configs()

        assert isinstance(result, DotDict)
        assert len(result) == 0

    @patch("scitex.io._load_configs.glob")
    def test_load_configs_exception_handling(self, mock_glob, capsys):
        """Test exception handling during config loading."""
        mock_glob.side_effect = Exception("Test error")

        result = load_configs()

        # Should return empty DotDict on error
        assert isinstance(result, DotDict)
        assert len(result) == 0

        # Should print error message
        captured = capsys.readouterr()
        assert "Error loading configs" in captured.out

    @patch("scitex.io._load_configs.glob")
    @patch("scitex.io._load_configs.load")
    def test_load_configs_merge_multiple_files(self, mock_load, mock_glob):
        """Test merging configs from multiple files."""
        mock_glob.return_value = [
            "./config/a.yaml",
            "./config/b.yaml",
            "./config/c.yaml",
        ]
        mock_load.side_effect = [
            {"param1": "value1", "shared": "from_a"},
            {"param2": "value2", "shared": "from_b"},
            {"param3": "value3"},
        ]

        result = load_configs(IS_DEBUG=False)

        # All params should be present
        assert result.param1 == "value1"
        assert result.param2 == "value2"
        assert result.param3 == "value3"
        # Later files should override earlier ones
        assert result.shared == "from_b"

    def test_load_configs_with_real_files(self, temp_config_dir):
        """Test with real config files in temp directory."""
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_config_dir)

        try:
            result = load_configs(IS_DEBUG=False)

            # Check loaded values
            assert result.param1 == "value1"
            assert result.param2 == 123
            assert result.param3 == "value3"
            assert result.nested.key1 == "val1"

            # Debug values should not be applied
            assert "param4" not in result
            assert "param5" not in result

        finally:
            os.chdir(original_cwd)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_configs.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-22 07:19:03 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_configs.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "/ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_configs.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_configs.py"
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2025-02-27 11:09:00 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/io/_load_configs.py
# 
# from ..dict import DotDict
# from ._load import load
# from ._glob import glob
# 
# 
# def load_configs(IS_DEBUG=None, show=False, verbose=False):
#     """Load YAML configuration files from ./config directory.
# 
#     Parameters
#     ----------
#     IS_DEBUG : bool, optional
#         Debug mode flag. If None, reads from IS_DEBUG.yaml
#     show : bool
#         Show configuration changes
#     verbose : bool
#         Print detailed information
# 
#     Returns
#     -------
#     DotDict
#         Merged configuration dictionary
#     """
# 
#     def apply_debug_values(config, IS_DEBUG):
#         """Apply debug values if IS_DEBUG is True."""
#         if not IS_DEBUG or not isinstance(config, (dict, DotDict)):
#             return config
# 
#         for key, value in list(config.items()):
#             if key.startswith(("DEBUG_", "debug_")):
#                 dk_wo_debug_prefix = key.split("_", 1)[1]
#                 config[dk_wo_debug_prefix] = value
#                 if show or verbose:
#                     print(f"{key} -> {dk_wo_debug_prefix}")
#             elif isinstance(value, (dict, DotDict)):
#                 config[key] = apply_debug_values(value, IS_DEBUG)
#         return config
# 
#     try:
#         # Set debug mode
#         IS_DEBUG = (
#             IS_DEBUG
#             or os.getenv("CI") == "True"
#             or (
#                 os.path.exists("./config/IS_DEBUG.yaml")
#                 and load("./config/IS_DEBUG.yaml").get("IS_DEBUG")
#             )
#         )
# 
#         # Load and merge configs
#         CONFIGS = {}
#         for lpath in glob("./config/*.yaml"):
#             if config := load(lpath):
#                 CONFIGS.update(apply_debug_values(config, IS_DEBUG))
# 
#         return DotDict(CONFIGS)
# 
#     except Exception as e:
#         print(f"Error loading configs: {e}")
#         return DotDict({})
# 
# 
# # def load_configs(IS_DEBUG=None, show=False, verbose=False):
# #     """
# #     Load configuration files from the ./config directory.
# 
# #     Parameters:
# #     -----------
# #     IS_DEBUG : bool, optional
# #         If True, use debug configurations. If None, check ./config/IS_DEBUG.yaml.
# #     show : bool, optional
# #         If True, display additional information during loading.
# #     verbose : bool, optional
# #         If True, print verbose output during loading.
# 
# #     Returns:
# #     --------
# #     DotDict
# #         A dictionary-like object containing the loaded configurations.
# #     """
# 
# #     def apply_debug_values(config, IS_DEBUG):
# #         if IS_DEBUG:
# #             if isinstance(config, (dict, DotDict)):
# #                 for key, value in list(config.items()):
# #                     try:
# #                         if key.startswith(("DEBUG_", "debug_")):
# #                             dk_wo_debug_prefix = key.split("_", 1)[1]
# #                             config[dk_wo_debug_prefix] = value
# #                             if show or verbose:
# #                                 print(f"\n{key} -> {dk_wo_debug_prefix}\n")
# #                         elif isinstance(value, (dict, DotDict)):
# #                             config[key] = apply_debug_values(value, IS_DEBUG)
# #                     except Exception as e:
# #                         print(e)
# #         return config
# 
# #     if os.getenv("CI") == "True":
# #         IS_DEBUG = True
# 
# #     try:
# #         # Check ./config/IS_DEBUG.yaml file if IS_DEBUG argument is not passed
# #         if IS_DEBUG is None:
# #             IS_DEBUG_PATH = "./config/IS_DEBUG.yaml"
# #             if os.path.exists(IS_DEBUG_PATH):
# #                 IS_DEBUG = load("./config/IS_DEBUG.yaml").get("IS_DEBUG")
# #             else:
# #                 IS_DEBUG = False
# 
# #         # Main
# #         CONFIGS = {}
# #         for lpath in glob("./config/*.yaml"):
# #             config = load(lpath)
# #             if config:
# #                 CONFIG = apply_debug_values(config, IS_DEBUG)
# #                 CONFIGS.update(CONFIG)
# 
# #         CONFIGS = DotDict(CONFIGS)
# 
# #     except Exception as e:
# #         print(e)
# #         CONFIGS = DotDict({})
# 
# #     return CONFIGS
# 
# 
# #
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_configs.py
# --------------------------------------------------------------------------------
