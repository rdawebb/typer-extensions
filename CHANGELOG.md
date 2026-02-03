# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Changed

- **BREAKING:** Renamed `@app.command_with_aliases()` decorator to `@app.command()` for simpler, more intuitive API
- **BREAKING:** Renamed `add_aliased_command()` decorator to `add_command()` for consitency with standard Typer API
- Updated all tests and examples to use new method names
- Added `wcwidth` dependency for accurate Unicode and multi-byte character width calculations in help text formatting
- Refactored `format_commands_section()` to `format_commands_with_aliases()` with signature returning `(formatted_commands, max_width)` tuple
- Renamed `list_commands()` to `list_commands_with_aliases()` for API clarity
- Improved help text alignment and padding when displaying commands with aliases
- Enhanced test fixtures with better ANSI escape code handling and new `assert_formatted_command` assertion
- Consolidated pre-commit hook configuration into single local repo section

### Added

- New `_rich_utils.py` module providing drop-in replacements for Typer's rich_utils functions
  - Enhanced help text formatting with support for command aliases
  - Graceful fallback when Rich library is unavailable
  - Support for `TYPER_USE_RICH` environment variable to disable Rich entirely
  - Proper handling of deprecated commands, multiline help, and complex formatting scenarios
- New `_import_hook.py` module implementing dynamic import interception
  - `TyperRichUtilsInterceptor` class for intercepting `typer.rich_utils` imports
  - Dynamic module replacement before Typer initialisation
  - Robust error handling and fallback mechanisms
- New `_patch.py` module for monkey-patching Typer's rich utilities
  - Version checking for Typer compatibility
  - Patch state tracking and logging
  - Environment variable-based opt-out (`TYPER_EXTENSIONS_RICH=0`)
  - Graceful degradation if Typer already imported
- 13 new comprehensive test files for enhanced functionality:
  - `test_rich_utils.py`: Core Rich utilities functionality
  - `test_rich_utils_coverage.py`: Edge cases with Rich enabled
  - `test_rich_utils_edge_cases.py`: Complex formatting scenarios
  - `test_rich_utils_fallbacks.py`: Fallback paths when Rich disabled
  - `test_rich_utils_more_edge_cases.py`: Additional edge case coverage
  - `test_import_hook.py`: Import hook interception logic
  - `test_patch.py`: Monkey-patching application and state
  - `test_patch_edge_cases.py`: Patching edge cases and error scenarios
  - `test_init_coverage.py`: Module initialization coverage
  - `test_init_error_handling.py`: Import error handling
  - `test_init_module.py`: Module loading and setup
  - `test_init_module_edge_cases.py`: Initialisation edge cases
  - `test_rich_utils_integration.py`: Integration tests with Rich and Typer
- Enhanced `test_smoke.py` with `__getattr__` fallback and `Context` export tests
- Complete API Reference documentation (`docs/API_REFERENCE.md`)
- Comprehensive User Guide with patterns and best practices (`docs/USER_GUIDE.md`)
- Migration guide for switching from standard Typer (`docs/MIGRATION.md`)
- `Context` class exported from core module for better Typer compatibility
- `__getattr__` fallback in `__init__.py` for dynamic Typer attribute access
- Enhanced example files with new method names and improved code patterns
- PyPI release validation script (scripts/pypi.py)
- TestPyPI release validation script (scripts/testpypi.py)

### Changed

- Updated existing test files for compatibility with new Rich integration system
- Enhanced integration tests in `test_basic.py`, `test_decorator_usage.py`, and `test_programmatic_usage.py`
- Improved `tests/conftest.py` with enhanced fixtures for Rich integration testing
- Refactored `scripts/release.py` to use module-level constants (TEST_ENV, DIST_DIR)
- Updated `scripts/release.py` to use `uv venv` instead of `python3 -m venv`
- Improved type hints throughout codebase


## [0.2.2] - 2026/01/15

### Added

- Exposed common Typer utility functions as static methods on `ExtendedTyper`
  (echo, secho, prompt, confirm, style, etc.) for convenience
- Comprehensive unit and integration tests for exposed utility functions with both primary commands and aliases

### Changed

- Changed project name to `typer-extensions` to reflect change in scope beyond purely command aliases
- Renamed `AliasedTyper` class to `ExtendedTyper` for improved clarity
- Renamed `AliasedGroup` class to `ExtendedGroup` for consistency
- Changed internal parameter `aliased_typer` to `extended_typer` throughout codebase for consistency with class names
- Updated all package paths from `typer_aliases` to `typer_extensions`
- Updated CI/CD workflow (Codecov action upgraded from v3 to v5)

### Deprecated
- Package name `typer-aliases` is deprecated in favor of `typer-extensions`
- Class name `AliasedTyper` is deprecated in favor of `ExtendedTyper`


## [0.2.1] - 2026/01/11

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
- Format utilities module (`src/typer_extensions/format.py`):
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


[Unreleased]: https://github.com/rdawebb/typer-extensions/compare/v0.2.2...HEAD
[0.2.2]: https://github.com/rdawebb/typer-extensions/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/rdawebb/typer-extensions/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/rdawebb/typer-extensions/compare/v0.1.0a1...v0.2.0
[0.1.0]: https://github.com/rdawebb/typer-extensions/releases/tag/v0.1.0a1
