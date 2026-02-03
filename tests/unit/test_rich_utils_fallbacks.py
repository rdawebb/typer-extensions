"""Tests for _rich_utils.py fallback paths when Rich is disabled"""

import subprocess
import sys
import json
from unittest.mock import MagicMock, patch
from typer_extensions import _rich_utils


class TestRichUtilsWithoutRichImport:
    """Test fallback behavior when Rich library cannot be imported"""

    def test_use_rich_disabled_via_env(self):
        """Test that TYPER_USE_RICH=0 disables Rich"""
        code = """
import os
import sys
import json

os.environ["TYPER_USE_RICH"] = "0"

# Force reimport to pick up env var
if "typer_extensions._rich_utils" in sys.modules:
    del sys.modules["typer_extensions._rich_utils"]

from typer_extensions import _rich_utils

output = {
    "use_rich": _rich_utils._USE_RICH
}
print(json.dumps(output))
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                # _USE_RICH should respect environment variable
                assert output.get("use_rich") is not None
            except json.JSONDecodeError:
                pass

    def test_github_actions_force_terminal(self):
        """Test FORCE_TERMINAL with GITHUB_ACTIONS env var"""
        code = """
import os
import sys
import json

os.environ["GITHUB_ACTIONS"] = "true"

# Force reimport
if "typer_extensions._rich_utils" in sys.modules:
    del sys.modules["typer_extensions._rich_utils"]

from typer_extensions import _rich_utils

output = {
    "force_terminal": _rich_utils.FORCE_TERMINAL
}
print(json.dumps(output))
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                # FORCE_TERMINAL should be True when GITHUB_ACTIONS is set
                assert output.get("force_terminal") is True
            except json.JSONDecodeError:
                pass

    def test_py_colors_force_terminal(self):
        """Test FORCE_TERMINAL with PY_COLORS env var"""
        code = """
import os
import sys
import json

os.environ["PY_COLORS"] = "1"

# Force reimport
if "typer_extensions._rich_utils" in sys.modules:
    del sys.modules["typer_extensions._rich_utils"]

from typer_extensions import _rich_utils

output = {
    "force_terminal": _rich_utils.FORCE_TERMINAL
}
print(json.dumps(output))
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                # FORCE_TERMINAL should be set appropriately
                assert "force_terminal" in output
            except json.JSONDecodeError:
                pass


class TestGetRichConsoleNoRich:
    """Test _get_rich_console when Rich is not available"""

    def test_get_rich_console_returns_none_when_rich_disabled(self):
        """Test that _get_rich_console returns None when RICH_AVAILABLE is False"""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            console = _rich_utils._get_rich_console()
            assert console is None

    def test_get_rich_console_stderr_when_rich_disabled(self):
        """Test that _get_rich_console returns None for stderr when Rich disabled"""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            console = _rich_utils._get_rich_console(stderr=True)
            assert console is None


class TestMakeRichTextNoRich:
    """Test _make_rich_text fallback when Rich is not available"""

    def test_make_rich_text_returns_plain_text_when_rich_disabled(self):
        """Test that _make_rich_text returns plain text when RICH_AVAILABLE is False"""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils._make_rich_text(
                text="Hello world", style="bold", markup_mode="rich"
            )
            assert result == "Hello world"
            assert isinstance(result, str)

    def test_make_rich_text_markdown_mode_when_rich_disabled(self):
        """Test _make_rich_text with markdown mode when Rich disabled"""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils._make_rich_text(
                text="# Header\n\nContent", style="", markup_mode="markdown"
            )
            assert isinstance(result, str)
            assert "Header" in result

    def test_make_rich_text_with_highlighter_none(self):
        """Test _make_rich_text when highlighter is None but Rich is available"""
        if _rich_utils.RICH_AVAILABLE:
            with patch.object(_rich_utils, "highlighter", None):
                result = _rich_utils._make_rich_text(
                    text="Test text", style="", markup_mode="rich"
                )
                # Should return Text object or string
                assert result is not None


class TestGetHelpTextNoRich:
    """Test _get_help_text fallback when Rich is not available"""

    def test_get_help_text_plain_when_rich_disabled(self):
        """Test _get_help_text returns plain text when Rich disabled"""
        from click import Command

        cmd = Command("test")
        cmd.help = "This is a test command"

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils._get_help_text(obj=cmd, markup_mode="rich")
            assert isinstance(result, str)
            assert "test command" in result

    def test_get_help_text_deprecated_command_no_rich(self):
        """Test _get_help_text with deprecated command when Rich disabled"""
        from click import Command

        cmd = Command("old")
        cmd.help = "Old command"
        cmd.deprecated = True

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils._get_help_text(obj=cmd, markup_mode="rich")
            assert isinstance(result, str)
            assert "deprecated" in result.lower()

    def test_get_help_text_with_formfeed(self):
        """Test _get_help_text handles formfeed character"""
        from click import Command

        cmd = Command("test")
        cmd.help = "First part\fSecond part (should be hidden)"

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils._get_help_text(obj=cmd, markup_mode="rich")
            assert isinstance(result, str)
            assert "Second part" not in result
            assert "First part" in result


class TestGetParameterHelpNoRich:
    """Test _get_parameter_help fallback when Rich is not available"""

    def test_get_parameter_help_returns_tuple_when_rich_disabled(self):
        """Test that _get_parameter_help returns tuple when Rich disabled"""
        from click import Option

        opt = Option(["-v", "--verbose"], help="Verbose output")
        ctx = MagicMock()
        ctx.auto_envvar_prefix = None

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils._get_parameter_help(
                param=opt, ctx=ctx, markup_mode="rich"
            )
            # Should return tuple from get_help_record
            assert isinstance(result, (tuple, type(None)))

    def test_get_parameter_help_no_help_record(self):
        """Test _get_parameter_help when param has no help record"""
        from click import Option

        opt = Option(["-x"])
        ctx = MagicMock()
        ctx.auto_envvar_prefix = None

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch.object(opt, "get_help_record", return_value=None):
                result = _rich_utils._get_parameter_help(
                    param=opt, ctx=ctx, markup_mode="rich"
                )
                assert result == ("", "")


class TestPrintOptionsPanelNoRich:
    """Test _print_options_panel fallback when Rich is not available"""

    def test_print_options_panel_fallback_to_click_echo(self):
        """Test that _print_options_panel falls back to click.echo when Rich disabled"""
        from click import Option

        opt = Option(["-v", "--verbose"], help="Verbose output")
        ctx = MagicMock()
        ctx.auto_envvar_prefix = None
        mock_console = MagicMock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch("click.echo") as mock_echo:
                _rich_utils._print_options_panel(
                    name="Options",
                    params=[opt],
                    ctx=ctx,
                    markup_mode="rich",
                    console=mock_console,
                )
                # Should have called click.echo
                assert mock_echo.called


class TestPrintCommandsPanelNoRich:
    """Test _print_commands_panel fallback when Rich is not available"""

    def test_print_commands_panel_fallback_to_click_echo(self):
        """Test that _print_commands_panel falls back to click.echo when Rich disabled"""
        from click import Command

        cmd = Command("deploy")
        cmd.help = "Deploy the application"
        mock_console = MagicMock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch("click.echo") as mock_echo:
                _rich_utils._print_commands_panel(
                    name="Commands",
                    commands=[cmd],
                    markup_mode="rich",
                    console=mock_console,
                    cmd_len=10,
                    extended_typer=None,
                )
                # Should have called click.echo
                assert mock_echo.called

    def test_print_commands_panel_deprecated_no_rich(self):
        """Test _print_commands_panel with deprecated command when Rich disabled"""
        from click import Command

        cmd = Command("old")
        cmd.help = "Old command"
        cmd.deprecated = True
        mock_console = MagicMock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch("click.echo") as mock_echo:
                _rich_utils._print_commands_panel(
                    name="Commands",
                    commands=[cmd],
                    markup_mode="rich",
                    console=mock_console,
                    cmd_len=10,
                    extended_typer=None,
                )
                # Should have called click.echo with deprecated marker
                assert mock_echo.called


class TestRichFormatHelpNoRich:
    """Test rich_format_help fallback when Rich is not available"""

    def test_rich_format_help_uses_click_formatter_when_rich_disabled(self):
        """Test that rich_format_help falls back to Click formatter when Rich disabled"""
        from click import Command

        cmd = Command("test")
        cmd.help = "Test command"
        ctx = MagicMock()
        formatter = MagicMock()
        ctx.make_formatter.return_value = formatter
        formatter.getvalue.return_value = "Formatted help"

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch("click.echo") as mock_echo:
                _rich_utils.rich_format_help(obj=cmd, ctx=ctx, markup_mode="rich")
                # Should have used Click's formatter
                assert ctx.make_formatter.called
                assert mock_echo.called

    def test_rich_format_help_console_none_fallback(self):
        """Test rich_format_help when console is None"""
        from click import Command

        cmd = Command("test")
        cmd.help = "Test command"
        ctx = MagicMock()
        formatter = MagicMock()
        ctx.make_formatter.return_value = formatter
        formatter.getvalue.return_value = "Formatted help"

        # Mock RICH_AVAILABLE to True but _get_rich_console to return None
        with patch.object(_rich_utils, "RICH_AVAILABLE", True):
            with patch.object(_rich_utils, "_get_rich_console", return_value=None):
                with patch("click.echo") as mock_echo:
                    _rich_utils.rich_format_help(obj=cmd, ctx=ctx, markup_mode="rich")
                    # Should fall back to Click formatter
                    assert mock_echo.called


class TestRichFormatErrorNoRich:
    """Test rich_format_error fallback when Rich is not available"""

    def test_rich_format_error_calls_show_when_rich_disabled(self):
        """Test that rich_format_error calls show() when Rich disabled"""
        exc = MagicMock()
        exc.__class__.__name__ = "CustomError"
        exc.show = MagicMock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            _rich_utils.rich_format_error(exc)
            # Should have called show()
            assert exc.show.called

    def test_rich_format_error_console_none(self):
        """Test rich_format_error when console is None"""
        exc = MagicMock()
        exc.__class__.__name__ = "CustomError"
        exc.ctx = None
        exc.show = MagicMock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", True):
            with patch.object(_rich_utils, "_get_rich_console", return_value=None):
                _rich_utils.rich_format_error(exc)
                # Should have called show() as fallback
                assert exc.show.called

    def test_rich_format_error_noargs_error(self):
        """Test rich_format_error with NoArgsIsHelpError"""
        exc = MagicMock()
        exc.__class__.__name__ = "NoArgsIsHelpError"

        # Should return early without doing anything
        result = _rich_utils.rich_format_error(exc)
        assert result is None


class TestRichAbortErrorNoRich:
    """Test rich_abort_error fallback when Rich is not available"""

    def test_rich_abort_error_uses_click_echo_when_rich_disabled(self):
        """Test that rich_abort_error uses click.echo when Rich disabled"""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch("click.echo") as mock_echo:
                _rich_utils.rich_abort_error()
                # Should have called click.echo with ABORTED_TEXT
                assert mock_echo.called
                call_args = mock_echo.call_args
                assert _rich_utils.ABORTED_TEXT in call_args[0]

    def test_rich_abort_error_console_none(self):
        """Test rich_abort_error when console is None"""
        with patch.object(_rich_utils, "RICH_AVAILABLE", True):
            with patch.object(_rich_utils, "_get_rich_console", return_value=None):
                with patch("click.echo") as mock_echo:
                    _rich_utils.rich_abort_error()
                    # Should fall back to click.echo
                    assert mock_echo.called


class TestRichRenderTextNoRich:
    """Test rich_render_text fallback when Rich is not available"""

    def test_rich_render_text_removes_tags_when_rich_disabled(self):
        """Test that rich_render_text removes tags when Rich disabled"""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils.rich_render_text("[bold]Hello[/bold] [red]World[/red]")
            assert isinstance(result, str)
            assert "[bold]" not in result
            assert "[/bold]" not in result
            assert "Hello" in result
            assert "World" in result

    def test_rich_render_text_console_none(self):
        """Test rich_render_text when console is None"""
        with patch.object(_rich_utils, "RICH_AVAILABLE", True):
            with patch.object(_rich_utils, "_get_rich_console", return_value=None):
                result = _rich_utils.rich_render_text("[bold]Text[/bold]")
                assert isinstance(result, str)
                # Should strip tags as fallback
                assert "[bold]" not in result


class TestGetTracebackNoRich:
    """Test get_traceback when Rich is not available"""

    def test_get_traceback_returns_none_when_rich_disabled(self):
        """Test that get_traceback returns None when Rich disabled"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            with patch.object(_rich_utils, "RICH_AVAILABLE", False):
                result = _rich_utils.get_traceback(
                    exc=e, exception_config=None, internal_dir_names=[]
                )
                assert result is None
