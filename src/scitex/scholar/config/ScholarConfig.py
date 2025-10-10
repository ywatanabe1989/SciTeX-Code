#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-10 20:42:40 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/config/ScholarConfig.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/config/ScholarConfig.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

import re
from pathlib import Path
from typing import Optional, Union

import yaml

from scitex.errors import ScholarError
from scitex.logging import getLogger

from .core._CascadeConfig import CascadeConfig
from .core._PathManager import PathManager

logger = getLogger(__name__)


class ScholarConfig:
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.name = self.__class__.__name__
        if config_path and Path(config_path).exists():
            config_data = self.load_yaml(config_path)
        else:
            default_path = Path(__file__).parent / "default.yaml"
            config_data = self.load_yaml(default_path)

        self.cascade = CascadeConfig(config_data, "SCITEX_SCHOLAR_")
        self._setup_path_manager()

    def __getattr__(self, name):
        """Delegate all get_ methods to path_manager"""
        if name.startswith("get_") and hasattr(self.path_manager, name):
            return getattr(self.path_manager, name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __dir__(self):
        """Include path_manager's get_ methods in dir() output"""
        own_attrs = object.__dir__(self)
        path_manager_get_methods = [
            attr
            for attr in dir(self.path_manager)
            if attr.startswith("get_")
            and callable(getattr(self.path_manager, attr))
        ]
        return list(own_attrs) + path_manager_get_methods

    # Delegate methods for cleaner API (composition over inheritance)
    def resolve(self, key, direct_val=None, default=None, type=str, mask=None):
        """Resolve configuration value with precedence: direct → config → env → default"""
        return self.cascade.resolve(key, direct_val, default, type, mask)

    def get(self, key):
        """Get value from config dict only"""
        return self.cascade.get(key)

    def print(self):
        """Print how each config was resolved"""
        return self.cascade.print()

    def clear_log(self):
        """Clear resolution log"""
        return self.cascade.clear_log()

    def load_yaml(self, path: Path) -> dict:
        try:
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
                elif value and not (
                    value.startswith('"') and value.endswith('"')
                ):
                    return f'"{value}"'
                else:
                    return value or "null"

            content = re.sub(r"\$\{([^}]+)\}", env_replacer, content)
            # logger.info(f"ScholarConfig object configured with: {path}")
            return yaml.safe_load(content)
        except Exception as e:
            raise ScholarError(
                f"{path} not loaded and ScholarConfig object not created"
            )

    @classmethod
    def load(cls, path: Optional[Union[str, Path]] = None):
        return cls(path)

    # Path Management ----------------------------------------
    def _setup_path_manager(self):
        scholar_dir = self.cascade.resolve("scholar_dir", default="~/.scitex")
        base_path = Path(scholar_dir).expanduser() / "scholar"
        self.path_manager = PathManager(scholar_dir=base_path)

    @property
    def paths(self):
        """Access to path manager for organized directory structure"""
        return self.path_manager

# EOF
