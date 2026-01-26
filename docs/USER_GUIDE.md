# User Guide

Complete guide to using typer-extensions effectively.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Concepts](#basic-concepts)
3. [Common Patterns](#common-patterns)
4. [Configuration](#configuration)
5. [Advanced Usage](#advanced-usage)
6. [Best Practices](#best-practices)

---

## Getting Started

### Installation

```bash
pip install typer-extensions
```

### Your First Aliased Command

Create a file `app.py`:

```python
from typer_extensions import ExtendedTyper

app = ExtendedTyper()

@app.command("hello", aliases=["hi", "hey"])
def greet(name: str = "World"):
    """Greet someone."""
    print(f"Hello, {name}!")

if __name__ == "__main__":
    app()
```

Run it:

```bash
$ python app.py --help
Commands:
  hello (hi, hey)  Greet someone.

$ python app.py hello Alice
Hello, Alice!

$ python app.py hi Bob
Hello, Bob!

$ python app.py hey Charlie
Hello, Charlie!
```

---

## Basic Concepts

### Commands vs Aliases

**Primary command:** The canonical name shown in help text.

**Aliases:** Alternative names that invoke the same command.

```python
@app.command("list", aliases=["ls", "l"])
def list_items():
    """List items."""
    pass

# "list" is the primary command
# "ls" and "l" are aliases
# All three do the same thing
```

### How Aliases Work

1. User types a command name or alias
2. `typer-extensions` resolves it to the primary command
3. The primary command function executes
4. Help text shows primary + aliases grouped

> [!NOTE]
> **Key point:** There's only ONE function, accessed multiple ways.

---

## Common Patterns

### Pattern 1: Git-like CLI

Mimic Git's short command syntax:

```python
app = ExtendedTyper()

@app.command("checkout", aliases=["co"])
def checkout(branch: str):
    """Switch to a branch."""
    print(f"Switched to {branch}")

@app.command("commit", aliases=["ci"])
def commit(message: str):
    """Commit changes."""
    print(f"Committed: {message}")

@app.command("status", aliases=["st"])
def status():
    """Show status."""
    print("On branch main")
```

**Usage:**
```bash
$ app co develop     # Short form
$ app checkout main  # Long form
```

### Pattern 2: Package Manager

Multiple aliases for common operations:

```python
@app.command("install", aliases=["i", "add", "get"])
def install(package: str):
    """Install a package."""
    print(f"Installing {package}")

@app.command("remove", aliases=["rm", "uninstall", "del"])
def remove(package: str):
    """Remove a package."""
    print(f"Removing {package}")

@app.command("list", aliases=["ls", "l", "show"])
def list_packages():
    """List installed packages."""
    print("Installed packages: ...")
```

### Pattern 3: Cross-Platform Commands

Platform-specific aliases:

```python
import platform

app = ExtendedTyper()

@app.command("list")
def list_files():
    """List files."""
    # Implementation

# Add platform-appropriate aliases
if platform.system() == "Windows":
    app.add_alias("list", "dir")
else:
    app.add_alias("list", "ls")
```

### Pattern 4: Backwards Compatibility

Keep old command names as aliases:

```python
# New command name
@app.command("remove", aliases=["delete", "del"])
def remove_item(name: str):
    """Remove an item."""
    print(f"Removed {name}")

# Users of old "delete" command still work
# But "remove" is the canonical name
```

### Pattern 5: User Customization

Load aliases from configuration:

```python
import json

app = ExtendedTyper()

# Define commands
@app.command("list")
def list_items():
    pass

@app.command("delete")
def delete_item():
    pass

# Load user's custom aliases
try:
    with open("aliases.json") as f:
        config = json.load(f)
        for cmd, aliases in config.get("aliases", {}).items():
            for alias in aliases:
                app.add_alias(cmd, alias)
except FileNotFoundError:
    pass  # Use defaults
```

**aliases.json:**
```json
{
  "aliases": {
    "list": ["ls", "l", "show"],
    "delete": ["rm", "remove"]
  }
}
```

---

## Configuration

### Display Format

Control how aliases appear in help text.

**Default (parentheses):**
```python
app = ExtendedTyper()  # Default: "({aliases})"
# Shows: "list (ls, l)"
```

**Brackets:**
```python
app = ExtendedTyper(alias_display_format="[{aliases}]")
# Shows: "list [ls, l]"
```

**Pipe separator:**
```python
app = ExtendedTyper(alias_display_format="| {aliases}")
# Shows: "list | ls, l"
```

**Custom:**
```python
app = ExtendedTyper(alias_display_format="<{aliases}>")
# Shows: "list <ls, l>"
```

### Separator

Control how multiple aliases are joined.

**Comma (default):**
```python
app = ExtendedTyper(alias_separator=", ")
# Shows: "list (ls, l, dir)"
```

**Pipe:**
```python
app = ExtendedTyper(alias_separator=" | ")
# Shows: "list (ls | l | dir)"
```

**Slash:**
```python
app = ExtendedTyper(alias_separator=" / ")
# Shows: "list (ls / l / dir)"
```

### Truncation

Limit displayed aliases for long lists.

**Default (3 inline):**
```python
app = ExtendedTyper(max_num_aliases=3)
# 4 aliases: "list (ls, l, dir, +1 more)"
# 3 aliases: "list (ls, l, dir)"
```

**More inline:**
```python
app = ExtendedTyper(max_num_aliases=5)
# Shows up to 5 before truncating
```

**Fewer inline:**
```python
app = ExtendedTyper(max_num_aliases=1)
# 3 aliases: "list (ls, +2 more)"
```

### Case Sensitivity

Control whether alias matching is case-sensitive.

**Case-sensitive (default):**
```python
app = ExtendedTyper(alias_case_sensitive=True)
app.add_alias("list", "ls")
# "ls" works, "LS" doesn't
```

**Case-insensitive:**
```python
app = ExtendedTyper(alias_case_sensitive=False)
app.add_alias("list", "ls")
# "ls", "LS", "Ls", "lS" all work
```

**Default behavior (None):**
```python
app = ExtendedTyper()  # alias_case_sensitive defaults to None

# When None, typer-extensions syncs with Typer's case_sensitive setting
# from context_settings (defaults to True)

# To match Typer's behavior:
app = ExtendedTyper(
    context_settings={"case_sensitive": False},
    # alias_case_sensitive will automatically be False
)

# Or explicitly set both:
app = ExtendedTyper(
    context_settings={"case_sensitive": False},
    alias_case_sensitive=False
)
```

**Key difference:**
- `context_settings.case_sensitive` controls Typer's command matching
- `alias_case_sensitive` controls alias matching
- When `alias_case_sensitive=None` (default), they stay in sync

### Hide Aliases in Help

Don't show aliases in help text.

```python
app = ExtendedTyper(show_aliases_in_help=False)

@app.command("list", aliases=["ls", "l"])
def list_items():
    """List items."""
    pass

# Help shows: "list  List items"
# (no aliases shown, but they still work)
```

---

## Advanced Usage

> [!TIP]
> **Use dynamic alias management when:** Loading aliases from config files, user preferences, or making decisions at runtime. Use decorators for static aliases defined at development time.

### Dynamic Alias Management

Add/remove aliases at runtime:

```python
app = ExtendedTyper()

@app.command("list")
def list_items():
    print("Listing...")

# Add aliases dynamically
app.add_alias("list", "ls")
app.add_alias("list", "l")

# Remove if needed
app.remove_alias("l")

# Query current aliases
aliases = app.get_aliases("list")  # ["ls"]
```

### Programmatic Command Registration

Register commands without decorators:

```python
app = ExtendedTyper()

def list_items():
    print("Listing...")

def delete_item(name: str):
    print(f"Deleting {name}")

# Register programmatically
app.add_command(list_items, "list", aliases=["ls"])
app.add_command(delete_item, "delete", aliases=["rm"])
```

### Querying Alias Mappings

Get complete overview of aliases:

```python
# Get all aliased commands with aliases
mapping = app.list_commands_with_aliases()
print(mapping)
# {"list": ["ls", "l"], "delete": ["rm", "remove"]}

# Get aliases for specific command
list_aliases = app.get_aliases("list")
print(list_aliases)  # ["ls", "l"]
```

### Mixed Registration Methods

Combine decorator and programmatic approaches:

```python
app = ExtendedTyper()

# Decorator method
@app.command("list", aliases=["ls"])
def list_items():
    pass

# Programmatic method
def delete_item():
    pass
app.add_command(delete_item, "delete", aliases=["rm"])

# Add more aliases dynamically
app.add_alias("list", "l")
app.add_alias("delete", "remove")
```

### Working with Typer Features

Aliases work with all Typer features:

**Arguments:**
```python
@app.command("greet", aliases=["hi"])
def greet(name: str = app.Argument(...)):
    """Greet someone."""
    print(f"Hello, {name}!")

# Both work:
# app greet Alice
# app hi Bob
```

**Options:**
```python
@app.command("list", aliases=["ls"])
def list_items(
    verbose: bool = app.Option(False, "--verbose", "-v")
):
    """List items."""
    if verbose:
        print("Verbose listing...")
    else:
        print("Listing...")

# app ls -v
# app list --verbose
```

**Context:**
```python
from typer_extensions import Context

@app.command("info", aliases=["i"])
def show_info(ctx: Context):
    """Show info."""
    print(f"Command: {ctx.info_name}")

# Works with aliases
```

---

## Best Practices

### Choose Meaningful Aliases

**Good:**
```python
@app.command("checkout", aliases=["co"])  # Common Git convention
@app.command("list", aliases=["ls"])      # Unix convention
```

**Avoid:**
```python
@app.command("checkout", aliases=["x", "zz"])  # Cryptic
```

### Limit Number of Aliases

**Good:**
```python
@app.command("list", aliases=["ls", "l"])  # 2-3 aliases
```

**Avoid:**
```python
@app.command(
    "list",
    aliases=["ls", "l", "dir", "ll", "la", "show", "display", "view"]
)  # Too many
```

### Be Consistent

**Good (consistent pattern):**
```python
@app.command("checkout", aliases=["co"])
@app.command("commit", aliases=["ci"])
@app.command("status", aliases=["st"])
# All follow two-letter pattern
```

**Avoid (inconsistent):**
```python
@app.command("checkout", aliases=["co", "chk", "switch"])
@app.command("commit", aliases=["c"])
@app.command("status", aliases=["stat", "s"])
# Mixed patterns
```

### Document Aliases

Include aliases in command help:

```python
@app.command("list", aliases=["ls", "l"])
def list_items():
    """List all items.

    Aliases: ls, l (shown in help automatically)

    Examples:
        app list
        app ls
        app l
    """
    pass
```

### Consider Your Audience

**For Unix users:**
```python
app.add_alias("list", "ls")
app.add_alias("remove", "rm")
```

**For Windows users:**
```python
app.add_alias("list", "dir")
app.add_alias("remove", "del")
```

**For both:**
```python
@app.command("list", aliases=["ls", "dir"])
```

### Test Aliases

> [!IMPORTANT]
> **Always test aliases!** Include alias invocations in your test suite to ensure they work as expected and don't break during refactoring.

Include aliases in your tests:

```python
def test_list_via_primary_name(cli_runner):
    result = cli_runner.invoke(app, ["list"])
    assert result.exit_code == 0

def test_list_via_alias(cli_runner):
    result = cli_runner.invoke(app, ["ls"])
    assert result.exit_code == 0
```

---

## Troubleshooting

### Alias Doesn't Work

> [!WARNING]
> **Common issue:** An alias will conflict if it matches an existing command name or another alias. Always check the error message, it will tell you exactly what's conflicting!

**Check if alias was registered:**
```python
aliases = app.get_aliases("list")
print(aliases)  # Should include your alias
```

**Check for conflicts:**
```python
# Will raise ValueError if conflict
try:
    app.add_alias("list", "rm")  # Conflicts with delete
except ValueError as e:
    print(e)
```

### Help Text Not Showing Aliases

**Check configuration:**
```python
# Ensure show_aliases_in_help is True (default)
app = ExtendedTyper(show_aliases_in_help=True)
```

**Check if command has aliases:**
```python
mapping = app.list_commands_with_aliases()
print(mapping)  # Should include your command
```

### Case Sensitivity Issues

**If aliases work differently than expected:**
```python
# Check case sensitivity setting
app = ExtendedTyper(alias_case_sensitive=False)
# Now "ls", "LS", "Ls" all work
```

---

## Next Steps

- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Best Practices](BEST_PRACTICES.md)** - Detailed recommendations
- **[Migration Guide](MIGRATION.md)** - Migrating from plain Typer
- **[Examples](../examples/)** - More code examples

---

## Need Help?

- 📖 Check the [API Reference](API_REFERENCE.md)
- 🐛 [Report an issue](https://github.com/rdawebb/typer-extensions/issues)
- 💬 [Start a discussion](https://github.com/rdawebb/typer-extensions/discussions)
