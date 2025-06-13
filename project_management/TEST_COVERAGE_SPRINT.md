<!-- ---
!-- Timestamp: 2025-06-02 14:35:00
!-- Author: Test Coverage Coordinator
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/project_management/TEST_COVERAGE_SPRINT.md
!-- --- -->

# Test Coverage Sprint Plan - 67.4% to 80%

## 🎯 Sprint Goal
Implement 58 test files to reach 80% coverage (366/457 files) for v1.11.0 release

## 📊 Current Status
- **Current**: 308/457 files (67.4%)
- **Target**: 366/457 files (80.0%)
- **Gap**: 58 files needed

## 🚀 Module Assignments

### ⚠️ UPDATE: io._load_modules already fully implemented!

### Agent A: str module (17 files)
**Priority**: HIGHEST - Text processing utilities
```
tests/scitex/str/
├── test__clean_path.py       # Path string cleaning
├── test__color_text.py       # Terminal color formatting
├── test__decapitalize.py     # String decapitalization
├── test__grep.py             # Pattern matching in strings
├── test__latex.py            # LaTeX string formatting
├── test__mask_api.py         # API key masking (deprecated)
├── test__mask_api_key.py     # API key masking
├── test__parse.py            # String parsing utilities
├── test__print_block.py      # Block text printing
├── test__print_debug.py      # Debug printing
├── test__printc.py           # Colored printing
├── test__readable_bytes.py   # Byte size formatting
├── test__remove_ansi.py      # ANSI code removal
├── test__replace.py          # String replacement
├── test__search.py           # String searching
├── test__squeeze_space.py    # Space normalization
└── test___init__.py          # Module initialization
```

### Agent B: db._SQLite3Mixins (11 files)
**Priority**: HIGH - Complete SQLite3 database support
```
tests/scitex/db/_SQLite3Mixins/
├── test__BatchMixin.py         # Batch operations
├── test__BlobMixin.py          # BLOB data handling
├── test__ConnectionMixin.py    # Connection management
├── test__ImportExportMixin.py  # Data import/export
├── test__IndexMixin.py         # Index management
├── test__MaintenanceMixin.py   # Database maintenance
├── test__QueryMixin.py         # Query execution
├── test__RowMixin.py           # Row operations
├── test__TableMixin.py         # Table management
├── test__TransactionMixin.py   # Transaction handling
└── test___init__.py            # Module initialization
```

### Agent C: dict + dsp.utils (14 files)
**Priority**: MEDIUM - Utility modules

**dict module (7 files)**:
```
tests/scitex/dict/
├── test__DotDict.py         # Dot notation dictionary
├── test__listed_dict.py     # Listed dictionary
├── test__pop_keys.py        # Key removal utilities
├── test__replace.py         # Dictionary replacement
├── test__safe_merge.py      # Safe dictionary merging
├── test__to_str.py          # Dictionary to string
└── test___init__.py         # Module initialization
```

**dsp.utils module (7 files)**:
```
tests/scitex/dsp/utils/
├── test__differential_bandpass_filters.py  # Bandpass filters
├── test__ensure_3d.py                      # 3D array ensuring
├── test__ensure_even_len.py                # Even length ensuring
├── test__zero_pad.py                       # Zero padding
├── test_filter.py                          # Filter utilities
├── test_pac.py                             # PAC utilities
└── test___init__.py                        # Module initialization
```

### Agent D: utils + db._PostgreSQLMixins (12 files)
**Priority**: MEDIUM - Complete utilities and PostgreSQL

**utils module (6 files)**:
```
tests/scitex/utils/
├── test__compress_hdf5.py   # HDF5 compression
├── test__email.py           # Email utilities
├── test__grid.py            # Grid generation
├── test__notify.py          # Notification system
├── test__search.py          # Search utilities
└── test___init__.py         # Module initialization
```

**db._PostgreSQLMixins (6 files)**:
```
tests/scitex/db/_PostgreSQLMixins/
├── test__IndexMixin.py         # Index management
├── test__MaintenanceMixin.py   # Database maintenance
├── test__QueryMixin.py         # Query execution
├── test__RowMixin.py           # Row operations
├── test__SchemaMixin.py        # Schema management
└── test__TableMixin.py         # Table management
```

### Agent E: Other modules (4 files)
**Priority**: LOW - Gap filling for 80% coverage
```
Various modules needing completion:
├── tests/scitex/decorators/test__combined.py
├── tests/scitex/decorators/test__signal_fn.py
├── tests/scitex/nn/test__GaussianFilter.py
└── tests/scitex/nn/test__ChannelGainChanger.py
```

## 📋 Testing Guidelines

### Test Structure
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# <timestamp>
# <author>
# <filepath>

"""Test for scitex.<module>.<function>"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import pandas as pd

# Import the function/class to test
from scitex.<module> import <function>


class Test<Function>:
    """Tests for <function>"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.sample_data = ...
    
    def test_basic_functionality(self):
        """Test basic usage"""
        result = <function>(self.sample_data)
        assert result == expected
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Empty input
        # None input
        # Invalid types
    
    def test_error_handling(self):
        """Test error conditions"""
        with pytest.raises(ValueError):
            <function>(invalid_input)
    
    @pytest.mark.parametrize("input,expected", [
        (input1, expected1),
        (input2, expected2),
    ])
    def test_parametrized(self, input, expected):
        """Test multiple scenarios"""
        assert <function>(input) == expected


def test_<function>():
    """Main test function for pytest"""
    test = Test<Function>()
    test.setup_method()
    test.test_basic_functionality()
    test.test_edge_cases()
    test.test_error_handling()
```

### Quality Standards
1. **Mock external dependencies** (file I/O, network, databases)
2. **Test edge cases** (empty, None, invalid types)
3. **Use parametrization** for multiple test cases
4. **Include docstrings** explaining what's being tested
5. **Follow SciTeX conventions** (naming, structure)
6. **Minimum 10-15 test methods** per file
7. **Cover all public functions/methods**

### Running Tests
```bash
# Run specific module tests
pytest tests/scitex/<module>/ -xvs

# Run with coverage
pytest tests/scitex/<module>/ --cov=scitex.<module> --cov-report=html

# Run all tests
./run_tests.sh
```

## 🏁 Sprint Timeline
- **Start**: 2025-06-02 14:30
- **Target**: Complete within 24-48 hours
- **Checkpoint**: Every 4 hours on BULLETIN-BOARD.md

## 📝 Progress Tracking
Agents should update BULLETIN-BOARD.md with:
1. Module claimed
2. Files completed
3. Total test methods added
4. Any blockers or issues
5. Overall progress percentage

Let's achieve 80% coverage together! 🚀

<!-- EOF -->