# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [2.0.1] - 2026/01/11

### Added

- Pre-release validation script (`scripts/release.py`) for build, test, and package verification
- `release` recipe in Justfile for automated pre-release validation workflow
- Exposed `Argument` and `Option` as static methods on `AliasedTyper` for convenience
- `examples/argument_option_usage.py` demonstrating use of Arguments and Options with aliased commands
- Comprehensive unit tests for Typer's Argument and Option compatibility
- Integration tests verifying Arguments and Options work identically with primary commands and aliases

### Changed

- Improved `clean.py` script with build artifact management
- Added `.test-env` to `.gitignore` for isolated test environments
- Fixed README.md filename casing in `pyproject.toml`
- Improved docstrings in `examples/` files

### Build

- `py.typed` marker file for PEP 561 type hinting support


## [0.2.0] - 2026/01/10

### Added

#### Help Text Formatting
- Customisable alias display in help output via Rich formatting:
  - `alias_display_format` parameter for custom format strings
  - `alias_separator` parameter to customise alias list separator
  - `max_num_aliases` parameter to control truncation with "+N more" indicator
- Format utilities module (`src/typer_aliases/format.py`):
  - `truncate_aliases()` for alias list truncation
  - `format_command_with_aliases()` for individual command formatting
  - `format_commands_section()` for bulk command formatting
- `examples/help_formatting_usage.py` demonstrating all formatting options

#### Programmatic API
- Dynamic command and alias management methods:
  - `add_aliased_command()` for programmatically registering commands with aliases
  - `add_alias()` for dynamically adding aliases to existing commands
  - `remove_alias()` for removing aliases
  - `get_aliases()` for retrieving aliases for a specific command
  - `list_commands_with_aliases()` for querying all commands and their aliases

#### Testing & Examples
- Comprehensive integration tests for help formatting
- Unit tests for format utilities with edge case coverage
- Integration tests for programmatic API usage
- Example scripts demonstrating both decorator and programmatic approaches:
  - `basic_usage.py`: Basic decorator syntax and patterns
  - `advanced_usage.py`: Advanced patterns with Typer options, context, and deprecated commands
  - `help_formatting_usage.py`: Help formatting customisation scenarios

#### Developer
- Replaced Makefile with Justfile for task automation
- Helper scripts for development workflows (`just_help.py`, `clean.py`)

### Changed

- `AliasedTyper` initialisation now defaults to Rich markup mode
- `AliasedTyper` now syncs with Typer's case_sensitive setting unless explicitly overridden to prevent mismatches
- `AliasedGroup` now inherits from `TyperGroup`
- `AliasedGroup.get_command()` refactored for cleaner multi-command app handling
- Test structure reorganised for better maintainability

### Fixed

- Proper handling of `rich_markup_mode` and `rich_help_panel` parameters in group creation
- Removed redundant tracking of removed aliases
- Fixed test assertions to use `clean_output` fixture for reliable cross-platform comparisons
- Python 3.9 compatibility: Replaced PEP 604 union syntax (`|`) with `Union` for type hints


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


[Unreleased]: https://github.com/rdawebb/typer-aliases/compare/v0.1.0a1...HEAD
[0.2.1]: https://github.com/rdawebb/typer-aliases/compare/v0.1.0a1...v0.2.1
[0.2.0]: https://github.com/rdawebb/typer-aliases/compare/v0.1.0a1...v0.2.0
[0.1.0]: https://github.com/rdawebb/typer-aliases/releases/tag/v0.1.0a1
