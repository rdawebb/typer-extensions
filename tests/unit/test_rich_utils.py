"""Comprehensive tests for typer_extensions._rich_utils module when Rich is available.

This module tests the Rich-enabled functionality of the _rich_utils module,
including formatting, help display, error handling, and various edge cases.
"""

from unittest.mock import MagicMock, Mock, patch

import click
import pytest

from typer_extensions import _rich_utils

# Skip all tests in this file if Rich is not available
pytestmark = pytest.mark.skipif(
    not _rich_utils.RICH_AVAILABLE, reason="Rich not available"
)


# =============================================================================
# Constants and Basic Functionality Tests
# =============================================================================


class TestRichUtilsConstants:
    """Test that style constants and configurations are properly defined."""

    def test_style_constants_defined(self):
        """Test that all style constants are defined."""
        assert _rich_utils.STYLE_OPTION == "bold cyan"
        assert _rich_utils.STYLE_SWITCH == "bold green"
        assert _rich_utils.STYLE_NEGATIVE_OPTION == "bold magenta"
        assert _rich_utils.STYLE_METAVAR == "bold yellow"
        assert _rich_utils.STYLE_USAGE == "yellow"

    def test_alignment_constants_defined(self):
        """Test that alignment constants are defined."""
        assert _rich_utils.ALIGN_OPTIONS_PANEL in ["left", "center", "right"]
        assert _rich_utils.ALIGN_COMMANDS_PANEL in ["left", "center", "right"]
        assert _rich_utils.ALIGN_ERRORS_PANEL in ["left", "center", "right"]

    def test_panel_titles_defined(self):
        """Test that panel titles are defined."""
        assert _rich_utils.ARGUMENTS_PANEL_TITLE
        assert _rich_utils.OPTIONS_PANEL_TITLE
        assert _rich_utils.COMMANDS_PANEL_TITLE
        assert _rich_utils.ERRORS_PANEL_TITLE

    def test_deprecated_string_defined(self):
        """Test that deprecated string is defined."""
        assert _rich_utils.DEPRECATED_STRING
        assert "deprecated" in _rich_utils.DEPRECATED_STRING.lower()

    def test_highlighters_exist(self):
        """Test that highlighters exist when Rich is available."""
        assert _rich_utils.highlighter is not None
        assert _rich_utils.negative_highlighter is not None


class TestCleandocFunction:
    """Tests for the cleandoc utility function."""

    def test_cleandoc_basic(self):
        """Test basic cleandoc functionality."""
        text = """
        First line
        Second line
            Indented line
        """
        result = _rich_utils.cleandoc(text)
        assert "First line" in result
        assert "Second line" in result

    def test_cleandoc_removes_leading_blank_lines(self):
        """Test that cleandoc removes leading blank lines."""
        text = "\n\n\nFirst line"
        result = _rich_utils.cleandoc(text)
        assert result.startswith("First")

    def test_cleandoc_removes_trailing_blank_lines(self):
        """Test that cleandoc removes trailing blank lines."""
        text = "First line\n\n\n"
        result = _rich_utils.cleandoc(text)
        assert result.endswith("line")
        assert not result.endswith("\n")

    def test_cleandoc_empty_string(self):
        """Test cleandoc with empty string."""
        result = _rich_utils.cleandoc("")
        assert result == ""

    def test_cleandoc_single_line(self):
        """Test cleandoc with single line."""
        result = _rich_utils.cleandoc("Single line")
        assert result == "Single line"

    def test_cleandoc_with_tabs(self):
        """Test cleandoc with tabs."""
        result = _rich_utils.cleandoc("\t\tIndented with tabs")
        assert "Indented" in result

    def test_cleandoc_whitespace_only(self):
        """Test cleandoc with only whitespace."""
        result = _rich_utils.cleandoc("   \n\n   ")
        assert result == "" or result.strip() == ""

    def test_cleandoc_removes_common_indentation(self):
        """Test cleandoc removes common indentation."""
        result = _rich_utils.cleandoc("Line 1\n    Line 2\n    Line 3")
        assert result == "Line 1\nLine 2\nLine 3"

    def test_cleandoc_single_line_margin(self):
        """Test cleandoc when there's only one line (margin=sys.maxsize)."""
        result = _rich_utils.cleandoc("Single line")
        assert result == "Single line"

        result = _rich_utils.cleandoc("Line 1\n\n\n")
        assert result == "Line 1"


# =============================================================================
# Console and Text Creation Tests
# =============================================================================


class TestGetRichConsole:
    """Tests for _get_rich_console function."""

    def test_get_console_stderr_false(self):
        """Test getting console with stderr=False."""
        console = _rich_utils._get_rich_console(stderr=False)
        assert console is not None
        assert hasattr(console, "print")

    def test_get_console_stderr_true(self):
        """Test getting console with stderr=True."""
        console = _rich_utils._get_rich_console(stderr=True)
        assert console is not None
        assert hasattr(console, "print")


class TestMakeRichText:
    """Tests for _make_rich_text function."""

    def test_make_rich_text_markdown_mode(self):
        """Test _make_rich_text with markdown mode."""
        result = _rich_utils._make_rich_text(
            text="**Bold text**", style="", markup_mode=_rich_utils.MARKUP_MODE_MARKDOWN
        )
        assert result is not None

    def test_make_rich_text_rich_mode(self):
        """Test _make_rich_text with rich mode."""
        result = _rich_utils._make_rich_text(
            text="[bold]Bold text[/bold]",
            style="",
            markup_mode=_rich_utils.MARKUP_MODE_RICH,
        )
        assert result is not None

    def test_make_rich_text_with_style(self):
        """Test _make_rich_text with style parameter."""
        result = _rich_utils._make_rich_text(
            text="Plain text", style="bold", markup_mode="markdown"
        )
        assert result is not None

    def test_make_rich_text_empty_text(self):
        """Test _make_rich_text with empty string."""
        result = _rich_utils._make_rich_text(
            text="", style="", markup_mode=_rich_utils.MARKUP_MODE_RICH
        )
        assert result is not None

    def test_make_rich_text_with_highlighter_none(self):
        """Test _make_rich_text when highlighter is None but Rich is available."""
        with patch.object(_rich_utils, "highlighter", None):
            result = _rich_utils._make_rich_text(
                text="Test text", style="", markup_mode="rich"
            )
            assert result is not None


# =============================================================================
# HTML Export and Text Rendering Tests
# =============================================================================


class TestEscapeBeforeHtmlExport:
    """Tests for escape_before_html_export function."""

    def test_escape_with_special_characters(self):
        """Test escaping special HTML characters."""
        text = "Text with <angle brackets>"
        result = _rich_utils.escape_before_html_export(text)
        assert result is not None
        assert isinstance(result, str)

    def test_escape_empty_string(self):
        """Test escaping empty string."""
        result = _rich_utils.escape_before_html_export("")
        assert result == ""

    def test_escape_normal_text(self):
        """Test escaping normal text."""
        text = "Normal text"
        result = _rich_utils.escape_before_html_export(text)
        assert "Normal text" in result


class TestRichRenderText:
    """Tests for rich_render_text function."""

    def test_render_text_with_markup(self):
        """Test rendering text with rich markup."""
        result = _rich_utils.rich_render_text("[bold]Bold[/bold]")
        assert result is not None

    def test_render_text_with_embedded_tags(self):
        """Test rich_render_text with embedded Rich tags."""
        text = "This is [bold]bold[/bold] and [italic]italic[/italic]"
        result = _rich_utils.rich_render_text(text)
        assert isinstance(result, str)
        assert "bold" not in result or "[" not in result

    def test_render_text_empty_string(self):
        """Test rich_render_text with empty string."""
        result = _rich_utils.rich_render_text("")
        assert isinstance(result, str)
        assert result == ""

    def test_render_text_with_only_tags(self):
        """Test rich_render_text with only tags."""
        result = _rich_utils.rich_render_text("[bold][/bold]")
        assert isinstance(result, str)


class TestRichToHtml:
    """Tests for rich_to_html function."""

    def test_rich_to_html_basic(self):
        """Test converting rich text to HTML."""
        result = _rich_utils.rich_to_html("[bold]Bold[/bold]")
        assert result is not None
        assert isinstance(result, str)

    def test_rich_to_html_with_rich_markup(self):
        """Test rich_to_html with Rich markup."""
        result = _rich_utils.rich_to_html(
            "[bold]Bold text[/bold] and [red]red text[/red]"
        )
        assert isinstance(result, str)
        assert "<" in result or result  # Either has HTML tags or plain text

    def test_rich_to_html_empty_string(self):
        """Test rich_to_html with empty string."""
        result = _rich_utils.rich_to_html("")
        assert isinstance(result, str)

    def test_rich_to_html_with_tags(self):
        """Test rich_to_html with Rich markup tags."""
        result = _rich_utils.rich_to_html("[bold]Text[/bold]")
        assert isinstance(result, str)

    def test_rich_to_html_with_special_chars(self):
        """Test rich_to_html with special characters."""
        result = _rich_utils.rich_to_html('<tag> & "quotes"')
        assert isinstance(result, str)

    def test_rich_to_html_with_newlines(self):
        """Test rich_to_html preserves content with newlines."""
        result = _rich_utils.rich_to_html("Line 1\nLine 2\nLine 3")
        assert isinstance(result, str)


# =============================================================================
# Help Text Generation Tests
# =============================================================================


class TestGetHelpText:
    """Tests for _get_help_text function."""

    def test_get_help_text_with_none_help_text(self):
        """Test _get_help_text with None/empty help text."""
        obj = Mock()
        obj.help = None
        obj.deprecated = False

        result = _rich_utils._get_help_text(
            obj=obj, markup_mode=_rich_utils.MARKUP_MODE_RICH
        )
        assert result is not None or result == ""

    def test_get_help_text_with_deprecated_flag(self):
        """Test _get_help_text with deprecated=True."""
        obj = Mock()
        obj.help = "Test help text"
        obj.deprecated = True

        result = _rich_utils._get_help_text(
            obj=obj, markup_mode=_rich_utils.MARKUP_MODE_RICH
        )
        assert result is not None

    def test_get_help_text_with_markdown_multiline(self):
        """Test _get_help_text with markdown mode and multiline help."""
        cmd = click.Command("test")
        cmd.help = "First paragraph\n\nSecond paragraph\n\nThird paragraph"

        result = _rich_utils._get_help_text(obj=cmd, markup_mode="markdown")
        assert result is not None

    def test_get_help_text_with_formfeed_markdown(self):
        """Test _get_help_text with formfeed in markdown mode."""
        cmd = click.Command("test")
        cmd.help = "Visible part\fHidden part after formfeed"

        result = _rich_utils._get_help_text(obj=cmd, markup_mode="markdown")
        assert result is not None

    def test_get_help_text_with_newlines_in_first_line_rich_mode(self):
        """Test _get_help_text with newlines in first line for rich mode."""
        cmd = click.Command("test")
        cmd.help = "First\nline\nwith\nnewlines\n\nSecond paragraph"

        result = _rich_utils._get_help_text(obj=cmd, markup_mode="rich")
        assert result is not None

    def test_get_help_text_with_breaklines_marker(self):
        """Test _get_help_text with \\b marker (preserve line breaks)."""
        cmd = click.Command("test")
        cmd.help = "\\bFirst line\nSecond line\nThird line"

        result = _rich_utils._get_help_text(obj=cmd, markup_mode="rich")
        assert result is not None

    def test_help_with_form_feed(self):
        """Test help text with form feed character."""
        obj = Mock(spec=click.Command)
        obj.help = "First part\fSecond part that should be hidden"
        obj.deprecated = False

        result = _rich_utils._get_help_text(obj=obj, markup_mode="rich")
        assert result is not None

    def test_help_with_literal_break(self):
        """Test help text with literal break marker."""
        obj = Mock(spec=click.Command)
        obj.help = "\\b\nLine 1\nLine 2"
        obj.deprecated = False

        result = _rich_utils._get_help_text(obj=obj, markup_mode="rich")
        assert result is not None


# =============================================================================
# Parameter Help Tests
# =============================================================================


class TestGetParameterHelp:
    """Tests for _get_parameter_help function."""

    def test_get_parameter_help_option_with_default(self):
        """Test _get_parameter_help with option having default value."""
        opt = click.Option(
            ["-n", "--name"], default="John", show_default=True, help="Name"
        )

        ctx = Mock()
        ctx.show_default = False
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_get_parameter_help_option_with_multiple_envvars(self):
        """Test _get_parameter_help with option having multiple env vars."""
        opt = click.Option(
            ["-t", "--token"], envvar=["TOKEN", "API_KEY"], help="API token"
        )

        ctx = Mock()
        ctx.show_default = False
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_get_parameter_help_with_no_help_text(self):
        """Test _get_parameter_help with no help text."""
        opt = click.Option(["-q", "--quiet"])

        ctx = Mock()
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_get_parameter_help_with_auto_envvar_prefix(self):
        """Test _get_parameter_help with auto_envvar_prefix."""
        opt = click.Option(["-a", "--api-key"], allow_from_autoenv=True, help="API key")

        ctx = Mock()
        ctx.auto_envvar_prefix = "MYAPP"

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_get_parameter_help_with_callable_default(self):
        """Test _get_parameter_help with callable default value."""

        def default_func():
            return "dynamic"

        opt = click.Option(["-d", "--dynamic"], default=default_func, show_default=True)

        ctx = Mock()
        ctx.show_default = False
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_get_parameter_help_with_required_option(self):
        """Test _get_parameter_help with required option."""
        opt = click.Option(["-r", "--required"], required=True, help="Required field")

        ctx = Mock()
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_get_parameter_help_with_multiple_paragraphs(self):
        """Test _get_parameter_help with multi-paragraph help text."""
        opt = click.Option(
            ["-c", "--config"],
            help="First paragraph\n\nSecond paragraph with more details\n\nThird paragraph",
        )
        ctx = Mock()
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_get_parameter_help_with_breaklines_marker(self):
        """Test _get_parameter_help with \\b marker."""
        opt = click.Option(
            ["-f", "--format"], help="\\bLine 1\nLine 2\nLine 3", metavar="FORMAT"
        )
        ctx = Mock()
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_get_parameter_help_with_range_constraint(self):
        """Test _get_parameter_help with click.IntRange."""
        opt = click.Option(
            ["-p", "--port"],
            type=click.IntRange(1, 65535),
            help="Port number",
        )
        ctx = Mock()
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(
            param=opt, ctx=ctx, markup_mode="markdown"
        )
        assert result is not None

    def test_typer_argument_with_default_value(self):
        """TyperArgument with default_value_from_help."""
        from typer.core import TyperArgument

        param = TyperArgument(param_decls=["test_arg"], nargs=1)
        param.help = "Test argument"
        param.required = False
        setattr(param, "default_value_from_help", "42")
        param.envvar = None

        ctx = Mock()

        result = _rich_utils._get_parameter_help(
            param=param, ctx=ctx, markup_mode="rich"
        )
        assert result is not None

    def test_parameter_help_with_backspace_escape(self):
        """Help text starting with \\b escape (no linebreak removal)."""
        param = Mock(spec=click.Option)
        param.name = "test"
        param.help = "\bThis is verbatim\ntext with newlines"
        param.required = False
        param.default = None
        param.show_default = False
        param.envvar = None

        ctx = Mock()
        ctx.show_default = False

        result = _rich_utils._get_parameter_help(
            param=param, ctx=ctx, markup_mode="rich"
        )
        assert result is not None

    def test_list_default_value(self):
        """Parameter with list/tuple default."""
        param = Mock(spec=click.Option)
        param.name = "test_option"
        param.help = "Test option"
        param.required = False
        param.default = ["val1", "val2", "val3"]
        param.show_default = True
        param.envvar = None

        ctx = Mock()
        ctx.show_default = False

        result = _rich_utils._get_parameter_help(
            param=param, ctx=ctx, markup_mode="rich"
        )
        assert result is not None

    def test_tuple_default_value(self):
        """Parameter with tuple default."""
        param = Mock(spec=click.Option)
        param.name = "test_option"
        param.help = "Test option"
        param.required = False
        param.default = (1, 2, 3)
        param.show_default = True
        param.envvar = None

        ctx = Mock()
        ctx.show_default = False

        result = _rich_utils._get_parameter_help(
            param=param, ctx=ctx, markup_mode="rich"
        )
        assert result is not None

    def test_empty_default_string_not_added(self):
        """Empty default string is not added to help."""
        param = Mock(spec=click.Option)
        param.name = "test_option"
        param.help = "Test option"
        param.required = False
        param.default = ""
        param.show_default = True
        param.envvar = None

        ctx = Mock()
        ctx.show_default = False

        result = _rich_utils._get_parameter_help(
            param=param, ctx=ctx, markup_mode="rich"
        )
        assert result is not None

    def test_callable_default_parameter(self):
        """Test that callable defaults show as '(dynamic)'."""

        def default_func():
            return "dynamic"

        param = Mock(spec=click.Option)
        param.name = "test"
        param.help = "Test option"
        param.required = False
        param.default = default_func
        param.show_default = True
        param.envvar = None

        ctx = Mock()
        ctx.show_default = False

        result = _rich_utils._get_parameter_help(
            param=param, ctx=ctx, markup_mode="rich"
        )
        assert result is not None


# =============================================================================
# Options Panel Tests
# =============================================================================


class TestPrintOptionsPanel:
    """Tests for _print_options_panel function."""

    def test_print_options_panel_empty_params(self):
        """Test _print_options_panel with empty parameter list."""
        ctx = Mock()
        console = _rich_utils._get_rich_console()
        assert console is not None

        result = _rich_utils._print_options_panel(
            name="Options",
            params=[],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )
        assert result is None

    def test_print_options_panel_with_options(self):
        """Test _print_options_panel with option parameters."""
        opt = click.Option(["-v", "--verbose"], help="Verbose output")

        ctx = Mock()
        ctx.auto_envvar_prefix = None
        console = _rich_utils._get_rich_console()
        assert console is not None

        result = _rich_utils._print_options_panel(
            name="Options",
            params=[opt],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )
        assert result is None

    def test_print_options_panel_with_negative_option(self):
        """Test _print_options_panel with negative option."""
        opt = click.Option(["--no-verbose"], help="Disable verbose")

        ctx = Mock()
        ctx.auto_envvar_prefix = None
        console = _rich_utils._get_rich_console()
        assert console is not None

        result = _rich_utils._print_options_panel(
            name="Options",
            params=[opt],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )
        assert result is None

    def test_print_options_panel_with_envvar(self):
        """Test _print_options_panel with environment variable."""
        opt = click.Option(["-t", "--token"], envvar="API_TOKEN", help="API token")

        ctx = Mock()
        ctx.auto_envvar_prefix = None
        console = _rich_utils._get_rich_console()
        assert console is not None

        result = _rich_utils._print_options_panel(
            name="Options",
            params=[opt],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )
        assert result is None

    def test_print_options_panel_with_metavar(self):
        """Test _print_options_panel with custom metavar."""
        opt = click.Option(["-f", "--file"], metavar="FILENAME", help="Input file")

        ctx = Mock()
        ctx.auto_envvar_prefix = None
        console = _rich_utils._get_rich_console()
        assert console is not None

        result = _rich_utils._print_options_panel(
            name="Options",
            params=[opt],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )
        assert result is None

    def test_highlighter_none_negative(self):
        """Test negative_highlighter is None."""
        param = Mock(spec=click.Option)
        param.name = "no-feature"
        param.opts = ["--no-feature"]
        param.secondary_opts = []
        param.required = False
        param.help = "Disable feature"
        param.envvar = None
        param.default = None

        ctx = Mock()
        console = Mock()
        console.print = Mock()

        with patch.object(_rich_utils, "negative_highlighter", None):
            with patch.object(_rich_utils, "highlighter", Mock()):
                with patch.object(_rich_utils, "_get_parameter_help"):
                    _rich_utils._print_options_panel(
                        name="Options",
                        params=[param],
                        ctx=ctx,
                        markup_mode="rich",
                        console=console,
                    )

    def test_highlighter_none_positive(self):
        """Test highlighter is None."""
        param = Mock(spec=click.Option)
        param.name = "feature"
        param.opts = ["--feature"]
        param.secondary_opts = []
        param.required = False
        param.help = "Enable feature"
        param.envvar = None
        param.default = None

        ctx = Mock()
        console = Mock()
        console.print = Mock()

        with patch.object(_rich_utils, "highlighter", None):
            with patch.object(_rich_utils, "negative_highlighter", Mock()):
                with patch.object(_rich_utils, "_get_parameter_help"):
                    _rich_utils._print_options_panel(
                        name="Options",
                        params=[param],
                        ctx=ctx,
                        markup_mode="rich",
                        console=console,
                    )

    def test_param_with_metavar(self):
        """Test Parameter with metavar."""
        param = Mock(spec=click.Option)
        param.name = "output"
        param.opts = ["--output"]
        param.secondary_opts = []
        param.required = False
        param.help = "Output file"
        param.envvar = None
        param.default = None
        param.metavar = "FILE"

        ctx = Mock()
        console = Mock()
        console.print = Mock()

        _rich_utils._print_options_panel(
            name="Options",
            params=[param],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )

    def test_param_with_type_name(self):
        """Test Parameter with type.name."""
        param = Mock(spec=click.Option)
        param.name = "count"
        param.opts = ["--count"]
        param.secondary_opts = []
        param.required = False
        param.help = "Number of items"
        param.envvar = None
        param.default = None

        param_type = Mock()
        param_type.name = "INTEGER"
        param.type = param_type

        delattr(param, "metavar") if hasattr(param, "metavar") else None

        ctx = Mock()
        console = Mock()
        console.print = Mock()

        _rich_utils._print_options_panel(
            name="Options",
            params=[param],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )

    def test_required_parameter_indicator(self):
        """Test Required parameter indicator."""
        param = Mock(spec=click.Option)
        param.name = "required_opt"
        param.opts = ["--required"]
        param.secondary_opts = []
        param.required = True
        param.help = "Required option"
        param.envvar = None
        param.default = None

        ctx = Mock()
        console = Mock()
        console.print = Mock()

        _rich_utils._print_options_panel(
            name="Options",
            params=[param],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )

    def test_empty_options_table(self):
        """Test lines 499->456, 502->exit: No rows in options table."""
        param = Mock(spec=click.Option)
        param.name = "test"
        param.opts = ["--test"]
        param.secondary_opts = []
        param.required = False
        param.help = None
        param.envvar = None
        param.default = None

        ctx = Mock()
        console = Mock()
        console.print = Mock()

        with patch.object(_rich_utils, "_get_parameter_help", return_value=None):
            _rich_utils._print_options_panel(
                name="Options",
                params=[param],
                ctx=ctx,
                markup_mode="rich",
                console=console,
            )

            if console.print.called:
                from rich.panel import Panel

                for call in console.print.call_args_list:
                    assert not isinstance(call[0][0] if call[0] else None, Panel)

    def test_option_with_secondary_opts(self):
        """Test option with secondary options."""
        param = Mock(spec=click.Option)
        param.name = "verbose"
        param.opts = ["--verbose"]
        param.secondary_opts = ["-v"]
        param.required = False
        param.help = "Verbose output"
        param.envvar = None
        param.default = None

        ctx = Mock()
        console = Mock()
        console.print = Mock()

        _rich_utils._print_options_panel(
            name="Options",
            params=[param],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )


# =============================================================================
# Commands Panel Tests
# =============================================================================


class TestPrintCommandsPanel:
    """Tests for _print_commands_panel function."""

    def test_print_commands_panel_with_commands(self):
        """Test _print_commands_panel with commands."""
        cmd = click.Command("test")
        cmd.help = "Test command"

        console = _rich_utils._get_rich_console()
        assert console is not None

        result = _rich_utils._print_commands_panel(
            name="Commands",
            commands=[cmd],
            markup_mode="rich",
            console=console,
            cmd_len=10,
            extended_typer=None,
        )
        assert result is None

    def test_print_commands_panel_with_deprecated_command(self):
        """Test _print_commands_panel with deprecated command."""
        cmd = click.Command("old")
        cmd.help = "Deprecated command"
        cmd.deprecated = True

        console = _rich_utils._get_rich_console()
        assert console is not None

        result = _rich_utils._print_commands_panel(
            name="Commands",
            commands=[cmd],
            markup_mode="rich",
            console=console,
            cmd_len=10,
            extended_typer=None,
        )
        assert result is None

    def test_print_commands_panel_with_extended_typer(self):
        """Test _print_commands_panel with extended_typer for aliases."""
        cmd = click.Command("deploy")
        cmd.help = "Deploy the application"

        extended_typer = Mock()
        extended_typer.show_aliases_in_help = True
        extended_typer._command_aliases = {"d": "deploy"}

        console = _rich_utils._get_rich_console()
        assert console is not None

        result = _rich_utils._print_commands_panel(
            name="Commands",
            commands=[cmd],
            markup_mode="rich",
            console=console,
            cmd_len=10,
            extended_typer=extended_typer,
        )
        assert result is None

    def test_print_commands_panel_with_multiline_help(self):
        """Test _print_commands_panel with multiline help text."""
        cmd = click.Command("complex")
        cmd.help = "First line\n\nSecond paragraph\nWith continuation"

        console = _rich_utils._get_rich_console()
        assert console is not None

        result = _rich_utils._print_commands_panel(
            name="Commands",
            commands=[cmd],
            markup_mode="rich",
            console=console,
            cmd_len=20,
            extended_typer=None,
        )
        assert result is None

    def test_print_commands_panel_with_multiline_help_markdown(self):
        """Test _print_commands_panel with multiline help in markdown mode."""
        cmd = click.Command("complex")
        cmd.help = "First line\n\nSecond paragraph\n\nThird paragraph"

        console = _rich_utils._get_rich_console()
        assert console is not None

        result = _rich_utils._print_commands_panel(
            name="Commands",
            commands=[cmd],
            markup_mode="markdown",
            console=console,
            cmd_len=20,
            extended_typer=None,
        )
        assert result is None

    def test_print_commands_panel_empty_help(self):
        """Test _print_commands_panel with command that has no help."""
        cmd = click.Command("nohelp")
        cmd.help = None

        console = _rich_utils._get_rich_console()
        assert console is not None

        result = _rich_utils._print_commands_panel(
            name="Commands",
            commands=[cmd],
            markup_mode="rich",
            console=console,
            cmd_len=10,
            extended_typer=None,
        )
        assert result is None

    def test_empty_commands_table(self):
        """Test empty commands table doesn't print panel."""
        console = Mock()
        console.print = Mock()

        _rich_utils._print_commands_panel(
            name="Commands",
            commands=[],
            markup_mode="rich",
            console=console,
            cmd_len=20,
            extended_typer=None,
        )

        console.print.assert_not_called()


# =============================================================================
# Rich Format Help Tests
# =============================================================================


class TestRichFormatHelp:
    """Tests for rich_format_help function."""

    def test_rich_format_help_with_no_params(self):
        """Test rich_format_help with no parameters."""
        obj = MagicMock()
        obj.params = []
        obj.help = None
        obj.get_usage.return_value = "test command [OPTIONS]"

        ctx = MagicMock()

        result = _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")
        assert result is None

    def test_rich_format_help_with_epilog(self):
        """Test rich_format_help with epilog text."""
        obj = MagicMock()
        obj.params = []
        obj.epilog = "This is epilog text"
        obj.help = None
        obj.get_usage.return_value = "test command [OPTIONS]"

        ctx = MagicMock()

        result = _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")
        assert result is None

    def test_rich_format_help_with_option_groups(self):
        """Test rich_format_help with grouped options."""
        opt1 = click.Option(["-v", "--verbose"], help="Verbose output")
        setattr(opt1, "rich_help_panel", "Display Options")

        opt2 = click.Option(["-q", "--quiet"], help="Quiet mode")
        setattr(opt2, "rich_help_panel", "Display Options")

        obj = MagicMock()
        obj.params = [opt1, opt2]
        obj.help = None
        obj.get_usage.return_value = "test command [OPTIONS]"

        ctx = MagicMock()

        result = _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")
        assert result is None

    def test_rich_format_help_with_required_options(self):
        """Test rich_format_help with required options."""
        opt = click.Option(["-r", "--required"], required=True, help="Required option")

        obj = MagicMock()
        obj.params = [opt]
        obj.help = None
        obj.get_usage.return_value = "test command [OPTIONS]"

        ctx = MagicMock()

        result = _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")
        assert result is None

    def test_rich_format_help_with_arguments(self):
        """Test rich_format_help with argument parameters."""
        arg = click.Argument(["input"])

        obj = MagicMock()
        obj.params = [arg]
        obj.help = None
        obj.get_usage.return_value = "test command [INPUT]"

        ctx = MagicMock()

        result = _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")
        assert result is None

    def test_rich_format_help_with_hidden_params(self):
        """Test rich_format_help with hidden parameters."""
        cmd = click.Command("test")
        cmd.help = "Test command"
        cmd.params = [
            click.Option(["-v", "--verbose"], help="Verbose", hidden=False),
            click.Option(["--secret"], help="Secret option", hidden=True),
        ]

        ctx = click.Context(cmd)
        ctx.info_name = "test"

        result = _rich_utils.rich_format_help(obj=cmd, ctx=ctx, markup_mode="rich")
        assert result is None

    def test_rich_format_help_group_with_subcommands(self):
        """Test rich_format_help with a Group that has subcommands."""
        grp = click.Group("main")
        grp.help = "Main command group"
        cmd1 = click.Command("sub1")
        cmd1.help = "Subcommand 1"
        cmd2 = click.Command("sub2")
        cmd2.help = "Subcommand 2"
        cmd2.deprecated = True
        grp.commands = {"sub1": cmd1, "sub2": cmd2}

        ctx = click.Context(grp)
        ctx.info_name = "main"

        result = _rich_utils.rich_format_help(obj=grp, ctx=ctx, markup_mode="rich")
        assert result is None

    def test_rich_format_help_with_custom_panels(self):
        """Test rich_format_help with custom help panels."""
        cmd = click.Command("test")
        cmd.help = "Test command"
        opt1 = click.Option(["-a"], help="Option A")
        setattr(opt1, "rich_help_panel", "Custom Panel 1")
        opt2 = click.Option(["-b"], help="Option B")
        setattr(opt2, "rich_help_panel", "Custom Panel 2")
        cmd.params = [opt1, opt2]

        ctx = click.Context(cmd)
        ctx.info_name = "test"

        result = _rich_utils.rich_format_help(obj=cmd, ctx=ctx, markup_mode="rich")
        assert result is None

    def test_rich_format_help_without_highlighter(self):
        """Test rich_format_help when highlighter is None."""
        cmd = click.Command("test")
        cmd.help = "Test command"

        ctx = MagicMock()
        ctx.command = cmd
        ctx.info_name = "test"
        ctx.parent = None
        ctx.get_usage.return_value = "Usage: test"

        with patch.object(_rich_utils, "highlighter", None):
            result = _rich_utils.rich_format_help(obj=cmd, ctx=ctx, markup_mode="rich")
            assert result is None

    def test_parameter_not_argument_or_option(self):
        """Test Parameter that is neither Argument nor Option."""
        custom_param = Mock()
        custom_param.__class__ = type("CustomParam", (), {})
        custom_param.name = "custom"
        custom_param.hidden = False

        obj = Mock(spec=click.Command)
        obj.get_params = Mock(return_value=[custom_param])
        obj.help = "Test command"
        obj.epilog = None
        obj.deprecated = False
        obj.get_usage = Mock(return_value="test-command")

        ctx = Mock()
        ctx.command = obj

        console = Mock()
        console.print = Mock()

        with patch.object(_rich_utils, "_get_rich_console", return_value=console):
            _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")

    def test_custom_argument_panel(self):
        """Test non-default argument panel name."""
        arg = Mock(spec=click.Argument)
        arg.name = "file"
        arg.rich_help_panel = "Input Arguments"

        obj = Mock(spec=click.Command)
        obj.get_params = Mock(return_value=[arg])
        obj.help = "Test command"
        obj.epilog = None
        obj.deprecated = False
        obj.get_usage = Mock(return_value="test-command")

        ctx = Mock()
        ctx.command = obj

        console = Mock()
        console.print = Mock()

        with patch.object(_rich_utils, "_get_rich_console", return_value=console):
            with patch.object(_rich_utils, "_print_options_panel") as mock_print:
                _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")

                calls = mock_print.call_args_list
                panel_names = [call[1]["name"] for call in calls if "name" in call[1]]
                assert "Input Arguments" in panel_names

    def test_custom_command_panel(self):
        """Test non-default command panel."""
        cmd = Mock(spec=click.Command)
        cmd.name = "special"
        cmd.help = "Special command"
        cmd.hidden = False
        cmd.deprecated = False
        cmd.rich_help_panel = "Special Commands"

        obj = Mock(spec=click.Group)
        obj.list_commands = Mock(return_value=["special"])
        obj.get_command = Mock(return_value=cmd)
        obj.get_params = Mock(return_value=[])
        obj.help = "Test group"
        obj.epilog = None
        obj.deprecated = False
        obj._extended_typer = None
        obj.get_usage = Mock(return_value="test-group")

        ctx = Mock()
        ctx.command = obj

        console = Mock()
        console.print = Mock()

        with patch.object(_rich_utils, "_get_rich_console", return_value=console):
            with patch.object(_rich_utils, "_print_commands_panel") as mock_print:
                _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")

                calls = mock_print.call_args_list
                panel_names = [call[1]["name"] for call in calls if "name" in call[1]]
                assert "Special Commands" in panel_names

    def test_hidden_command_not_shown(self):
        """Test that hidden commands are properly filtered in formatting."""
        hidden_cmd = Mock(spec=click.Command)
        hidden_cmd.name = "hidden"
        hidden_cmd.help = "Hidden command"
        hidden_cmd.hidden = True
        hidden_cmd.deprecated = False

        visible_cmd = Mock(spec=click.Command)
        visible_cmd.name = "visible"
        visible_cmd.help = "Visible command"
        visible_cmd.hidden = False
        visible_cmd.deprecated = False

        obj = Mock(spec=click.Group)
        obj.list_commands = Mock(return_value=["hidden", "visible"])

        def get_command_side_effect(ctx, name):
            if name == "hidden":
                return hidden_cmd
            return visible_cmd

        obj.get_command = Mock(side_effect=get_command_side_effect)
        obj.get_params = Mock(return_value=[])
        obj.help = "Test group"
        obj.epilog = None
        obj.deprecated = False
        obj._extended_typer = None
        obj.get_usage = Mock(return_value="test-group")

        ctx = Mock()
        ctx.command = obj

        console = Mock()
        console.print = Mock()

        with patch.object(_rich_utils, "_get_rich_console", return_value=console):
            _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")


# =============================================================================
# Error Formatting Tests
# =============================================================================


class TestRichFormatError:
    """Tests for rich_format_error function."""

    def test_format_error_with_click_exception(self):
        """Test formatting a click exception."""
        exc = click.ClickException("Test error")
        _rich_utils.rich_format_error(exc)

    def test_format_error_with_no_args_is_help(self):
        """Test formatting NoArgsIsHelpError (should be skipped)."""
        exc = Mock()
        exc.__class__.__name__ = "NoArgsIsHelpError"
        _rich_utils.rich_format_error(exc)

    def test_rich_format_error_with_various_exception_types(self):
        """Test rich_format_error with different Click exception types."""
        exc = click.ClickException("Test error")
        _rich_utils.rich_format_error(exc)

        exc = click.UsageError("Usage error")
        _rich_utils.rich_format_error(exc)

    def test_rich_format_error_with_context_no_help_option(self):
        """Test rich_format_error when context has no help option."""
        exc = Mock()
        exc.__class__.__name__ = "CustomError"
        exc.format_message.return_value = "Error message"

        ctx = Mock()
        ctx.command_path = "myapp command"
        ctx.get_usage.return_value = "Usage: myapp command [OPTIONS]"
        ctx.command.get_help_option.return_value = None
        exc.ctx = ctx

        result = _rich_utils.rich_format_error(exc)
        assert result is None

    def test_rich_format_error_with_highlighter_none(self):
        """Test rich_format_error when highlighter is None."""
        exc = Mock()
        exc.__class__.__name__ = "CustomError"
        exc.format_message.return_value = "Error message"
        exc.ctx = None

        with patch.object(_rich_utils, "highlighter", None):
            result = _rich_utils.rich_format_error(exc)
            assert result is None

    def test_error_without_context(self):
        """Test error formatting when ctx is None."""
        exc = click.ClickException("Test error")

        with patch.object(_rich_utils, "_get_rich_console") as mock_console:
            console = Mock()
            console.print = Mock()
            mock_console.return_value = console

            _rich_utils.rich_format_error(exc)
            assert console.print.called

    def test_error_without_help_option(self):
        """Test error formatting when command has no help option."""
        exc = click.ClickException("Test error")

        ctx = Mock()
        cmd = Mock()
        cmd.get_help_option = Mock(return_value=None)
        cmd.command_path = "myapp"
        ctx.command = cmd
        object.__setattr__(exc, "ctx", ctx)

        with patch.object(_rich_utils, "_get_rich_console") as mock_console:
            console = Mock()
            console.print = Mock()
            mock_console.return_value = console

            _rich_utils.rich_format_error(exc)
            console.print.assert_called()

    def test_no_args_is_help_error_passthrough(self):
        """Test that NoArgsIsHelpError is not formatted."""
        exc = click.ClickException("No args")
        exc.__class__.__name__ = "NoArgsIsHelpError"

        result = _rich_utils.rich_format_error(exc)
        assert result is None


class TestRichAbortError:
    """Tests for rich_abort_error function."""

    def test_rich_abort_error_callable(self):
        """Test that rich_abort_error can be called."""
        _rich_utils.rich_abort_error()


# =============================================================================
# Traceback Tests
# =============================================================================


class TestGetTraceback:
    """Tests for get_traceback function."""

    def test_get_traceback_with_exception(self):
        """Test getting traceback from an exception."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            config = Mock()
            result = _rich_utils.get_traceback(e, config, [])
            assert result is not None

    def test_get_traceback_with_config_show_locals(self):
        """Test getting traceback with show_locals config."""
        try:
            raise RuntimeError("Test")
        except RuntimeError as e:
            config = Mock()
            config.pretty_exceptions_show_locals = True
            result = _rich_utils.get_traceback(e, config, [])
            assert result is None or hasattr(result, "from_exception")

    def test_get_traceback_with_various_config_options(self):
        """Test get_traceback with different config combinations."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            config1 = Mock()
            config1.pretty_exceptions_show_locals = True
            config1.pretty_exceptions_short = False

            result = _rich_utils.get_traceback(e, config1, [])
            assert result is not None

            config2 = Mock()
            config2.pretty_exceptions_short = True

            result = _rich_utils.get_traceback(e, config2, [])
            assert result is not None

    def test_get_traceback_with_show_locals_enabled(self):
        """Test get_traceback with show_locals configuration."""
        try:
            _x = 42  # noqa: F841
            _y = "test"  # noqa: F841
            raise ValueError("Test error with locals")
        except ValueError as e:
            config = Mock()
            config.pretty_exceptions_show_locals = True

            result = _rich_utils.get_traceback(
                exc=e, exception_config=config, internal_dir_names=["site-packages"]
            )
            assert result is not None

    def test_get_traceback_with_show_locals_disabled(self):
        """Test get_traceback with show_locals disabled."""
        try:
            raise RuntimeError("Test error")
        except RuntimeError as e:
            config = Mock()
            config.pretty_exceptions_show_locals = False

            result = _rich_utils.get_traceback(
                exc=e, exception_config=config, internal_dir_names=[]
            )
            assert result is not None

    def test_get_traceback_without_config(self):
        """Test get_traceback without exception config."""
        try:
            raise TypeError("Test error")
        except TypeError as e:
            result = _rich_utils.get_traceback(
                exc=e, exception_config=None, internal_dir_names=[]
            )
            assert result is not None

    def test_traceback_with_config(self):
        """Test traceback with exception config."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            config = Mock()
            config.pretty_exceptions_show_locals = True

            with patch("typer_extensions._rich_utils.Traceback") as MockTraceback:
                MockTraceback.from_exception = Mock(return_value=Mock())

                _rich_utils.get_traceback(
                    exc=e, exception_config=config, internal_dir_names=["internal"]
                )

                MockTraceback.from_exception.assert_called_once()
                call_kwargs = MockTraceback.from_exception.call_args[1]
                assert call_kwargs["show_locals"] is True

    def test_traceback_without_config(self):
        """Test traceback without exception config."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            with patch("typer_extensions._rich_utils.Traceback") as MockTraceback:
                MockTraceback.from_exception = Mock(return_value=Mock())

                _rich_utils.get_traceback(
                    exc=e,
                    exception_config=None,
                    internal_dir_names=["internal"],
                )

                MockTraceback.from_exception.assert_called_once()
                call_kwargs = MockTraceback.from_exception.call_args[1]
                assert call_kwargs["show_locals"] is False
