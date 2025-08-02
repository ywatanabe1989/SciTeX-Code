#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 05:07:35 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/config/_CascadeConfig.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/config/_CascadeConfig.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex import logging

logger = logging.getLogger(__name__)


class CascadeConfig:
    """Universal config resolver with precedence: direct → config → env → default

    # Usage examples:
    # Django-style
    django_config = CascadeConfig(config_dict={}, env_prefix="DJANGO_", auto_uppercase=True)
    debug = django_config.resolve("debug", direct_debug, default=False, type=bool)

    # Custom app
    app_config = CascadeConfig(yaml_data, "MYAPP_")
    port = app_config.resolve("port", direct_port, default=8000, type=int)

    # Sensitive data (auto-detected or explicit)
    secret = app_config.resolve("secret_key", direct_secret, default="")
    api_key = app_config.resolve("api_key", direct_api, default="", mask=False)

    # No prefix
    simple_config = CascadeConfig(config_data, "")
    host = simple_config.resolve("HOST", direct_host, default="localhost")
    """

    SENSITIVE_EXPRESSIONS = [
        "API",
        "PASSWORD",
        "SECRET",
        "TOKEN",
        "KEY",
        "PASS",
        "AUTH",
        "CREDENTIAL",
        "PRIVATE",
        "CERT",
    ]

    def __init__(self, config_dict=None, env_prefix="", auto_uppercase=True):
        self.config_dict = config_dict or {}
        self.env_prefix = env_prefix
        self.auto_uppercase = auto_uppercase
        self.resolution_log = []

    def __repr__(self):
        return f"CascadeConfig(prefix='{self.env_prefix}', configs={len(self.config_dict)})"

    def get(self, key):
        """Get value from config dict only"""
        return self.config_dict.get(key)

    def resolve(self, key, direct_val=None, default=None, type=str, mask=None):
        """Get value with precedence hierarchy"""
        source = None
        final_value = None

        if direct_val is not None:
            source = "direct"
            final_value = direct_val
        elif key in self.config_dict:
            source = "config"
            final_value = self.config_dict[key]
        else:
            env_key = f"{self.env_prefix}{key.upper() if self.auto_uppercase else key}"
            env_val = os.getenv(env_key)
            if env_val:
                source = f"env:{env_key}"
                final_value = self._convert_type(env_val, type)
            else:
                source = "default"
                final_value = default

        if mask is False:
            should_mask = False
        else:
            should_mask = self._is_sensitive(key)

        display_value = (
            self._mask_value(final_value) if should_mask else final_value
        )

        self.resolution_log.append(
            {
                "key": key,
                "source": source,
                "value": display_value,
                "type": type.__name__,
            }
        )

        logger.info(f"{key} resolved as {display_value}")

        return final_value

    def print_resolutions(self):
        """Print how each config was resolved"""
        if not self.resolution_log:
            print("No configurations resolved yet")
            return

        print("Configuration Resolution Log:")
        print("-" * 50)
        for entry in self.resolution_log:
            print(
                f"{entry['key']:<20} = {entry['value']:<20} ({entry['source']})"
            )

    def clear_log(self):
        """Clear resolution log"""
        self.resolution_log = []

    def _convert_type(self, value, type):
        if type == int:
            return int(value)
        elif type == float:
            return float(value)
        elif type == bool:
            return value.lower() in ("true", "1", "yes")
        elif type == list:
            return value.split(",")
        return value

    def _is_sensitive(self, key):
        """Check if key contains sensitive expressions"""
        key_upper = key.upper()
        return any(expr in key_upper for expr in self.SENSITIVE_EXPRESSIONS)

    def _mask_value(self, value):
        """Mask sensitive values for display"""
        if value is None:
            return None
        value_str = str(value)
        if len(value_str) <= 4:
            return "****"
        return value_str[:2] + "*" * (len(value_str) - 4) + value_str[-2:]

# EOF
