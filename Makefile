# makefile-tier: lib
.DEFAULT_GOAL := help

.PHONY: help install dev test test-cov lint format typecheck docker-test build pre-commit clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*##"}{printf "  %-20s %s\n", $$1, $$2}'

install: ## Install dev dependencies + pre-commit hooks
	pip install -e ".[dev]"
	pre-commit install

dev: install ## Alias for install (no separate dev server)

test: ## Run unit tests
	pytest tests/ --tb=short

test-cov: ## Run tests with coverage
	pytest tests/ --cov=django_pytest --cov-report=term-missing --cov-report=xml

lint: ## Run ruff linter
	ruff check django_pytest tests

format: ## Auto-format code
	ruff format django_pytest tests

typecheck: ## Run mypy type checking
	mypy django_pytest

docker-test: ## Run tests in Docker (CI-compatible)
	docker build -f Dockerfile.test -t django-pytest-test .
	docker run --rm django-pytest-test

build: ## Build wheel distribution package
	python -m build

pre-commit: ## Run all pre-commit checks
	pre-commit run --all-files

clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage build dist *.egg-info 2>/dev/null || true
