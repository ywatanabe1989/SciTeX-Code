#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:38:00 (ywatanabe)"
# File: ./mcp_servers/scitex-config/server.py
# ----------------------------------------

"""MCP server for SciTeX configuration management (PATH.yaml, PARAMS.yaml, etc.)."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import yaml
import json
import ast
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from scitex_base.base_server import ScitexBaseMCPServer


class ScitexConfigMCPServer(ScitexBaseMCPServer):
    """MCP server for SciTeX configuration file management."""
    
    def __init__(self):
        super().__init__("config", "0.1.0")
        
    def _register_module_tools(self):
        """Register config-specific tools."""
        
        @self.app.tool()
        async def extract_paths_from_code(
            code: str,
            project_root: str = "."
        ) -> Dict[str, List[Dict[str, str]]]:
            """Extract file paths from code and suggest PATH.yaml entries."""
            
            paths = {
                "absolute_paths": [],
                "relative_paths": [],
                "suggested_variables": []
            }
            
            # Patterns for path detection
            patterns = [
                (r'["\'](/[^"\']+\.[a-zA-Z]+)["\']', "absolute"),
                (r'["\'](\./[^"\']+\.[a-zA-Z]+)["\']', "relative"),
                (r'open\s*\(\s*["\']([^"\']+)["\']', "file_operation"),
                (r'\.read_csv\s*\(\s*["\']([^"\']+)["\']', "csv_file"),
                (r'\.to_csv\s*\(\s*["\']([^"\']+)["\']', "csv_output"),
                (r'\.savefig\s*\(\s*["\']([^"\']+)["\']', "figure_output"),
                (r'load\s*\(\s*["\']([^"\']+)["\']', "load_operation"),
                (r'save\s*\(\s*["\']([^"\']+)["\']', "save_operation"),
            ]
            
            for pattern, path_type in patterns:
                matches = re.findall(pattern, code)
                for match in matches:
                    path_info = {
                        "path": match,
                        "type": path_type,
                        "line": self._find_line_number(code, match)
                    }
                    
                    if match.startswith('/'):
                        paths["absolute_paths"].append(path_info)
                    else:
                        paths["relative_paths"].append(path_info)
                        
                    # Generate suggested variable name
                    var_name = self._path_to_config_var(match, path_type)
                    paths["suggested_variables"].append({
                        "variable": var_name,
                        "value": self._convert_to_relative_path(match, project_root),
                        "original": match,
                        "usage": path_type
                    })
                    
            # Remove duplicates
            paths["suggested_variables"] = self._deduplicate_suggestions(paths["suggested_variables"])
            
            return paths
            
        @self.app.tool()
        async def extract_parameters_from_code(
            code: str
        ) -> Dict[str, List[Dict[str, Any]]]:
            """Extract parameters from code and suggest PARAMS.yaml entries."""
            
            params = {
                "numeric_constants": [],
                "string_constants": [],
                "boolean_flags": [],
                "suggested_parameters": []
            }
            
            # Skip import statements and comments
            code_lines = [line for line in code.split('\n') 
                         if not line.strip().startswith(('import', 'from', '#'))]
            code_clean = '\n'.join(code_lines)
            
            # Patterns for parameter detection
            patterns = [
                # Numeric assignments
                (r'(\w+)\s*=\s*(\d+\.?\d*)', "numeric"),
                # String assignments (excluding paths)
                (r'(\w+)\s*=\s*["\']([^/]+)["\']', "string"),
                # Boolean assignments
                (r'(\w+)\s*=\s*(True|False)', "boolean"),
                # Common parameter patterns
                (r'threshold\s*=\s*(\d+\.?\d*)', "threshold"),
                (r'n_\w+\s*=\s*(\d+)', "count"),
                (r'batch_size\s*=\s*(\d+)', "batch_size"),
                (r'learning_rate\s*=\s*(\d+\.?\d*)', "learning_rate"),
                (r'epochs?\s*=\s*(\d+)', "epochs"),
                (r'seed\s*=\s*(\d+)', "seed"),
            ]
            
            for pattern, param_type in patterns:
                matches = re.findall(pattern, code_clean, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        if len(match) == 2:
                            var_name, value = match
                        else:
                            value = match[0]
                            var_name = self._infer_var_name(pattern)
                    else:
                        value = match
                        var_name = self._infer_var_name(pattern)
                        
                    # Skip certain common variables
                    if var_name.lower() in ['i', 'j', 'k', 'x', 'y', 'z', '_', '__']:
                        continue
                        
                    param_info = {
                        "name": var_name.upper(),
                        "value": self._parse_value(value),
                        "type": param_type,
                        "line": self._find_line_number(code, f"{var_name} = {value}")
                    }
                    
                    if param_type in ["numeric", "threshold", "count", "batch_size", 
                                     "learning_rate", "epochs", "seed"]:
                        params["numeric_constants"].append(param_info)
                    elif param_type == "string":
                        params["string_constants"].append(param_info)
                    elif param_type == "boolean":
                        params["boolean_flags"].append(param_info)
                        
                    params["suggested_parameters"].append({
                        "parameter": param_info["name"],
                        "value": param_info["value"],
                        "type": param_type,
                        "category": self._categorize_parameter(var_name, param_type)
                    })
                    
            # Deduplicate and organize
            params["suggested_parameters"] = self._organize_parameters(params["suggested_parameters"])
            
            return params
            
        @self.app.tool()
        async def generate_path_yaml(
            paths: Dict[str, str],
            detected_paths: List[Dict[str, str]] = None,
            project_name: str = "project"
        ) -> str:
            """Generate PATH.yaml with smart organization and comments."""
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Default structure
            default_paths = {
                "# Data paths": {
                    "DATA_DIR": "./data",
                    "RAW_DATA": "./data/raw",
                    "PROCESSED_DATA": "./data/processed",
                },
                "# Output paths": {
                    "OUTPUT_DIR": "./output",
                    "FIGURES_DIR": "./output/figures",
                    "RESULTS_DIR": "./output/results",
                    "MODELS_DIR": "./output/models",
                },
                "# Config paths": {
                    "CONFIG_DIR": "./config",
                },
                "# Script paths": {
                    "SCRIPTS_DIR": "./scripts",
                    "SCRIPT_OUTPUT": f"./scripts/{project_name}/{project_name}_out",
                }
            }
            
            # Build YAML content
            yaml_lines = [
                f'# Time-stamp: "{timestamp} (ywatanabe)"',
                f'# File: ./config/PATH.yaml',
                '# ----------------------------------------',
                '',
                'PATH:'
            ]
            
            # Add default paths with organization
            for section, section_paths in default_paths.items():
                yaml_lines.append(f'  {section}')
                for key, value in section_paths.items():
                    yaml_lines.append(f'  {key}: "{value}"')
                yaml_lines.append('')
                
            # Add custom paths
            if paths:
                yaml_lines.append('  # Project-specific paths')
                for key, value in paths.items():
                    yaml_lines.append(f'  {key}: "{value}"')
                yaml_lines.append('')
                
            # Add detected paths
            if detected_paths:
                yaml_lines.append('  # Auto-detected paths')
                for path_info in detected_paths:
                    yaml_lines.append(f'  {path_info["variable"]}: "{path_info["value"]}"')
                    
            return '\n'.join(yaml_lines)
            
        @self.app.tool()
        async def generate_params_yaml(
            params: Dict[str, Any],
            detected_params: List[Dict[str, Any]] = None
        ) -> str:
            """Generate PARAMS.yaml with categorized parameters."""
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Default parameters by category
            default_params = {
                "# General settings": {
                    "RANDOM_SEED": 42,
                    "VERBOSE": True,
                    "N_JOBS": -1,
                },
                "# Data processing": {
                    "BATCH_SIZE": 32,
                    "VALIDATION_SPLIT": 0.2,
                    "TEST_SPLIT": 0.1,
                },
                "# Statistical": {
                    "SIGNIFICANCE_THRESHOLD": 0.05,
                    "CONFIDENCE_LEVEL": 0.95,
                    "N_BOOTSTRAPS": 1000,
                },
                "# Model parameters": {
                    "LEARNING_RATE": 0.001,
                    "N_EPOCHS": 100,
                    "EARLY_STOPPING_PATIENCE": 10,
                }
            }
            
            # Build YAML content
            yaml_lines = [
                f'# Time-stamp: "{timestamp} (ywatanabe)"',
                f'# File: ./config/PARAMS.yaml',
                '# ----------------------------------------',
                '',
                'PARAMS:'
            ]
            
            # Add default parameters
            for section, section_params in default_params.items():
                yaml_lines.append(f'  {section}')
                for key, value in section_params.items():
                    yaml_lines.append(f'  {key}: {value}')
                yaml_lines.append('')
                
            # Add custom parameters
            if params:
                yaml_lines.append('  # Custom parameters')
                for key, value in params.items():
                    yaml_lines.append(f'  {key}: {value}')
                yaml_lines.append('')
                
            # Add detected parameters by category
            if detected_params:
                categories = {}
                for param in detected_params:
                    cat = param.get("category", "Other")
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(param)
                    
                for cat, cat_params in categories.items():
                    yaml_lines.append(f'  # {cat}')
                    for param in cat_params:
                        yaml_lines.append(f'  {param["parameter"]}: {param["value"]}")
                    yaml_lines.append('')
                    
            return '\n'.join(yaml_lines)
            
        @self.app.tool()
        async def generate_all_config_files(
            project_name: str = "project",
            detected_paths: List[Dict[str, str]] = None,
            detected_params: List[Dict[str, Any]] = None,
            include_optional: bool = True
        ) -> Dict[str, str]:
            """Generate all SciTeX configuration files."""
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            configs = {}
            
            # Generate PATH.yaml
            configs["config/PATH.yaml"] = await self.generate_path_yaml(
                {}, detected_paths, project_name
            )
            
            # Generate PARAMS.yaml
            configs["config/PARAMS.yaml"] = await self.generate_params_yaml(
                {}, detected_params
            )
            
            # Generate IS_DEBUG.yaml
            configs["config/IS_DEBUG.yaml"] = f'''# Time-stamp: "{timestamp} (ywatanabe)"
# File: ./config/IS_DEBUG.yaml
# ----------------------------------------

IS_DEBUG: false

# Debug mode settings
DEBUG:
  # Use smaller datasets in debug mode
  USE_SAMPLE_DATA: true
  SAMPLE_SIZE: 100
  
  # Reduce iterations
  MAX_ITERATIONS: 10
  N_EPOCHS: 5
  
  # Paths for debug
  DEBUG_DATA_PATH: "./data/debug/sample.csv"
  DEBUG_OUTPUT_DIR: "./output/debug"
  
  # Verbose output
  VERBOSE: true
  LOG_LEVEL: "DEBUG"
'''
            
            if include_optional:
                # Generate COLORS.yaml
                configs["config/COLORS.yaml"] = f'''# Time-stamp: "{timestamp} (ywatanabe)"
# File: ./config/COLORS.yaml
# ----------------------------------------

COLORS:
  # Primary colors
  PRIMARY: "#1f77b4"
  SECONDARY: "#ff7f0e"
  TERTIARY: "#2ca02c"
  
  # Status colors
  SUCCESS: "#2ca02c"
  WARNING: "#ff7f0e"
  ERROR: "#d62728"
  INFO: "#9467bd"
  
  # Plot colors (tab10 colormap)
  PLOT_COLORS:
    - "#1f77b4"  # blue
    - "#ff7f0e"  # orange
    - "#2ca02c"  # green
    - "#d62728"  # red
    - "#9467bd"  # purple
    - "#8c564b"  # brown
    - "#e377c2"  # pink
    - "#7f7f7f"  # gray
    - "#bcbd22"  # olive
    - "#17becf"  # cyan
    
  # Heatmap colormaps
  HEATMAP_SEQUENTIAL: "viridis"
  HEATMAP_DIVERGING: "RdBu_r"
  
  # Transparency
  ALPHA_FILL: 0.3
  ALPHA_LINE: 0.8
'''
                
                # Generate LOGGING.yaml
                configs["config/LOGGING.yaml"] = f'''# Time-stamp: "{timestamp} (ywatanabe)"
# File: ./config/LOGGING.yaml
# ----------------------------------------

LOGGING:
  # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
  LEVEL: "INFO"
  
  # File logging
  FILE:
    ENABLED: true
    PATH: "./logs"
    FILENAME: "{project_name}.log"
    MAX_SIZE: "10MB"
    BACKUP_COUNT: 5
    
  # Console logging
  CONSOLE:
    ENABLED: true
    COLORIZE: true
    
  # Format
  FORMAT:
    DEFAULT: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DETAILED: "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    
  # Module-specific levels
  MODULES:
    scitex: "INFO"
    matplotlib: "WARNING"
    pandas: "WARNING"
'''
                
            return configs
            
        @self.app.tool()
        async def validate_config_files(
            config_dir: str = "./config"
        ) -> Dict[str, Any]:
            """Validate existing configuration files."""
            
            config_path = Path(config_dir)
            validation = {
                "valid": True,
                "score": 100,
                "files": {},
                "issues": [],
                "warnings": []
            }
            
            required_files = ["PATH.yaml", "PARAMS.yaml", "IS_DEBUG.yaml"]
            optional_files = ["COLORS.yaml", "LOGGING.yaml"]
            
            # Check required files
            for file_name in required_files:
                file_path = config_path / file_name
                if not file_path.exists():
                    validation["issues"].append(f"Missing required config: {file_name}")
                    validation["valid"] = False
                    validation["score"] -= 20
                else:
                    validation["files"][file_name] = self._validate_yaml_file(file_path)
                    
            # Check optional files
            for file_name in optional_files:
                file_path = config_path / file_name
                if not file_path.exists():
                    validation["warnings"].append(f"Missing optional config: {file_name}")
                    validation["score"] -= 5
                else:
                    validation["files"][file_name] = self._validate_yaml_file(file_path)
                    
            # Check for unused configs
            all_configs = list(config_path.glob("*.yaml")) + list(config_path.glob("*.yml"))
            known_configs = required_files + optional_files
            for config in all_configs:
                if config.name not in known_configs:
                    validation["warnings"].append(f"Unknown config file: {config.name}")
                    
            validation["score"] = max(0, validation["score"])
            return validation
            
        @self.app.tool()
        async def migrate_config_to_scitex(
            old_config: str,
            config_type: str = "auto"
        ) -> Dict[str, str]:
            """Migrate existing configuration to SciTeX format."""
            
            # Detect format if auto
            if config_type == "auto":
                if "json" in old_config or old_config.strip().startswith('{'):
                    config_type = "json"
                elif "=" in old_config and not ":" in old_config:
                    config_type = "ini"
                elif ".py" in old_config or "import" in old_config:
                    config_type = "python"
                else:
                    config_type = "yaml"
                    
            migrated = {}
            
            if config_type == "json":
                try:
                    data = json.loads(old_config)
                    migrated = self._migrate_from_json(data)
                except:
                    # Try as file path
                    with open(old_config, 'r') as f:
                        data = json.load(f)
                    migrated = self._migrate_from_json(data)
                    
            elif config_type == "python":
                # Extract constants from Python file
                if os.path.exists(old_config):
                    with open(old_config, 'r') as f:
                        old_config = f.read()
                migrated = self._migrate_from_python(old_config)
                
            elif config_type == "ini":
                migrated = self._migrate_from_ini(old_config)
                
            else:  # yaml
                migrated = self._migrate_from_yaml(old_config)
                
            # Generate proper SciTeX configs
            result = {}
            if migrated.get("paths"):
                result["config/PATH.yaml"] = await self.generate_path_yaml(migrated["paths"])
            if migrated.get("params"):
                result["config/PARAMS.yaml"] = await self.generate_params_yaml(migrated["params"])
                
            return result
            
    def _path_to_config_var(self, path: str, path_type: str) -> str:
        """Convert path to configuration variable name."""
        
        # Handle different path types
        if path_type == "csv_file":
            if "train" in path.lower():
                return "TRAIN_DATA"
            elif "test" in path.lower():
                return "TEST_DATA"
            elif "val" in path.lower():
                return "VAL_DATA"
            else:
                return "INPUT_DATA"
        elif path_type == "figure_output":
            return "FIGURES_DIR"
        elif path_type == "csv_output":
            return "RESULTS_FILE"
            
        # Generic conversion
        base = Path(path).stem.upper()
        base = re.sub(r'[^A-Z0-9_]', '_', base)
        
        # Add suffix based on extension
        ext = Path(path).suffix.lower()
        if ext in ['.csv', '.tsv', '.txt']:
            return f"{base}_FILE"
        elif ext in ['.png', '.jpg', '.pdf']:
            return f"{base}_FIGURE"
        elif ext in ['.h5', '.hdf5']:
            return f"{base}_DATA"
        else:
            return base
            
    def _convert_to_relative_path(self, path: str, project_root: str) -> str:
        """Convert absolute path to relative."""
        if path.startswith('/'):
            # Try to make relative to project root
            try:
                return os.path.relpath(path, project_root)
            except:
                return path
        return path
        
    def _find_line_number(self, code: str, pattern: str) -> int:
        """Find line number of pattern in code."""
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if pattern in line:
                return i
        return 0
        
    def _parse_value(self, value: str) -> Union[int, float, bool, str]:
        """Parse string value to appropriate type."""
        if value in ['True', 'False']:
            return value == 'True'
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except:
            return value
            
    def _infer_var_name(self, pattern: str) -> str:
        """Infer variable name from pattern."""
        if 'threshold' in pattern:
            return 'threshold'
        elif 'n_' in pattern:
            return 'n_items'
        elif 'batch_size' in pattern:
            return 'batch_size'
        elif 'learning_rate' in pattern:
            return 'learning_rate'
        elif 'epoch' in pattern:
            return 'epochs'
        elif 'seed' in pattern:
            return 'random_seed'
        return 'parameter'
        
    def _categorize_parameter(self, name: str, param_type: str) -> str:
        """Categorize parameter based on name and type."""
        name_lower = name.lower()
        
        if any(x in name_lower for x in ['seed', 'random']):
            return "Random"
        elif any(x in name_lower for x in ['threshold', 'alpha', 'p_value', 'significance']):
            return "Statistical"
        elif any(x in name_lower for x in ['batch', 'epoch', 'iteration', 'steps']):
            return "Training"
        elif any(x in name_lower for x in ['learning_rate', 'lr', 'momentum', 'decay']):
            return "Optimization"
        elif any(x in name_lower for x in ['n_', 'num_', 'count', 'size']):
            return "Counts"
        elif any(x in name_lower for x in ['path', 'dir', 'file']):
            return "Paths"
        elif param_type == "boolean":
            return "Flags"
        else:
            return "General"
            
    def _deduplicate_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Remove duplicate suggestions."""
        seen = set()
        unique = []
        for s in suggestions:
            key = (s["variable"], s["value"])
            if key not in seen:
                seen.add(key)
                unique.append(s)
        return unique
        
    def _organize_parameters(self, params: List[Dict]) -> List[Dict]:
        """Organize parameters by category and remove duplicates."""
        # Group by category
        by_category = {}
        for p in params:
            cat = p["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(p)
            
        # Deduplicate within categories
        organized = []
        for cat, cat_params in by_category.items():
            seen = set()
            for p in cat_params:
                if p["parameter"] not in seen:
                    seen.add(p["parameter"])
                    organized.append(p)
                    
        return organized
        
    def _validate_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate individual YAML file."""
        result = {
            "valid": True,
            "issues": [],
            "structure": {}
        }
        
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                
            result["structure"] = self._analyze_structure(data)
            
            # Check for common issues
            if not data:
                result["issues"].append("Empty file")
                result["valid"] = False
            elif not isinstance(data, dict):
                result["issues"].append("Root must be a dictionary")
                result["valid"] = False
            else:
                # File-specific validation
                if file_path.name == "PATH.yaml":
                    if "PATH" not in data:
                        result["issues"].append("Missing PATH root key")
                        result["valid"] = False
                elif file_path.name == "PARAMS.yaml":
                    if "PARAMS" not in data:
                        result["issues"].append("Missing PARAMS root key")
                        result["valid"] = False
                elif file_path.name == "IS_DEBUG.yaml":
                    if "IS_DEBUG" not in data:
                        result["issues"].append("Missing IS_DEBUG key")
                        result["valid"] = False
                        
        except Exception as e:
            result["valid"] = False
            result["issues"].append(f"Parse error: {str(e)}")
            
        return result
        
    def _analyze_structure(self, data: Any, level: int = 0) -> Dict:
        """Analyze YAML structure recursively."""
        if isinstance(data, dict):
            return {
                "type": "dict",
                "keys": list(data.keys()),
                "children": {k: self._analyze_structure(v, level+1) for k, v in data.items()}
            }
        elif isinstance(data, list):
            return {
                "type": "list",
                "length": len(data),
                "items": self._analyze_structure(data[0], level+1) if data else None
            }
        else:
            return {
                "type": type(data).__name__,
                "value": str(data)[:50] if isinstance(data, str) else data
            }
            
    def _migrate_from_json(self, data: Dict) -> Dict[str, Dict]:
        """Migrate from JSON config."""
        migrated = {"paths": {}, "params": {}}
        
        for key, value in data.items():
            if any(x in key.lower() for x in ['path', 'dir', 'file']):
                migrated["paths"][key.upper()] = value
            else:
                migrated["params"][key.upper()] = value
                
        return migrated
        
    def _migrate_from_python(self, code: str) -> Dict[str, Dict]:
        """Migrate from Python constants."""
        migrated = {"paths": {}, "params": {}}
        
        # Parse AST to find assignments
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            name = target.id
                            if name.isupper():  # Constants
                                try:
                                    value = ast.literal_eval(node.value)
                                    if isinstance(value, str) and ('/' in value or '\\' in value):
                                        migrated["paths"][name] = value
                                    else:
                                        migrated["params"][name] = value
                                except:
                                    pass
        except:
            # Fallback to regex
            const_pattern = r'^([A-Z_]+)\s*=\s*(.+)$'
            for line in code.split('\n'):
                match = re.match(const_pattern, line)
                if match:
                    name, value = match.groups()
                    migrated["params"][name] = value.strip('"\'')
                    
        return migrated
        
    def _migrate_from_ini(self, content: str) -> Dict[str, Dict]:
        """Migrate from INI format."""
        migrated = {"paths": {}, "params": {}}
        
        section = "params"
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('['):
                section = "paths" if "path" in line.lower() else "params"
            elif '=' in line:
                key, value = line.split('=', 1)
                migrated[section][key.strip().upper()] = value.strip()
                
        return migrated
        
    def _migrate_from_yaml(self, content: str) -> Dict[str, Dict]:
        """Migrate from non-standard YAML."""
        try:
            data = yaml.safe_load(content)
            return self._migrate_from_json(data)
        except:
            return {"paths": {}, "params": {}}
            
    def get_module_description(self) -> str:
        """Get description of config functionality."""
        return (
            "SciTeX configuration server manages PATH.yaml, PARAMS.yaml, and other "
            "configuration files. It extracts paths and parameters from code, generates "
            "proper config files, validates existing configs, and migrates from other formats."
        )
        
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            "extract_paths_from_code",
            "extract_parameters_from_code",
            "generate_path_yaml",
            "generate_params_yaml",
            "generate_all_config_files",
            "validate_config_files",
            "migrate_config_to_scitex",
            "get_module_info",
            "validate_code"
        ]
        
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate config usage in code."""
        issues = []
        
        # Check for CONFIG loading
        if "stx.io.load_configs()" not in code and "load_configs()" not in code:
            issues.append("Missing CONFIG = stx.io.load_configs()")
            
        # Check for hardcoded paths
        hardcoded = re.findall(r'["\'](/[^"\']+\.[a-zA-Z]+)["\']', code)
        if hardcoded:
            issues.append(f"Hardcoded absolute paths found: {hardcoded[:3]}")
            
        # Check for CONFIG usage
        if "CONFIG" in code but "CONFIG." not in code:
            issues.append("CONFIG loaded but not used")
            
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "score": max(0, 100 - len(issues) * 20)
        }


# Main entry point
if __name__ == "__main__":
    server = ScitexConfigMCPServer()
    asyncio.run(server.run())

# EOF