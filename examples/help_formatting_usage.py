"""Help formatting customisation examples for typer-aliases

This example demonstrates how to customise the display of aliases in help text. Run with '--help' to see how aliases are displayed in the help text with different formatting options.
"""

from typer_aliases import AliasedTyper

print("=" * 70)
print("EXAMPLE 1: Default formatting")
print("=" * 70)
print("Run: python help_formatting.py default --help\n")

# Default: parentheses, comma separator, max 3 displayed inline
app_default = AliasedTyper()


@app_default.command_with_aliases("list", aliases=["ls", "l"])
def list_default():
    """List items with default alias display."""
    print("Listing...")


@app_default.command_with_aliases("delete", aliases=["rm", "remove", "del"])
def delete_default():
    """Delete items with default alias display."""
    print("Deleting...")


print("=" * 70)
print("EXAMPLE 2: Custom format with brackets")
print("=" * 70)
print("Run: python help_formatting.py brackets --help\n")

# Custom: brackets instead of parentheses
app_brackets = AliasedTyper(alias_display_format="[{aliases}]")


@app_brackets.command_with_aliases("list", aliases=["ls", "l"])
def list_brackets():
    """List items with bracketed aliases."""
    print("Listing...")


@app_brackets.command_with_aliases("delete", aliases=["rm"])
def delete_brackets():
    """Delete items with bracketed aliases."""
    print("Deleting...")


print("=" * 70)
print("EXAMPLE 3: Custom separator")
print("=" * 70)
print("Run: python help_formatting.py separator --help\n")

# Custom: pipe separator
app_separator = AliasedTyper(alias_separator=" | ")


@app_separator.command_with_aliases("list", aliases=["ls", "l", "dir"])
def list_separator():
    """List items with pipe-separated aliases."""
    print("Listing...")


@app_separator.command_with_aliases("delete", aliases=["rm", "remove"])
def delete_separator():
    """Delete items with pipe-separated aliases."""
    print("Deleting...")


print("=" * 70)
print("EXAMPLE 4: Truncation with many aliases")
print("=" * 70)
print("Run: python help_formatting.py truncate --help\n")

# Truncation: max 2 displayed inline
app_truncate = AliasedTyper(max_num_aliases=2)


@app_truncate.command_with_aliases("list", aliases=["ls", "l", "dir", "ll", "la"])
def list_truncate():
    """List items with truncated alias display."""
    print("Listing...")


@app_truncate.command_with_aliases("delete", aliases=["rm", "remove", "del", "erase"])
def delete_truncate():
    """Delete items with truncated alias display."""
    print("Deleting...")


print("=" * 70)
print("EXAMPLE 5: Aliases hidden in help")
print("=" * 70)
print("Run: python help_formatting.py hidden --help\n")

# Hidden: don't show aliases in help
app_hidden = AliasedTyper(show_aliases_in_help=False)


@app_hidden.command_with_aliases("list", aliases=["ls", "l"])
def list_hidden():
    """List items (aliases not shown in help)."""
    print("Listing...")


@app_hidden.command_with_aliases("delete", aliases=["rm"])
def delete_hidden():
    """Delete items (aliases not shown in help)."""
    print("Deleting...")


print("=" * 70)
print("EXAMPLE 6: Combined custom options")
print("=" * 70)
print("Run: python help_formatting.py custom --help\n")

# Combined: brackets, pipe separator, max 2 displayed inline
app_custom = AliasedTyper(
    alias_display_format="[{aliases}]", alias_separator=" / ", max_num_aliases=2
)


@app_custom.command_with_aliases("list", aliases=["ls", "l", "dir", "ll"])
def list_custom():
    """List items with fully customised display."""
    print("Listing...")


@app_custom.command_with_aliases("delete", aliases=["rm", "remove"])
def delete_custom():
    """Delete items with fully customised display."""
    print("Deleting...")


# Create main app that delegates to examples
main_app = AliasedTyper()
main_app.add_typer(app_default, name="default")
main_app.add_typer(app_brackets, name="brackets")
main_app.add_typer(app_separator, name="separator")
main_app.add_typer(app_truncate, name="truncate")
main_app.add_typer(app_hidden, name="hidden")
main_app.add_typer(app_custom, name="custom")


if __name__ == "__main__":
    print("\nRun any example above to see help formatting in action!")
    main_app()
