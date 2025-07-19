# SciTeX Error Handling Guide

## Overview

The SciTeX error handling system provides comprehensive, module-specific exceptions with clear error messages, context information, and helpful suggestions. This guide explains how to use the error system effectively.

## Error Hierarchy

All SciTeX errors inherit from `SciTeXError`, providing a consistent interface:

```
SciTeXError (base)
├── ConfigurationError
│   ├── ConfigFileNotFoundError
│   └── ConfigKeyError
├── IOError
│   ├── FileFormatError
│   ├── SaveError
│   └── LoadError
├── ScholarError
│   ├── SearchError
│   ├── EnrichmentError
│   └── PDFDownloadError
├── PlottingError
│   ├── FigureNotFoundError
│   └── AxisError
├── DataError
│   ├── ShapeError
│   └── DTypeError
├── PathError
│   ├── InvalidPathError
│   └── PathNotFoundError
├── TemplateError
│   └── TemplateViolationError
├── NNError
│   └── ModelError
└── StatsError
    └── TestError
```

## Basic Usage

### Importing Errors

```python
from scitex import errors
# or
import scitex as stx
# then use stx.errors.*
```

### Catching Errors

```python
try:
    # Your code here
    config = load_config("./config/experiment.yaml")
except stx.errors.ConfigFileNotFoundError as e:
    print(f"Config error: {e}")
    # Handle missing config
except stx.errors.ConfigKeyError as e:
    print(f"Missing key: {e}")
    # Use default values
```

### Error Features

Each error includes:
1. **Clear message** - What went wrong
2. **Context** - Additional debugging information
3. **Suggestion** - How to fix the issue

Example:
```python
try:
    raise errors.ShapeError((100, 50), (100, 60), "matrix multiplication")
except errors.ShapeError as e:
    print(e)
```

Output:
```
SciTeX Error: Shape mismatch in matrix multiplication

Context:
  expected_shape: (100, 50)
  actual_shape: (100, 60)
  operation: matrix multiplication

Suggestion: Reshape or transpose your data to match expected dimensions
```

## Module-Specific Errors

### Configuration Errors

```python
# Missing config file
raise errors.ConfigFileNotFoundError("./config/missing.yaml")

# Missing config key
raise errors.ConfigKeyError("LEARNING_RATE", 
                           available_keys=["BATCH_SIZE", "EPOCHS"])
```

### IO Errors

```python
# Wrong file format
raise errors.FileFormatError("data.txt", 
                            expected_format="csv", 
                            actual_format="txt")

# Save failure
raise errors.SaveError("output.pkl", "Permission denied")

# Load failure
raise errors.LoadError("input.h5", "File corrupted")
```

### Scholar Module Errors

```python
# Search failure
raise errors.SearchError("deep learning", "PubMed", "API limit exceeded")

# Enrichment failure
raise errors.EnrichmentError("Paper Title", "Journal not indexed")

# PDF download failure
raise errors.PDFDownloadError("http://example.com/paper.pdf", "403 Forbidden")
```

### Data Processing Errors

```python
# Shape mismatch
raise errors.ShapeError((10, 20), (10, 30), "dot product")

# Data type mismatch
raise errors.DTypeError("float32", "int64", "convolution")
```

### Path Errors

```python
# Invalid path format
raise errors.InvalidPathError("/absolute/path", "Must be relative")

# Path doesn't exist
raise errors.PathNotFoundError("./missing/directory")
```

## Validation Helpers

SciTeX provides validation functions that raise appropriate errors:

```python
# Validate path format
errors.check_path("./data/file.csv")  # OK
errors.check_path("/absolute/path")   # Raises InvalidPathError

# Check file existence
errors.check_file_exists("./existing_file.py")  # OK
errors.check_file_exists("./missing.txt")       # Raises PathNotFoundError

# Check shape compatibility
errors.check_shape_compatibility((10, 20), (10, 20), "operation")  # OK
errors.check_shape_compatibility((10, 20), (10, 30), "operation")  # Raises ShapeError
```

## Warning Functions

For non-fatal issues, use warning functions:

```python
# Deprecation warning
errors.warn_deprecated("old_function", "new_function", version="3.0")

# Performance warning
errors.warn_performance("large matrix operation", 
                       "Consider using GPU acceleration")

# Data loss warning
errors.warn_data_loss("float64 to float32 conversion",
                     "Precision will be reduced")
```

## Best Practices

### 1. Use Specific Errors

```python
# Good - specific error type
raise errors.ConfigKeyError("MISSING_KEY")

# Avoid - generic error
raise Exception("Config key not found")
```

### 2. Provide Context

```python
# Good - includes context
context = {
    "file": filepath,
    "line": line_number,
    "expected": expected_value,
    "actual": actual_value
}
raise errors.SciTeXError("Processing failed", context=context)

# Avoid - no context
raise errors.SciTeXError("Processing failed")
```

### 3. Include Suggestions

```python
# Good - helpful suggestion
raise errors.PathError(
    "Invalid path format",
    suggestion="Use relative paths starting with './' or '../'"
)

# Avoid - no guidance
raise errors.PathError("Invalid path")
```

### 4. Catch at Appropriate Levels

```python
def process_data(filepath):
    try:
        # Validate inputs
        errors.check_path(filepath)
        errors.check_file_exists(filepath)
        
        # Process data
        data = load_data(filepath)
        return transform_data(data)
        
    except errors.PathError as e:
        # Handle path issues
        logger.error(f"Path error: {e}")
        return None
    except errors.IOError as e:
        # Handle IO issues
        logger.error(f"IO error: {e}")
        return None
```

### 5. Create Custom Errors When Needed

```python
class MyModuleError(errors.SciTeXError):
    """Custom error for my module."""
    pass

class SpecificError(MyModuleError):
    """Specific error case."""
    def __init__(self, param1, param2):
        super().__init__(
            f"Error with {param1} and {param2}",
            context={"param1": param1, "param2": param2},
            suggestion="Check parameter values"
        )
```

## Integration with Logging

```python
import logging
from scitex import errors

logger = logging.getLogger(__name__)

try:
    # Your code
    result = process_data()
except errors.SciTeXError as e:
    # Log the full error with context
    logger.error(f"Processing failed: {e}")
    # Log just the message
    logger.error(f"Error: {e.message}")
    # Log context separately
    if e.context:
        logger.debug(f"Context: {e.context}")
```

## Testing Error Handling

```python
import pytest
from scitex import errors

def test_function_raises_correct_error():
    """Test that function raises appropriate error."""
    with pytest.raises(errors.ConfigKeyError) as exc_info:
        # Code that should raise ConfigKeyError
        load_missing_config_key()
    
    # Check error details
    assert "MISSING_KEY" in str(exc_info.value)
    assert exc_info.value.context["missing_key"] == "MISSING_KEY"
```

## Migration Guide

To update existing code to use the new error system:

1. Replace generic exceptions:
   ```python
   # Old
   raise ValueError("Invalid shape")
   
   # New
   raise errors.ShapeError(expected, actual, "operation")
   ```

2. Add context to errors:
   ```python
   # Old
   raise Exception(f"Failed to load {file}")
   
   # New
   raise errors.LoadError(file, "Corrupted data")
   ```

3. Use validation helpers:
   ```python
   # Old
   if not path.startswith("./"):
       raise Exception("Bad path")
   
   # New
   errors.check_path(path)
   ```

## Summary

The SciTeX error system provides:
- **Consistency** - All errors follow the same pattern
- **Clarity** - Clear messages with context
- **Helpfulness** - Suggestions for fixing issues
- **Modularity** - Module-specific error types
- **Validation** - Built-in validation helpers
- **Warnings** - Non-fatal issue reporting

By using this system consistently, SciTeX code becomes more maintainable, debuggable, and user-friendly.