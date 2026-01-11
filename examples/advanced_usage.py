"""Advanced usage examples for typer-aliases

This example demonstrates various decorator patterns and features with a dummy Git-like CLI tool. Run with '--help' to see how aliases are displayed in the help text.
"""

import typer
from typer_aliases import AliasedTyper

# Case-insensitive aliases
app = AliasedTyper(
    alias_case_sensitive=False, help="A Git-like CLI tool with command aliases"
)


# Example 1: Command with multiple aliases
@app.command_with_aliases("checkout", aliases=["co", "switch"])
def checkout(branch: str):
    """Checkout a branch."""
    print(f"Switched to branch '{branch}'")


# Example 2: Command with Typer options
@app.command_with_aliases("commit", aliases=["ci"])
def commit(
    message: str = typer.Option(..., "--message", "-m", help="Commit message"),
    amend: bool = typer.Option(False, "--amend", help="Amend previous commit"),
):
    """Commit changes."""
    if amend:
        print(f"Amending previous commit: {message}")
    else:
        print(f"Creating new commit: {message}")


# Example 3: Command with arguments and options
@app.command_with_aliases("branch", aliases=["br"])
def branch(
    name: str = typer.Argument(None, help="Branch name"),
    delete: bool = typer.Option(False, "--delete", "-d", help="Delete branch"),
    list_all: bool = typer.Option(False, "--all", "-a", help="List all branches"),
):
    """Manage branches."""
    if list_all:
        print("Branches:")
        print("* main")
        print("  develop")
        print("  feature-x")
    elif delete and name:
        print(f"Deleted branch '{name}'")
    elif name:
        print(f"Created branch '{name}'")
    else:
        print("Current branch: main")


# Example 4: Inferred name with aliases
@app.command_with_aliases(aliases=["st"])
def status():
    """Show repository status."""
    print("On branch main")
    print("Your branch is up to date with 'origin/main'")
    print("")
    print("nothing to commit, working tree clean")


# Example 5: No aliases (equivalent to @app.command())
@app.command_with_aliases("log")
def show_log(
    count: int = typer.Option(10, "--count", "-n", help="Number of commits"),
):
    """Show commit history."""
    print(f"Showing last {count} commits:")
    for i in range(count):
        print(f"  commit {i + 1}: Example commit message")


# Example 6: Bare decorator (no parentheses)
@app.command_with_aliases
def help():
    """Show help information."""
    print("Git-like CLI Help")
    print("=================")
    print("Use --help with any command for more information")


# Example 7: Command with context
@app.command_with_aliases("config", aliases=["cfg"])
def config(
    ctx: typer.Context,
    key: str = typer.Argument(None),
    value: str = typer.Argument(None),
):
    """Get or set configuration."""
    if key and value:
        print(f"Set {key} = {value}")
    elif key:
        print(f"{key} = example_value")
    else:
        print("Configuration:")
        print("  user.name = John Doe")
        print("  user.email = john@example.com")


# Example 8: Deprecated command
@app.command_with_aliases(
    "old-command",
    aliases=["old", "legacy"],
    deprecated=True,
    help="This command is deprecated. Use 'new-command' instead.",
)
def old_command():
    """Old deprecated command."""
    print("Warning: This command is deprecated!")


if __name__ == "__main__":
    app()
