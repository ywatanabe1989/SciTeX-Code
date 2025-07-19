#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 06:32:00 (ywatanabe)"
# File: ./mcp_servers/scitex-gen/server.py
# ----------------------------------------

"""MCP server for SciTeX gen (general utilities) module operations."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import asyncio
from typing import Dict, Any, List, Tuple, Optional
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scitex-base'))
from base_server import ScitexBaseMCPServer, ScitexTranslatorMixin


class ScitexGenMCPServer(ScitexBaseMCPServer, ScitexTranslatorMixin):
    """MCP server for SciTeX gen module translations and operations."""
    
    def __init__(self):
        super().__init__("gen", "0.1.0")
        self.create_translation_tools("stx.gen")
        
        # Gen module patterns for common operations
        self.normalization_patterns = [
            (r"sklearn\.preprocessing\.StandardScaler\(\)", "sklearn", "standardize"),
            (r"sklearn\.preprocessing\.MinMaxScaler\(\)", "sklearn", "minmax"),
            (r"sklearn\.preprocessing\.Normalizer\(\)", "sklearn", "normalize"),
            (r"scipy\.stats\.zscore\((.*?)\)", "scipy", "zscore"),
            (r"(\w+)\s*=\s*\((\w+)\s*-\s*np\.mean\((\w+)\)\)\s*/\s*np\.std\((\w+)\)", "numpy", "manual_zscore"),
            (r"(\w+)\s*=\s*\((\w+)\s*-\s*(\w+)\.min\(\)\)\s*/\s*\((\w+)\.max\(\)\s*-\s*(\w+)\.min\(\)\)", "numpy", "manual_minmax"),
        ]
        
        self.caching_patterns = [
            (r"@functools\.lru_cache", "functools", "lru_cache"),
            (r"@lru_cache", "functools", "lru_cache"),
            (r"@cache", "functools", "cache"),
            (r"from joblib import Memory", "joblib", "memory"),
            (r"@memory\.cache", "joblib", "memory_cache"),
        ]
        
        self.path_patterns = [
            (r"os\.path\.join\((.*?)\)", "os", "path_join"),
            (r"Path\((.*?)\)", "pathlib", "path_create"),
            (r"os\.makedirs\((.*?)\)", "os", "makedirs"),
            (r"(\w+)\.mkdir\((.*?)\)", "pathlib", "mkdir"),
            (r"__file__", "builtin", "file_path"),
            (r"os\.path\.dirname\((.*?)\)", "os", "dirname"),
            (r"os\.path\.basename\((.*?)\)", "os", "basename"),
        ]
        
        self.timestamp_patterns = [
            (r"datetime\.now\(\)", "datetime", "now"),
            (r"time\.time\(\)", "time", "time"),
            (r"datetime\.utcnow\(\)", "datetime", "utcnow"),
            (r"datetime\.strftime\((.*?)\)", "datetime", "strftime"),
        ]
        
    def _register_module_tools(self):
        """Register gen-specific tools."""
        
        @self.app.tool()
        async def analyze_utility_usage(code: str) -> Dict[str, Any]:
            """Analyze general utility usage patterns in the code."""
            utilities = {
                "normalization": [],
                "caching": [],
                "path_operations": [],
                "timestamps": [],
                "environment": [],
                "data_transformations": []
            }
            
            # Analyze normalization operations
            for pattern, lib, method in self.normalization_patterns:
                matches = re.finditer(pattern, code, re.MULTILINE)
                for match in matches:
                    utilities["normalization"].append({
                        "operation": match.group(0),
                        "library": lib,
                        "method": method,
                        "line": code[:match.start()].count('\n') + 1,
                    })
            
            # Analyze caching usage
            for pattern, lib, method in self.caching_patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    utilities["caching"].append({
                        "operation": match.group(0),
                        "library": lib,
                        "method": method,
                        "line": code[:match.start()].count('\n') + 1,
                    })
            
            # Analyze path operations
            for pattern, lib, method in self.path_patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    utilities["path_operations"].append({
                        "operation": match.group(0),
                        "library": lib,
                        "method": method,
                        "line": code[:match.start()].count('\n') + 1,
                    })
            
            # Analyze timestamp operations
            for pattern, lib, method in self.timestamp_patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    utilities["timestamps"].append({
                        "operation": match.group(0),
                        "library": lib,
                        "method": method,
                        "line": code[:match.start()].count('\n') + 1,
                    })
            
            # Check for environment checks
            if "sys.platform" in code or "os.environ" in code:
                utilities["environment"].append("Environment checking detected")
            
            # Check for data transformations
            if any(word in code for word in ["transpose", "reshape", "flatten", "squeeze"]):
                utilities["data_transformations"].append("Array transformation operations detected")
            
            return {
                "utilities_found": utilities,
                "total_patterns": sum(len(v) for v in utilities.values() if isinstance(v, list)),
                "categories_used": [k for k, v in utilities.items() if v],
            }
        
        @self.app.tool()
        async def suggest_gen_improvements(code: str) -> List[Dict[str, str]]:
            """Suggest gen module improvements for utility operations."""
            suggestions = []
            
            # Check for manual normalization
            manual_zscore = re.search(
                r"(\w+)\s*=\s*\((\w+)\s*-\s*np\.mean\((\w+)\)\)\s*/\s*np\.std\((\w+)\)",
                code
            )
            if manual_zscore:
                suggestions.append({
                    "issue": "Manual z-score normalization",
                    "suggestion": "Use stx.gen.to_z() for cleaner z-score normalization",
                    "severity": "medium",
                    "example": f"normalized = stx.gen.to_z(data)"
                })
            
            # Check for manual min-max scaling
            manual_minmax = re.search(
                r"(\w+)\s*=\s*\((\w+)\s*-\s*(\w+)\.min\(\)\)\s*/\s*\((\w+)\.max\(\)\s*-\s*(\w+)\.min\(\)\)",
                code
            )
            if manual_minmax:
                suggestions.append({
                    "issue": "Manual min-max normalization",
                    "suggestion": "Use stx.gen.to_01() for 0-1 normalization",
                    "severity": "medium",
                    "example": f"normalized = stx.gen.to_01(data)"
                })
            
            # Check for no caching on expensive functions
            function_defs = re.findall(r"def\s+(\w+)\s*\([^)]*\):", code)
            for func in function_defs:
                func_body = re.search(rf"def\s+{func}\s*\([^)]*\):(.*?)(?=\n(?:def|class|\Z))", code, re.DOTALL)
                if func_body:
                    body = func_body.group(1)
                    # Check for expensive operations
                    if any(op in body for op in ["np.linalg", "scipy", "sklearn", "time.sleep", "for"]):
                        # Check if already cached
                        if not re.search(rf"@.*cache.*\s*def\s+{func}", code):
                            suggestions.append({
                                "issue": f"Function '{func}' performs expensive operations without caching",
                                "suggestion": f"Add @stx.gen.cache decorator to cache results",
                                "severity": "high",
                                "example": f"@stx.gen.cache\ndef {func}(...):"
                            })
            
            # Check for path operations without proper handling
            if "os.path.join" in code and "__file__" in code:
                suggestions.append({
                    "issue": "Using os.path operations for file paths",
                    "suggestion": "Use stx.gen.src() or stx.path utilities for robust path handling",
                    "severity": "low",
                    "example": "current_dir = stx.gen.src(__file__)"
                })
            
            # Check for manual timestamp generation
            if "datetime.now().strftime" in code or "time.strftime" in code:
                suggestions.append({
                    "issue": "Manual timestamp formatting",
                    "suggestion": "Use stx.gen.TimeStamper for consistent timestamp management",
                    "severity": "low",
                    "example": "ts = stx.gen.TimeStamper()\nts.stamp('event')"
                })
            
            # Check for print statements that could use tee
            print_count = code.count("print(")
            if print_count > 5:
                suggestions.append({
                    "issue": f"Multiple print statements ({print_count} found)",
                    "suggestion": "Consider using stx.gen.tee() to log output to file as well",
                    "severity": "info",
                    "example": "with stx.gen.tee('output.log'):\n    # Your code here"
                })
            
            # Check for environment-specific code
            if "if sys.platform" in code or "if os.name" in code:
                suggestions.append({
                    "issue": "Platform-specific code branches",
                    "suggestion": "Use stx.gen.check_host() for cleaner environment detection",
                    "severity": "low",
                    "example": "if stx.gen.is_host('linux'):\n    # Linux-specific code"
                })
            
            return suggestions
        
        @self.app.tool()
        async def convert_normalization_to_scitex(
            operation: str,
            variable_name: str = "data"
        ) -> Dict[str, str]:
            """Convert normalization operations to SciTeX gen functions."""
            conversions = {
                "zscore": f"{variable_name}_normalized = stx.gen.to_z({variable_name})",
                "minmax": f"{variable_name}_normalized = stx.gen.to_01({variable_name})",
                "clip_outliers": f"{variable_name}_clipped = stx.gen.clip_perc({variable_name}, percentile=95)",
                "remove_bias": f"{variable_name}_unbiased = stx.gen.unbias({variable_name})",
            }
            
            if operation in conversions:
                return {
                    "operation": operation,
                    "scitex_code": conversions[operation],
                    "description": f"SciTeX normalization for {operation}",
                }
            else:
                return {
                    "operation": operation,
                    "scitex_code": f"# Custom normalization needed for {operation}",
                    "description": "Manual implementation required",
                }
        
        @self.app.tool()
        async def create_experiment_setup(
            experiment_name: str,
            description: str = "",
            config_path: Optional[str] = None
        ) -> Dict[str, str]:
            """Generate SciTeX experiment initialization code."""
            code_lines = [
                "#!/usr/bin/env python3",
                "# -*- coding: utf-8 -*-",
                f"# Experiment: {experiment_name}",
                "# ----------------------------------------",
                "",
                "import scitex as stx",
                "",
                "# Initialize experiment with reproducible settings",
                f"config = stx.gen.start(",
                f'    description="{description or experiment_name}",',
            ]
            
            if config_path:
                code_lines.append(f'    config_path="{config_path}",')
            
            code_lines.extend([
                "    verbose=True",
                ")",
                "",
                "# Set up time tracking",
                "ts = stx.gen.TimeStamper()",
                "ts.stamp('Experiment started')",
                "",
                "# Your experiment code here",
                "",
                "# Close experiment and save outputs",
                "ts.stamp('Experiment completed')",
                "stx.gen.close()",
            ])
            
            return {
                "experiment_name": experiment_name,
                "code": "\n".join(code_lines),
                "components": [
                    "Experiment initialization",
                    "Time tracking",
                    "Reproducible environment",
                    "Output management"
                ]
            }
        
    def get_module_description(self) -> str:
        """Get description of gen module functionality."""
        return (
            "SciTeX gen module provides general utilities for scientific computing including "
            "data normalization (to_z, to_01, clip_perc), caching, path management, "
            "timestamp tracking, environment detection, and experiment lifecycle management. "
            "Essential for reproducible scientific workflows."
        )
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            "get_module_info",
            "validate_code",
            "translate_to_scitex",
            "translate_from_scitex",
            "suggest_improvements",
            "analyze_utility_usage",
            "suggest_gen_improvements",
            "convert_normalization_to_scitex",
            "create_experiment_setup",
        ]
    
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate gen module usage."""
        issues = []
        warnings = []
        
        # Check for manual implementations when gen utilities exist
        if "import scitex as stx" in code:
            # Check for manual normalization
            if re.search(r"\(.*-.*\.mean\(\)\).*\/.*\.std\(\)", code):
                if "stx.gen.to_z" not in code:
                    issues.append("Manual z-score normalization instead of stx.gen.to_z()")
            
            # Check for manual min-max
            if re.search(r"\(.*-.*\.min\(\)\).*\/.*\(.*\.max\(\).*-.*\.min\(\)\)", code):
                if "stx.gen.to_01" not in code:
                    issues.append("Manual min-max scaling instead of stx.gen.to_01()")
            
            # Check for os.makedirs when using stx
            if "os.makedirs" in code:
                warnings.append("Using os.makedirs - stx.io.save() creates directories automatically")
            
            # Check for manual caching implementations
            if "cache = {}" in code or "if.*in.*cache:" in code:
                if "@stx.gen.cache" not in code:
                    warnings.append("Manual caching implementation - consider @stx.gen.cache decorator")
        
        # Check for experiment lifecycle
        if "stx.gen.start" in code and "stx.gen.close" not in code:
            warnings.append("Missing stx.gen.close() after stx.gen.start()")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": max(0, 100 - len(issues) * 20 - len(warnings) * 10),
        }
    
    async def module_to_scitex(
        self,
        code: str,
        preserve_comments: bool,
        add_config_support: bool
    ) -> Dict[str, Any]:
        """Translate general utility operations to SciTeX."""
        translated = code
        conversions = []
        
        # Add import if needed
        has_gen_ops = any(
            re.search(p[0], code) 
            for p in self.normalization_patterns + self.caching_patterns + self.path_patterns
        )
        
        if has_gen_ops and "import scitex as stx" not in translated:
            lines = translated.split('\n')
            import_idx = -1
            for i, line in enumerate(lines):
                if line.strip().startswith(('import', 'from')):
                    import_idx = i
            if import_idx >= 0:
                lines.insert(import_idx + 1, "import scitex as stx")
                translated = '\n'.join(lines)
        
        # Convert normalization operations
        # Manual z-score
        zscore_pattern = r"(\w+)\s*=\s*\((\w+)\s*-\s*np\.mean\((\w+)(?:,\s*axis=(\d+))?\)\)\s*/\s*np\.std\((\w+)(?:,\s*axis=(\d+))?\)"
        matches = list(re.finditer(zscore_pattern, translated))
        for match in reversed(matches):
            var_out = match.group(1)
            var_in = match.group(2)
            # Ensure it's the same variable
            if match.group(3) == var_in and match.group(5) == var_in:
                replacement = f"{var_out} = stx.gen.to_z({var_in})"
                translated = translated[:match.start()] + replacement + translated[match.end():]
                conversions.append("Converted manual z-score to stx.gen.to_z()")
        
        # Manual min-max
        minmax_pattern = r"(\w+)\s*=\s*\((\w+)\s*-\s*(\w+)\.min\(\)\)\s*/\s*\((\w+)\.max\(\)\s*-\s*(\w+)\.min\(\)\)"
        matches = list(re.finditer(minmax_pattern, translated))
        for match in reversed(matches):
            var_out = match.group(1)
            var_in = match.group(2)
            if match.group(3) == var_in and match.group(4) == var_in and match.group(5) == var_in:
                replacement = f"{var_out} = stx.gen.to_01({var_in})"
                translated = translated[:match.start()] + replacement + translated[match.end():]
                conversions.append("Converted manual min-max to stx.gen.to_01()")
        
        # Convert sklearn scalers
        scaler_pattern = r"(\w+)\s*=\s*StandardScaler\(\).*?\1\.fit_transform\((\w+)\)"
        matches = list(re.finditer(scaler_pattern, translated, re.DOTALL))
        for match in reversed(matches):
            data_var = match.group(2)
            replacement = f"stx.gen.to_z({data_var})"
            translated = re.sub(match.group(0), replacement, translated)
            conversions.append("Converted StandardScaler to stx.gen.to_z()")
        
        # Convert caching decorators
        cache_patterns = [
            (r"@functools\.lru_cache(?:\([^)]*\))?", "@stx.gen.cache"),
            (r"@lru_cache(?:\([^)]*\))?", "@stx.gen.cache"),
        ]
        for pattern, replacement in cache_patterns:
            if re.search(pattern, translated):
                translated = re.sub(pattern, replacement, translated)
                conversions.append(f"Converted {pattern} to {replacement}")
        
        # Convert path operations
        if "__file__" in translated:
            # Add src() calls
            file_patterns = [
                (r"os\.path\.dirname\(__file__\)", "stx.gen.src(__file__)"),
                (r"Path\(__file__\)\.parent", "stx.gen.src(__file__)"),
            ]
            for pattern, replacement in file_patterns:
                if pattern in translated:
                    translated = translated.replace(pattern, replacement)
                    conversions.append(f"Converted {pattern} to {replacement}")
        
        # Convert timestamp operations
        if "datetime.now()" in translated or "time.time()" in translated:
            # Check if TimeStamper would be beneficial
            timestamp_count = translated.count("datetime.now()") + translated.count("time.time()")
            if timestamp_count > 2:
                # Add TimeStamper suggestion in comment
                if not preserve_comments:
                    lines = translated.split('\n')
                    for i, line in enumerate(lines):
                        if "datetime.now()" in line or "time.time()" in line:
                            lines[i] = f"# Consider using stx.gen.TimeStamper() for multiple timestamps\n{line}"
                            break
                    translated = '\n'.join(lines)
                    conversions.append("Added TimeStamper suggestion for multiple timestamps")
        
        # Add experiment lifecycle if main block exists
        if "if __name__ == '__main__':" in translated and "stx.gen.start" not in translated:
            # Insert start/close around main
            main_match = re.search(r"if\s+__name__\s*==\s*['\"]__main__['\"]:\s*\n", translated)
            if main_match:
                indent = "    "
                insert_pos = main_match.end()
                # Find the main block content
                lines = translated[insert_pos:].split('\n')
                main_lines = []
                for line in lines:
                    if line and not line.startswith((' ', '\t')):
                        break
                    main_lines.append(line)
                
                # Add start at beginning
                start_code = f"{indent}# Initialize experiment\n{indent}config = stx.gen.start()\n\n"
                # Add close at end
                close_code = f"\n{indent}# Clean up\n{indent}stx.gen.close()\n"
                
                translated = (
                    translated[:insert_pos] + 
                    start_code + 
                    '\n'.join(main_lines) + 
                    close_code +
                    translated[insert_pos + len('\n'.join(main_lines)):]
                )
                conversions.append("Added experiment lifecycle management")
        
        return {
            "translated_code": translated,
            "conversions": conversions,
            "success": True,
        }
    
    async def module_from_scitex(
        self,
        code: str,
        target_style: str
    ) -> Dict[str, Any]:
        """Translate SciTeX gen operations back to standard Python."""
        translated = code
        dependencies = set()
        
        # Convert normalization functions
        norm_conversions = [
            (r"stx\.gen\.to_z\(([^)]+)\)", r"((\1) - np.mean(\1)) / np.std(\1)", "numpy"),
            (r"stx\.gen\.to_01\(([^)]+)\)", r"((\1) - (\1).min()) / ((\1).max() - (\1).min())", "numpy"),
            (r"stx\.gen\.clip_perc\(([^,]+),\s*percentile=(\d+)\)", r"np.clip(\1, *np.percentile(\1, [100-\2, \2]))", "numpy"),
            (r"stx\.gen\.unbias\(([^)]+)\)", r"(\1) - np.mean(\1)", "numpy"),
        ]
        
        for pattern, replacement, dep in norm_conversions:
            if re.search(pattern, translated):
                translated = re.sub(pattern, replacement, translated)
                dependencies.add(dep)
        
        # Convert caching
        if "@stx.gen.cache" in translated:
            translated = translated.replace("@stx.gen.cache", "@functools.lru_cache(maxsize=None)")
            dependencies.add("functools")
        
        # Convert path operations
        if "stx.gen.src(__file__)" in translated:
            translated = translated.replace("stx.gen.src(__file__)", "os.path.dirname(__file__)")
            dependencies.add("os")
        
        # Convert TimeStamper usage
        if "stx.gen.TimeStamper" in translated:
            # Simple replacement with datetime
            translated = re.sub(
                r"(\w+)\s*=\s*stx\.gen\.TimeStamper\(\)",
                r"# TimeStamper replaced with datetime\nimport datetime",
                translated
            )
            translated = re.sub(
                r"(\w+)\.stamp\(['\"]([^'\"]+)['\"]\)",
                r'print(f"{datetime.datetime.now()}: \2")',
                translated
            )
            dependencies.add("datetime")
        
        # Convert experiment lifecycle
        if "stx.gen.start(" in translated:
            # Replace with simple setup
            translated = re.sub(
                r"(\w+)\s*=\s*stx\.gen\.start\([^)]*\)",
                r"# Experiment setup\nimport random\nimport numpy as np\nrandom.seed(42)\nnp.random.seed(42)",
                translated
            )
            dependencies.add("random")
            dependencies.add("numpy")
        
        if "stx.gen.close(" in translated:
            translated = translated.replace("stx.gen.close()", "# Cleanup complete")
        
        # Remove scitex import if not needed
        if "stx." not in translated:
            translated = re.sub(r"import scitex as stx\n?", "", translated)
        
        # Add required imports
        import_lines = []
        if "numpy" in dependencies:
            import_lines.append("import numpy as np")
        if "functools" in dependencies:
            import_lines.append("import functools")
        if "os" in dependencies:
            import_lines.append("import os")
        if "datetime" in dependencies:
            import_lines.append("import datetime")
        if "random" in dependencies:
            import_lines.append("import random")
        
        if import_lines:
            # Find where to insert imports
            lines = translated.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#'):
                    insert_idx = i
                    break
            
            for imp in reversed(import_lines):
                lines.insert(insert_idx, imp)
            translated = '\n'.join(lines)
        
        return {
            "translated_code": translated,
            "dependencies": list(dependencies),
            "success": True,
        }
    
    async def analyze_improvement_opportunities(self, code: str) -> List[Dict[str, str]]:
        """Analyze code for gen module improvement opportunities."""
        opportunities = []
        
        # Check for repeated computations
        function_calls = re.findall(r"(\w+)\([^)]*\)", code)
        call_counts = {}
        for call in function_calls:
            call_counts[call] = call_counts.get(call, 0) + 1
        
        expensive_ops = ['mean', 'std', 'corrcoef', 'cov', 'svd', 'eig', 'inv', 'solve']
        for op in expensive_ops:
            if f"np.{op}" in call_counts and call_counts[f"np.{op}"] > 2:
                opportunities.append({
                    "pattern": f"Multiple calls to np.{op}()",
                    "suggestion": f"Cache results with @stx.gen.cache decorator",
                    "benefit": "Avoid redundant computation",
                })
        
        # Check for verbose timestamp management
        if "datetime" in code and ("strftime" in code or "timestamp" in code):
            timestamp_ops = code.count("datetime.now()") + code.count("time.time()")
            if timestamp_ops > 3:
                opportunities.append({
                    "pattern": f"{timestamp_ops} timestamp operations",
                    "suggestion": "Use stx.gen.TimeStamper for organized time tracking",
                    "benefit": "Better timestamp management and analysis",
                })
        
        # Check for manual array transformations
        if "reshape" in code or "transpose" in code:
            if "stx.gen.transpose" not in code:
                opportunities.append({
                    "pattern": "Array transformation operations",
                    "suggestion": "Consider stx.gen array utilities for cleaner code",
                    "benefit": "More readable array operations",
                })
        
        # Check for print-based logging
        print_count = code.count("print(")
        if print_count > 10:
            opportunities.append({
                "pattern": f"Heavy use of print statements ({print_count} found)",
                "suggestion": "Use stx.gen.tee() to capture output to file",
                "benefit": "Persistent logging and debugging",
            })
        
        # Check for manual even/odd operations
        if "% 2 == 0" in code or "% 2 == 1" in code:
            opportunities.append({
                "pattern": "Manual even/odd checking",
                "suggestion": "Use stx.gen.to_even() or stx.gen.to_odd()",
                "benefit": "Cleaner array length adjustments",
            })
        
        return opportunities


# Main entry point
if __name__ == "__main__":
    server = ScitexGenMCPServer()
    asyncio.run(server.run())

# EOF