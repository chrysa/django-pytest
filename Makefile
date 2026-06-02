.PHONY: help install test test-cov lint format typecheck docker-test pre-commit clean

help:
	@echo "Available targets:"
	@echo "  install     Install dev dependencies + pre-commit hooks"
	@echo "  test        Run unit tests"
	@echo "  test-cov    Run tests with coverage"
	@echo "  lint        Run ruff linter"
	@echo "  format      Auto-format code"
	@echo "  typecheck   Run mypy type checking"
	@echo "  docker-test Run tests in Docker (CI-compatible)"
	@echo "  pre-commit  Run all pre-commit checks"
	@echo "  clean       Remove build artifacts"

install:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest tests/ --tb=short

test-cov:
	pytest tests/ --cov=django_pytest --cov-report=term-missing --cov-report=xml

lint:
	ruff check django_pytest tests

format:
	ruff format django_pytest tests

typecheck:
	mypy django_pytest

docker-test:
	docker build -f Dockerfile.test -t django-pytest-test .
	docker run --rm django-pytest-test

pre-commit:
	pre-commit run --all-files

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage build dist *.egg-info 2>/dev/null || true
