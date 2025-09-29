#!/usr/bin/env python3
"""Tests for scitex.gen._print_config module."""

import pytest
import sys
from unittest.mock import patch, MagicMock, call
from io import StringIO
import argparse

from scitex.gen import print_config
from scitex.gen._print_config import print_config_main



class TestPrintConfig:
    """Test cases for print_config function."""

    @patch("scitex.gen._print_config.scitex.io.load_configs")
    @patch("builtins.print")
    def test_print_config_no_key(self, mock_print, mock_load_configs):
        """Test print_config with no key - should print all configs."""

        # Mock config data
        mock_config = {
            "database": {"host": "localhost", "port": 5432},
            "api": {"key": "secret123", "timeout": 30},
        }
        mock_load_configs.return_value = mock_config

        # Call with no key
        print_config(None)

        # Should print available configurations message
        assert any(
            "Available configurations:" in str(call)
            for call in mock_print.call_args_list
        )
        # pprint is called internally, so we check if print was called multiple times
        assert mock_print.call_count >= 1

    @patch("scitex.gen._print_config.scitex.io.load_configs")
    @patch("builtins.print")
    def test_print_config_simple_key(self, mock_print, mock_load_configs):
        """Test print_config with simple top-level key."""

        mock_config = {"version": "1.0.0", "debug": True, "timeout": 30}
        mock_load_configs.return_value = mock_config

        # Test string value
        print_config("version")
        mock_print.assert_called_with("1.0.0")

        # Test boolean value
        mock_print.reset_mock()
        print_config("debug")
        mock_print.assert_called_with(True)

        # Test integer value
        mock_print.reset_mock()
        print_config("timeout")
        mock_print.assert_called_with(30)

    @patch("scitex.gen._print_config.scitex.io.load_configs")
    @patch("builtins.print")
    def test_print_config_nested_key(self, mock_print, mock_load_configs):
        """Test print_config with nested dot-separated keys."""

        mock_config = {
            "database": {
                "postgres": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {"user": "admin", "password": "secret"},
                }
            }
        }
        mock_load_configs.return_value = mock_config

        # Test 2-level nesting
        print_config("database.postgres")
        expected = {
            "host": "localhost",
            "port": 5432,
            "credentials": {"user": "admin", "password": "secret"},
        }
        mock_print.assert_called_with(expected)

        # Test 3-level nesting
        mock_print.reset_mock()
        print_config("database.postgres.host")
        mock_print.assert_called_with("localhost")

        # Test 4-level nesting
        mock_print.reset_mock()
        print_config("database.postgres.credentials.user")
        mock_print.assert_called_with("admin")

    @patch("scitex.gen._print_config.scitex.io.load_configs")
    @patch("builtins.print")
    def test_print_config_list_access(self, mock_print, mock_load_configs):
        """Test print_config with list index access."""

        mock_config = {
            "servers": ["server1", "server2", "server3"],
            "ports": [8080, 8081, 8082],
            "nested": {
                "items": [
                    {"name": "item1", "value": 10},
                    {"name": "item2", "value": 20},
                ]
            },
        }
        mock_load_configs.return_value = mock_config

        # Access list by index
        print_config("servers.0")
        mock_print.assert_called_with("server1")

        mock_print.reset_mock()
        print_config("servers.2")
        mock_print.assert_called_with("server3")

        # Access nested list item
        mock_print.reset_mock()
        print_config("nested.items.1.name")
        mock_print.assert_called_with("item2")

    @patch("scitex.gen._print_config.scitex.io.load_configs")
    @patch("builtins.print")
    def test_print_config_invalid_key(self, mock_print, mock_load_configs):
        """Test print_config with invalid/non-existent key."""

        mock_config = {"existing": "value"}
        mock_load_configs.return_value = mock_config

        # Non-existent key
        print_config("nonexistent")
        mock_print.assert_called_with(None)

        # Invalid nested key
        mock_print.reset_mock()
        print_config("existing.nested.deep")
        mock_print.assert_called_with(None)

    @patch("scitex.gen._print_config.scitex.io.load_configs")
    @patch("builtins.print")
    def test_print_config_dotdict_support(self, mock_print, mock_load_configs):
        """Test print_config with DotDict objects."""

        # Mock DotDict behavior
        mock_dotdict = MagicMock()
        mock_dotdict.get.side_effect = lambda k: (
            {"inner": "value"} if k == "nested" else None
        )

        mock_config = {"data": mock_dotdict}
        mock_load_configs.return_value = mock_config

        print_config("data.nested")
        mock_dotdict.get.assert_called_with("nested")

    @patch("scitex.gen._print_config.scitex.io.load_configs")
    @patch("builtins.print")
    def test_print_config_exception_handling(self, mock_print, mock_load_configs):
        """Test print_config exception handling."""

        # Mock config that raises exception
        mock_load_configs.side_effect = Exception("Config load failed")

        # Should handle exception gracefully
        print_config("any.key")

        # Check that error was printed
        assert any("Error:" in str(call) for call in mock_print.call_args_list)


class TestPrintConfigMain:
    """Test cases for print_config_main function."""

    @patch("scitex.gen._print_config.print_config")
    def test_print_config_main_no_args(self, mock_print_config):
        """Test print_config_main with no arguments."""

        print_config_main([])
        mock_print_config.assert_called_once_with(None)

    @patch("scitex.gen._print_config.print_config")
    def test_print_config_main_with_key(self, mock_print_config):
        """Test print_config_main with key argument."""

        print_config_main(["database.host"])
        mock_print_config.assert_called_once_with("database.host")

    @patch("scitex.gen._print_config.print_config")
    def test_print_config_main_with_nested_key(self, mock_print_config):
        """Test print_config_main with complex nested key."""

        print_config_main(["path.to.nested.config.value"])
        mock_print_config.assert_called_once_with("path.to.nested.config.value")

    @patch("scitex.gen._print_config.sys.argv")
    @patch("scitex.gen._print_config.print_config")
    def test_print_config_main_from_sys_argv(self, mock_print_config, mock_argv):
        """Test print_config_main using sys.argv."""

        # Simulate command line usage
        mock_argv.__getitem__.side_effect = lambda i: ["script.py", "test.key"][i]
        mock_argv.__len__.return_value = 2

        print_config_main(None)  # None means use sys.argv
        mock_print_config.assert_called_once_with("test.key")

    def test_print_config_main_help(self, capsys):
        """Test print_config_main help message."""

        with pytest.raises(SystemExit) as exc_info:
            print_config_main(["--help"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Print configuration values" in captured.out
        assert "Configuration key" in captured.out


class TestIntegration:
    """Integration tests for the print_config module."""

    @patch("scitex.gen._print_config.scitex.io.load_configs")
    def test_realistic_config_navigation(self, mock_load_configs, capsys):
        """Test realistic configuration navigation scenarios."""

        # Realistic config structure
        mock_config = {
            "PATH": {
                "TITAN": {"MAT": "/data/matlab", "DATA": "/data/raw"},
                "CREST": {
                    "HOME": "/home/user",
                    "PROJECTS": ["/proj/alpha", "/proj/beta", "/proj/gamma"],
                },
            },
            "SETTINGS": {
                "debug": False,
                "verbosity": 2,
                "features": ["logging", "caching", "monitoring"],
            },
        }
        mock_load_configs.return_value = mock_config

        # Test various access patterns
        test_cases = [
            (["PATH.TITAN.MAT"], "/data/matlab"),
            (["PATH.CREST.PROJECTS.1"], "/proj/beta"),
            (["SETTINGS.features.0"], "logging"),
            (["SETTINGS.verbosity"], "2"),  # Note: print converts to string
        ]

        for args, expected in test_cases:
            print_config_main(args)
            captured = capsys.readouterr()
            assert expected in captured.out

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_print_config.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-10-13 18:53:04 (ywatanabe)"
# # /home/yusukew/proj/scitex_repo/src/scitex/gen/_print_config.py
# 
# """
# 1. Functionality:
#    - Prints configuration values from YAML files
# 2. Input:
#    - Configuration key (dot-separated for nested structures)
# 3. Output:
#    - Corresponding configuration value
# 4. Prerequisites:
#    - scitex package with load_configs function
# 
# Example:
#     python _print_config.py PATH.TITAN.MAT
# """
# 
# 
# import sys
# import os
# import argparse
# from pprint import pprint
# import sys
# 
# 
# def print_config(key):
# 
#     CONFIG = scitex.io.load_configs()
# 
#     if key is None:
#         print("Available configurations:")
#         pprint(CONFIG)
#         return
# 
#     try:
#         keys = key.split(".")
#         value = CONFIG
#         for k in keys:
# 
#             if isinstance(value, (dict, scitex.gen.utils._DotDict.DotDict)):
#                 value = value.get(k)
# 
#             elif isinstance(value, list):
#                 try:
#                     value = value[int(k)]
#                 except (ValueError, IndexError):
#                     value = None
# 
#             elif isinstance(value, str):
#                 break
# 
#             else:
#                 value = None
# 
#             if value is None:
#                 break
# 
#         print(value)
# 
#     except Exception as e:
#         print(f"Error: {e}")
#         print("Available configurations:")
#         pprint(value)
# 
# 
# def print_config_main(args=None):
#     if args is None:
#         args = sys.argv[1:]
# 
#     parser = argparse.ArgumentParser(description="Print configuration values")
#     parser.add_argument(
#         "key",
#         nargs="?",
#         default=None,
#         help="Configuration key (dot-separated for nested structures)",
#     )
#     parsed_args = parser.parse_args(args)
#     print_config(parsed_args.key)
# 
# 
# if __name__ == "__main__":
#     print_config_main()

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_print_config.py
# --------------------------------------------------------------------------------
