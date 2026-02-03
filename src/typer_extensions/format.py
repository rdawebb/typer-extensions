"""Help text formatting utilities"""

from typing import Union

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
    if max_num < 0:
        max_num = 0

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
    try:
        width = wcswidth(text)
        return width if width >= 0 else len(text)

    except ImportError:
        # wcwidth not available
        return len(text)


def format_commands_with_aliases(
    commands: list[tuple[str, Union[str, None]]],
    command_aliases: dict[str, list[str]],
    *,
    display_format: str = "({aliases})",
    max_num: int = 3,
    separator: str = ", ",
) -> tuple[list[tuple[str, Union[str, None]]], int]:
    """Format a list of commands with their aliases

    Args:
        commands: The list of commands to format
        command_aliases: A dictionary mapping command names to their aliases
        display_format: The format string for displaying aliases
        max_num: The maximum number of aliases to display
        separator: The separator to use between aliases

    Returns:
        Tuple of (formatted_commands, max_formatted_length)
    """
    if not commands:
        return [], 0

    cmd_widths: dict[str, int] = {}
    alias_widths: dict[str, int] = {}
    alias_displays: dict[str, str] = {}
    max_cmd_length = 0
    max_aliases_length = 0

    for cmd_name, _ in commands:
        cmd_width = calculate_width(cmd_name)
        cmd_widths[cmd_name] = cmd_width
        max_cmd_length = max(max_cmd_length, cmd_width)

        if cmd_name in command_aliases:
            aliases_str = truncate_aliases(
                command_aliases[cmd_name],
                max_num=max_num,
                separator=separator,
            )
            aliases_display = display_format.format(aliases=aliases_str)
            alias_displays[cmd_name] = aliases_display
            alias_width = calculate_width(aliases_display)
            alias_widths[cmd_name] = alias_width
            max_aliases_length = max(max_aliases_length, alias_width)

    formatted_cmds: list[tuple[str, Union[str, None]]] = []
    max_formatted_length = 0

    for cmd_name, help_text in commands:
        if cmd_name in command_aliases:
            cmd_width = cmd_widths[cmd_name]
            alias_width = alias_widths[cmd_name]

            padded_cmd = cmd_name + " " * (max_cmd_length - cmd_width)
            aliases_display = alias_displays[cmd_name]
            padded_aliases = aliases_display + " " * (max_aliases_length - alias_width)

            formatted_cmd = f"{padded_cmd}   {padded_aliases}"
            formatted_cmd_length = len(formatted_cmd)
            max_formatted_length = max(max_formatted_length, formatted_cmd_length)
        else:
            formatted_cmd = cmd_name
            formatted_cmd_length = cmd_width
            max_formatted_length = max(max_formatted_length, formatted_cmd_length)

        formatted_cmds.append((formatted_cmd, help_text))

    return formatted_cmds, max_formatted_length
