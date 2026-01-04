.PHONY: help install test test-cov clean lint format

help:
	@echo "Photidy Development Commands"
	@echo "============================"
	@echo ""
	@echo "Setup:"
	@echo "  make install              Install Python dependencies"
	@echo "  make install-dev          Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test                  Run all tests"
	@echo "  make test-cov              Run all tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint                 Run linting and formatting checks (ruff)"
	@echo "  make format               Format code with ruff"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean                Remove build artifacts and cache"
	@echo ""
	@echo "Use 'make <command>' to execute a specific command."
	@echo ""

install:
	uv pip install -e .

install-dev:
	uv sync --all-extras

test:
	uv run pytest -v --no-cov

test-cov:
	uv run pytest --cov=src --cov-report=html --cov-report=term

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests
	uv run ruff check --fix src tests

clean:
	uv run python scripts/clean.py
