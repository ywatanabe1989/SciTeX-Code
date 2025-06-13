# High-Priority Modules for Test Implementation

Based on the analysis of the codebase structure and the focus on test-driven development, the following modules have been identified as high-priority for test implementation:

## 1. Core Path Utilities

Path utilities are foundational and used across many parts of the codebase:

- `scitex/path/_clean.py` - Simple but critical utility for path normalization
- `scitex/path/_split.py` - Path splitting functionality 
- `scitex/path/_getsize.py` - File size determination
- `scitex/path/_increment_version.py` - Version management for files

These modules are fundamental building blocks for other components and are relatively simple to test without complex dependencies.

## 2. IO Utilities

IO utilities are essential for data persistence and manipulation:

- `scitex/io/_save.py` - Already started with tests for PyTorch and CSV deduplication
- `scitex/io/_load.py` - Counterpart to `_save.py`
- `scitex/io/_json2md.py` - Conversion utilities
- `scitex/io/_glob.py` - File pattern matching

These are critical for ensuring data consistency, especially given the new feature request for IO consistency tests.

## 3. String Manipulation Utilities

String utilities are widely used and easy to test:

- `scitex/str/_clean_path.py` - Path string cleaning
- `scitex/str/_color_text.py` - Text coloring functionality
- `scitex/str/_readable_bytes.py` - Human-readable byte formatting
- `scitex/str/_replace.py` - String replacement utilities

These utilities should be straightforward to test with various input/output pairs.

## 4. Dictionary Utilities

Dictionary handling utilities:

- `scitex/dict/_DotDict.py` - Dictionary with dot notation access
- `scitex/dict/_pop_keys.py` - Removing keys from dictionaries
- `scitex/dict/_replace.py` - Dictionary replacement functions
- `scitex/dict/_safe_merge.py` - Safe merging of dictionaries

These are used for configuration handling and data transformation.

## 5. DataFrame Utilities

DataFrame utilities are particularly important given the IO consistency feature request:

- `scitex/pd/_force_df.py` - Converting to dataframes
- `scitex/pd/_replace.py` - Replacing values in dataframes
- `scitex/pd/_slice.py` - Dataframe slicing
- `scitex/pd/_sort.py` - Dataframe sorting

## Implementation Approach

For each module:

1. Review the existing test template file
2. Identify the core functionality that needs testing
3. Develop test cases covering:
   - Normal operation scenarios
   - Edge cases
   - Error conditions
4. Implement tests following our established pattern from `test__save.py`
5. Run tests to verify functionality
6. Document any issues or concerns that arise

## Initial Focus

The immediate focus will be on:

1. `scitex/path/_clean.py` - Simple but widely used function
2. `scitex/str/_readable_bytes.py` - Used for reporting file sizes
3. `scitex/dict/_safe_merge.py` - Key utility for configuration handling

These represent different utility categories and should be relatively straightforward to test, providing a good starting point for expanding test coverage.