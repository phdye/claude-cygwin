.PHONY: help install install-dev test lint format clean build docs

help:
	@echo "Available commands:"
	@echo "  install      Install package"
	@echo "  install-dev  Install package with development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package"

install:
	pip install -e .

install-dev:
	pip install -e .[dev]
	pre-commit install

test:
	pytest -v --cov=claude_shell_connector

lint:
	flake8 src tests
	black --check src tests
	isort --check-only src tests
	mypy src

format:
	black src tests
	isort src tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

docs:
	cd docs && make html