# Migration Guide

Guide for migrating from plain Typer to typer-extensions.

---

## Table of Contents

1. [Why Migrate?](#why-migrate)
2. [Before You Start](#before-you-start)
3. [Migration Steps](#migration-steps)
4. [Migration Patterns](#migration-patterns)
5. [Breaking Changes](#breaking-changes)
6. [Rollback Plan](#rollback-plan)

---

## Why Migrate?

### Benefits of typer-extensions

**Before (Plain Typer):**
- Duplicate commands for aliases
- Cluttered help text
- More code to maintain
- Inconsistent alias management

**After (typer-extensions):**
- Single command definition
- Clean, grouped help text
- Less code, easier maintenance
- Powerful alias management

### When to Migrate

✅ **Good candidates:**
- CLI tools with command shortcuts
- Apps mimicking Git/NPM/etc conventions
- Tools with platform-specific aliases
- Projects with user-customizable commands

⚠️ **May not need migration:**
- Simple CLIs with few commands
- Apps with no aliases
- Projects where duplication is intentional

---

## Before You Start

### Prerequisites

1. **Understand your current setup**
   - List all commands and their aliases
   - Identify duplicate command functions
   - Note any custom help formatting

2. **Install typer-extensions**
   ```bash
   pip install typer-extensions
   ```

3. **Backup your code**
   ```bash
   git commit -am "Before typer-extensions migration"
   ```

### Compatibility

- **Python:** 3.9+ (same as Typer)
- **Typer:** >= 0.9.0
- **Click:** >= 8.0.0

✅ **Full backward compatibility:** typer-extensions extends Typer, doesn't replace it.

---

## Migration Steps

### Step 1: Import ExtendedTyper

**Before:**
```python
import typer

app = typer.Typer()
```

**After:**
```python
from typer_extensions import ExtendedTyper

app = ExtendedTyper()
```

> [!NOTE]
> This is the only required change! Your existing commands still work.

> [!TIP]
> **About case sensitivity:** If your existing Typer app uses `context_settings={"case_sensitive": False}`, typer-extensions will automatically sync the alias matching to be case-insensitive as well. No additional configuration needed!

```python
# Your existing case-insensitive Typer app
app = ExtendedTyper(context_settings={"case_sensitive": False})
# ✓ Both commands and aliases are case-insensitive
```

### Step 2: Identify Duplicate Commands

Find command duplicates in your code:

**Before:**
```python
@app.command()
def list_items():
    """List all items."""
    print("Listing...")

@app.command()
def ls():
    """List all items."""
    print("Listing...")

@app.command()
def l():
    """List all items."""
    print("Listing...")
```

### Step 3: Consolidate to Single Command

**After:**
```python
@app.command("list", aliases=["ls", "l"])
def list_items():
    """List all items."""
    print("Listing...")
```

**Result:**
- 3 functions → 1 function
- 3 help entries → 1 entry (with aliases shown)
- Same functionality

### Step 4: Test

```bash
# Test primary command
python app.py list

# Test aliases
python app.py ls
python app.py l

# Test help
python app.py --help
```

### Step 5: Repeat

Migrate remaining commands one at a time.

---

## Migration Patterns

### Pattern 1: Simple Duplicates

**Before:**
```python
@app.command()
def delete(name: str):
    """Delete an item."""
    remove_item(name)

@app.command()
def rm(name: str):
    """Delete an item."""
    remove_item(name)

@app.command()
def remove(name: str):
    """Delete an item."""
    remove_item(name)
```

**After:**
```python
@app.command("delete", aliases=["rm", "remove"])
def delete_item(name: str):
    """Delete an item."""
    remove_item(name)
```

### Pattern 2: Wrapper Functions

**Before:**
```python
def _list_impl():
    """Actual implementation."""
    print("Listing...")

@app.command()
def list():
    """List items."""
    _list_impl()

@app.command()
def ls():
    """List items."""
    _list_impl()
```

**After:**
```python
@app.command("list", aliases=["ls"])
def list_items():
    """List items."""
    print("Listing...")
```

### Pattern 3: Different Function Names

**Before:**
```python
@app.command(name="list")
def list_items():
    """List items."""
    pass

@app.command(name="ls")
def list_short():
    """List items."""
    pass
```

**After:**
```python
@app.command("list", aliases=["ls"])
def list_items():
    """List items."""
    pass
```

### Pattern 4: Commands with Options

**Before:**
```python
import typer

@app.command()
def list(verbose: bool = typer.Option(False, "-v")):
    """List items."""
    pass

@app.command()
def ls(verbose: bool = typer.Option(False, "-v")):
    """List items."""
    pass
```

**After:**
```python
@app.command("list", aliases=["ls"])
def list_items(verbose: bool = app.Option(False, "-v")):
    """List items."""
    pass
```

### Pattern 5: Platform-Specific Commands

**Before:**
```python
import platform

@app.command()
def list():
    """List items."""
    pass

if platform.system() == "Windows":
    @app.command()
    def dir():
        """List items."""
        pass
else:
    @app.command()
    def ls():
        """List items."""
        pass
```

**After:**
```python
import platform

@app.command("list")
def list_items():
    """List items."""
    pass

# Add platform-specific aliases
if platform.system() == "Windows":
    app.add_alias("list", "dir")
else:
    app.add_alias("list", "ls")
```

---

## Migration Checklist

> [!TIP]
> **Migrate one command group at a time!** Don't try to migrate everything at once. This lets you test each group independently and makes it easier to spot issues.

Use this checklist for each command group:

- [ ] Identify all duplicate/wrapper functions
- [ ] Choose primary command name
- [ ] List all aliases
- [ ] Replace duplicates with single `@command`
- [ ] Remove duplicate functions
- [ ] Test primary command
- [ ] Test each alias
- [ ] Check help text
- [ ] Update tests
- [ ] Update documentation

---

## Breaking Changes

> [!IMPORTANT]
> **Good news:** typer-extensions has NO breaking changes!

### Fully Compatible

✅ **Standard Typer commands still work:**
```python
from typer_extensions import ExtendedTyper

app = ExtendedTyper()

# Standard Typer command (no aliases)
@app.command()
def hello():
    """Say hello."""
    pass

# Works exactly like standard Typer
```

✅ **All Typer features work:**
- Arguments and Options
- Callbacks
- Context
- Command groups
- Everything else

✅ **Can mix both styles:**
```python
# Aliased command
@app.command("list", aliases=["ls"])
def list_items():
    pass

# Standard command
@app.command()
def create():
    pass

# Both work perfectly together
```

### API Changes

**Only additions, no changes:**
- `@app.command()` - Still works (unchanged)
- `@app.command()` - NEW (added)
- `app.add_alias()` - NEW (added)
- All other methods - NEW (added)

---

## Rollback Plan

If you need to rollback:

### Option 1: Keep typer-extensions, Use Standard Commands

```python
from typer_extensions import ExtendedTyper

app = ExtendedTyper()

# Just use standard @app.command()
# Ignore alias features
@app.command()
def list():
    pass
```

### Option 2: Switch Back to Plain Typer

```python
# Change this:
from typer_extensions import ExtendedTyper
app = ExtendedTyper()

# To this:
import typer
app = typer.Typer()

# Remove @command decorators
# Use standard @app.command()
```

### Option 3: Gradual Migration

Migrate one command at a time:

```python
from typer_extensions import ExtendedTyper

app = ExtendedTyper()

# Migrated command
@app.command("list", aliases=["ls"])
def list_items():
    pass

# Not yet migrated (still works fine)
@app.command()
def delete():
    pass

@app.command()
def rm():
    pass
```

---

## Complete Example

### Before: Plain Typer

```python
import typer

app = typer.Typer()

@app.command()
def list():
    """List all items."""
    print("Listing items...")

@app.command()
def ls():
    """List all items."""
    print("Listing items...")

@app.command()
def l():
    """List all items."""
    print("Listing items...")

@app.command()
def delete(name: str):
    """Delete an item."""
    print(f"Deleting {name}")

@app.command()
def rm(name: str):
    """Delete an item."""
    print(f"Deleting {name}")

@app.command()
def remove(name: str):
    """Delete an item."""
    print(f"Deleting {name}")

if __name__ == "__main__":
    app()
```

**Help output:**
```
Commands:
  delete     Delete an item.
  l          List all items.
  list       List all items.
  ls         List all items.
  rm         Delete an item.
  remove     Delete an item.
```

**Issues:**
- 6 functions for 2 commands
- Cluttered help (6 entries)
- Maintenance burden

### After: typer-extensions

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

**Help output:**
```
Commands:
  list     (ls, l)          List all items.
  delete   (rm, remove)     Delete an item.
```

**Benefits:**
- 2 functions (not 6)
- Clean help (2 entries with aliases)
- Easy to maintain

---

## Testing After Migration

### Test Suite Updates

**Before:**
```python
def test_list_command(cli_runner):
    result = cli_runner.invoke(app, ["list"])
    assert "Listing" in result.output

def test_ls_command(cli_runner):
    result = cli_runner.invoke(app, ["ls"])
    assert "Listing" in result.output

def test_l_command(cli_runner):
    result = cli_runner.invoke(app, ["l"])
    assert "Listing" in result.output
```

**After (more concise):**
```python
@pytest.mark.parametrize("cmd", ["list", "ls", "l"])
def test_list_commands_with_aliases(cli_runner, cmd):
    result = cli_runner.invoke(app, [cmd])
    assert "Listing" in result.output
```

---

## Common Migration Issues

### Issue 1: Function Name Conflicts

**Problem:**
```python
# Can't have two functions named "list"
@app.command(name="list")
def list():
    pass

@app.command(name="ls")
def list():  # NameError!
    pass
```

**Solution:**
```python
@app.command("list", aliases=["ls"])
def list_items():  # One function, different name
    pass
```

### Issue 2: Different Help Text

**Problem:**
```python
@app.command()
def list():
    """List items."""
    pass

@app.command()
def ls():
    """Quick list."""  # Different help!
    pass
```

**Solution:**
Choose one help text or consolidate:
```python
@app.command("list", aliases=["ls"])
def list_items():
    """List items (use 'ls' for quick access)."""
    pass
```

---

## Gradual Migration Strategy

> [!IMPORTANT]
> **Don't migrate everything at once!** A phased approach lets you test each group independently, catch issues early, and maintain a working codebase throughout the migration.

**Phase 1:** Install and test
```python
from typer_extensions import ExtendedTyper
app = ExtendedTyper()
# Keep existing commands unchanged
```

**Phase 2:** Migrate one command group
```python
# Migrate list/ls/l first
@app.command("list", aliases=["ls", "l"])
def list_items():
    pass

# Keep others unchanged
@app.command()
def delete():
    pass
```

**Phase 3:** Migrate remaining commands
```python
# Migrate all command groups
@app.command("list", aliases=["ls", "l"])
def list_items():
    pass

@app.command("delete", aliases=["rm", "remove"])
def delete_item(name: str):
    pass
```

**Phase 4:** Clean up and optimize
- Remove old functions
- Update tests
- Update documentation

---

## Need Help?

- **[User Guide](USER_GUIDE.md)** - Complete usage guide
- **[API Reference](API_REFERENCE.md)** - Full API docs
- **[Examples](../examples/)** - Working examples
- **[Issues](https://github.com/rdawebb/typer-extensions/issues)** - Report problems
- **[Discussions](https://github.com/rdawebb/typer-extensions/discussions)** - Ask questions
