.PHONY: help install install-dev test test-cov lint format type-check clean build dist

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package in development mode
	pip install -e .

install-dev:  ## Install the package with development dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=isf_shader_renderer --cov-report=html --cov-report=term-missing

lint:  ## Run linting checks
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

format:  ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

type-check:  ## Run type checking
	mypy src/

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:  ## Build the package
	python -m build

dist: clean build  ## Create distribution packages

check: lint type-check test  ## Run all checks (lint, type-check, test)

pre-commit:  ## Install pre-commit hooks
	pre-commit install

example-config:  ## Create an example configuration file
	python -c "from isf_shader_renderer.config import create_default_config; create_default_config('config.yaml')"

run-example:  ## Run the example shader
	isf-renderer --shader examples/shaders/example.fs --time 0.0 --time 1.0 --time 2.0 --output examples/output/example_%04d.png --width 640 --height 480 