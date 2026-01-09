# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added

- Programmatic API methods for dynamic command and alias management:
  - `add_aliased_command()` for programmatically registering commands with aliases
  - `add_alias()` for dynamically adding aliases to existing commands
  - `remove_alias()` for removing aliases with proper tracking
  - `get_aliases()` for retrieving aliases for a specific command
  - `list_commands_with_aliases()` for querying all commands and their aliases
- Alias removal tracking to prevent removed aliases from being invoked
- Comprehensive integration tests for programmatic API usage
- Unit tests for all programmatic API methods
- `clean_output` pytest fixture for consistent test assertions across environments
- Example scripts in the `examples/` directory demonstrating both decorator and programmatic approaches:
  - `basic_usage.py`: Basic decorator syntax and command registration patterns
  - `advanced_usage.py`: Advanced decorator patterns with Typer options, context, and deprecated commands
  - `progammatic_usage.py`: Programmatic API usage, dynamic alias management, configuration loading, and plugin simulation
- Justfile as modern replacement for Makefile with task automation
- Helper scripts for development workflows (just_help.py, clean.py)


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


[Unreleased]: https://github.com/rdawebb/typer-aliases/compare/v0.1.0-alpha...HEAD)
[0.1.0]: https://github.com/rdawebb/typer-aliases/releases/tag/v0.1.0-alpha)
