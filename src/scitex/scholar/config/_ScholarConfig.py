#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 19:53:07 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/config/_ScholarConfig.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/config/_ScholarConfig.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import re

from pathlib import Path
from typing import Optional
from typing import Union
import yaml
from ._PathManager import PathManager
from ._CascadeConfig import CascadeConfig


class ScholarConfig:
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        if config_path and Path(config_path).exists():
            config_data = self._load_yaml_with_env_substitution(config_path)
        else:
            default_path = Path(__file__).parent / "default.yaml"
            config_data = self._load_yaml_with_env_substitution(default_path)

        self.cascade = CascadeConfig(config_data, "SCITEX_SCHOLAR_")
        self._setup_path_manager()

    # Delegate methods for cleaner API (composition over inheritance)
    def resolve(self, key, direct_val=None, default=None, type=str, mask=None):
        """Resolve configuration value with precedence: direct → config → env → default"""
        return self.cascade.resolve(key, direct_val, default, type, mask)
    
    def get(self, key):
        """Get value from config dict only"""
        return self.cascade.get(key)
    
    def print_resolutions(self):
        """Print how each config was resolved"""
        return self.cascade.print_resolutions()
    
    def clear_log(self):
        """Clear resolution log"""
        return self.cascade.clear_log()

    # Path management convenience methods
    @property
    def paths(self):
        """Access to path manager for organized directory structure"""
        return self.path_manager
    
    def get_cache_dir(self, cache_type: str = "general") -> Path:
        """Get cache directory for specific cache type"""
        return self.path_manager.cache_dir / cache_type
    
    def get_auth_cache_dir(self, auth_type: str) -> Path:
        """Get authentication cache directory"""
        return self.path_manager.get_auth_cache_dir(auth_type)
    
    def get_chrome_cache_dir(self) -> Path:
        """Get Chrome cache directory"""
        return self.path_manager.get_chrome_cache_dir()
    
    def get_screenshots_dir(self, screenshot_type: str = "general") -> Path:
        """Get screenshots directory"""
        return self.path_manager.get_screenshots_dir(screenshot_type)
    
    def get_downloads_dir(self) -> Path:
        """Get downloads directory"""
        return self.path_manager.get_downloads_dir()

    def _load_yaml_with_env_substitution(self, path: Path) -> dict:
        with open(path) as f:
            content = f.read()

        def env_replacer(match):
            env_expr = match.group(1)
            if ":-" in env_expr:
                var_name, default_value = env_expr.split(":-", 1)
                value = os.getenv(var_name, default_value.strip('"'))
            else:
                value = os.getenv(env_expr)

            if value in ["true", "false"]:
                return value
            elif value == "null":
                return "null"
            elif value and not (value.startswith('"') and value.endswith('"')):
                return f'"{value}"'
            else:
                return value or "null"

        content = re.sub(r"\$\{([^}]+)\}", env_replacer, content)
        return yaml.safe_load(content)

    def _setup_path_manager(self):
        scholar_dir = self.cascade.resolve("scholar_dir", default="~/.scitex")
        base_path = Path(scholar_dir).expanduser() / "scholar"
        self.path_manager = PathManager(scholar_dir=base_path)

    @classmethod
    def load(cls, path: Optional[Union[str, Path]] = None):
        return cls(path)

# EOF
