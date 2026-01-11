"""Programmatic API usage examples for typer-aliases

This example demonstrates dynamic command and alias registration without decorators. Run with '--help' to see how the available commands and their aliases are displayed in the help text.
"""

from typer_aliases import AliasedTyper

app = AliasedTyper()


# Example 1: Programmatic command registration
def list_items():
    """List all items."""
    print("Listing all items...")
    print("- Item 1")
    print("- Item 2")


def delete_item(name: str):
    """Delete an item."""
    print(f"Deleting {name}...")


def create_item(name: str, description: str = ""):
    """Create a new item."""
    print(f"Creating {name}...")
    if description:
        print(f"Description: {description}")


# Register commands programmatically
app.add_aliased_command(list_items, "list", aliases=["ls", "l"])
app.add_aliased_command(delete_item, "delete", aliases=["rm", "remove"])
app.add_aliased_command(create_item, "create", aliases=["new"])


# Example 2: Adding aliases to existing commands
@app.command("status")
def show_status():
    """Show current status."""
    print("Status: OK")
    print("All systems operational")


# Add aliases after registration
app.add_alias("status", "st")
app.add_alias("status", "info")


# Example 3: Dynamic alias management based on "configuration"
def simulate_load_config():
    """Simulate loading aliases from a configuration file."""
    return {
        "list": ["dir"],  # Add Windows-style alias
        "delete": ["del"],  # Add DOS-style alias
    }


# Load additional aliases from "config"
config = simulate_load_config()
for command, aliases in config.items():
    for alias in aliases:
        try:
            app.add_alias(command, alias)
            print(f"Added alias '{alias}' for command '{command}'")
        except ValueError as e:
            print(f"Warning: {e}")


# Example 4: Query and display current aliases
@app.command("show-aliases")
def show_all_aliases():
    """Show all commands and their aliases."""
    print("\nConfigured Command Aliases")
    print("=" * 50)

    aliases_map = app.list_commands_with_aliases()

    if not aliases_map:
        print("No aliases configured")
        return

    for cmd, aliases in sorted(aliases_map.items()):
        aliases_str = ", ".join(aliases)
        print(f"  {cmd:15} → {aliases_str}")


# Example 5: Plugin simulation - dynamically add commands
def register_plugins():
    """Simulate a plugin system by adding commands dynamically."""

    # Plugin 1: Backup functionality
    def backup_data():
        """Backup all data."""
        print("Backing up data...")
        print("Backup complete!")

    app.add_aliased_command(backup_data, "backup", aliases=["bak", "save"])

    # Plugin 2: Export functionality
    def export_data(format: str = "json"):
        """Export data."""
        print(f"Exporting data as {format}...")

    app.add_aliased_command(export_data, "export", aliases=["exp"])

    print("Plugins registered: backup, export")


# Register plugins on startup
register_plugins()


# Example 6: Conditional alias management
def setup_user_preferences():
    """Setup user-specific alias preferences."""
    # Simulate user preference: prefers short aliases
    user_prefers_short = True

    if user_prefers_short:
        # Add ultra-short aliases
        try:
            app.add_alias("list", "i")  # 'i' for 'items'
            app.add_alias("create", "c")
            app.add_alias("delete", "d")
            print("Short aliases enabled")
        except ValueError:
            print("Some short aliases already in use")


setup_user_preferences()


# Example 7: Runtime alias modification
@app.command("alias")
def manage_alias(command: str, alias: str, remove: bool = False):
    """Add or remove an alias at runtime."""
    if remove:
        removed = app.remove_alias(alias)
        if removed:
            print(f"✓ Removed alias '{alias}'")
        else:
            print(f"✗ Alias '{alias}' not found")
    else:
        try:
            app.add_alias(command, alias)
            print(f"✓ Added alias '{alias}' for command '{command}'")
        except ValueError as e:
            print(f"✗ Error: {e}")


# Example 8: Query aliases for a specific command
@app.command("which-aliases")
def which_aliases(command: str):
    """Show aliases for a specific command."""
    aliases = app.get_aliases(command)

    if aliases:
        aliases_str = ", ".join(aliases)
        print(f"Command '{command}' has aliases: {aliases_str}")
    else:
        print(f"Command '{command}' has no aliases")


if __name__ == "__main__":
    print("\nProgrammatic API Example")
    print("=" * 50)
    print("Run 'python programmatic_usage.py show-aliases' to see all aliases")
    print("=" * 50)
    print()
    app()
