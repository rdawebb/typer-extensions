help:
  uv run python scripts/just_help.py

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

type:
  uv run ty check src tests

check:
  uv run ruff format src tests
  uv run ruff check src tests
  uv run ty check src tests

pre:
  uv run prek run --all-files

release:
  @which python3 > /dev/null && python3 scripts/release.py || python scripts/release.py

clean:
  @which python3 > /dev/null && uv run python3 scripts/clean.py || uv run python scripts/clean.py
