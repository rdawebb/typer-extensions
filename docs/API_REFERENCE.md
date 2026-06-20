# API Reference

Complete API documentation for typer-extensions.

---

## Table of Contents 

- [ExtendedTyper Class](#ExtendedTyper-class)
- [Decorator Methods](#decorator-methods)
- [Programmatic Registration](#programmatic-registration)
- [Sub-Applications](#sub-applications)
- [Alias Management](#alias-management)
- [Query Methods](#query-methods)
- [Configuration Options](#configuration-options)
- [Formatter Functions](#formatter-functions)

---

## ExtendedTyper Class

The main class that extends `typer.Typer` with alias support.

```python
from typer_extensions import ExtendedTyper

app = ExtendedTyper(
    alias_case_sensitive=True,
    show_aliases_in_help=True,
    alias_display_format="({aliases})",
    alias_separator=", ",
    max_num_aliases=3,
    # ... all standard Typer parameters ...
)
```

### Constructor Parameters

#### `alias_case_sensitive: Optional[bool] = None`

Whether alias matching is case-sensitive. When `None` (default), syncs with Typer's `context_settings.case_sensitive` (defaults to `True`).

**Default behavior (None):**
```python
# When not specified, follows Typer's case sensitivity setting
app = ExtendedTyper()
# Aliases are case-sensitive (same as Typer's default)

# Match Typer's case-insensitive setting
app = ExtendedTyper(context_settings={"case_sensitive": False})
# Aliases are also case-insensitive (automatically synced)
```

**Explicit True (case-sensitive):**
```python
app = ExtendedTyper(alias_case_sensitive=True)
app.add_alias("list", "ls")
# "ls" works, "LS" doesn't
```

**Explicit False (case-insensitive):**
```python
app = ExtendedTyper(alias_case_sensitive=False)
app.add_alias("list", "ls")
# "ls", "LS", "Ls", "lS" all work
```

**Override Typer's setting:**
```python
# If you want aliases case-insensitive but Typer commands case-sensitive
app = ExtendedTyper(
    context_settings={"case_sensitive": True},
    alias_case_sensitive=False
)
# Commands: case-sensitive
# Aliases: case-insensitive
```

#### `show_aliases_in_help: bool = True`

Whether to display aliases in help text.

**Examples:**
```python
# Show aliases (default)
app = ExtendedTyper(show_aliases_in_help=True)
# Help shows: "list (ls, l)  List items"

# Hide aliases
app = ExtendedTyper(show_aliases_in_help=False)
# Help shows: "list  List items"
```

#### `alias_display_format: str = "({aliases})"`

Format string for displaying aliases. Must include `{aliases}` placeholder.

**Examples:**
```python
# Parentheses (default)
app = ExtendedTyper(alias_display_format="({aliases})")
# Shows: "list (ls, l)"

# Brackets
app = ExtendedTyper(alias_display_format="[{aliases}]")
# Shows: "list [ls, l]"

# Pipe
app = ExtendedTyper(alias_display_format="| {aliases}")
# Shows: "list | ls, l"
```

#### `alias_separator: str = ", "`

String used to separate multiple aliases.

**Examples:**
```python
# Comma (default)
app = ExtendedTyper(alias_separator=", ")
# Shows: "list (ls, l, dir)"

# Pipe
app = ExtendedTyper(alias_separator=" | ")
# Shows: "list (ls | l | dir)"

# Slash
app = ExtendedTyper(alias_separator=" / ")
# Shows: "list (ls / l / dir)"
```

#### `max_num_aliases: int = 3`

Maximum number of aliases to show before truncating with "+N more".

**Examples:**
```python
# Default: show 3
app = ExtendedTyper(max_num_aliases=3)
# 4 aliases: "list (ls, l, dir, +1 more)"

# Show more
app = ExtendedTyper(max_num_aliases=5)
# 6 aliases: "list (a, b, c, d, e, +1 more)"

# Show fewer
app = ExtendedTyper(max_num_aliases=2)
# 4 aliases: "list (ls, l, +2 more)"
```

---

## Decorator Methods

### `@app.command()`

Decorator for registering commands with aliases.

```python
@app.command(
    name: Optional[str] = None,
    *,
    aliases: Optional[list[str]] = None,
    **kwargs: Any
) -> Callable[[Callable[..., Any]], Command]
```

#### Parameters

- **`name`** (str, optional): Command name. If not provided, inferred from function name.
- **`aliases`** (list[str], optional): List of aliases for the command.
- **`**kwargs`**: Additional Typer command arguments (help, context_settings, deprecated, etc.)

#### Returns

Decorator function or Command object (if used without parentheses).

#### Raises

- **`ValueError`**: If any alias conflicts with existing commands or aliases.

#### Examples

**Explicit name with aliases:**
```python
@app.command("list", aliases=["ls", "l"])
def list_items():
    """List all items."""
    print("Listing...")
```

**Inferred name:**
```python
@app.command(aliases=["ls", "l"])
def list():
    """List all items."""
    print("Listing...")
```

**No aliases:**
```python
@app.command("list")
def list_items():
    """List all items."""
    print("Listing...")
```

**Bare decorator (no parentheses):**
```python
@app.command
def list():
    """List all items."""
    print("Listing...")
```

**With Typer options:**
```python
@app.command(
    "list",
    aliases=["ls"],
    help="List all items",
    deprecated=True
)
def list_items():
    print("Listing...")
```

---

## Programmatic Registration

### `app.add_command()`

Register a command with aliases programmatically.

```python
app.add_command(
    func: Callable[..., Any],
    name: Optional[str] = None,
    aliases: Optional[list[str]] = None,
    **kwargs: Any
) -> Command
```

#### Parameters

- **`func`**: The command function.
- **`name`** (str, optional): Command name. If not provided, inferred from function name.
- **`aliases`** (list[str], optional): List of aliases.
- **`**kwargs`**: Additional Typer command arguments.

#### Returns

Click Command object for the registered command.

#### Raises

- **`ValueError`**: If any alias conflicts with existing commands or aliases.

#### Examples

**Basic usage:**
```python
def list_items():
    print("Listing...")

app.add_command(list_items, "list", aliases=["ls", "l"])
```

**Inferred name:**
```python
def list():
    print("Listing...")

app.add_command(list, aliases=["ls"])
# Uses function name "list"
```

**With options:**
```python
def list_items(verbose: bool = False):
    print("Listing...")

app.add_command(
    list_items,
    "list",
    aliases=["ls"],
    help="List all items"
)
```

---

## Sub-Applications

### `app.add_typer()`

Mount a sub-application (a nested `Typer`/`ExtendedTyper` instance) as a command group, with optional aliases for the group name.

```python
app.add_typer(
    typer_instance: typer.Typer,
    *,
    aliases: Optional[list[str]] = None,
    name: Optional[str] = None,
    **kwargs: Any
) -> None
```

#### Parameters

- **`typer_instance`**: The sub-application to mount.
- **`aliases`** (list[str], optional, keyword-only): Aliases for the sub-app's group name.
- **`name`** (str, optional): The CLI name for the group. See the name resolution rule below.
- **`**kwargs`**: All other arguments are passed through to Typer's `add_typer()` (`callback`, `help`, `invoke_without_command`, `rich_help_panel`, etc.).

#### Name resolution

When `aliases` are provided, the group name must be resolvable:

1. If `name` is given explicitly, it is used.
2. Otherwise, the name is inferred from the sub-app's registered callback.
3. If neither is available, a `ValueError` is raised.

> [!IMPORTANT]
> **`name` is effectively required** when aliasing a sub-app that has no registered callback to infer a name from. Always pass `name=` when using `aliases`.

#### Alias namespace

Sub-app aliases share the **same namespace** as command aliases. A sub-app alias that collides with an existing command or alias raises `ValueError`. Aliases resolve only at the sub-app boundary, the alias replaces the group name, while the nested commands keep their own names.

#### Returns

`None` (matches Typer's `add_typer()`).

#### Raises

- **`ValueError`**: If the name cannot be resolved, or an alias conflicts with an existing command/alias.

#### Examples

**Sub-app with an alias:**
```python
remote_app = ExtendedTyper(help="Manage remote repositories")

@remote_app.command("add")
def remote_add(name: str, url: str):
    """Add a remote."""
    print(f"Added remote '{name}' at {url}")

@remote_app.command("remove", aliases=["rm"])
def remote_remove(name: str):
    """Remove a remote."""
    print(f"Removed remote '{name}'")

app.add_typer(remote_app, name="remote", aliases=["rem"])
# "app remote add ...", "app rem add ..." both work
# "app remote rm ...", "app rem rm ..." both work (nested alias)
```

The group alias appears in help text just like a command alias:
```
Commands:
  remote (rem)  Manage remote repositories
```

**Inferred name (callback present):**
```python
sub = ExtendedTyper()

@sub.callback()
def config():
    """Manage configuration."""

# Name inferred from the callback as "config"
app.add_typer(sub, aliases=["cfg"])
```

---

## Alias Management

### `app.add_alias()`

Add an alias to an existing command.

```python
app.add_alias(
    command_name: str,
    alias: str
) -> None
```

#### Parameters

- **`command_name`**: The primary command name.
- **`alias`**: The alias to add.

#### Raises

- **`ValueError`**: If command doesn't exist, or alias conflicts with existing commands/aliases.

#### Examples

**Add to existing command:**
```python
@app.command("list")
def list_items():
    pass

app.add_alias("list", "ls")
app.add_alias("list", "l")
# Now "list", "ls", and "l" all work
```

**Add to decorated command:**
```python
@app.command("list", aliases=["ls"])
def list_items():
    pass

app.add_alias("list", "l")
# Now has aliases: ["ls", "l"]
```

**Error handling:**
```python
try:
    app.add_alias("nonexistent", "ne")
except ValueError as e:
    print(f"Error: {e}")
    # Error: Command 'nonexistent' does not exist
```

### `app.remove_alias()`

Remove an alias.

```python
app.remove_alias(
    alias: str
) -> bool
```

#### Parameters

- **`alias`**: The alias to remove.

#### Returns

`True` if alias was removed, `False` if it didn't exist.

#### Examples

**Remove existing alias:**
```python
@app.command("list", aliases=["ls", "l"])
def list_items():
    pass

removed = app.remove_alias("ls")
print(removed)  # True
# Now only "list" and "l" work
```

**Idempotent (safe to call multiple times):**
```python
result1 = app.remove_alias("ls")  # True
result2 = app.remove_alias("ls")  # False (already removed)
```

**Remove non-existent alias:**
```python
removed = app.remove_alias("nonexistent")
print(removed)  # False
```

---

## Query Methods

### `app.get_aliases()`

Get all aliases for a command.

```python
app.get_aliases(
    command_name: str
) -> list[str]
```

#### Parameters

- **`command_name`**: The primary command name.

#### Returns

List of aliases (empty list if none or command doesn't exist). Returns a copy, so modifications don't affect internal state.

#### Examples

**Get aliases:**
```python
@app.command("list", aliases=["ls", "l", "dir"])
def list_items():
    pass

aliases = app.get_aliases("list")
print(aliases)  # ["ls", "l", "dir"]
```

**No aliases:**
```python
@app.command("create")
def create_item():
    pass

aliases = app.get_aliases("create")
print(aliases)  # []
```

**Non-existent command:**
```python
aliases = app.get_aliases("nonexistent")
print(aliases)  # []
```

**Returns copy (immutable):**

> [!NOTE]
> **Safe to modify:** The returned list is a copy, not the internal list. Modifications won't affect the app's alias mappings.

```python
aliases = app.get_aliases("list")
aliases.append("modified")  # Doesn't affect app

original = app.get_aliases("list")
print(original)  # Still ["ls", "l", "dir"]
```

### `app.list_commands_with_aliases()`

Get all aliased commands and their aliases.

```python
app.list_commands_with_aliases() -> dict[str, list[str]]
```

#### Returns

Dictionary mapping command names to their aliases. Only includes commands that have aliases. Returns a deep copy.

#### Examples

**List all:**
```python
@app.command("list", aliases=["ls", "l"])
def list_items():
    pass

@app.command("delete", aliases=["rm"])
def delete_item():
    pass

@app.command("create")
def create_item():
    pass

mapping = app.list_commands_with_aliases()
print(mapping)
# {"list": ["ls", "l"], "delete": ["rm"]}
# Note: "create" excluded (no aliases)
```

**Empty result:**
```python
app = ExtendedTyper()

@app.command("list")
def list_items():
    pass

mapping = app.list_commands_with_aliases()
print(mapping)  # {}
```

---

## Configuration Options

Complete reference for ExtendedTyper configuration.

### Configuration Summary

```python
app = ExtendedTyper(
    # Alias Behavior
    alias_case_sensitive=True,           # bool: Match case exactly

    # Help Display
    show_aliases_in_help=True,           # bool: Show/hide aliases
    alias_display_format="({aliases})",  # str: Wrapper format
    alias_separator=", ",                # str: Between aliases
    max_num_aliases=3,                   # int: Before truncation

    # Standard Typer Options
    name=None,                           # str: Group name
    help=None,                           # str: Help text
    add_completion=True,                 # bool: Shell completion
    # ... all other Typer options ...
)
```

> ![NOTE]
> For all available Typer options, see the [Typer documentation](https://typer.tiangolo.com/)

### Configuration Patterns

**Git-like style:**
```python
app = ExtendedTyper(
    alias_display_format="({aliases})",
    alias_separator=", ",
    max_num_aliases=2
)
# Shows: "checkout (co, sw, +1 more)"
```

**Unix style:**
```python
app = ExtendedTyper(
    alias_display_format="[{aliases}]",
    alias_separator=" | ",
    max_num_aliases=3
)
# Shows: "list [ls | l | dir]"
```

**Minimal style:**
```python
app = ExtendedTyper(
    alias_display_format="| {aliases}",
    max_num_aliases=1
)
# Shows: "list | ls, +2 more"
```

---

## Formatter Functions

Low-level formatting utilities (typically not called directly).

### `format_commands_with_aliases()`

Format a list of commands with their aliases for help display. Returns the formatted command rows and the maximum formatted length (used for column alignment).

```python
from typer_extensions.format import format_commands_with_aliases

formatted, max_len = format_commands_with_aliases(
    commands: list[tuple[str, str | None]],
    command_aliases: dict[str, list[str]],
    *,
    display_format: str = "({aliases})",
    max_num: int = 3,
    separator: str = ", ",
) -> tuple[list[tuple[str, str | None]], int]
```

**Example:**
```python
formatted, _ = format_commands_with_aliases(
    [("list", "List items.")],
    {"list": ["ls", "l"]},
)
print(formatted[0][0])  # "list   (ls, l)"
```

### `truncate_aliases()`

Truncate an alias list to `max_num` and join with the separator, appending "+N more" when there are extras.

```python
from typer_extensions.format import truncate_aliases

truncated = truncate_aliases(
    aliases: list[str],
    max_num: int,
    separator: str = ", ",
) -> str
```

**Example:**
```python
result = truncate_aliases(["a", "b", "c", "d"], max_num=2)
print(result)  # "a, b, +2 more"
```

---

## Type Hints

All public APIs include full type hints:

```python
from typer_extensions import Command, Context
from typing import Callable, Optional, Any

# Example signatures
def command(
    self,
    name: Optional[str] = None,
    *,
    aliases: Optional[list[str]] = None,
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], Command]: ...

def get_aliases(self, command_name: str) -> list[str]: ...

def list_commands_with_aliases(self) -> dict[str, list[str]]: ...
```

---

## Error Reference

### ValueError Exceptions

**Duplicate alias:**
```python
app.add_alias("list", "ls")
app.add_alias("delete", "ls")
# ValueError: Alias 'ls' is already registered for command 'list'
```

**Command not found:**
```python
app.add_alias("nonexistent", "ne")
# ValueError: Command 'nonexistent' does not exist
```

**Self-aliasing:**
```python
app.add_alias("list", "list")
# ValueError: Alias 'list' cannot be the same as command name 'list'
```

### No Exceptions

> [!TIP]
> **Safe to call:** Query and remove operations never raise errors. They return sensible defaults (empty list, False, etc.) when something doesn't exist. This makes defensive programming easier.

These operations don't raise errors:

```python
# Removing non-existent alias
app.remove_alias("nonexistent")  # Returns False, no error

# Querying non-existent command
app.get_aliases("nonexistent")  # Returns [], no error

# Empty alias list
@app.command("list", aliases=[])  # Works fine
```

---

## See Also

- **[User Guide](USER_GUIDE.md)** - Tutorials and patterns
- **[Best Practices](BEST_PRACTICES.md)** - Recommendations
- **[Migration Guide](MIGRATION.md)** - From plain Typer
- **[Examples](../examples/)** - Runnable code examples
