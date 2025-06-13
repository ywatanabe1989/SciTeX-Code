#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:51:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__yaml.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__yaml.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for YAML saving functionality
"""

import os
import tempfile
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, date

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from scitex.io._save_modules import save_yaml


@pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
class TestSaveYAML:
    """Test suite for save_yaml function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.yaml")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_simple_dict(self):
        """Test saving simple dictionary"""
        data = {"a": 1, "b": 2, "c": "hello"}
        save_yaml(data, self.test_file)
        
        assert os.path.exists(self.test_file)
        with open(self.test_file, "r") as f:
            loaded = yaml.safe_load(f)
        assert loaded == data

    def test_save_nested_dict(self):
        """Test saving nested dictionary"""
        data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {
                    "username": "admin",
                    "password": "secret"
                }
            },
            "features": ["feature1", "feature2", "feature3"],
            "debug": True
        }
        save_yaml(data, self.test_file)
        
        with open(self.test_file, "r") as f:
            loaded = yaml.safe_load(f)
        assert loaded == data

    def test_save_list(self):
        """Test saving list"""
        data = [1, 2, 3, "four", 5.5, True, None]
        save_yaml(data, self.test_file)
        
        with open(self.test_file, "r") as f:
            loaded = yaml.safe_load(f)
        assert loaded == data

    def test_save_configuration_style(self):
        """Test saving configuration-style data"""
        config = {
            "model": {
                "type": "transformer",
                "layers": 12,
                "hidden_size": 768,
                "attention_heads": 12,
                "dropout": 0.1
            },
            "training": {
                "batch_size": 32,
                "learning_rate": 0.001,
                "epochs": 100,
                "optimizer": "adam",
                "scheduler": {
                    "type": "cosine",
                    "warmup_steps": 1000
                }
            },
            "data": {
                "train_path": "/path/to/train.csv",
                "valid_path": "/path/to/valid.csv",
                "test_path": "/path/to/test.csv",
                "preprocessing": ["tokenize", "normalize", "augment"]
            }
        }
        save_yaml(config, self.test_file)
        
        with open(self.test_file, "r") as f:
            loaded = yaml.safe_load(f)
        assert loaded == config

    def test_save_multiline_strings(self):
        """Test saving multiline strings"""
        data = {
            "description": """This is a long description
that spans multiple lines
and should be preserved in YAML format""",
            "code": "def hello():\n    print('Hello, World!')\n    return True"
        }
        save_yaml(data, self.test_file)
        
        with open(self.test_file, "r") as f:
            loaded = yaml.safe_load(f)
        assert loaded["description"] == data["description"]
        assert loaded["code"] == data["code"]

    def test_save_special_values(self):
        """Test saving special values"""
        data = {
            "none_value": None,
            "true_value": True,
            "false_value": False,
            "float_value": 3.14159,
            "int_value": 42,
            "empty_dict": {},
            "empty_list": []
        }
        save_yaml(data, self.test_file)
        
        with open(self.test_file, "r") as f:
            loaded = yaml.safe_load(f)
        assert loaded == data

    def test_save_dates(self):
        """Test saving date and datetime objects"""
        data = {
            "date": date(2023, 1, 1),
            "datetime": datetime(2023, 1, 1, 12, 30, 45)
        }
        save_yaml(data, self.test_file)
        
        with open(self.test_file, "r") as f:
            loaded = yaml.safe_load(f)
        assert loaded["date"] == data["date"]
        assert loaded["datetime"] == data["datetime"]

    def test_save_unicode(self):
        """Test saving Unicode characters"""
        data = {
            "english": "Hello",
            "japanese": "こんにちは",
            "emoji": "😊🎉",
            "special": "café",
            "mixed": "Hello世界"
        }
        save_yaml(data, self.test_file)
        
        with open(self.test_file, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
        assert loaded == data

    def test_save_anchors_and_aliases(self):
        """Test YAML anchors and aliases for repeated content"""
        base_config = {"timeout": 30, "retries": 3}
        data = {
            "service1": base_config,
            "service2": base_config,  # Same reference
            "service3": {"timeout": 60, "retries": 5}  # Different values
        }
        save_yaml(data, self.test_file)
        
        with open(self.test_file, "r") as f:
            loaded = yaml.safe_load(f)
        assert loaded["service1"] == loaded["service2"]
        assert loaded["service3"]["timeout"] == 60

    def test_save_ordered_dict(self):
        """Test saving ordered dictionary"""
        from collections import OrderedDict
        data = OrderedDict([
            ("z", 1),
            ("y", 2),
            ("x", 3),
            ("a", 4)
        ])
        save_yaml(data, self.test_file)
        
        with open(self.test_file, "r") as f:
            content = f.read()
        
        # Check order is preserved in file
        z_pos = content.index("z:")
        y_pos = content.index("y:")
        x_pos = content.index("x:")
        a_pos = content.index("a:")
        assert z_pos < y_pos < x_pos < a_pos

    def test_save_numpy_conversion(self):
        """Test saving numpy arrays (converted to lists)"""
        data = {
            "array_1d": np.array([1, 2, 3, 4, 5]).tolist(),
            "array_2d": np.array([[1, 2], [3, 4]]).tolist(),
            "float_array": np.array([1.1, 2.2, 3.3]).tolist()
        }
        save_yaml(data, self.test_file)
        
        with open(self.test_file, "r") as f:
            loaded = yaml.safe_load(f)
        assert loaded == data

    def test_save_custom_tags(self):
        """Test saving with default_flow_style option"""
        data = {"list": [1, 2, 3], "dict": {"a": 1, "b": 2}}
        save_yaml(data, self.test_file, default_flow_style=False)
        
        with open(self.test_file, "r") as f:
            content = f.read()
        
        # Check that it's in block style (not flow style)
        assert "list:" in content
        assert "- 1" in content  # Block style list

    def test_save_complex_scientific_config(self):
        """Test saving complex scientific configuration"""
        config = {
            "experiment": {
                "name": "deep_learning_experiment",
                "version": "1.0.0",
                "description": "Multi-task learning experiment",
                "tags": ["deep-learning", "multi-task", "computer-vision"]
            },
            "model": {
                "architecture": "resnet50",
                "pretrained": True,
                "num_classes": 10,
                "layers": {
                    "conv1": {"channels": 64, "kernel_size": 7, "stride": 2},
                    "conv2": {"channels": 128, "kernel_size": 3, "stride": 1}
                }
            },
            "hyperparameters": {
                "learning_rate": 0.001,
                "batch_size": 32,
                "epochs": 100,
                "early_stopping": {
                    "patience": 10,
                    "min_delta": 0.001
                }
            },
            "metrics": ["accuracy", "precision", "recall", "f1_score"]
        }
        save_yaml(config, self.test_file)
        
        with open(self.test_file, "r") as f:
            loaded = yaml.safe_load(f)
        assert loaded == config

    def test_save_empty_file(self):
        """Test saving empty/None data"""
        save_yaml(None, self.test_file)
        
        with open(self.test_file, "r") as f:
            loaded = yaml.safe_load(f)
        assert loaded is None

    def test_save_with_width_parameter(self):
        """Test saving with custom line width"""
        data = {
            "long_string": "This is a very long string that might normally be wrapped in YAML output but we can control the width"
        }
        save_yaml(data, self.test_file, width=200)
        
        with open(self.test_file, "r") as f:
            content = f.read()
        
        # String should not be wrapped
        assert "\n" not in content.split("long_string: ")[1]


# EOF
