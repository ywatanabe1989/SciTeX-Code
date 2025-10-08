<!-- ---
!-- Timestamp: 2025-10-08 15:01:08
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/logging/README.md
!-- --- -->

# SciTeX Logging

Enhanced logging system for SciTeX with color support, custom levels, and configurable formats.

## Features

- **Custom Log Levels**: `SUCCESS`, `FAIL` in addition to standard levels
- **Color-Coded Console Output**: Different colors for each log level
- **Configurable Formats**: Control log verbosity via environment variable
- **File Logging**: Automatic log rotation with configurable size limits
- **Print Capture**: Optionally capture print() statements to logs

## Quick Start

```python
from scitex import logging

logger = logging.getLogger(__name__)

logger.info("Processing data...")
logger.success("Operation completed successfully!")
logger.fail("Operation failed")
logger.warning("Warning message")
logger.error("Error occurred")

# With indentation for hierarchical logging
logger.info("Starting batch process")
logger.info("Processing item 1", indent=1)
logger.info("Downloading PDF", indent=2)
logger.success("Downloaded successfully", indent=2)
logger.info("Processing item 2", indent=1)
```

## Log Formats

Control log format using the `SCITEX_LOG_FORMAT` environment variable:

### Available Formats

| Format     | Output Example                                                      | Use Case               |
|------------|---------------------------------------------------------------------|------------------------|
| `minimal`  | `INFO: message`                                                     | Minimal output         |
| `default`  | `INFO: message`                                                     | Default, clean output  |
| `detailed` | `INFO: [module.name] message`                                       | Show module context    |
| `debug`    | `INFO: [file.py:123 - func()] message`                              | Development, debugging |
| `full`     | `2025-10-08 15:30:45 - INFO: [file.py:123 - module.func()] message` | Complete details       |

### Usage Examples

```bash
# Default simple format
python script.py

# Debug format with filename, line number, function name
SCITEX_LOG_FORMAT=debug python script.py

# Full format with timestamp and all details
SCITEX_LOG_FORMAT=full python script.py
```

## Configuration

### Basic Setup

```python
from scitex.logging import configure

# Simple configuration
configure(level="info")

# Full configuration
configure(
    level="debug",
    log_file="/path/to/logfile.log",
    enable_file=True,
    enable_console=True,
    capture_prints=True,
    max_file_size=10 * 1024 * 1024,  # 10MB
    backup_count=5
)
```

### Global Level Control

```python
from scitex.logging import set_level, get_level

# Set global log level
set_level("debug")  # or logging.DEBUG

# Get current level
current_level = get_level()
```

### File Logging Control

```python
from scitex.logging import enable_file_logging, is_file_logging_enabled

# Disable file logging
enable_file_logging(False)

# Check status
if is_file_logging_enabled():
    print("File logging is active")
```

## Custom Log Levels

### SUCCESS Level

Use for successful operations:

```python
logger.success("Downloaded 10 PDFs successfully")
logger.success(f"Authentication established at {url}")
```

### FAIL Level

Use for operation failures (different from ERROR):

```python
logger.fail("Download failed after 3 retries")
logger.fail(f"Could not find PDF URLs for {doi}")
```

## Indentation

Control message indentation for hierarchical logging:

```python
logger.info("Main process starting")
logger.info("Step 1: Initialize", indent=1)
logger.info("Loading config", indent=2)
logger.success("Config loaded", indent=2)
logger.info("Step 2: Execute", indent=1)
logger.info("Running task", indent=2)
logger.success("Task completed", indent=2)
```

**Output**:
```
INFO: Main process starting
INFO:   Step 1: Initialize
INFO:     Loading config
SUCCESS:     Config loaded
INFO:   Step 2: Execute
INFO:     Running task
SUCCESS:     Task completed
```

**Features**:
- `indent=N` parameter on all log methods (debug, info, warning, error, critical, success, fail)
- Default indent width: 2 spaces per level
- Configurable via `SciTeXConsoleFormatter(indent_width=4)`
- Works with all format templates

## Separators

Add visual separators around important messages:

```python
logger.info("Starting PDF Download", sep="-", n=40)
logger.info("Processing batch 1", sep="=", n=60, indent=1)
logger.success("Download Complete", sep="-", n=40)
```

**Output**:
```
----------------------------------------
INFO: Starting PDF Download
----------------------------------------

============================================================
INFO:   Processing batch 1
============================================================

----------------------------------------
SUCCESS: Download Complete
----------------------------------------
```

**Features**:
- `sep=None` - No separator (default behavior)
- `sep="-"` - Use dashes as separator
- `n=40` - Number of separator characters (default: 40)
- Works with `indent` for hierarchical decorated sections
- Applies to all log methods

**Combined Example**:
```python
logger.info("Main Process", sep="=", n=60)
logger.info("Step 1: Authentication", sep="-", n=40, indent=1)
logger.success("Authenticated", indent=2)
logger.info("Step 2: Download", sep="-", n=40, indent=1)
logger.success("Downloaded 10 PDFs", indent=2)
```

## Color Codes

Console output uses ANSI colors when connected to a TTY:

- **DEBUG**: Black (dim)
- **INFO**: Black
- **SUCCESS**: Green
- **WARNING**: Yellow
- **FAIL**: Light Red
- **ERROR**: Red
- **CRITICAL**: Magenta

## Format Template Variables

Available variables for custom format templates:

| Variable        | Description          | Example                 |
|-----------------|----------------------|-------------------------|
| `%(levelname)s` | Log level name       | INFO, DEBUG, etc.       |
| `%(message)s`   | Log message          | "Processing complete"   |
| `%(name)s`      | Logger name (module) | scitex.scholar.download |
| `%(filename)s`  | Source filename      | Scholar.py              |
| `%(lineno)d`    | Line number          | 123                     |
| `%(funcName)s`  | Function name        | download_batch          |
| `%(asctime)s`   | Timestamp            | 2025-10-08 15:30:45     |
| `%(pathname)s`  | Full path            | /path/to/file.py        |
| `%(module)s`    | Module name          | Scholar                 |

## Advanced Usage

### Custom Formatter

```python
from scitex.logging import SciTeXConsoleFormatter
import logging

# Create custom handler with specific format
handler = logging.StreamHandler()
handler.setFormatter(SciTeXConsoleFormatter(
    fmt="%(levelname)s: [%(filename)s:%(lineno)d] %(message)s"
))
```

### Programmatic Format Selection

```python
from scitex.logging import FORMAT_TEMPLATES

# Get available formats
print(FORMAT_TEMPLATES.keys())
# ['minimal', 'simple', 'detailed', 'debug', 'full']

# Use specific format
debug_fmt = FORMAT_TEMPLATES['debug']
```

## File Logging

Logs are written to `~/.scitex/logs/scitex-YYYY-MM-DD.log` by default.

### Log Rotation

- Files rotate when reaching `max_file_size` (default: 10MB)
- Keeps `backup_count` old files (default: 5)
- Old files: `scitex-YYYY-MM-DD.log.1`, `.2`, etc.

### Get Current Log Path

```python
from scitex.logging import get_log_path

log_path = get_log_path()
print(f"Logging to: {log_path}")
```

## Examples

### Scholar Module Logging

```python
from scitex import logging

logger = logging.getLogger(__name__)

# Stage logging with clear separators
logger.info(
    f"\n{'-'*40}\n{self.__class__.__name__} starting...\n{'-'*40}"
)

# Progress logging
logger.info(f"Processing {i+1}/{total} items...")

# Success/failure
logger.success(f"Downloaded {filename}")
logger.fail(f"Failed to download {filename}: {error}")
```

### With Environment Variable

```bash
# Production: simple output
python -m scitex.scholar --download

# Development: detailed debugging
SCITEX_LOG_FORMAT=debug python -m scitex.scholar --download

# Analysis: full details with timestamps
SCITEX_LOG_FORMAT=full python -m scitex.scholar --download > output.log
```

## API Reference

### Functions

- `configure(**kwargs)` - Configure logging system
- `set_level(level)` - Set global log level
- `get_level()` - Get current log level
- `enable_file_logging(enabled)` - Enable/disable file logging
- `is_file_logging_enabled()` - Check file logging status
- `get_log_path()` - Get current log file path

### Classes

- `SciTeXLogger` - Enhanced logger with success/fail methods
- `SciTeXConsoleFormatter` - Color formatter for console
- `SciTeXFileFormatter` - Plain formatter for files

### Constants

- `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` - Standard levels
- `SUCCESS`, `FAIL` - Custom levels
- `LOG_FORMAT` - Current format from env var
- `FORMAT_TEMPLATES` - Available format templates

## See Also

- [Python logging documentation](https://docs.python.org/3/library/logging.html)
- [SciTeX Scholar module](../scholar/README.md)

<!-- EOF -->