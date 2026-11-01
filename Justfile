# Install in editable mode
install:
    uv pip install -e .

# Install development dependencies
install-dev:
    uv sync --all-extras

# Run all tests
test:
    uv run pytest -v --no-cov

# Run all tests with coverage
test-cov:
    uv run pytest --cov=src --cov-report=html --cov-report=term

# Run linting checks (ruff)
lint:
    uv run ruff check src tests

# Format all Python files (ruff)
format:
    uv run ruff format src tests

# Type check all Python files (ty)
type:
    uv run ty check src tests

# Check all Python files (ruff + ty)
check: lint format type

# Run all pre-commit hooks
pre:
    uv run prek run --all-files

# Pre-release build & test
release:
    uv run python scripts/release.py

# Clean up temporary files, caches, and artifacts
clean:
    uv run python scripts/clean.py
