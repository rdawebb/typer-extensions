[![CI](https://github.com/rdawebb/typer-extensions/workflows/test/badge.svg)](https://github.com/rdawebb/typer-extensions/actions)
[![codecov](https://codecov.io/gh/rdawebb/typer-extensions/branch/main/graph/badge.svg?token=51D0ZPM7Y0)](https://codecov.io/gh/rdawebb/typer-extensions)
[![PyPI](https://img.shields.io/pypi/v/typer-extensions.svg)](https://pypi.org/project/typer-extensions/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# typer-extensions

**Command aliases for Typer CLI applications with grouped help text display**


## Overview

[Typer](https://typer.tiangolo.com/) is great, but it could be even better!

`typer-extensions` extends Typer to provide simple drop-in support for command aliases. Instead of duplicating commands, hiding commands, or maintaining wrapper functions, define aliases directly and have them displayed cleanly in help text.

**100% backwards compatible with Typer & existing Typer apps!**

### The Problem

Standard Typer requires duplicating or hiding commands to create aliases:

```python
from typer import Typer

app = Typer()

@app.command()
def list_items():
    """List all items."""
    print("Listing...")

# Registered as separate command, hidden in help
@app.command("ls", hidden=True)
def ls_items():
    list_items()

@app.command("l")("list")  # Duplicate!
```

**Help output:**
```
Commands:
  list      List all items.
  l         List all items.
```

**Issues:**
- Code duplication
- Help text shows commands & aliases separately
- Hidden 'aliases' not shown in help text
- Maintenance burden

### The Solution

With `typer-extensions`:

```python
from typer_extensions import ExtendedTyper

app = ExtendedTyper()

@app.command("list", aliases=["ls", "l"])
def list_items():
    """List all items."""
    print("Listing...")
```

**Help output:**
```
Commands:
  list (ls, l)  List all items.
```

**All work identically:**
```bash
app list
app ls
app l
```

---

## Features

✨ **Decorator-based alias registration** - Clean, intuitive syntax

🔧 **Programmatic API** - Dynamic alias management at runtime

📋 **Grouped help display** - Aliases shown with their primary command

⚙️ **Highly configurable** - Customise format, separators, truncation

🎯 **Type-safe** - Full type hints and editor support

🔄 **Fully backwards compatible** - Works with all Typer/Click features and existing Typer apps

✅ **Shell completion ready** - Alias support doesn't interfere with existing shell completion

🧪 **Well-tested** - Tested on Python 3.9-3.14 with 100% test coverage

---

## Installation

```bash
pip install typer-extensions
```

> [!NOTE]
> **Requirements:**
> - Python 3.9+
> - typer >= 0.9.0 (recommend installing the latest version)
> - click >= 8.0.0

---

## Quick Start

### Basic Usage

```python
from typer_extensions import ExtendedTyper

app = ExtendedTyper()

@app.command("list", aliases=["ls", "l"])
def list_items():
    """List all items."""
    print("Listing items...")

@app.command("delete", aliases=["rm", "remove"])
def delete_item(name: str):
    """Delete an item."""
    print(f"Deleting {name}")

if __name__ == "__main__":
    app()
```

**Run it:**
```bash
$ python app.py --help
Commands:
  list (ls, l)         List all items.
  delete (rm, remove)  Delete an item.

$ python app.py ls
Listing items...

$ python app.py rm test.txt
Deleting test.txt
```

> [!TIP]
> **Want to learn more?** Check the [API Reference](docs/API_REFERENCE.md) for detailed configuration options, or see the [User Guide](docs/USER_GUIDE.md) for patterns and best practices.

### Drop-in Compatibility

Have an existing Typer project? Add alias support without changing your code:

```python
# Before (regular Typer)
from typer import Typer
app = Typer()

# After (with typer-extensions)
from typer_extensions import ExtendedTyper
app = ExtendedTyper()

# That's it! Everything else stays the same.
# Existing commands, shell completion and help text configuration still work exactly as before.
```

Once migrated, you can add aliases to new commands using `@app.command(aliases=[])`, or to existing commands using the programmatic API.

> [!TIP]
> See [Migration Guide](docs/MIGRATION.md) for detailed migration strategies and patterns.

### Advanced Features

**Programmatic alias management:**
```python
# Add aliases dynamically
app.add_alias("list", "dir")

# Remove aliases
app.remove_alias("dir")

# Query aliases
aliases = app.get_aliases("list")  # ["ls", "l"]
```

**Custom help formatting:**
```python
app = ExtendedTyper(
    alias_display_format="[{aliases}]",   # Use brackets
    alias_separator=" | ",                # Pipe separator
    max_aliases_inline=2,                 # Show max 2, then "+N more"
)
```

**Configuration-based aliases:**
```python
# Load aliases from config
config = {"list": ["ls", "l", "dir"]}
for cmd, aliases in config.items():
    for alias in aliases:
        app.add_alias(cmd, alias)
```

---

## Documentation

📚 **[User Guide](docs/USER_GUIDE.md)** - Tutorials and common patterns

📖 **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation

🔄 **[Migration Guide](docs/MIGRATION.md)** - Migrating from standard Typer

---

## Examples

All examples are in the [`examples/`](examples/) directory:

- **[basic_usage.py](examples/basic_usage.py)** - Simple CLI with aliases
- **[advanced_usage.py](examples/advanced_usage.py)** - Git-like CLI with options
- **[programmatic_usage.py](examples/programmatic_usage.py)** - Dynamic alias management
- **[help_formatting.py](examples/help_formatting.py)** - Customising help display
- **[argument_option_usage.py](examples/argument_option_usage.py)** - Using Typer's Argument & Option

**Run any example:**
```bash
python examples/basic_usage.py --help
python examples/basic_usage.py ls
```

---

## Real-World Use Cases

### Git-like CLI
```python
@app.command("checkout", aliases=["co"])
def checkout(branch: str):
    """Switch branches."""
    ...

@app.command("status", aliases=["st"])
def status():
    """Show status."""
    ...
```

### Package Manager
```python
@app.command("install", aliases=["i", "add"])
def install(package: str):
    """Install a package."""
    ...

@app.command("remove", aliases=["rm", "uninstall"])
def remove(package: str):
    """Remove a package."""
    ...
```

### Cross-Platform Commands
```python
@app.command("list")
def list_files():
    """List files."""
    ...

# Add platform-specific aliases
if platform.system() == "Windows":
    app.add_alias("list", "dir")
else:
    app.add_alias("list", "ls")
```

---

## API Overview

### Decorator Registration
```python
@app.command(name, aliases=[...])
```

### Programmatic Registration
```python
app.add_command(func, name, aliases=[...])
```

### Alias Management
```python
app.add_alias(command, alias)            # Add alias
app.remove_alias(alias) → bool           # Remove alias
app.get_aliases(command) → list          # Query aliases
app.list_commands() → dict               # All mappings
```

### Configuration
```python
ExtendedTyper(
    alias_case_sensitive=None,           # Case-sensitive (default True, matching Typer)
    show_aliases_in_help=True,           # Display aliases in help
    alias_display_format="({aliases})",  # Display format
    alias_separator=", ",                # Between aliases
    max_num_aliases=3,                   # Before truncation
)
```

---

## Development

### Setup

**Standard setup with pip:**

```bash
git clone https://github.com/rdawebb/typer-extensions.git
cd typer-extensions
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

**Or with uv (recommended):**

```bash
git clone https://github.com/rdawebb/typer-extensions.git
cd typer-extensions
uv sync --all-extras
source .venv/bin/activate
```

**Quick commands with justfile:**

If you have [just](https://github.com/casey/just) installed (included in `[dev]`), common tasks are available:

```bash
just test          # Run tests
just lint          # Run linter
just format        # Format code
just type          # Check type safety
just test-cov      # Full test suite with coverage
just help          # List all available commands
```

> [!NOTE]
> If you prefer to use `just` without the dev setup, you can install it globally via `pip install rust-just` or your system package manager.

> [!TIP]
> See `Justfile` for all available commands.

### Testing

**With justfile (recommended):**

```bash
just check       # Run linting, formatting, and type checks
just test        # Run tests
just test-cov    # Run tests with coverage report
just pre         # Full pre-commit check (all checks + tests)
```

**Or with direct commands:**

```bash
pytest                   # Run all tests
pytest --cov             # With coverage
pytest -v                # Verbose output
ruff check .             # Lint
ruff format .            # Format
ty check src/            # Type check
```

### Contributing

Contributions are welcome! Please open an issue, ask a question, or submit a pull request.

---

## Project Status

**Current Version:** 0.2.1 (Beta)

✅ **Core Features Complete:**
- Alias registration (decorator + programmatic)
- Help text formatting
- Dynamic alias management
- Full test coverage

🚧 **In Development:**
- Dynamic config file loading with import/export
- Shell completion enhancement and typo suggestions
- Shared & chained subcommand aliases
- Performance optimisations

📋 **Planned Features:**
- Documentation site
- Per-alias help text
- Dataclass, Pydantic & Attrs support
- Custom themes and help text formatting
- Argument & Option customisation

> [!NOTE]
> See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## Why typer-extensions?

**For Users:**
- ⚡ Faster workflows with short aliases
- 🎯 Familiar commands (git-like shortcuts)
- 📖 Clear help text showing all options

**For Developers:**
- 🧹 DRY - no code duplication
- 🔧 Flexible - static or dynamic aliases
- 🎨 Customisable - match your style
- ✅ Tested - reliable, stable, and type-safe

**Compared to Alternatives:**
- **Plain Typer:** Requires command duplication or hiding
- **click-aliases:** Click-specific, no Typer integration
- **Custom solutions:** Reinventing the wheel

---

## Related Projects

- **[Typer](https://typer.tiangolo.com/)** - The CLI framework this extends
- **[Click](https://click.palletsprojects.com/)** - The underlying library
- **[Rich](https://rich.readthedocs.io/)** - Beautiful terminal formatting (used by Typer)

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

Built on the excellent [Typer](https://typer.tiangolo.com/) framework by Sebastián Ramírez.

Inspired by Git's command aliasing and various CLI tools that make shortcuts feel natural.

---

## Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/rdawebb/typer-extensions/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/rdawebb/typer-extensions/discussions)
- 📧 **Contact:** Create an issue for questions

---

## Links

- **GitHub:** https://github.com/rdawebb/typer-extensions
- **PyPI:** https://pypi.org/project/typer-extensions/
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---
