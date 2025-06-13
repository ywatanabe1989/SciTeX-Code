#!/usr/bin/env python3
"""Nox configuration for SciTeX project.

Nox is a command-line tool that automates testing in multiple Python environments.
It's similar to tox but uses standard Python files for configuration.
"""

import tempfile
from pathlib import Path

import nox

# Python versions to test against
PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]

# Package locations
PACKAGE = "scitex"
LOCATIONS = ["src", "tests", "noxfile.py", "docs/conf.py"]

# Test dependencies
TEST_DEPS = [
    "pytest>=6.0",
    "pytest-cov>=2.10",
    "pytest-xdist>=2.0",
    "pytest-timeout>=1.4",
    "pytest-mock>=3.3",
]

# Development dependencies
DEV_DEPS = [
    "black>=21.0",
    "isort>=5.0",
    "flake8>=3.8",
    "flake8-bugbear",
    "flake8-docstrings",
    "flake8-import-order",
    "bandit[toml]>=1.7",
    "safety>=1.10",
    "mypy>=0.900",
    "pylint>=2.10",
]

# Documentation dependencies
DOC_DEPS = [
    "sphinx>=4.0",
    "sphinx-rtd-theme>=1.0",
    "sphinx-autodoc-typehints>=1.12",
    "nbsphinx>=0.8",
    "recommonmark>=0.7",
]


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    """Run the test suite with coverage."""
    # Install dependencies
    session.install("-e", ".")
    session.install(*TEST_DEPS)
    
    # Run pytest
    args = session.posargs or ["tests/", "--cov=scitex", "--cov-report=term-missing", "-v"]
    session.run("pytest", *args)


@nox.session(python=PYTHON_VERSIONS)
def unit(session):
    """Run unit tests only."""
    session.install("-e", ".")
    session.install(*TEST_DEPS)
    
    args = session.posargs or [
        "tests/",
        "-m", "not integration",
        "--cov=scitex",
        "--cov-report=term-missing",
        "-v"
    ]
    session.run("pytest", *args)


@nox.session(python=PYTHON_VERSIONS)
def integration(session):
    """Run integration tests only."""
    session.install("-e", ".")
    session.install(*TEST_DEPS)
    
    args = session.posargs or [
        "tests/",
        "-m", "integration",
        "--cov=scitex",
        "--cov-report=term-missing",
        "-v"
    ]
    session.run("pytest", *args)


@nox.session(python="3.10")
def lint(session):
    """Run all linting tools."""
    session.install(*DEV_DEPS)
    
    # Run black
    session.run("black", "--check", "--diff", *LOCATIONS)
    
    # Run isort
    session.run("isort", "--check-only", "--diff", *LOCATIONS)
    
    # Run flake8
    session.run("flake8", *LOCATIONS)
    
    # Run bandit
    session.run("bandit", "-r", "src/scitex", "-ll")
    
    # Run safety
    session.run("safety", "check", "--json")


@nox.session(python="3.10")
def format(session):
    """Format code with black and isort."""
    session.install("black", "isort")
    
    # Run black
    session.run("black", *LOCATIONS)
    
    # Run isort
    session.run("isort", *LOCATIONS)


@nox.session(python="3.10")
def typecheck(session):
    """Run type checking with mypy."""
    session.install("-e", ".")
    session.install("mypy", "types-requests", "types-PyYAML")
    
    session.run("mypy", "src/scitex", "--ignore-missing-imports")


@nox.session(python="3.10")
def pylint(session):
    """Run pylint for additional code quality checks."""
    session.install("-e", ".")
    session.install("pylint")
    
    session.run("pylint", "src/scitex", "--rcfile=pyproject.toml")


@nox.session(python="3.10")
def security(session):
    """Run security checks."""
    session.install("bandit[toml]", "safety")
    
    # Run bandit
    session.run("bandit", "-r", "src/scitex", "-ll", "-x", "tests")
    
    # Run safety
    session.run("safety", "check", "--json")


@nox.session(python="3.10")
def coverage(session):
    """Generate coverage report."""
    session.install("-e", ".")
    session.install(*TEST_DEPS)
    session.install("coverage[toml]")
    
    # Run tests with coverage
    session.run(
        "pytest",
        "tests/",
        "--cov=scitex",
        "--cov-report=html",
        "--cov-report=xml",
        "--cov-report=term-missing",
        "--cov-fail-under=85",
    )
    
    # Generate coverage badge
    session.install("coverage-badge")
    session.run("coverage-badge", "-o", "coverage.svg", "-f")
    
    session.log("Coverage report generated in htmlcov/")


@nox.session(python="3.10")
def docs(session):
    """Build documentation."""
    session.install("-e", ".")
    session.install(*DOC_DEPS)
    
    # Build docs
    session.cd("docs")
    session.run("sphinx-build", "-b", "html", ".", "_build/html")
    
    session.log("Documentation built in docs/_build/html/")


@nox.session(python="3.10")
def docs_serve(session):
    """Build and serve documentation."""
    session.install("-e", ".")
    session.install(*DOC_DEPS)
    session.install("sphinx-autobuild")
    
    # Build and serve docs
    session.cd("docs")
    session.run("sphinx-autobuild", ".", "_build/html", "--port", "8000")


@nox.session(python="3.10")
def profile(session):
    """Profile test execution."""
    session.install("-e", ".")
    session.install(*TEST_DEPS)
    session.install("pytest-profiling", "snakeviz")
    
    # Run tests with profiling
    with tempfile.NamedTemporaryFile(suffix=".prof", delete=False) as f:
        profile_file = f.name
    
    session.run(
        "pytest",
        "tests/",
        f"--profile-svg",
        "-v",
        env={"PYTEST_PROFILE": profile_file}
    )
    
    # Visualize results
    session.run("snakeviz", profile_file)


@nox.session(python="3.10")
def benchmark(session):
    """Run benchmark tests."""
    session.install("-e", ".")
    session.install(*TEST_DEPS)
    session.install("pytest-benchmark")
    
    session.run(
        "pytest",
        "tests/",
        "-m", "benchmark",
        "--benchmark-only",
        "--benchmark-autosave",
        "-v"
    )


@nox.session(python=PYTHON_VERSIONS)
def xdist_tests(session):
    """Run tests in parallel using pytest-xdist."""
    session.install("-e", ".")
    session.install(*TEST_DEPS)
    
    session.run(
        "pytest",
        "tests/",
        "-n", "auto",
        "--cov=scitex",
        "--cov-report=term",
        "-v"
    )


@nox.session(python="3.10")
def clean(session):
    """Clean up temporary files and build artifacts."""
    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.egg-info",
        ".coverage",
        "coverage.xml",
        "coverage.svg",
        "htmlcov",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        ".nox",
        "dist",
        "build",
        "docs/_build",
    ]
    
    for pattern in patterns:
        session.log(f"Removing {pattern}")
        for path in Path(".").glob(pattern):
            session.run("rm", "-rf", str(path), external=True)


@nox.session(python="3.10")
def dev(session):
    """Set up development environment."""
    # Install package in editable mode with all dependencies
    session.install("-e", ".[all,dev]")
    
    # Install pre-commit
    session.install("pre-commit")
    session.run("pre-commit", "install")
    
    session.log("Development environment ready!")
    session.log("Run 'nox' to execute all default sessions")
    session.log("Run 'nox -l' to list all available sessions")


@nox.session(python="3.10")
def release(session):
    """Prepare a release."""
    session.install("twine", "wheel", "setuptools", "build")
    
    # Clean previous builds
    session.run("rm", "-rf", "dist", "build", external=True)
    
    # Build distribution
    session.run("python", "-m", "build")
    
    # Check distribution
    session.run("twine", "check", "dist/*")
    
    session.log("Release artifacts built in dist/")
    session.log("Run 'twine upload dist/*' to upload to PyPI")


# Set default sessions
nox.options.sessions = ["lint", "tests", "typecheck", "docs"]