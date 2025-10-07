#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 05:13:37 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/utils/JSLoader.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/utils/JSLoader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
JavaScript loader for managing and caching JavaScript files.

Provides efficient loading and parameter injection for JavaScript utilities.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from scitex import logging

logger = logging.getLogger(__name__)


class JSLoader:
    """Load and manage JavaScript files for browser automation."""

    def __init__(self, js_dir: Optional[Path] = None):
        """Initialize with JavaScript directory."""
        if js_dir is None:
            # Default to js directory relative to this file
            js_dir = Path(__file__).parent.parent / "js"

        self.js_dir = Path(js_dir)
        self._cache: Dict[str, str] = {}

        if not self.js_dir.exists():
            logger.warning(f"JavaScript directory not found: {self.js_dir}")

    def load(self, js_path: str) -> str:
        """
        Load JavaScript file with caching.

        Args:
            js_path: Relative path to JavaScript file

        Returns:
            JavaScript code as string
        """
        if js_path not in self._cache:
            full_path = self.js_dir / js_path

            if not full_path.exists():
                raise FileNotFoundError(
                    f"JavaScript file not found: {full_path}"
                )

            with open(full_path, "r", encoding="utf-8") as f:
                self._cache[js_path] = f.read()
                logger.debug(f"Loaded JavaScript: {js_path}")

        return self._cache[js_path]

    def load_with_params(self, js_path: str, params: Dict[str, Any]) -> str:
        """
        Load JavaScript and inject parameters.

        Args:
            js_path: Relative path to JavaScript file
            params: Parameters to inject into the script

        Returns:
            JavaScript code with injected parameters
        """
        script = self.load(js_path)
        params_json = json.dumps(params)

        # Wrap in IIFE (Immediately Invoked Function Expression) to avoid global pollution
        return f"""
        (function() {{
            const params = {params_json};
            {script}
        }})()
        """

    def load_module(self, module_name: str) -> Dict[str, str]:
        """
        Load all JavaScript files from a module directory.

        Args:
            module_name: Name of the module directory

        Returns:
            Dictionary mapping filenames to JavaScript code
        """
        module_dir = self.js_dir / module_name

        if not module_dir.exists():
            raise FileNotFoundError(
                f"Module directory not found: {module_dir}"
            )

        module_scripts = {}

        for js_file in module_dir.glob("*.js"):
            relative_path = f"{module_name}/{js_file.name}"
            module_scripts[js_file.stem] = self.load(relative_path)

        logger.info(
            f"Loaded {len(module_scripts)} scripts from module: {module_name}"
        )
        return module_scripts

    def clear_cache(self):
        """Clear the script cache."""
        self._cache.clear()
        logger.debug("Cleared JavaScript cache")

    def get_cached_scripts(self) -> list:
        """Get list of cached script paths."""
        return list(self._cache.keys())

# EOF
