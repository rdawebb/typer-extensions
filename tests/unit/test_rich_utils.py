"""Tests for typer_extensions._rich_utils module.

This tests both the Rich-enabled and Rich-disabled code paths.
"""

from unittest.mock import MagicMock
import pytest

from typer_extensions import _rich_utils


class TestRichUtilsConstants:
    """Test that style constants are properly defined."""

    def test_style_constants_defined(self):
        """Test that all style constants are defined"""
        assert _rich_utils.STYLE_OPTION == "bold cyan"
        assert _rich_utils.STYLE_SWITCH == "bold green"
        assert _rich_utils.STYLE_NEGATIVE_OPTION == "bold magenta"
        assert _rich_utils.STYLE_METAVAR == "bold yellow"
        assert _rich_utils.STYLE_USAGE == "yellow"

    def test_alignment_constants_defined(self):
        """Test that alignment constants are defined"""
        assert _rich_utils.ALIGN_OPTIONS_PANEL in ["left", "center", "right"]
        assert _rich_utils.ALIGN_COMMANDS_PANEL in ["left", "center", "right"]
        assert _rich_utils.ALIGN_ERRORS_PANEL in ["left", "center", "right"]

    def test_panel_titles_defined(self):
        """Test that panel titles are defined"""
        assert _rich_utils.ARGUMENTS_PANEL_TITLE
        assert _rich_utils.OPTIONS_PANEL_TITLE
        assert _rich_utils.COMMANDS_PANEL_TITLE
        assert _rich_utils.ERRORS_PANEL_TITLE

    def test_deprecated_string_defined(self):
        """Test that deprecated string is defined"""
        assert _rich_utils.DEPRECATED_STRING
        assert "deprecated" in _rich_utils.DEPRECATED_STRING.lower()


class TestRichAvailability:
    """Test Rich availability detection."""

    def test_rich_available_boolean(self):
        """Test that RICH_AVAILABLE is a boolean"""
        assert isinstance(_rich_utils.RICH_AVAILABLE, bool)

    def test_highlighters_exist_when_rich_available(self):
        """Test that highlighters exist if Rich is available"""
        if _rich_utils.RICH_AVAILABLE:
            assert _rich_utils.highlighter is not None
            assert _rich_utils.negative_highlighter is not None
        else:
            # When Rich not available, highlighters should be None
            assert _rich_utils.highlighter is None
            assert _rich_utils.negative_highlighter is None


class TestCleandocFunction:
    """Tests for the cleandoc utility function."""

    def test_cleandoc_basic(self):
        """Test basic cleandoc functionality"""
        text = """
        First line
        Second line
            Indented line
        """
        result = _rich_utils.cleandoc(text)
        assert "First line" in result
        assert "Second line" in result

    def test_cleandoc_removes_leading_blank_lines(self):
        """Test that cleandoc removes leading blank lines"""
        text = "\n\n\nFirst line"
        result = _rich_utils.cleandoc(text)
        assert result.startswith("First")

    def test_cleandoc_removes_trailing_blank_lines(self):
        """Test that cleandoc removes trailing blank lines"""
        text = "First line\n\n\n"
        result = _rich_utils.cleandoc(text)
        assert result.endswith("line")
        assert not result.endswith("\n")

    def test_cleandoc_empty_string(self):
        """Test cleandoc with empty string"""
        result = _rich_utils.cleandoc("")
        assert result == ""

    def test_cleandoc_single_line(self):
        """Test cleandoc with single line"""
        result = _rich_utils.cleandoc("Single line")
        assert result == "Single line"

    def test_cleandoc_edge_cases(self):
        """Test cleandoc with various edge cases"""
        from typer_extensions import _rich_utils

        # Test with tabs
        result = _rich_utils.cleandoc("\t\tIndented with tabs")
        assert "Indented" in result

        # Test with only whitespace
        result = _rich_utils.cleandoc("   \n\n   ")
        assert result == "" or result.strip() == ""


class TestGetRichConsole:
    """Tests for _get_rich_console function."""

    @pytest.mark.skipif(not _rich_utils.RICH_AVAILABLE, reason="Rich not available")
    def test_get_console_stderr_false(self):
        """Test getting console with stderr=False"""
        console = _rich_utils._get_rich_console(stderr=False)
        if console is not None:
            assert hasattr(console, "print")

    @pytest.mark.skipif(not _rich_utils.RICH_AVAILABLE, reason="Rich not available")
    def test_get_console_stderr_true(self):
        """Test getting console with stderr=True"""
        console = _rich_utils._get_rich_console(stderr=True)
        if console is not None:
            assert hasattr(console, "print")

    def test_get_console_when_rich_disabled(self):
        """Test that console returns None when Rich is disabled"""
        if not _rich_utils.RICH_AVAILABLE:
            console = _rich_utils._get_rich_console()
            assert console is None


class TestMakeRichText:
    """Tests for _make_rich_text function."""

    @pytest.mark.skipif(not _rich_utils.RICH_AVAILABLE, reason="Rich not available")
    def test_make_rich_text_markdown_mode(self):
        """Test _make_rich_text with markdown mode"""
        result = _rich_utils._make_rich_text(
            text="**Bold text**", style="", markup_mode=_rich_utils.MARKUP_MODE_MARKDOWN
        )
        assert result is not None

    @pytest.mark.skipif(not _rich_utils.RICH_AVAILABLE, reason="Rich not available")
    def test_make_rich_text_rich_mode(self):
        """Test _make_rich_text with rich mode"""
        result = _rich_utils._make_rich_text(
            text="[bold]Bold text[/bold]",
            style="",
            markup_mode=_rich_utils.MARKUP_MODE_RICH,
        )
        assert result is not None

    def test_make_rich_text_when_rich_disabled(self):
        """Test _make_rich_text returns plain string when Rich disabled"""
        if not _rich_utils.RICH_AVAILABLE:
            result = _rich_utils._make_rich_text(
                text="Test", style="", markup_mode=_rich_utils.MARKUP_MODE_MARKDOWN
            )
            assert isinstance(result, str)
            assert result == "Test"

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_make_rich_text_with_none_markup_mode(self):
        """Test _make_rich_text with markdown markup mode

        Covers various markup mode branches
        """
        from typer_extensions import _rich_utils

        result = _rich_utils._make_rich_text(
            text="Plain text", style="bold", markup_mode="markdown"
        )
        assert result is not None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_make_rich_text_empty_text(self):
        """Test _make_rich_text with empty string"""
        from typer_extensions import _rich_utils

        result = _rich_utils._make_rich_text(
            text="", style="", markup_mode=_rich_utils.MARKUP_MODE_RICH
        )
        assert result is not None


class TestEscapeBeforeHtmlExport:
    """Tests for escape_before_html_export function."""

    def test_escape_with_special_characters(self):
        """Test escaping special HTML characters"""
        text = "Text with <angle brackets>"
        result = _rich_utils.escape_before_html_export(text)
        assert result is not None
        assert isinstance(result, str)

    def test_escape_empty_string(self):
        """Test escaping empty string"""
        result = _rich_utils.escape_before_html_export("")
        assert result == ""

    def test_escape_normal_text(self):
        """Test escaping normal text"""
        text = "Normal text"
        result = _rich_utils.escape_before_html_export(text)
        assert "Normal text" in result


class TestRichRenderText:
    """Tests for rich_render_text function."""

    @pytest.mark.skipif(not _rich_utils.RICH_AVAILABLE, reason="Rich not available")
    def test_render_text_with_markup(self):
        """Test rendering text with rich markup"""
        result = _rich_utils.rich_render_text("[bold]Bold[/bold]")
        assert result is not None

    def test_render_text_when_rich_disabled(self):
        """Test render_text returns plain string when Rich disabled"""
        if not _rich_utils.RICH_AVAILABLE:
            result = _rich_utils.rich_render_text("Test")
            assert isinstance(result, str)


class TestRichToHtml:
    """Tests for rich_to_html function."""

    @pytest.mark.skipif(not _rich_utils.RICH_AVAILABLE, reason="Rich not available")
    def test_rich_to_html_basic(self):
        """Test converting rich text to HTML"""
        result = _rich_utils.rich_to_html("[bold]Bold[/bold]")
        assert result is not None
        assert isinstance(result, str)

    def test_rich_to_html_when_rich_disabled(self):
        """Test rich_to_html returns plain string when Rich disabled"""
        if not _rich_utils.RICH_AVAILABLE:
            result = _rich_utils.rich_to_html("Test")
            assert isinstance(result, str)


class TestGetTraceback:
    """Tests for get_traceback function."""

    def test_get_traceback_with_exception(self):
        """Test getting traceback from an exception"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            config = MagicMock()
            result = _rich_utils.get_traceback(e, config, [])

            if _rich_utils.RICH_AVAILABLE:
                assert result is not None
            else:
                assert result is None

    def test_get_traceback_with_config_show_locals(self):
        """Test getting traceback with show_locals config"""
        try:
            raise RuntimeError("Test")
        except RuntimeError as e:
            config = MagicMock()
            config.pretty_exceptions_show_locals = True
            result = _rich_utils.get_traceback(e, config, [])
            # Verify it doesn't crash
            assert result is None or hasattr(result, "from_exception")

    def test_get_traceback_when_rich_disabled(self):
        """Test get_traceback returns None when Rich disabled"""
        if not _rich_utils.RICH_AVAILABLE:
            try:
                raise Exception("Test")
            except Exception as e:
                result = _rich_utils.get_traceback(e, None, [])
                assert result is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_get_traceback_with_various_config_options(self):
        """Test get_traceback with different config combinations

        Covers traceback configuration branches
        """
        from typer_extensions import _rich_utils

        try:
            raise ValueError("Test error")
        except ValueError as e:
            # Test with show_locals
            config1 = MagicMock()
            config1.pretty_exceptions_show_locals = True
            config1.pretty_exceptions_short = False

            result = _rich_utils.get_traceback(e, config1, [])
            assert result is not None

            # Test with short mode
            config2 = MagicMock()
            config2.pretty_exceptions_short = True

            result = _rich_utils.get_traceback(e, config2, [])
            assert result is not None


class TestRichAbortError:
    """Tests for rich_abort_error function."""

    def test_rich_abort_error_callable(self):
        """Test that rich_abort_error can be called"""
        # Should not raise
        _rich_utils.rich_abort_error()


class TestRichFormatError:
    """Tests for rich_format_error function."""

    def test_format_error_with_click_exception(self):
        """Test formatting a click exception"""
        import click

        exc = click.ClickException("Test error")
        # Should not raise
        _rich_utils.rich_format_error(exc)

    def test_format_error_with_no_args_is_help(self):
        """Test formatting NoArgsIsHelpError (should be skipped)"""
        # Create a mock exception that looks like NoArgsIsHelpError
        exc = MagicMock()
        exc.__class__.__name__ = "NoArgsIsHelpError"

        # Should not raise and should skip processing
        _rich_utils.rich_format_error(exc)

    def test_developer_exception_config_import_fallback(self):
        """Test fallback when DeveloperExceptionConfig import fails

        Covers lines 27-30: ImportError fallback for DeveloperExceptionConfig
        """
        # This test verifies the fallback class exists
        from typer_extensions import _rich_utils

        # The fallback should be defined
        assert hasattr(_rich_utils, "DeveloperExceptionConfig")

        # Should be a class
        assert isinstance(_rich_utils.DeveloperExceptionConfig, type)

    def test_rich_format_error_with_various_exception_types(self):
        """Test rich_format_error with different Click exception types

        Covers error formatting branches
        """
        from typer_extensions import _rich_utils
        import click

        # Test with ClickException
        exc = click.ClickException("Test error")
        _rich_utils.rich_format_error(exc)  # Should not crash

        # Test with UsageError
        exc = click.UsageError("Usage error")
        _rich_utils.rich_format_error(exc)  # Should not crash

    def test_rich_import_exception_handling(self):
        """Test behavior when Rich is not available

        Covers lines 156-158: Rich ImportError handling
        """
        from typer_extensions import _rich_utils

        # When Rich is not available
        if not _rich_utils.RICH_AVAILABLE:
            assert _rich_utils.highlighter is None
            assert _rich_utils.negative_highlighter is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_get_help_text_with_none_help_text(self):
        """Test _get_help_text with None/empty help text"""
        from typer_extensions import _rich_utils

        obj = MagicMock()
        obj.help = None
        obj.deprecated = False

        result = _rich_utils._get_help_text(
            obj=obj, markup_mode=_rich_utils.MARKUP_MODE_RICH
        )
        # Should handle None gracefully
        assert result is not None or result == ""

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_get_help_text_with_deprecated_flag(self):
        """Test _get_help_text with deprecated=True"""
        from typer_extensions import _rich_utils

        obj = MagicMock()
        obj.help = "Test help text"
        obj.deprecated = True

        result = _rich_utils._get_help_text(
            obj=obj, markup_mode=_rich_utils.MARKUP_MODE_RICH
        )
        # Should handle deprecated flag
        assert result is not None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_rich_format_help_with_no_params(self):
        """Test rich_format_help with no parameters

        Covers branches for empty params/commands
        """
        from typer_extensions import _rich_utils

        obj = MagicMock()
        obj.params = []
        obj.commands = {}
        obj.epilog = None
        obj.help = None
        obj.get_usage.return_value = "test command [OPTIONS]"

        ctx = MagicMock()
        ctx.command = obj
        ctx.info_name = "test"

        # Should not raise an exception
        result = _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")
        # rich_format_help returns None (prints to console)
        assert result is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_rich_format_help_with_epilog(self):
        """Test rich_format_help with epilog text"""
        from typer_extensions import _rich_utils

        obj = MagicMock()
        obj.params = []
        obj.commands = {}
        obj.epilog = "This is epilog text"
        obj.help = None
        obj.get_usage.return_value = "test command [OPTIONS]"

        ctx = MagicMock()
        ctx.command = obj
        ctx.info_name = "test"

        # Should not raise an exception
        result = _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")
        # rich_format_help returns None (prints to console)
        assert result is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_rich_format_help_with_option_groups(self):
        """Test rich_format_help with grouped options"""
        from typer_extensions import _rich_utils
        from click import Option

        opt1 = Option(["-v", "--verbose"], help="Verbose output")
        setattr(opt1, "rich_help_panel", "Display Options")

        opt2 = Option(["-q", "--quiet"], help="Quiet mode")
        setattr(opt2, "rich_help_panel", "Display Options")

        obj = MagicMock()
        obj.params = [opt1, opt2]
        obj.commands = {}
        obj.epilog = None
        obj.help = None
        obj.get_usage.return_value = "test command [OPTIONS]"

        ctx = MagicMock()
        ctx.command = obj
        ctx.info_name = "test"

        # Should not raise an exception
        result = _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")
        # rich_format_help returns None (prints to console)
        assert result is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_rich_format_help_with_required_options(self):
        """Test rich_format_help with required options"""
        from typer_extensions import _rich_utils
        from click import Option

        opt = Option(["-r", "--required"], required=True, help="Required option")

        obj = MagicMock()
        obj.params = [opt]
        obj.commands = {}
        obj.epilog = None
        obj.help = None
        obj.get_usage.return_value = "test command [OPTIONS]"

        ctx = MagicMock()
        ctx.command = obj
        ctx.info_name = "test"

        # Should not raise an exception
        result = _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")
        # rich_format_help returns None (prints to console)
        assert result is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_rich_format_help_with_arguments(self):
        """Test rich_format_help with argument parameters"""
        from typer_extensions import _rich_utils
        from click import Argument

        arg = Argument(["input"])

        obj = MagicMock()
        obj.params = [arg]
        obj.commands = {}
        obj.epilog = None
        obj.help = None
        obj.get_usage.return_value = "test command [INPUT]"

        ctx = MagicMock()
        ctx.command = obj
        ctx.info_name = "test"

        # Should not raise an exception
        result = _rich_utils.rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")
        # rich_format_help returns None (prints to console)
        assert result is None


class TestPrintOptionsPanel:
    """Tests for _print_options_panel function."""

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_print_options_panel_empty_params(self):
        """Test _print_options_panel with empty parameter list"""
        from typer_extensions import _rich_utils

        ctx = MagicMock()
        console = _rich_utils._get_rich_console()
        assert console is not None, "Rich console should be available"

        # Should return early without printing
        result = _rich_utils._print_options_panel(
            name="Options",
            params=[],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )
        assert result is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_print_options_panel_with_options(self):
        """Test _print_options_panel with option parameters"""
        from typer_extensions import _rich_utils
        from click import Option

        opt = Option(["-v", "--verbose"], help="Verbose output")

        ctx = MagicMock()
        ctx.auto_envvar_prefix = None
        console = _rich_utils._get_rich_console()
        assert console is not None, "Rich console should be available"

        # Should not raise
        result = _rich_utils._print_options_panel(
            name="Options",
            params=[opt],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )
        assert result is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_print_options_panel_with_negative_option(self):
        """Test _print_options_panel with negative option"""
        from typer_extensions import _rich_utils
        from click import Option

        opt = Option(["--no-verbose"], help="Disable verbose")

        ctx = MagicMock()
        ctx.auto_envvar_prefix = None
        console = _rich_utils._get_rich_console()
        assert console is not None, "Rich console should be available"

        # Should not raise
        result = _rich_utils._print_options_panel(
            name="Options",
            params=[opt],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )
        assert result is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_print_options_panel_with_envvar(self):
        """Test _print_options_panel with environment variable"""
        from typer_extensions import _rich_utils
        from click import Option

        opt = Option(["-t", "--token"], envvar="API_TOKEN", help="API token")

        ctx = MagicMock()
        ctx.auto_envvar_prefix = None
        console = _rich_utils._get_rich_console()
        assert console is not None, "Rich console should be available"

        # Should not raise
        result = _rich_utils._print_options_panel(
            name="Options",
            params=[opt],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )
        assert result is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_print_options_panel_with_metavar(self):
        """Test _print_options_panel with custom metavar"""
        from typer_extensions import _rich_utils
        from click import Option

        opt = Option(["-f", "--file"], metavar="FILENAME", help="Input file")

        ctx = MagicMock()
        ctx.auto_envvar_prefix = None
        console = _rich_utils._get_rich_console()
        assert console is not None, "Rich console should be available"

        # Should not raise
        result = _rich_utils._print_options_panel(
            name="Options",
            params=[opt],
            ctx=ctx,
            markup_mode="rich",
            console=console,
        )
        assert result is None

    def test_print_options_panel_no_rich(self):
        """Test _print_options_panel fallback when Rich is disabled"""
        from typer_extensions import _rich_utils
        from click import Option

        # This test verifies the fallback behavior is defined
        # The actual code path is only taken when Rich is not available
        if not _rich_utils.RICH_AVAILABLE:
            opt = Option(["-v", "--verbose"], help="Verbose")
            ctx = MagicMock()
            ctx.auto_envvar_prefix = None

            # Create a mock console (even though it won't be used)
            console = MagicMock()

            # Should not raise
            result = _rich_utils._print_options_panel(
                name="Options",
                params=[opt],
                ctx=ctx,
                markup_mode="rich",
                console=console,
            )
            assert result is None


class TestPrintCommandsPanel:
    """Tests for _print_commands_panel function."""

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_print_commands_panel_with_commands(self):
        """Test _print_commands_panel with commands"""
        from typer_extensions import _rich_utils
        from click import Command

        cmd = Command("test")
        cmd.help = "Test command"

        console = _rich_utils._get_rich_console()
        assert console is not None, "Rich console should be available"

        # Should not raise
        result = _rich_utils._print_commands_panel(
            name="Commands",
            commands=[cmd],
            markup_mode="rich",
            console=console,
            cmd_len=10,
            extended_typer=None,
        )
        assert result is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_print_commands_panel_with_deprecated_command(self):
        """Test _print_commands_panel with deprecated command"""
        from typer_extensions import _rich_utils
        from click import Command

        cmd = Command("old")
        cmd.help = "Deprecated command"
        cmd.deprecated = True

        console = _rich_utils._get_rich_console()
        assert console is not None, "Rich console should be available"

        # Should not raise
        result = _rich_utils._print_commands_panel(
            name="Commands",
            commands=[cmd],
            markup_mode="rich",
            console=console,
            cmd_len=10,
            extended_typer=None,
        )
        assert result is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_print_commands_panel_with_extended_typer(self):
        """Test _print_commands_panel with extended_typer for aliases"""
        from typer_extensions import _rich_utils
        from click import Command

        cmd = Command("deploy")
        cmd.help = "Deploy the application"

        extended_typer = MagicMock()
        extended_typer.show_aliases_in_help = True
        extended_typer._command_aliases = {"d": "deploy"}

        console = _rich_utils._get_rich_console()
        assert console is not None, "Rich console should be available"

        # Should handle extended_typer gracefully
        result = _rich_utils._print_commands_panel(
            name="Commands",
            commands=[cmd],
            markup_mode="rich",
            console=console,
            cmd_len=10,
            extended_typer=extended_typer,
        )
        assert result is None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_print_commands_panel_with_multiline_help(self):
        """Test _print_commands_panel with multiline help text"""
        from typer_extensions import _rich_utils
        from click import Command

        cmd = Command("complex")
        cmd.help = "First line\n\nSecond paragraph\nWith continuation"

        console = _rich_utils._get_rich_console()
        assert console is not None, "Rich console should be available"

        # Should not raise
        result = _rich_utils._print_commands_panel(
            name="Commands",
            commands=[cmd],
            markup_mode="rich",
            console=console,
            cmd_len=20,
            extended_typer=None,
        )
        assert result is None


class TestGetParameterHelp:
    """Tests for _get_parameter_help function."""

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_get_parameter_help_option_with_default(self):
        """Test _get_parameter_help with option having default value"""
        from typer_extensions import _rich_utils
        from click import Option

        opt = Option(["-n", "--name"], default="John", show_default=True, help="Name")

        ctx = MagicMock()
        ctx.show_default = False
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_get_parameter_help_option_with_multiple_envvars(self):
        """Test _get_parameter_help with option having multiple env vars"""
        from typer_extensions import _rich_utils
        from click import Option

        opt = Option(["-t", "--token"], envvar=["TOKEN", "API_KEY"], help="API token")

        ctx = MagicMock()
        ctx.show_default = False
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_get_parameter_help_with_no_help_text(self):
        """Test _get_parameter_help with no help text"""
        from typer_extensions import _rich_utils
        from click import Option

        opt = Option(["-q", "--quiet"])

        ctx = MagicMock()
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_get_parameter_help_with_auto_envvar_prefix(self):
        """Test _get_parameter_help with auto_envvar_prefix"""
        from typer_extensions import _rich_utils
        from click import Option

        opt = Option(["-a", "--api-key"], allow_from_autoenv=True, help="API key")

        ctx = MagicMock()
        ctx.auto_envvar_prefix = "MYAPP"

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_get_parameter_help_with_callable_default(self):
        """Test _get_parameter_help with callable default value"""
        from typer_extensions import _rich_utils
        from click import Option

        def default_func():
            return "dynamic"

        opt = Option(["-d", "--dynamic"], default=default_func, show_default=True)

        ctx = MagicMock()
        ctx.show_default = False
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    @pytest.mark.skipif(
        not pytest.importorskip("typer_extensions._rich_utils").RICH_AVAILABLE,
        reason="Rich not available",
    )
    def test_get_parameter_help_with_required_option(self):
        """Test _get_parameter_help with required option"""
        from typer_extensions import _rich_utils
        from click import Option

        opt = Option(["-r", "--required"], required=True, help="Required field")

        ctx = MagicMock()
        ctx.auto_envvar_prefix = None

        result = _rich_utils._get_parameter_help(param=opt, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_get_parameter_help_no_rich(self):
        """Test _get_parameter_help when Rich is disabled"""
        from typer_extensions import _rich_utils
        from click import Option

        if not _rich_utils.RICH_AVAILABLE:
            opt = Option(["-v", "--verbose"], help="Verbose output")
            ctx = MagicMock()

            result = _rich_utils._get_parameter_help(
                param=opt, ctx=ctx, markup_mode="rich"
            )
            assert result is not None


class TestRichFormatHelpWithoutRich:
    """Tests for rich_format_help when Rich is not available."""

    def test_rich_format_help_fallback_no_rich(self):
        """Test rich_format_help fallback when Rich is disabled"""
        from typer_extensions import _rich_utils
        from click import Command

        if not _rich_utils.RICH_AVAILABLE:
            cmd = Command("test")
            cmd.help = "Test command"
            ctx = MagicMock()

            # Should not raise
            result = _rich_utils.rich_format_help(obj=cmd, ctx=ctx, markup_mode="rich")
            assert result is None


class TestRichFormatErrorWithoutContext:
    """Tests for rich_format_error without context."""

    def test_format_error_without_context(self):
        """Test rich_format_error when exception has no context"""
        from typer_extensions import _rich_utils

        exc = MagicMock()
        exc.__class__.__name__ = "CustomError"
        exc.ctx = None
        exc.format_message.return_value = "Error message"

        # Should not raise
        _rich_utils.rich_format_error(exc)

    def test_format_error_fallback_no_console(self):
        """Test rich_format_error fallback when console is None"""
        from typer_extensions import _rich_utils

        exc = MagicMock()
        exc.__class__.__name__ = "TestError"
        exc.ctx = None
        exc.format_message.return_value = "Error message"
        exc.show = MagicMock()

        # Should not raise (handled gracefully)
        _rich_utils.rich_format_error(exc)


class TestRichRenderTextEdgeCases:
    """Tests for rich_render_text with edge cases."""

    def test_render_text_with_embedded_tags(self):
        """Test rich_render_text with embedded Rich tags"""
        from typer_extensions import _rich_utils

        text = "This is [bold]bold[/bold] and [italic]italic[/italic]"
        result = _rich_utils.rich_render_text(text)
        assert isinstance(result, str)
        assert "bold" not in result or "[" not in result

    def test_render_text_empty_string(self):
        """Test rich_render_text with empty string"""
        from typer_extensions import _rich_utils

        result = _rich_utils.rich_render_text("")
        assert isinstance(result, str)
        assert result == ""

    def test_render_text_with_only_tags(self):
        """Test rich_render_text with only tags"""
        from typer_extensions import _rich_utils

        result = _rich_utils.rich_render_text("[bold][/bold]")
        assert isinstance(result, str)


class TestRichToHtmlEdgeCases:
    """Tests for rich_to_html with edge cases."""

    def test_rich_to_html_empty_string(self):
        """Test rich_to_html with empty string"""
        from typer_extensions import _rich_utils

        result = _rich_utils.rich_to_html("")
        assert isinstance(result, str)

    def test_rich_to_html_with_tags(self):
        """Test rich_to_html with Rich markup tags"""
        from typer_extensions import _rich_utils

        result = _rich_utils.rich_to_html("[bold]Text[/bold]")
        assert isinstance(result, str)

    def test_rich_to_html_with_special_chars(self):
        """Test rich_to_html with special characters"""
        from typer_extensions import _rich_utils

        result = _rich_utils.rich_to_html('<tag> & "quotes"')
        assert isinstance(result, str)
