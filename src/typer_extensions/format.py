"""Help text formatting utilities"""

from collections.abc import Sequence

from wcwidth import wcswidth


def truncate_aliases(
    aliases: list[str],
    max_num: int,
    separator: str = ", ",
) -> str:
    """Truncate the list of aliases to a maximum number, join with a separator, and truncate with '+ N more' if needed

    Args:
        aliases: The list of aliases to truncate
        max_num: The maximum number of aliases to display
        separator: The separator to use when joining aliases, defaults to ', '

    Returns:
        The formatted string of aliases, truncated if necessary
    """
    if not aliases:
        return ""

    # Handle negative max_num edge case
    max_num = max(max_num, 0)

    if len(aliases) <= max_num:
        return separator.join(aliases)

    visible = aliases[:max_num]
    hidden = len(aliases) - max_num

    return f"{separator.join(visible)}{separator if visible else ''}+{hidden} more"


def calculate_width(text: str) -> int:
    """Calculate the display width of a string

    Args:
        text: The text to measure

    Returns:
        The display width of the text
    """
    width = wcswidth(text)
    return width if width >= 0 else len(text)


def format_commands_with_aliases(
    names: Sequence[str],
    command_aliases: dict[str, list[str]],
    *,
    display_format: str = "({aliases})",
    max_num: int = 3,
    separator: str = ", ",
) -> list[str]:
    """Format command names with their aliases, padded into aligned columns

    Args:
        names: The command names to format
        command_aliases: A dictionary mapping command names to their aliases
        display_format: The format string for displaying aliases
        max_num: The maximum number of aliases to display
        separator: The separator to use between aliases

    Returns:
        The formatted names, in the same order as names
    """
    alias_displays = {
        name: display_format.format(
            aliases=truncate_aliases(command_aliases[name], max_num, separator)
        )
        for name in names
        if name in command_aliases
    }
    if not alias_displays:
        return list(names)

    def pad(text: str, width: int) -> str:
        return text + " " * (width - calculate_width(text))

    name_width = max(map(calculate_width, names))
    alias_width = max(map(calculate_width, alias_displays.values()))

    return [
        f"{pad(name, name_width)}   {pad(alias_displays[name], alias_width)}"
        if name in alias_displays
        else name
        for name in names
    ]
