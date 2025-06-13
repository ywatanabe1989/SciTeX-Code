# Makefile for SciTeX development

.PHONY: help install test lint docs clean build release coverage

help:
	@echo "Available commands:"
	@echo ""
	@echo "Installation:"
	@echo "  make install       Install package in development mode"
	@echo "  make install-all   Install with all optional dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run all tests with coverage"
	@echo "  make test-fast     Run tests in parallel"
	@echo "  make test-module   Run tests for specific module (MODULE=gen)"
	@echo "  make test-slow     Run all tests including slow ones"
	@echo "  make test-unit     Run only unit tests"
	@echo "  make test-integration  Run only integration tests"
	@echo "  make coverage      Generate detailed coverage report"
	@echo "  make coverage-html Open HTML coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          Run all code quality checks"
	@echo "  make format        Auto-format code with black and isort"
	@echo "  make typecheck     Run type checking with mypy"
	@echo "  make security      Run security checks with bandit"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs          Build documentation"
	@echo "  make docs-serve    Serve documentation locally"
	@echo ""
	@echo "Development:"
	@echo "  make clean         Clean all build artifacts"
	@echo "  make build         Build distribution packages"
	@echo "  make release       Create a new release"
	@echo "  make pre-commit    Run pre-commit hooks"

install:
	pip install -e .
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

install-all:
	pip install -e ".[all,dev]"
	pre-commit install

test:
	python -m pytest tests/ -v --cov=src/scitex --cov-report=html --cov-report=term-missing --cov-fail-under=85

test-fast:
	python -m pytest tests/ -v -n auto --cov=src/scitex --cov-report=term

test-module:
	@echo "Usage: make test-module MODULE=gen"
	python -m pytest tests/scitex/$(MODULE) -v --cov=src/scitex/$(MODULE) --cov-report=term-missing

test-slow:
	python -m pytest tests/ -v --cov=src/scitex -m "slow"

test-unit:
	python -m pytest tests/ -v --cov=src/scitex -m "not integration" --cov-report=term-missing

test-integration:
	python -m pytest tests/ -v --cov=src/scitex -m "integration" --cov-report=term-missing

coverage:
	python -m pytest tests/ --cov=src/scitex --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Coverage report generated:"
	@echo "  - HTML: htmlcov/index.html"
	@echo "  - XML: coverage.xml"
	@echo "  - Terminal: See above"

coverage-html: coverage
	@python -c "import webbrowser; webbrowser.open('htmlcov/index.html')"

lint:
	@echo "Running flake8..."
	flake8 src/scitex --max-line-length=88 --extend-ignore=E203,W503,E731
	@echo "Running black check..."
	black --check src/scitex tests
	@echo "Running isort check..."
	isort --check-only src/scitex tests
	@echo "Running mypy..."
	mypy src/scitex --ignore-missing-imports
	@echo "Running bandit..."
	bandit -r src/scitex -ll -x tests

format:
	black src/scitex tests
	isort src/scitex tests
	@echo "Code formatted successfully!"

typecheck:
	mypy src/scitex --ignore-missing-imports --show-error-codes

security:
	bandit -r src/scitex -ll -x tests
	safety check --json

docs:
	cd docs && make clean && make html
	@echo "Documentation built in docs/_build/html/"

docs-serve:
	cd docs/_build/html && python -m http.server

docs-watch:
	cd docs && sphinx-autobuild . _build/html

clean:
	rm -rf build dist *.egg-info
	rm -rf .coverage htmlcov .pytest_cache coverage.xml
	rm -rf docs/_build
	rm -rf .tox .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete

build: clean
	python -m build

release: test lint
	@echo "Creating release..."
	@echo "Current version: $$(python -c 'import scitex; print(scitex.__version__)')"
	@echo "Enter new version: "; read VERSION; \
	echo "__version__ = '$$VERSION'" > src/scitex/__version__.py; \
	git add src/scitex/__version__.py; \
	git commit -m "Bump version to $$VERSION"; \
	git tag -a "v$$VERSION" -m "Release version $$VERSION"; \
	echo "Version bumped to $$VERSION"
	@echo "Run 'git push && git push --tags' to publish"

# Pre-commit hooks
pre-commit:
	pre-commit run --all-files

pre-commit-update:
	pre-commit autoupdate

# Development shortcuts
dev-install:
	pip install -e ".[dev]"

dev-test:
	python -m pytest tests/ -v -x --tb=short -m "not slow"

dev-coverage:
	python -m pytest tests/ --cov=src/scitex --cov-report=html
	@python -c "import webbrowser; webbrowser.open('htmlcov/index.html')"

# CI/CD helpers
ci-test:
	python -m pytest tests/ --cov=src/scitex --cov-report=xml --cov-fail-under=85

ci-lint:
	flake8 src/scitex --count --select=E9,F63,F7,F82 --show-source --statistics
	black --check src/scitex
	isort --check-only src/scitex

# Tox environments
tox:
	tox

tox-parallel:
	tox -p auto

tox-py39:
	tox -e py39

tox-lint:
	tox -e lint

tox-coverage:
	tox -e coverage

# Advanced testing
test-failed:
	python -m pytest tests/ -v --lf

test-debug:
	python -m pytest tests/ -v -s --pdb

test-profile:
	python -m pytest tests/ --profile

test-benchmark:
	python -m pytest tests/ -v -m "benchmark" --benchmark-only

# Coverage utilities
coverage-report:
	coverage report -m

coverage-badge:
	coverage-badge -o coverage.svg -f

# Quality reports
quality-report:
	@echo "Generating quality report..."
	@mkdir -p reports
	flake8 src/scitex --format=html --htmldir=reports/flake8
	mypy src/scitex --html-report reports/mypy
	bandit -r src/scitex -f html -o reports/bandit.html
	@echo "Reports generated in reports/"

# Maintenance
update-deps:
	pip-compile requirements.in -o requirements.txt --upgrade
	pip-compile requirements-dev.in -o requirements-dev.txt --upgrade

check-deps:
	pip-audit
	safety check

# Docker support
docker-build:
	docker build -t scitex:latest .

docker-test:
	docker run --rm scitex:latest pytest

docker-shell:
	docker run --rm -it -v $$(pwd):/app scitex:latest bash