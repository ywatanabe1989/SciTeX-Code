<!-- ---
!-- Timestamp: 2025-06-29 10:22:57
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/mcp_servers/suggestions.md
!-- --- -->

# Improved SciTeX MCP Server Organization

## Current Issues with Organization

1. **Mixing responsibilities** - IO translator handles both file operations and path management
2. **Monolithic translators** - Single translator trying to handle multiple scitex modules
3. **Hard to maintain** - Adding new scitex modules requires modifying existing translators
4. **Poor separation** - Framework concerns mixed with module-specific logic

## Proposed Module-Based Organization

```
scitex_translators/
├── server.py                          # Main MCP server
├── core/                              # Core translation infrastructure
│   ├── __init__.py
│   ├── base_translator.py             # Abstract base translator
│   ├── context_analyzer.py            # Code context analysis
│   ├── ast_utils.py                   # AST parsing utilities
│   └── validation.py                  # Generic validation utilities
├── modules/                           # One translator per scitex module
│   ├── __init__.py
│   ├── io_translator.py               # scitex.io module
│   ├── plt_translator.py              # scitex.plt module  
│   ├── stats_translator.py            # scitex.stats module
│   ├── dsp_translator.py              # scitex.dsp module
│   ├── pd_translator.py               # scitex.pd module
│   ├── str_translator.py              # scitex.str module
│   ├── gen_translator.py              # scitex.gen module
│   └── framework_translator.py        # Framework structure
├── config/                            # Configuration extraction
│   ├── __init__.py
│   ├── path_extractor.py              # PATH.yaml generation
│   ├── param_extractor.py             # PARAMS.yaml generation
│   └── color_extractor.py             # COLORS.yaml generation
├── validators/                        # Module-specific validators
│   ├── __init__.py
│   ├── io_validator.py
│   ├── plt_validator.py
│   └── framework_validator.py
└── examples/
    ├── test_each_module.py
    └── integration_test.py
```

## Base Translator Architecture

```python
# core/base_translator.py
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any

class BaseTranslator(ABC):
    """Base class for all scitex module translators."""
    
    def __init__(self):
        self.module_name = self._get_module_name()
        self.patterns = self._load_patterns()
        self.dependencies = self._get_dependencies()
    
    @abstractmethod
    def _get_module_name(self) -> str:
        """Return the scitex module name (e.g., 'io', 'plt')."""
        pass
    
    @abstractmethod
    def _load_patterns(self) -> Dict[str, List]:
        """Load translation patterns for this module."""
        pass
    
    @abstractmethod
    def _get_dependencies(self) -> List[str]:
        """Return standard library dependencies for reverse translation."""
        pass
    
    async def to_scitex(self, code: str, context: Dict = None) -> Tuple[str, List[str]]:
        """Translate standard Python to scitex for this module."""
        translated = code
        conversions = []
        
        # Apply module-specific patterns
        for pattern_name, patterns in self.patterns["to_scitex"].items():
            translated, conv = await self._apply_patterns(translated, patterns)
            conversions.extend(conv)
        
        # Post-process if needed
        translated = await self._post_process_to_scitex(translated, context)
        
        return translated, conversions
    
    async def from_scitex(self, code: str, target_style: str = "standard") -> Tuple[str, List[str]]:
        """Translate scitex back to standard Python for this module."""
        translated = code
        dependencies = []
        
        # Apply reverse patterns
        for pattern_name, patterns in self.patterns["from_scitex"].items():
            translated, deps = await self._apply_reverse_patterns(translated, patterns)
            dependencies.extend(deps)
        
        # Post-process if needed
        translated = await self._post_process_from_scitex(translated, target_style)
        
        return translated, dependencies
    
    # Template methods that can be overridden
    async def _post_process_to_scitex(self, code: str, context: Dict) -> str:
        return code
    
    async def _post_process_from_scitex(self, code: str, target_style: str) -> str:
        return code
```

## Module-Specific Translators

### 1. IO Module Translator

```python
# modules/io_translator.py
from ..core.base_translator import BaseTranslator

class IOTranslator(BaseTranslator):
    def _get_module_name(self) -> str:
        return "io"
    
    def _load_patterns(self) -> Dict[str, List]:
        return {
            "to_scitex": {
                "load_operations": [
                    (r"pd\.read_csv\((.*?)\)", r"stx.io.load(\1)"),
                    (r"np\.load\((.*?)\)", r"stx.io.load(\1)"),
                    (r"json\.load\(open\((.*?)\)\)", r"stx.io.load(\1)"),
                ],
                "save_operations": [
                    (r"\.to_csv\((.*?)\)", r"stx.io.save(self, \1)"),
                    (r"np\.save\((.*?),\s*(.*?)\)", r"stx.io.save(\2, \1)"),
                    (r"json\.dump\((.*?),\s*open\((.*?),.*?\)\)", r"stx.io.save(\1, \2)"),
                ],
                "cache_operations": [
                    # Add cache-specific patterns
                ],
            },
            "from_scitex": {
                "load_operations": [
                    (r"stx\.io\.load\((.*?)\)", self._smart_load_replacement),
                ],
                "save_operations": [
                    (r"stx\.io\.save\((.*?)\)", self._smart_save_replacement),
                ],
            }
        }
    
    def _get_dependencies(self) -> List[str]:
        return ["pandas", "numpy", "json", "pickle", "os"]
    
    async def _post_process_to_scitex(self, code: str, context: Dict) -> str:
        """Add scitex.io specific post-processing."""
        # Add output directory creation
        # Convert paths to relative
        # Add symlink_from_cwd parameters
        return code
```

### 2. Plotting Module Translator

```python
# modules/plt_translator.py
from ..core.base_translator import BaseTranslator

class PLTTranslator(BaseTranslator):
    def _get_module_name(self) -> str:
        return "plt"
    
    def _load_patterns(self) -> Dict[str, List]:
        return {
            "to_scitex": {
                "figure_creation": [
                    (r"plt\.subplots\((.*?)\)", r"stx.plt.subplots(\1)"),
                    (r"plt\.figure\((.*?)\)", r"stx.plt.figure(\1)"),
                ],
                "axis_operations": [
                    # Combined axis labeling patterns
                    (r"ax\.set_xlabel\(['\"]?(.*?)['\"]?\)\s*\n\s*ax\.set_ylabel\(['\"]?(.*?)['\"]?\)\s*\n\s*ax\.set_title\(['\"]?(.*?)['\"]?\)",
                     r"ax.set_xyt('\1', '\2', '\3')"),
                ],
                "save_operations": [
                    (r"plt\.savefig\((.*?)\)", r"stx.io.save(fig, \1, symlink_from_cwd=True)"),
                ],
            },
            "from_scitex": {
                "figure_creation": [
                    (r"stx\.plt\.subplots\((.*?)\)", r"plt.subplots(\1)"),
                ],
                "axis_operations": [
                    (r"ax\.set_xyt\((.*?)\)", self._expand_set_xyt),
                ],
            }
        }
    
    def _get_dependencies(self) -> List[str]:
        return ["matplotlib"]
    
    async def _post_process_to_scitex(self, code: str, context: Dict) -> str:
        """Add plot-specific enhancements."""
        # Add data export for reproducibility
        # Handle legend separation
        # Ensure proper figure management
        return code
```

### 3. Stats Module Translator

```python
# modules/stats_translator.py
from ..core.base_translator import BaseTranslator

class StatsTranslator(BaseTranslator):
    def _get_module_name(self) -> str:
        return "stats"
    
    def _load_patterns(self) -> Dict[str, List]:
        return {
            "to_scitex": {
                "statistical_tests": [
                    (r"scipy\.stats\.ttest_ind\((.*?)\)", r"stx.stats.tests.ttest_ind(\1)"),
                    (r"scipy\.stats\.pearsonr\((.*?)\)", r"stx.stats.tests.corr_test(\1, method='pearson')"),
                ],
                "p_value_formatting": [
                    # Add patterns for p-value star conversion
                ],
                "multiple_comparisons": [
                    # Add FDR correction patterns
                ],
            },
            "from_scitex": {
                "statistical_tests": [
                    (r"stx\.stats\.tests\.ttest_ind\((.*?)\)", r"scipy.stats.ttest_ind(\1)"),
                ],
            }
        }
    
    def _get_dependencies(self) -> List[str]:
        return ["scipy", "statsmodels"]
```

### 4. DSP Module Translator

```python
# modules/dsp_translator.py
from ..core.base_translator import BaseTranslator

class DSPTranslator(BaseTranslator):
    def _get_module_name(self) -> str:
        return "dsp"
    
    def _load_patterns(self) -> Dict[str, List]:
        return {
            "to_scitex": {
                "filtering": [
                    (r"scipy\.signal\.butter\((.*?)\)", r"stx.dsp.filt.bandpass(\1)"),
                    (r"scipy\.signal\.filtfilt\((.*?)\)", r"stx.dsp.filt.apply(\1)"),
                ],
                "transforms": [
                    (r"scipy\.signal\.hilbert\((.*?)\)", r"stx.dsp.hilbert(\1)"),
                    (r"scipy\.signal\.welch\((.*?)\)", r"stx.dsp.psd(\1)"),
                ],
            },
            "from_scitex": {
                "filtering": [
                    (r"stx\.dsp\.filt\.bandpass\((.*?)\)", r"scipy.signal.filtfilt(butter_filter, \1)"),
                ],
            }
        }
    
    def _get_dependencies(self) -> List[str]:
        return ["scipy", "numpy"]
```

## Updated Server Implementation

```python
# server.py
from mcp.server import Server
from .modules import (
    IOTranslator, PLTTranslator, StatsTranslator, 
    DSPTranslator, PDTranslator, FrameworkTranslator
)
from .core.context_analyzer import ContextAnalyzer
from .validators import ComplianceValidator

app = Server("scitex-translators")

# Initialize all module translators
translators = {
    "io": IOTranslator(),
    "plt": PLTTranslator(),
    "stats": StatsTranslator(),
    "dsp": DSPTranslator(),
    "pd": PDTranslator(),
    "framework": FrameworkTranslator(),
}

context_analyzer = ContextAnalyzer()
validator = ComplianceValidator(translators)

@app.tool()
async def translate_to_scitex(
    source_code: str,
    target_modules: List[str] = ["io", "plt"],
    preserve_comments: bool = True,
    add_config_support: bool = True,
) -> Dict[str, Any]:
    """Translate using specified module translators."""
    
    # Analyze code context first
    context = await context_analyzer.analyze(source_code)
    
    result = {
        "translated_code": source_code,
        "conversions": [],
        "warnings": [],
        "config_files": {},
    }
    
    # Apply framework translation if needed
    if "framework" in target_modules or context["needs_framework"]:
        translated, conversions = await translators["framework"].to_scitex(
            result["translated_code"], context
        )
        result["translated_code"] = translated
        result["conversions"].extend(conversions)
    
    # Apply each module translator in dependency order
    module_order = ["io", "plt", "stats", "dsp", "pd"]  # Order matters!
    
    for module in module_order:
        if module in target_modules and module in translators:
            translated, conversions = await translators[module].to_scitex(
                result["translated_code"], context
            )
            result["translated_code"] = translated
            result["conversions"].extend(conversions)
    
    # Validate result
    validation = await validator.validate_all_modules(result["translated_code"])
    result["warnings"] = validation["warnings"]
    result["compliant"] = validation["compliant"]
    
    return result

@app.tool()
async def translate_module_specific(
    source_code: str,
    module: str,
    direction: str = "to_scitex",  # "to_scitex" or "from_scitex"
) -> Dict[str, Any]:
    """Translate using a specific module translator only."""
    
    if module not in translators:
        return {"error": f"Unknown module: {module}"}
    
    translator = translators[module]
    
    if direction == "to_scitex":
        translated, conversions = await translator.to_scitex(source_code)
        return {
            "translated_code": translated,
            "conversions": conversions,
            "module": module,
        }
    else:
        translated, dependencies = await translator.from_scitex(source_code)
        return {
            "translated_code": translated,
            "dependencies": dependencies,
            "module": module,
        }
```

## Benefits of This Organization

1. **Clear separation of concerns** - Each module handles its own patterns
2. **Easy to extend** - Add new scitex modules by creating new translators
3. **Maintainable** - Module-specific logic is isolated
4. **Testable** - Each translator can be tested independently
5. **Reusable** - Translators can be used outside the MCP server
6. **Composable** - Mix and match modules as needed
7. **Order-aware** - Apply translations in the correct dependency order

This organization much better reflects the modular nature of scitex and makes the codebase much more maintainable!

<!-- EOF -->