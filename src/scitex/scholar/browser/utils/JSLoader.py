#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: JSLoader.py
# ----------------------------------------

"""
JavaScript loader for managing and caching JavaScript files.

Provides efficient loading and parameter injection for JavaScript utilities.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any

from scitex import log

logger = log.getLogger(__name__)


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
    
    def load(self, script_path: str) -> str:
        """
        Load JavaScript file with caching.
        
        Args:
            script_path: Relative path to JavaScript file
            
        Returns:
            JavaScript code as string
        """
        if script_path not in self._cache:
            full_path = self.js_dir / script_path
            
            if not full_path.exists():
                raise FileNotFoundError(f"JavaScript file not found: {full_path}")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                self._cache[script_path] = f.read()
                logger.debug(f"Loaded JavaScript: {script_path}")
        
        return self._cache[script_path]
    
    def load_with_params(self, script_path: str, params: Dict[str, Any]) -> str:
        """
        Load JavaScript and inject parameters.
        
        Args:
            script_path: Relative path to JavaScript file
            params: Parameters to inject into the script
            
        Returns:
            JavaScript code with injected parameters
        """
        script = self.load(script_path)
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
            raise FileNotFoundError(f"Module directory not found: {module_dir}")
        
        module_scripts = {}
        
        for js_file in module_dir.glob("*.js"):
            relative_path = f"{module_name}/{js_file.name}"
            module_scripts[js_file.stem] = self.load(relative_path)
        
        logger.info(f"Loaded {len(module_scripts)} scripts from module: {module_name}")
        return module_scripts
    
    def clear_cache(self):
        """Clear the script cache."""
        self._cache.clear()
        logger.debug("Cleared JavaScript cache")
    
    def get_cached_scripts(self) -> list:
        """Get list of cached script paths."""
        return list(self._cache.keys())