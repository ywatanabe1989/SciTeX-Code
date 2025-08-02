#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 19:34:26 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/setup.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./setup.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Setup script for SciTeX package."""

from setuptools import find_packages, setup

# Read version from __version__.py
version_file = os.path.join("src", "scitex", "__version__.py")
version_dict = {}
with open(version_file) as f:
    exec(f.read(), version_dict)
version = version_dict["__version__"]

# Read requirements
with open("requirements.txt") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]
    # Remove duplicate entries and fix typos
    requirements = list(dict.fromkeys(requirements))
    # Fix typo in papermill
    requirements = [
        req.replace("pepermill", "papermill") if req == "pepermill" else req
        for req in requirements
    ]

# Read README for long description
readme_path = "README.md"
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="scitex",
    version=version,
    author="Yusuke Watanabe",
    author_email="ywatanabe@scitex.ai",  # Update with actual email
    description="A comprehensive scientific computing framework for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ywatanabe1989/SciTeX-Code",  # Update with actual URL
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",  # Update with actual license
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "scitex": ["**/*.yaml", "**/*.yml", "**/*.json", "**/*.txt"],
    },
    entry_points={
        "console_scripts": [
            # Add any command-line scripts here if needed
            # "scitex=scitex.cli:main",
        ],
    },
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
            "sphinx",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "sphinx-autodoc-typehints",
        ],
    },
    keywords="scientific computing, data analysis, machine learning, visualization, research",
)

# EOF
