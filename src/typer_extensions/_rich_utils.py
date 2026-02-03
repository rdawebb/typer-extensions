"""Rich utilities for Typer Extensions.

This module provides drop-in replacements for Typer's rich_utils functions
that provide support for alias formatting and graceful fallbacks.
"""

from __future__ import annotations

import io
import sys
from collections import defaultdict
from gettext import gettext as gt
from os import environ, getenv
from typing import TYPE_CHECKING, Any, Generator, Literal, Optional, Union

import click

if TYPE_CHECKING:
    from rich.columns import Columns
    from rich.console import Console, RenderableType
    from rich.highlighter import RegexHighlighter
    from rich.markdown import Markdown
    from rich.text import Text
    from rich.traceback import Traceback

# Import Typer's DeveloperExceptionConfig for get_traceback
try:
    from typer.models import DeveloperExceptionConfig
except ImportError:  # pragma: no cover
    # Fallback for older Typer versions
    class DeveloperExceptionConfig:
        pass


# Feature flag - set TYPER_USE_RICH=0 to disable Rich entirely
_USE_RICH = environ.get("TYPER_USE_RICH", "1") == "1"


# Constants (re-exported from original rich_utils)
STYLE_OPTION = "bold cyan"
STYLE_SWITCH = "bold green"
STYLE_NEGATIVE_OPTION = "bold magenta"
STYLE_NEGATIVE_SWITCH = "bold red"
STYLE_METAVAR = "bold yellow"
STYLE_METAVAR_SEPARATOR = "dim"
STYLE_USAGE = "yellow"
STYLE_USAGE_COMMAND = "bold"
STYLE_DEPRECATED = "red"
STYLE_DEPRECATED_COMMAND = "dim"
STYLE_HELPTEXT_FIRST_LINE = ""
STYLE_HELPTEXT = "dim"
STYLE_OPTION_HELP = ""
STYLE_OPTION_DEFAULT = "dim"
STYLE_OPTION_ENVVAR = "dim yellow"
STYLE_REQUIRED_SHORT = "red"
STYLE_REQUIRED_LONG = "dim red"
STYLE_OPTIONS_PANEL_BORDER = "dim"
ALIGN_OPTIONS_PANEL: Literal["left", "center", "right"] = "left"
STYLE_OPTIONS_TABLE_SHOW_LINES = False
STYLE_OPTIONS_TABLE_LEADING = 0
STYLE_OPTIONS_TABLE_PAD_EDGE = False
STYLE_OPTIONS_TABLE_PADDING = (0, 1)
STYLE_OPTIONS_TABLE_BOX = None
STYLE_OPTIONS_TABLE_ROW_STYLES = None
STYLE_OPTIONS_TABLE_BORDER_STYLE = None
STYLE_COMMANDS_PANEL_BORDER = "dim"
ALIGN_COMMANDS_PANEL: Literal["left", "center", "right"] = "left"
STYLE_COMMANDS_TABLE_SHOW_LINES = False
STYLE_COMMANDS_TABLE_LEADING = 0
STYLE_COMMANDS_TABLE_PAD_EDGE = False
STYLE_COMMANDS_TABLE_PADDING = (0, 1)
STYLE_COMMANDS_TABLE_BOX = None
STYLE_COMMANDS_TABLE_ROW_STYLES = None
STYLE_COMMANDS_TABLE_BORDER_STYLE = None
STYLE_COMMANDS_TABLE_FIRST_COLUMN = "bold cyan"
STYLE_ERRORS_PANEL_BORDER = "red"
ALIGN_ERRORS_PANEL: Literal["left", "center", "right"] = "left"
STYLE_ERRORS_SUGGESTION = "dim"
STYLE_ABORTED = "red"
_TERMINAL_WIDTH = getenv("TERMINAL_WIDTH")
MAX_WIDTH = int(_TERMINAL_WIDTH) if _TERMINAL_WIDTH else None
COLOR_SYSTEM: Optional[Literal["auto", "standard", "256", "truecolor", "windows"]] = (
    "auto"
)
_TYPER_FORCE_DISABLE_TERMINAL = getenv("_TYPER_FORCE_DISABLE_TERMINAL")
FORCE_TERMINAL = (
    True
    if getenv("GITHUB_ACTIONS") or getenv("FORCE_COLOR") or getenv("PY_COLORS")
    else None
)
if _TYPER_FORCE_DISABLE_TERMINAL:
    FORCE_TERMINAL = False

# Fixed strings
DEPRECATED_STRING = gt("(deprecated) ")
DEFAULT_STRING = gt("[default: {}]")
ENVVAR_STRING = gt("[env var: {}]")
REQUIRED_SHORT_STRING = "*"
REQUIRED_LONG_STRING = gt("[required]")
RANGE_STRING = " [{}]"
ARGUMENTS_PANEL_TITLE = gt("Arguments")
OPTIONS_PANEL_TITLE = gt("Options")
COMMANDS_PANEL_TITLE = gt("Commands")
ERRORS_PANEL_TITLE = gt("Error")
ABORTED_TEXT = gt("Aborted.")
RICH_HELP = gt("Try [blue]'{command_path} {help_option}'[/] for help.")

MARKUP_MODE_MARKDOWN = "markdown"
MARKUP_MODE_RICH = "rich"
_RICH_HELP_PANEL_NAME = "rich_help_panel"

MarkupModeStrict = Literal["markdown", "rich"]


RICH_AVAILABLE = False
highlighter = None
negative_highlighter = None

if _USE_RICH:  # pragma: no cover
    try:
        from rich.align import Align
        from rich.columns import Columns
        from rich.console import Console, group
        from rich.emoji import Emoji
        from rich.highlighter import RegexHighlighter
        from rich.markdown import Markdown
        from rich.markup import escape
        from rich.padding import Padding
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich.theme import Theme
        from rich.traceback import Traceback

        class OptionHighlighter(RegexHighlighter):
            """Highlight options in help text."""

            highlights = [
                r"(^|\W)(?P<switch>\-\w+)(?![a-zA-Z0-9])",
                r"(^|\W)(?P<option>\-\-[\w\-]+)(?![a-zA-Z0-9])",
                r"(?P<metavar>\<[^\>]+\>)",
                r"(?P<usage>Usage: )",
            ]

        class NegativeOptionHighlighter(RegexHighlighter):
            """Highlight negative options in help text."""

            highlights = [
                r"(^|\W)(?P<negative_switch>\-\w+)(?![a-zA-Z0-9])",
                r"(^|\W)(?P<negative_option>\-\-[\w\-]+)(?![a-zA-Z0-9])",
            ]

        highlighter = OptionHighlighter()
        negative_highlighter = NegativeOptionHighlighter()

        RICH_AVAILABLE = True

    except ImportError:
        # Rich library not available
        pass


## Core helper functions


def _get_rich_console(stderr: bool = False) -> Optional[Console]:
    """Get Rich Console instance.

    Args:
        stderr: Whether to output to stderr

    Returns:
        Console instance or None if Rich disabled
    """
    if not RICH_AVAILABLE:
        return None

    return Console(
        theme=Theme(
            {
                "option": STYLE_OPTION,
                "switch": STYLE_SWITCH,
                "negative_option": STYLE_NEGATIVE_OPTION,
                "negative_switch": STYLE_NEGATIVE_SWITCH,
                "metavar": STYLE_METAVAR,
                "metavar_sep": STYLE_METAVAR_SEPARATOR,
                "usage": STYLE_USAGE,
            },
        ),
        highlighter=highlighter,
        color_system=COLOR_SYSTEM,
        force_terminal=FORCE_TERMINAL,
        width=MAX_WIDTH,
        stderr=stderr,
    )


def _make_rich_text(
    *, text: str, style: str = "", markup_mode: MarkupModeStrict
) -> Union[Union[Markdown, Text], str]:
    """Take a string, remove indentations, and return styled text.

    Args:
        text: Text to format
        style: Style to apply
        markup_mode: "rich" or "markdown"

    Returns:
        Markdown or Text object (or plain string if Rich disabled)
    """
    # Remove indentations from input text
    text = cleandoc(text)

    if not RICH_AVAILABLE:
        return text

    if markup_mode == MARKUP_MODE_MARKDOWN:
        text = Emoji.replace(text)
        return Markdown(text, style=style)
    else:
        assert markup_mode == MARKUP_MODE_RICH
        if highlighter is not None:
            return highlighter(Text.from_markup(text, style=style))
        # Fallback if highlighter is None
        return Text.from_markup(text, style=style)


def _get_help_text(
    *,
    obj: Union[click.Command, click.Group],
    markup_mode: MarkupModeStrict,
) -> Union[RenderableType, str]:
    """Build primary help text for a click command or group.

    Args:
        obj: Click command or group
        markup_mode: "rich" or "markdown"

    Returns:
        A Rich Group renderable (if Rich available) or plain text
    """
    if not RICH_AVAILABLE:
        # Fallback to plain text
        if obj.deprecated:
            deprecated_help = DEPRECATED_STRING + (cleandoc(obj.help or ""))
            return deprecated_help.partition("\f")[0]
        else:
            help_text = cleandoc(obj.help or "")
            return help_text.partition("\f")[0]

    # Create a generator to be used with @group decorator
    @group()
    def _generator() -> Generator[Union[Text, Markdown], None, None]:
        """Generator that yields Text/Markdown objects"""
        # Prepend deprecated status
        if obj.deprecated:
            yield Text(DEPRECATED_STRING, style=STYLE_DEPRECATED)

        # Fetch and dedent the help text
        help_text = cleandoc(obj.help or "")
        help_text = help_text.partition("\f")[0]

        # Get the first paragraph
        first_line, *remaining_paragraphs = help_text.split("\n\n")

        # Remove single linebreaks
        if markup_mode != MARKUP_MODE_MARKDOWN and not first_line.startswith("\b"):
            first_line = first_line.replace("\n", " ")

        yield _make_rich_text(
            text=first_line.strip(),
            style=STYLE_HELPTEXT_FIRST_LINE,
            markup_mode=markup_mode,
        )

        # Get remaining lines
        if remaining_paragraphs:
            yield Text("")
            remaining_lines = "\n\n".join(remaining_paragraphs)
            yield _make_rich_text(
                text=remaining_lines,
                style=STYLE_HELPTEXT,
                markup_mode=markup_mode,
            )

    return _generator()


def _get_parameter_help(
    *,
    param: Union[click.Option, click.Argument, click.Parameter],
    ctx: click.Context,
    markup_mode: MarkupModeStrict,
) -> Union[Columns, tuple[str, str]]:
    """Build primary help text for a click option or argument.

    Args:
        param: Click parameter
        ctx: Click context
        markup_mode: "rich" or "markdown"

    Returns:
        Columns object or plain text tuple if Rich disabled
    """
    if not RICH_AVAILABLE:
        # Fallback to plain text
        help_record = param.get_help_record(ctx)
        return help_record if help_record else ("", "")

    # Import here to avoid cyclic imports
    from typer.core import TyperArgument, TyperOption

    items: list = []

    # Get environment variable
    envvar = getattr(param, "envvar", None)
    var_str = ""

    if envvar is None:
        if (
            getattr(param, "allow_from_autoenv", None)
            and getattr(ctx, "auto_envvar_prefix", None) is not None
            and param.name is not None
        ):
            envvar = f"{ctx.auto_envvar_prefix}_{param.name.upper()}"

    if envvar is not None:
        if isinstance(envvar, str):
            var_str = envvar
        else:
            var_str = ", ".join(str(item) for item in envvar)

    # Get help text
    help_text = getattr(param, "help", None)
    if help_text:
        paragraphs = help_text.split("\n\n")
        first_paragraph, *remaining = paragraphs

        # Remove single linebreaks
        if markup_mode != MARKUP_MODE_MARKDOWN and not first_paragraph.startswith("\b"):
            first_paragraph = first_paragraph.replace("\n", " ")
        first_paragraph = first_paragraph.strip()

        items.append(
            _make_rich_text(
                text=first_paragraph,
                style=STYLE_OPTION_HELP,
                markup_mode=markup_mode,
            )
        )

        if remaining:
            items.append(Text(""))
            remaining_text = "\n\n".join(remaining)
            items.append(
                _make_rich_text(
                    text=remaining_text,
                    style=STYLE_HELPTEXT,
                    markup_mode=markup_mode,
                )
            )

    # Add default value
    if isinstance(param, (TyperArgument, TyperOption)):
        # Get from typer metadata
        default_value = getattr(param, "default_value_from_help", None)
        if default_value is not None:
            items.append(
                Text(
                    DEFAULT_STRING.format(default_value),
                    style=STYLE_OPTION_DEFAULT,
                )
            )
    elif param.default is not None and (
        getattr(param, "show_default", False) or getattr(ctx, "show_default", False)
    ):
        if isinstance(param.default, (list, tuple)):
            default_str = ", ".join(str(d) for d in param.default)
        elif callable(param.default):
            default_str = "(dynamic)"
        else:
            default_str = str(param.default)

        if default_str:
            items.append(
                Text(
                    DEFAULT_STRING.format(default_str),
                    style=STYLE_OPTION_DEFAULT,
                )
            )

    # Add environment variable
    if var_str:
        items.append(
            Text(
                ENVVAR_STRING.format(var_str),
                style=STYLE_OPTION_ENVVAR,
            )
        )

    # Add required indicator
    if param.required:
        items.append(
            Text(
                REQUIRED_LONG_STRING,
                style=STYLE_REQUIRED_LONG,
            )
        )

    return Columns(items)


def _print_options_panel(
    *,
    name: str,
    params: Union[list[click.Option], list[click.Argument]],
    ctx: click.Context,
    markup_mode: MarkupModeStrict,
    console: Console,
) -> None:
    """Print options panel with graceful fallback.

    Args:
        name: Panel name
        params: List of parameters
        ctx: Click context
        markup_mode: "rich" or "markdown"
        console: Rich console (or None)
    """
    if not params:
        return

    if not RICH_AVAILABLE:
        # Fallback to plain text
        click.echo(f"\n{name}:")
        for param in params:
            help_record = param.get_help_record(ctx)
            if help_record:
                opts, help_text = help_record
                click.echo(f"  {opts:<30}  {help_text}")
        return

    options_table = Table(
        highlight=False,
        show_header=False,
        show_edge=False,
        show_lines=STYLE_OPTIONS_TABLE_SHOW_LINES,
        leading=STYLE_OPTIONS_TABLE_LEADING,
        pad_edge=STYLE_OPTIONS_TABLE_PAD_EDGE,
        padding=STYLE_OPTIONS_TABLE_PADDING,
        box=STYLE_OPTIONS_TABLE_BOX,
        row_styles=STYLE_OPTIONS_TABLE_ROW_STYLES,
        border_style=STYLE_OPTIONS_TABLE_BORDER_STYLE,
    )
    options_table.add_column(no_wrap=True)
    options_table.add_column()

    for param in params:
        # Get option names
        if isinstance(param, click.Argument):
            opts = [param.human_readable_name or param.name or ""]
        else:
            opts = list(param.opts) + list(param.secondary_opts or [])

        opts_str = " / ".join(opts)

        # Check if option is negative
        is_negative = any(
            opt.startswith("--no-") or opt.startswith("-N")
            for opt in (param.opts + (param.secondary_opts or []))
        )

        if is_negative:
            if negative_highlighter is not None:
                opts_text = negative_highlighter(Text(opts_str))
        else:
            if highlighter is not None:
                opts_text = highlighter(Text(opts_str))

        # Add metavar if present
        if hasattr(param, "metavar") and param.metavar:
            opts_text.append(" ")
            opts_text.append(param.metavar, style=STYLE_METAVAR)
        elif hasattr(param, "type") and hasattr(param.type, "name"):
            opts_text.append(" ")
            opts_text.append(f"<{param.type.name}>", style=STYLE_METAVAR)

        # Add required indicator
        if param.required:
            opts_text.append(
                " " + REQUIRED_SHORT_STRING,
                style=STYLE_REQUIRED_SHORT,
            )

        help_cols = _get_parameter_help(
            param=param,
            ctx=ctx,
            markup_mode=markup_mode,
        )

        if isinstance(help_cols, Columns):
            options_table.add_row(opts_text, help_cols)

    if options_table.row_count:
        console.print(
            Panel(
                Align(options_table, align=ALIGN_OPTIONS_PANEL),
                border_style=STYLE_OPTIONS_PANEL_BORDER,
                title=name,
                title_align=ALIGN_OPTIONS_PANEL,
            )
        )


def _print_commands_panel(
    *,
    name: str,
    commands: list[click.Command],
    markup_mode: MarkupModeStrict,
    console: Console,
    cmd_len: int,
    extended_typer: Optional[Any] = None,
) -> None:
    """Print commands panel with graceful fallback.

    Args:
        name: Panel name
        commands: List of commands
        markup_mode: "rich" or "markdown"
        console: Rich console (or None)
        cmd_len: Max command length for alignment
        extended_typer: Optional extended Typer instance for alias support
    """
    if not RICH_AVAILABLE:
        # Fallback to standard Click help
        if commands:
            click.echo(f"\n{name}:")
            for command in commands:
                cmd_name = command.name or ""
                help_text = (command.help or "").partition("\f")[0].splitlines()[0]
                if command.deprecated:
                    cmd_name += " (deprecated)"
                click.echo(f"  {cmd_name:<{cmd_len}}  {help_text}")

    command_display_names: dict[str, str] = {}
    max_display_len = cmd_len

    if extended_typer is not None:
        if getattr(extended_typer, "show_aliases_in_help", False) and getattr(
            extended_typer, "_command_aliases", {}
        ):
            try:
                cache_key = f"_formatted_commands_cache_{id(commands)}"
                if not hasattr(extended_typer, cache_key):
                    from typer_extensions.format import format_commands_with_aliases

                    cmd_tuples = [
                        (str(getattr(cmd, "name", "")), getattr(cmd, "help", None))
                        for cmd in commands
                    ]

                    formatted_tuples, max_len = format_commands_with_aliases(
                        cmd_tuples,
                        extended_typer._command_aliases,
                        display_format=getattr(
                            extended_typer, "alias_display_format", "({aliases})"
                        ),
                        max_num=getattr(extended_typer, "max_num_aliases", 3),
                        separator=getattr(extended_typer, "alias_separator", ", "),
                    )

                    setattr(extended_typer, cache_key, (formatted_tuples, max_len))

                formatted_tuples, max_len = getattr(extended_typer, cache_key)

                for cmd, (formatted_name, _) in zip(commands, formatted_tuples):
                    command_display_names[cmd.name or ""] = formatted_name

                max_display_len = max_len

            except Exception:
                pass

    commands_table = Table(
        highlight=False,
        show_header=False,
        show_edge=False,
        show_lines=STYLE_COMMANDS_TABLE_SHOW_LINES,
        leading=STYLE_COMMANDS_TABLE_LEADING,
        pad_edge=STYLE_COMMANDS_TABLE_PAD_EDGE,
        padding=STYLE_COMMANDS_TABLE_PADDING,
        box=STYLE_COMMANDS_TABLE_BOX,
        row_styles=STYLE_COMMANDS_TABLE_ROW_STYLES,
        border_style=STYLE_COMMANDS_TABLE_BORDER_STYLE,
    )
    commands_table.add_column(
        style=STYLE_COMMANDS_TABLE_FIRST_COLUMN,
        no_wrap=True,
        width=max_display_len + 2,
    )
    commands_table.add_column(no_wrap=False)

    # Track deprecated commands
    deprecated_rows = []
    rows = []

    for command in commands:
        deprecated_text = Text()
        if command.deprecated:
            deprecated_text = Text(
                DEPRECATED_STRING,
                style=STYLE_DEPRECATED,
            )
        deprecated_rows.append(deprecated_text)

        display_name = command_display_names.get(command.name or "", command.name or "")

        # Command help
        help_text = command.help or ""
        help_text = help_text.partition("\f")[0]
        first_line = help_text.split("\n\n")[0] if help_text else ""

        if markup_mode != MARKUP_MODE_MARKDOWN and not first_line.startswith("\b"):
            first_line = first_line.replace("\n", " ")

        rows.append(
            [
                Text(display_name or "", style=STYLE_COMMANDS_TABLE_FIRST_COLUMN),
                _make_rich_text(
                    text=first_line.strip(),
                    markup_mode=markup_mode,
                ),
            ]
        )

    # Merge deprecated markers if any
    rows_with_deprecated = rows
    if any(deprecated_rows):
        rows_with_deprecated = []
        for row, deprecated_text in zip(rows, deprecated_rows):
            rows_with_deprecated.append([*row, deprecated_text])

    for row in rows_with_deprecated:
        commands_table.add_row(*row)

    if commands_table.row_count:
        console.print(
            Panel(
                commands_table,
                border_style=STYLE_COMMANDS_PANEL_BORDER,
                title=name,
                title_align=ALIGN_COMMANDS_PANEL,
            )
        )


## Formatting functions


def rich_format_help(
    *,
    obj: Union[click.Command, click.Group],
    ctx: click.Context,
    markup_mode: MarkupModeStrict,
) -> None:
    """Print nicely formatted help text using rich.

    Args:
        obj: Click command or group
        ctx: Click context
        markup_mode: "rich" or "markdown"
    """
    if not RICH_AVAILABLE:
        # Fallback to standard Click help
        formatter = ctx.make_formatter()
        obj.format_help(ctx, formatter)
        click.echo(formatter.getvalue())
        return

    console = _get_rich_console()
    if console is None:
        # Fallback to standard Click help
        formatter = ctx.make_formatter()
        obj.format_help(ctx, formatter)
        click.echo(formatter.getvalue())
        return

    # Print usage
    if highlighter is not None:
        console.print(
            Padding(highlighter(obj.get_usage(ctx)), 1), style=STYLE_USAGE_COMMAND
        )

    # Print command / group help if applicable
    if obj.help:
        console.print(
            Padding(
                Align(
                    _get_help_text(
                        obj=obj,
                        markup_mode=markup_mode,
                    ),
                    pad=False,
                ),
                (0, 1, 1, 1),
            )
        )

    # Organise parameters into panels
    panel_to_arguments: defaultdict[str, list[click.Argument]] = defaultdict(list)
    panel_to_options: defaultdict[str, list[click.Option]] = defaultdict(list)

    for param in obj.get_params(ctx):
        # Skip if option is hidden
        if getattr(param, "hidden", False):
            continue
        if isinstance(param, click.Argument):
            panel_name = (
                getattr(param, _RICH_HELP_PANEL_NAME, None) or ARGUMENTS_PANEL_TITLE
            )
            panel_to_arguments[panel_name].append(param)
        elif isinstance(param, click.Option):
            panel_name = (
                getattr(param, _RICH_HELP_PANEL_NAME, None) or OPTIONS_PANEL_TITLE
            )
            panel_to_options[panel_name].append(param)

    # Print arguments panels
    default_arguments = panel_to_arguments.get(ARGUMENTS_PANEL_TITLE, [])
    _print_options_panel(
        name=ARGUMENTS_PANEL_TITLE,
        params=default_arguments,
        ctx=ctx,
        markup_mode=markup_mode,
        console=console,
    )
    for panel_name, arguments in panel_to_arguments.items():
        if panel_name == ARGUMENTS_PANEL_TITLE:
            continue
        _print_options_panel(
            name=panel_name,
            params=arguments,
            ctx=ctx,
            markup_mode=markup_mode,
            console=console,
        )

    # Print options panels
    default_options = panel_to_options.get(OPTIONS_PANEL_TITLE, [])
    _print_options_panel(
        name=OPTIONS_PANEL_TITLE,
        params=default_options,
        ctx=ctx,
        markup_mode=markup_mode,
        console=console,
    )
    for panel_name, options in panel_to_options.items():
        if panel_name == OPTIONS_PANEL_TITLE:
            continue
        _print_options_panel(
            name=panel_name,
            params=options,
            ctx=ctx,
            markup_mode=markup_mode,
            console=console,
        )

    # Print commands panels (groups)
    if isinstance(obj, click.Group):
        panel_to_commands: defaultdict[str, list[click.Command]] = defaultdict(list)
        for command_name in obj.list_commands(ctx):
            command = obj.get_command(ctx, command_name)
            if command and not command.hidden:
                panel_name = (
                    getattr(command, _RICH_HELP_PANEL_NAME, None)
                    or COMMANDS_PANEL_TITLE
                )
                panel_to_commands[panel_name].append(command)

        # Identify the longest command name in all panels
        max_cmd_len = max(
            [
                len(command.name or "")
                for commands in panel_to_commands.values()
                for command in commands
            ],
            default=0,
        )

        # Print each command group panel
        default_commands = panel_to_commands.get(COMMANDS_PANEL_TITLE, [])
        _print_commands_panel(
            name=COMMANDS_PANEL_TITLE,
            commands=default_commands,
            markup_mode=markup_mode,
            console=console,
            cmd_len=max_cmd_len,
            extended_typer=getattr(obj, "_extended_typer", None),
        )
        for panel_name, commands in panel_to_commands.items():
            if panel_name == COMMANDS_PANEL_TITLE:
                continue
            _print_commands_panel(
                name=panel_name,
                commands=commands,
                markup_mode=markup_mode,
                console=console,
                cmd_len=max_cmd_len,
                extended_typer=getattr(obj, "_extended_typer", None),
            )

    # Epilogue if applicable
    if obj.epilog:
        lines = obj.epilog.split("\n\n")
        epilogue = "\n".join([x.replace("\n", " ").strip() for x in lines])
        epilogue_text = _make_rich_text(text=epilogue, markup_mode=markup_mode)
        console.print(Padding(Align(epilogue_text, pad=False), 1))


def rich_format_error(self: click.ClickException) -> None:
    """Print richly formatted click errors.

    Args:
        self: The ClickException instance
    """
    # Don't do anything when it's a NoArgsIsHelpError
    if self.__class__.__name__ == "NoArgsIsHelpError":
        return

    if not RICH_AVAILABLE:
        # Fallback to standard Click error
        return self.show()

    console = _get_rich_console(stderr=True)

    if not console:
        # Fallback to standard Click error
        return self.show()

    ctx: Union[click.Context, None] = getattr(self, "ctx", None)
    if ctx is not None:
        console.print(ctx.get_usage())

    if ctx is not None and ctx.command.get_help_option(ctx) is not None:
        console.print(
            RICH_HELP.format(
                command_path=ctx.command_path, help_option=ctx.help_option_names[0]
            ),
            style=STYLE_ERRORS_SUGGESTION,
        )

    if highlighter is not None:
        console.print(
            Panel(
                highlighter(self.format_message()),
                border_style=STYLE_ERRORS_PANEL_BORDER,
                title=ERRORS_PANEL_TITLE,
                title_align=ALIGN_ERRORS_PANEL,
            )
        )


def rich_abort_error() -> None:
    """Print richly formatted abort error."""
    if not RICH_AVAILABLE:
        # Fallback to plain text
        import sys

        click.echo(ABORTED_TEXT, file=sys.stderr)
        return

    console = _get_rich_console(stderr=True)
    if not console:
        # Fallback to plain text
        import sys

        click.echo(ABORTED_TEXT, file=sys.stderr)
        return

    console.print(ABORTED_TEXT, style=STYLE_ABORTED)


## Utility functions


def cleandoc(doc: str) -> str:
    """Remove any whitespace from the second line onwards.

    Adapted from inspect.cleandoc()

    Args:
        doc: The docstring to clean up.

    Returns:
        The cleaned-up docstring.
    """
    lines = doc.expandtabs().split("\n")

    # Find minimum indentation of any non-blank lines after first line
    margin = min(
        (len(line) - len(line.lstrip(" ")) for line in lines[1:] if line.strip()),
        default=sys.maxsize,
    )

    # Remove indentation
    lines[0] = lines[0].lstrip(" ")
    if margin < sys.maxsize:
        for i in range(1, len(lines)):
            lines[i] = lines[i][margin:]

    # Remove any leading/trailing blank lines.
    while lines and not lines[-1]:
        lines.pop()
    while lines and not lines[0]:
        lines.pop(0)

    return "\n".join(lines)


def escape_before_html_export(input_text: str) -> str:
    """Ensure that the input string can be used for HTML export.

    Args:
        input_text: Text to escape

    Returns:
        Escaped text
    """
    if not RICH_AVAILABLE:
        # Fallback to basic HTML escaping
        return (
            input_text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .strip()
        )

    return escape(input_text).strip()


def rich_to_html(input_text: str) -> str:
    """Print the HTML version of a rich-formatted input string.

    Args:
        input_text: Rich-formatted text

    Returns:
        HTML string
    """
    if not RICH_AVAILABLE:
        # Fallback to escaped plain text
        return escape_before_html_export(input_text)

    console = Console(record=True, highlight=False, file=io.StringIO())
    if not console:
        # Fallback to escaped plain text
        return escape_before_html_export(input_text)

    console.print(input_text, overflow="ignore", crop=False)

    return console.export_html(inline_styles=True, code_format="{code}").strip()


def rich_render_text(text: str) -> str:
    """Remove rich tags and render a pure text representation.

    Args:
        text: Rich-formatted text

    Returns:
        Plain text
    """
    if not RICH_AVAILABLE:
        # Fallback to simple tag removal of Rich tags
        import re

        text = re.sub(r"\[/?[^\]]+\]", "", text)
        return text.rstrip("\n")

    console = _get_rich_console()
    if not console:
        # Fallback to plain text
        import re

        text = re.sub(r"\[/?[^\]]+\]", "", text)
        return text.rstrip("\n")

    return "".join(segment.text for segment in console.render(text)).rstrip("\n")


def get_traceback(
    exc: BaseException,
    exception_config: Any,  # DeveloperExceptionConfig
    internal_dir_names: list[str],
) -> Optional[Traceback]:
    """Get formatted traceback for exception.

    Args:
        exc: Exception to format
        exception_config: Developer exception config
        internal_dir_names: Internal directories to suppress

    Returns:
        Traceback object or None if Rich disabled
    """
    if not RICH_AVAILABLE:
        return None

    show_locals = False
    if exception_config and hasattr(exception_config, "pretty_exceptions_show_locals"):
        show_locals = exception_config.pretty_exceptions_show_locals

    rich_tb = Traceback.from_exception(
        type(exc),
        exc,
        exc.__traceback__,
        show_locals=show_locals,
        suppress=internal_dir_names,
        width=MAX_WIDTH,
    )
    return rich_tb
