#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup script for mngs redirect package"""

from setuptools import setup, find_packages

setup(
    name="mngs",
    version="2.0.0",
    description="DEPRECATED: mngs has been renamed to scitex. Please install scitex instead.",
    long_description="""# DEPRECATED: mngs → scitex

The `mngs` package has been renamed to `scitex`.

## Installation
```bash
pip install scitex
```

## Migration
Simply replace your imports:
```python
# Old
import mngs
from mngs.io import save

# New
import scitex
from scitex.io import save
```

This package now serves as a redirect to maintain backward compatibility.
""",
    long_description_content_type="text/markdown",
    author="ywatanabe1989",
    author_email="ywatanabe@alumni.u-tokyo.ac.jp",
    url="https://github.com/ywatanabe1989/SciTeX-Code",
    packages=find_packages(),
    install_requires=["scitex>=2.0.0"],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)