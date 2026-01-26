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
    return wcswidth(text) if wcswidth(text) > 0 else len(text)


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
    formatted_commands: list[tuple[str, Union[str, None]]] = []

    max_cmd_length = max(
        (calculate_width(cmd_name) for cmd_name, _ in commands),
        default=0,
    )
    max_aliases_length = 0
    max_formatted_length = 0

    for cmd_name in command_aliases:
        aliases_str = truncate_aliases(
            command_aliases[cmd_name],
            max_num=max_num,
            separator=separator,
        )
        aliases_display = display_format.format(aliases=aliases_str)
        display_length = calculate_width(aliases_display)
        max_aliases_length = max(max_aliases_length, display_length)

    for cmd_name, help_text in commands:
        if cmd_name in command_aliases:
            aliases = command_aliases[cmd_name]
            aliases_str = truncate_aliases(
                aliases,
                max_num=max_num,
                separator=separator,
            )
            aliases_display = display_format.format(aliases=aliases_str)

            cmd_display_length = calculate_width(cmd_name)
            alias_display_length = calculate_width(aliases_display)

            padded_cmd = cmd_name + " " * (max_cmd_length - cmd_display_length)
            padded_aliases = aliases_display + " " * (
                max_aliases_length - alias_display_length
            )

            formatted_cmd = f"{padded_cmd}   {padded_aliases}"
            formatted_cmd_length = calculate_width(formatted_cmd)
            max_formatted_length = max(max_formatted_length, formatted_cmd_length)
        else:
            formatted_cmd = cmd_name

        formatted_commands.append((formatted_cmd, help_text))

    return formatted_commands, max_formatted_length
