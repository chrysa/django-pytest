# makefile-tier: lib
.DEFAULT_GOAL := help

MATRIX_PYTHON ?= 3.13 3.14
MATRIX_DJANGO ?= 5.2 6.0

.PHONY: help install dev test test-cov lint format typecheck docker-test docker-test-matrix build pre-commit clean

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
	ruff check src/django_pytest tests

format: ## Auto-format code
	ruff format src/django_pytest tests

typecheck: ## Run mypy type checking
	mypy src/django_pytest

docker-test: ## Run tests in Docker (CI-compatible)
	docker build -f Dockerfile.test -t django-pytest-test .
	docker run --rm django-pytest-test

docker-test-matrix: ## Run tests in Docker across Python x Django (override MATRIX_PYTHON / MATRIX_DJANGO)
	@fail=0; for py in $(MATRIX_PYTHON); do for dj in $(MATRIX_DJANGO); do \
		echo "=== Python $$py / Django $$dj ==="; \
		rm -rf coverage.xml; touch coverage.xml; \
		docker build -q -f Dockerfile.test --build-arg PYTHON_VERSION=$$py --build-arg DJANGO_VERSION=$$dj -t django-pytest-test:$$py-$$dj . >/dev/null \
		&& docker run --rm -v "$(PWD)/coverage.xml:/app/coverage.xml" django-pytest-test:$$py-$$dj || fail=1; \
	done; done; exit $$fail

build: ## Build wheel distribution package
	python -m build

pre-commit: ## Run all pre-commit checks
	pre-commit run --all-files

clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage build dist *.egg-info 2>/dev/null || true

.PHONY: ci
ci: lint typecheck test  ## CI: run all checks (lint + typecheck + test)
