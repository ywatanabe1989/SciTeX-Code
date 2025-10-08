<!-- ---
!-- Timestamp: 2025-10-09 10:10:21
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/path/README.md
!-- --- -->

<!-- ---
!-- Timestamp: 2025-01-15 11:02:49
!-- Author: ywatanabe
!-- File: ./src/scitex/path/README.md
!-- --- -->
# [`scitex.path`](https://github.com/ywatanabe1989/scitex/tree/main/src/scitex/path/)

## Overview
The `scitex.path` module provides a set of utilities for handling file paths, directory operations, and version control related tasks in Python. It simplifies common path-related operations and adds functionality for finding files and directories.

## Installation
```bash
pip install scitex
```

## Features
- Path manipulation and information retrieval
- Directory and file search functionality
- Git repository root finding
- Version control helpers

## Quick Start
```python
import scitex

# Path information
fpath = scitex.path.this_path()  # Returns the current file path, e.g., "/tmp/fake.py"
spath = scitex.path.spath()  # Returns a safe path, e.g., '/tmp/fake-ywatanabe/.'
dir, fname, ext = scitex.path.split(fpath)  # Splits path into directory, filename, and extension

# Find directories and files
dirs = scitex.path.find_dir(".", "path")  # Finds directories matching the pattern, e.g., [./src/scitex/path]
files = scitex.path.find_file(".", "*wavelet.py")  # Finds files matching the pattern, e.g., ['./src/scitex/dsp/_wavelet.py']

# Git and versioning
git_root = scitex.path.find_git_root()  # Finds the root of the Git repository
latest_file = scitex.path.find_latest("path/to/files", "*.txt")  # Finds the latest version of a file
new_version = scitex.path.increment_version("file_v1.txt")  # Increments the version of a file
```

## API Reference
- `scitex.path.this_path()`: Returns the path of the current file
- `scitex.path.spath()`: Returns a safe path (user-specific temporary directory)
- `scitex.path.split(path)`: Splits a path into directory, filename, and extension
- `scitex.path.find_dir(root, pattern)`: Finds directories matching a pattern
- `scitex.path.find_file(root, pattern)`: Finds files matching a pattern
- `scitex.path.find_git_root()`: Finds the root directory of the current Git repository
- `scitex.path.find_latest(directory, pattern)`: Finds the latest version of a file matching the pattern
- `scitex.path.increment_version(file_path)`: Increments the version of a file

## Use Cases
- Simplifying path manipulations in Python scripts
- Searching for specific files or directories within a project
- Managing versioned files and directories
- Working with Git repositories programmatically

## TODO
- [ ] May utilizing `pathlib` will replace or enhance this module

## Contributing
Contributions to improve `scitex.path` are welcome. Please submit pull requests or open issues on the GitHub repository.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
Yusuke Watanabe (ywatanabe@scitex.ai)

For more information and updates, please visit the [scitex GitHub repository](https://github.com/ywatanabe1989/scitex).

<!-- EOF -->