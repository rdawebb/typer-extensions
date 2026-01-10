"""Script for Justfile help generation"""

HELP_TEXT = """
Available Development Recipes - typer-aliases
=============================================

Setup:
  just install              Install Python dependencies
  just install-dev          Install development dependencies

Testing:
  just test                 Run all tests
  just test-cov             Run all tests with coverage report

Code Quality:
  just lint                 Run linting checks (ruff)
  just format               Format code (ruff)
  just type                 Run type checking (ty)
  just check                Run all checks
  just pre                  Run all pre-commit checks

Maintenance:
  just clean                Remove build artifacts and cache
  just release              Build & validate new release candidate

Use 'just <recipe>' to execute a specific recipe
"""


def print_help():
    print(HELP_TEXT)


if __name__ == "__main__":
    print_help()
