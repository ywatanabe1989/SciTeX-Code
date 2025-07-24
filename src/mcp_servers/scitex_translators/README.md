# SciTeX Unified Translator MCP Server

A unified, intelligent MCP server for translating between standard Python and SciTeX code styles.

## Architecture Overview

This server implements the improved architecture proposed in the feature request:

```
scitex_translators/
├── server.py              # Unified MCP server
├── core/                  # Shared infrastructure
│   ├── base_translator.py # Abstract base class for translators
│   └── context_analyzer.py # Code analysis and context understanding
├── modules/               # One translator per scitex module
│   ├── io_translator.py   # I/O operations translator
│   ├── plt_translator.py  # (Future) Plotting translator
│   └── ai_translator.py   # (Future) AI/ML translator
├── validators/            # Validation utilities
│   └── base_validator.py  # Code validation functionality
└── config/               # (Future) Configuration extraction
```

## Key Features

### 1. Context-Aware Translation
- Analyzes code structure to understand dependencies
- Suggests appropriate SciTeX modules automatically
- Preserves coding style preferences

### 2. Pluggable Architecture
- Easy to add new module translators
- Each translator inherits from `BaseTranslator`
- Shared utilities reduce code duplication

### 3. Intelligent Validation
- Syntax validation
- Style checking
- Complexity analysis
- Module-specific rules

### 4. Bidirectional Translation
- Standard Python → SciTeX
- SciTeX → Standard Python
- SciTeX → NumPy style
- SciTeX → Pandas style

## Installation

```bash
cd src/mcp_servers/scitex_translators
pip install -e .
```

## Usage

### Starting the Server

```bash
scitex-unified-translator
```

### Available Tools

1. **translate_to_scitex** - Convert standard Python to SciTeX
2. **translate_from_scitex** - Convert SciTeX to standard Python
3. **analyze_code** - Analyze code and suggest modules
4. **validate_code** - Check syntax, style, and complexity
5. **list_modules** - Show available translators
6. **get_module_info** - Get details about a specific module
7. **batch_translate** - Translate multiple snippets

### Example Usage

```python
# Standard Python code
import numpy as np
import pandas as pd

# Load data
data = np.load('data.npy')
df = pd.read_csv('results.csv')

# Save results
np.save('processed.npy', data)
df.to_excel('summary.xlsx', index=False)
```

Translates to:

```python
import scitex.io as io

# Load data
data = io.load('data.npy')
df = io.load('results.csv')

# Save results
io.save(data, 'processed.npy')
io.save(df, 'summary.xlsx')
```

## Implementation Status

### Phase 1: Core Infrastructure ✅
- [x] Base translator abstract class
- [x] Context analyzer
- [x] Shared validation utilities
- [x] Unified server structure

### Phase 2: Module Migration (In Progress)
- [x] IO translator implementation
- [ ] PLT translator migration
- [ ] AI translator migration
- [ ] Module ordering logic

### Phase 3: Enhanced Features
- [ ] Configuration extraction modules
- [ ] Advanced module-specific validators
- [ ] Comprehensive test suite

### Phase 4: Deployment
- [ ] Documentation updates
- [ ] Backward compatibility layer
- [ ] Migration guides

## Benefits Over Previous Architecture

1. **Maintainability**: Single server, multiple translators
2. **Code Reuse**: Shared base classes and utilities
3. **Intelligence**: Context-aware translation
4. **Extensibility**: Easy to add new modules
5. **Validation**: Built-in quality checks

## Adding a New Translator

1. Create a new file in `modules/`:
```python
from scitex_translators.core.base_translator import BaseTranslator

class MyModuleTranslator(BaseTranslator):
    def _setup_module_info(self):
        self.module_name = "mymodule"
        self.scitex_functions = ["func1", "func2"]
        self.standard_equivalents = {
            "standard.func": "mymodule.func1"
        }
    
    def _transform_to_scitex(self, tree, context):
        # Implement AST transformation
        pass
    
    def _transform_from_scitex(self, tree, context, target_style):
        # Implement reverse transformation
        pass
```

2. Import in `modules/__init__.py`
3. The server will automatically load it

## Development

The unified architecture makes it easy to:
- Add new translators
- Enhance context analysis
- Improve validation rules
- Support new target styles

## Future Enhancements

- VS Code extension integration
- Real-time translation preview
- Project-wide translation
- Custom style configurations
- Machine learning for pattern detection