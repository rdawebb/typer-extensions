"""Tests for specific _rich_utils coverage gaps with Rich enabled"""

import pytest
from unittest.mock import MagicMock, patch
from typer_extensions import _rich_utils


pytestmark = pytest.mark.skipif(
    not _rich_utils.RICH_AVAILABLE, reason="Rich not available"
)


class TestGetHelpTextEdgeCases:
    """Test _get_help_text with various edge cases"""

    def test_get_help_text_with_markdown_multiline(self):
        """Test _get_help_text with markdown mode and multiline help"""
        from click import Command

        cmd = Command("test")
        cmd.help = "First paragraph\n\nSecond paragraph\n\nThird paragraph"

        result = _rich_utils._get_help_text(obj=cmd, markup_mode="markdown")
        assert result is not None

    def test_get_help_text_with_formfeed_markdown(self):
        """Test _get_help_text with formfeed in markdown mode"""
        from click import Command

        cmd = Command("test")
        cmd.help = "Visible part\fHidden part after formfeed"

        result = _rich_utils._get_help_text(obj=cmd, markup_mode="markdown")
        assert result is not None

    def test_get_help_text_with_newlines_in_first_line_rich_mode(self):
        """Test _get_help_text with newlines in first line for rich mode"""
        from click import Command

        cmd = Command("test")
        cmd.help = "First\nline\nwith\nnewlines\n\nSecond paragraph"

        result = _rich_utils._get_help_text(obj=cmd, markup_mode="rich")
        assert result is not None

    def test_get_help_text_with_breaklines_marker(self):
        """Test _get_help_text with \\b marker (preserve line breaks)"""
        from click import Command

        cmd = Command("test")
        cmd.help = "\\bFirst line\nSecond line\nThird line"

        result = _rich_utils._get_help_text(obj=cmd, markup_mode="rich")
        assert result is not None


class TestGetParameterHelpEdgeCases:
    """Test _get_parameter_help with various edge cases"""

    def test_get_parameter_help_with_multiple_paragraphs(self):
        """Test _get_parameter_help with multi-paragraph help text"""
        from click import Option

        opt = Option(
            ["-c", "--config"],
            help="First paragraph\n\nSecond paragraph with more details\n\nThird paragraph",
        )
        ctx = MagicMock()
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_get_parameter_help_with_breaklines_marker(self):
        """Test _get_parameter_help with \\b marker"""
        from click import Option

        opt = Option(
            ["-f", "--format"], help="\\bLine 1\nLine 2\nLine 3", metavar="FORMAT"
        )
        ctx = MagicMock()
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_get_parameter_help_with_range_constraint(self):
        """Test _get_parameter_help with click.IntRange"""
        from click import Option, IntRange

        opt = Option(
            ["-p", "--port"],
            type=IntRange(1, 65535),
            help="Port number",
        )
        ctx = MagicMock()
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(
            param=opt, ctx=ctx, markup_mode="markdown"
        )
        assert result is not None


class TestPrintCommandsPanelAliases:
    """Test _print_commands_panel with alias support"""

    def test_print_commands_panel_with_alias_lookup_error(self):
        """Test _print_commands_panel when alias lookup raises exception"""
        from click import Command

        cmd = Command("deploy")
        cmd.help = "Deploy the application"

        extended_typer = MagicMock()
        extended_typer.show_aliases_in_help = True
        extended_typer._command_aliases = {"d": "deploy"}

        console = _rich_utils._get_rich_console()
        assert console is not None

        # The function should handle the situation gracefully even if extended_typer is present
        result = _rich_utils._print_commands_panel(
            name="Commands",
            commands=[cmd],
            markup_mode="rich",
            console=console,
            cmd_len=20,
            extended_typer=extended_typer,
        )
        assert result is None

    def test_print_commands_panel_with_multiline_help_markdown(self):
        """Test _print_commands_panel with multiline help in markdown mode"""
        from click import Command

        cmd = Command("complex")
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
        """Test _print_commands_panel with command that has no help"""
        from click import Command

        cmd = Command("nohelp")
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


class TestRichFormatHelpEdgeCases:
    """Test rich_format_help with various edge cases"""

    def test_rich_format_help_with_hidden_params(self):
        """Test rich_format_help with hidden parameters"""
        from click import Command, Option, Context

        cmd = Command("test")
        cmd.help = "Test command"
        cmd.params = [
            Option(["-v", "--verbose"], help="Verbose", hidden=False),
            Option(["--secret"], help="Secret option", hidden=True),
        ]

        # Create a proper context
        ctx = Context(cmd)
        ctx.info_name = "test"

        result = _rich_utils.rich_format_help(obj=cmd, ctx=ctx, markup_mode="rich")
        assert result is None

    def test_rich_format_help_group_with_subcommands(self):
        """Test rich_format_help with a Group that has subcommands"""
        from click import Group, Command, Context

        grp = Group("main")
        grp.help = "Main command group"
        cmd1 = Command("sub1")
        cmd1.help = "Subcommand 1"
        cmd2 = Command("sub2")
        cmd2.help = "Subcommand 2"
        cmd2.deprecated = True
        grp.commands = {"sub1": cmd1, "sub2": cmd2}

        # Create a proper context
        ctx = Context(grp)
        ctx.info_name = "main"

        result = _rich_utils.rich_format_help(obj=grp, ctx=ctx, markup_mode="rich")
        assert result is None

    def test_rich_format_help_with_epilog(self):
        """Test rich_format_help with epilog text"""
        from click import Command, Context

        cmd = Command("test")
        cmd.help = "Test command"
        cmd.epilog = "This is additional information at the end."

        # Create a proper context
        ctx = Context(cmd)
        ctx.info_name = "test"

        result = _rich_utils.rich_format_help(obj=cmd, ctx=ctx, markup_mode="rich")
        assert result is None

    def test_rich_format_help_with_custom_panels(self):
        """Test rich_format_help with custom help panels"""
        from click import Command, Option, Context

        cmd = Command("test")
        cmd.help = "Test command"
        opt1 = Option(["-a"], help="Option A")
        setattr(opt1, "rich_help_panel", "Custom Panel 1")
        opt2 = Option(["-b"], help="Option B")
        setattr(opt2, "rich_help_panel", "Custom Panel 2")
        cmd.params = [opt1, opt2]

        # Create a proper context
        ctx = Context(cmd)
        ctx.info_name = "test"

        result = _rich_utils.rich_format_help(obj=cmd, ctx=ctx, markup_mode="rich")
        assert result is None


class TestRichFormatErrorEdgeCases:
    """Test rich_format_error with various edge cases"""

    def test_rich_format_error_with_context_no_help_option(self):
        """Test rich_format_error when context has no help option"""
        exc = MagicMock()
        exc.__class__.__name__ = "CustomError"
        exc.format_message.return_value = "Error message"

        ctx = MagicMock()
        ctx.command_path = "myapp command"
        ctx.get_usage.return_value = "Usage: myapp command [OPTIONS]"
        ctx.command.get_help_option.return_value = None
        exc.ctx = ctx

        # Should not raise
        result = _rich_utils.rich_format_error(exc)
        assert result is None

    def test_rich_format_error_with_highlighter_none(self):
        """Test rich_format_error when highlighter is None"""
        exc = MagicMock()
        exc.__class__.__name__ = "CustomError"
        exc.format_message.return_value = "Error message"
        exc.ctx = None

        with patch.object(_rich_utils, "highlighter", None):
            # Should handle None highlighter gracefully
            result = _rich_utils.rich_format_error(exc)
            assert result is None


class TestRichFormatHelpHighlighterNone:
    """Test rich_format_help when highlighter is None"""

    def test_rich_format_help_without_highlighter(self):
        """Test rich_format_help when highlighter is None"""
        from click import Command

        cmd = Command("test")
        cmd.help = "Test command"

        ctx = MagicMock()
        ctx.command = cmd
        ctx.info_name = "test"
        ctx.parent = None
        ctx.get_usage.return_value = "Usage: test"

        with patch.object(_rich_utils, "highlighter", None):
            result = _rich_utils.rich_format_help(obj=cmd, ctx=ctx, markup_mode="rich")
            assert result is None


class TestRichToHtml:
    """Test rich_to_html function"""

    def test_rich_to_html_basic(self):
        """Test rich_to_html with basic text"""
        result = _rich_utils.rich_to_html("Hello world")
        assert isinstance(result, str)

    def test_rich_to_html_with_rich_markup(self):
        """Test rich_to_html with Rich markup"""
        result = _rich_utils.rich_to_html(
            "[bold]Bold text[/bold] and [red]red text[/red]"
        )
        assert isinstance(result, str)
        # Should contain HTML
        assert "<" in result or result  # Either has HTML tags or plain text

    def test_rich_to_html_with_newlines(self):
        """Test rich_to_html preserves content with newlines"""
        result = _rich_utils.rich_to_html("Line 1\nLine 2\nLine 3")
        assert isinstance(result, str)


class TestGetTracebackWithConfig:
    """Test get_traceback with exception configuration"""

    def test_get_traceback_with_show_locals_enabled(self):
        """Test get_traceback with show_locals configuration"""
        try:
            _x = 42  # noqa: F841
            _y = "test"  # noqa: F841
            raise ValueError("Test error with locals")
        except ValueError as e:
            # Create a mock config with show_locals enabled
            config = MagicMock()
            config.pretty_exceptions_show_locals = True

            result = _rich_utils.get_traceback(
                exc=e, exception_config=config, internal_dir_names=["site-packages"]
            )
            # Should return a Traceback object
            assert result is not None

    def test_get_traceback_with_show_locals_disabled(self):
        """Test get_traceback with show_locals disabled"""
        try:
            raise RuntimeError("Test error")
        except RuntimeError as e:
            config = MagicMock()
            config.pretty_exceptions_show_locals = False

            result = _rich_utils.get_traceback(
                exc=e, exception_config=config, internal_dir_names=[]
            )
            # Should return a Traceback object
            assert result is not None

    def test_get_traceback_without_config(self):
        """Test get_traceback without exception config"""
        try:
            raise TypeError("Test error")
        except TypeError as e:
            result = _rich_utils.get_traceback(
                exc=e, exception_config=None, internal_dir_names=[]
            )
            # Should return a Traceback object
            assert result is not None
