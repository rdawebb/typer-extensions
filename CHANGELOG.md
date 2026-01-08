# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.1.0] - 2026/01/08

### Added

- `AliasedTyper` class extending Typer with command alias support
- `AliasedGroup` custom Click Group for handling command aliases
- `command_with_aliases` decorator for convenient command registration with aliases
- `HasName` protocol for improved type safety
- Alias registration with configurable case sensitivity
- Alias resolution with proper conflict detection
- Comprehensive unit tests covering:
  - Alias registration and validation
  - Alias resolution logic
  - Multi-command scenario handling
  - Single-command app compatibility
  - Decorator usage and integration
- CI/CD pipeline with GitHub Actions for testing across Python 3.10-3.14
- Pre-commit hooks for code quality (linting, formatting, type checking, syntax validation)
- Initial project structure with Makefile and development tooling
