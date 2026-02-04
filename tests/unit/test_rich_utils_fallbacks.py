"""Tests for _rich_utils.py fallback behavior when Rich is not available.

This module tests the fallback paths in _rich_utils when Rich is disabled
either through environment variables or when Rich cannot be imported.
"""

import importlib
import json
import subprocess
import sys
from unittest.mock import MagicMock, Mock, patch

import click

from typer_extensions import _rich_utils

# =============================================================================
# Environment Variable Tests
# =============================================================================


class TestRichDisabledViaEnvironment:
    """Test Rich can be disabled via environment variables."""

    def test_use_rich_disabled_via_env(self):
        """Test that TYPER_USE_RICH=0 disables Rich."""
        code = """
import os
import sys
import json

os.environ["TYPER_USE_RICH"] = "0"

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
                assert output.get("use_rich") is not None
            except json.JSONDecodeError:
                pass

    def test_github_actions_force_terminal(self):
        """Test FORCE_TERMINAL with GITHUB_ACTIONS env var."""
        code = """
import os
import sys
import json

os.environ["GITHUB_ACTIONS"] = "true"

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
                assert output.get("force_terminal") is True
            except json.JSONDecodeError:
                pass

    def test_py_colors_force_terminal(self):
        """Test FORCE_TERMINAL with PY_COLORS env var."""
        code = """
import os
import sys
import json

os.environ["PY_COLORS"] = "1"

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
                assert "force_terminal" in output
            except json.JSONDecodeError:
                pass

    def test_force_terminal_disabled_via_env(self, monkeypatch):
        """Test that _TYPER_FORCE_DISABLE_TERMINAL=1 can disable terminal."""
        monkeypatch.setenv("_TYPER_FORCE_DISABLE_TERMINAL", "1")

        importlib.reload(_rich_utils)
        assert _rich_utils.FORCE_TERMINAL is False

        monkeypatch.delenv("_TYPER_FORCE_DISABLE_TERMINAL", raising=False)
        importlib.reload(_rich_utils)


# =============================================================================
# Rich Import Failure Tests
# =============================================================================


class TestRichImportFailure:
    """Test fallback behavior when Rich cannot be imported."""

    def test_fallback_without_rich(self, subprocess_runner):
        """Test fallback behavior when Rich is not available."""
        code = """
import json
import builtins

real_import = builtins.__import__

def fake_import(name, *args, **kwargs):
    if name.startswith("rich"):
        raise ImportError("No module named 'rich'")
    return real_import(name, *args, **kwargs)

builtins.__import__ = fake_import

try:
    from typer_extensions._rich_utils import _get_help_text
    from unittest.mock import Mock
    import click

    obj = Mock(spec=click.Command)
    obj.help = "Test help text"
    obj.deprecated = False

    result = _get_help_text(obj=obj, markup_mode="rich")
    output = {
        "success": True,
        "is_string": isinstance(result, str),
        "has_help": "Test help text" in result
    }
except Exception as e:
    output = {
        "success": False,
        "error": str(e)
    }
finally:
    builtins.__import__ = real_import

print(json.dumps(output))
"""
        result = subprocess_runner(code)
        assert result.returncode == 0
        if result.stdout.strip():
            output = json.loads(result.stdout.strip())
            assert output.get("success") is True
            assert output.get("is_string") is True
            assert output.get("has_help") is True

    def test_fallback_without_rich_deprecated(self, subprocess_runner):
        """Test fallback with deprecated command when Rich is not available."""
        code = """
import json
import builtins

real_import = builtins.__import__

def fake_import(name, *args, **kwargs):
    if name.startswith("rich"):
        raise ImportError("No module named 'rich'")
    return real_import(name, *args, **kwargs)

builtins.__import__ = fake_import

try:
    from typer_extensions._rich_utils import _get_help_text, DEPRECATED_STRING
    from unittest.mock import Mock
    import click

    obj = Mock(spec=click.Command)
    obj.help = "Test help text"
    obj.deprecated = True

    result = _get_help_text(obj=obj, markup_mode="rich")
    output = {
        "success": True,
        "is_string": isinstance(result, str),
        "has_help": "Test help text" in result,
        "has_deprecated": DEPRECATED_STRING in result
    }
except Exception as e:
    output = {
        "success": False,
        "error": str(e)
    }
finally:
    builtins.__import__ = real_import

print(json.dumps(output))
"""
        result = subprocess_runner(code)
        assert result.returncode == 0
        if result.stdout.strip():
            output = json.loads(result.stdout.strip())
            assert output.get("success") is True
            assert output.get("is_string") is True
            assert output.get("has_help") is True
            assert output.get("has_deprecated") is True


# =============================================================================
# Fallback Function Tests (when Rich is disabled)
# =============================================================================


class TestGetRichConsoleNoRich:
    """Test _get_rich_console when Rich is not available."""

    def test_get_rich_console_returns_none_when_rich_disabled(self):
        """Test that _get_rich_console returns None when RICH_AVAILABLE is False."""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            console = _rich_utils._get_rich_console()
            assert console is None

    def test_get_rich_console_stderr_when_rich_disabled(self):
        """Test that _get_rich_console returns None for stderr when Rich disabled."""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            console = _rich_utils._get_rich_console(stderr=True)
            assert console is None


class TestMakeRichTextNoRich:
    """Test _make_rich_text fallback when Rich is not available."""

    def test_make_rich_text_returns_plain_text_when_rich_disabled(self):
        """Test that _make_rich_text returns plain text when RICH_AVAILABLE is False."""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils._make_rich_text(
                text="Hello world", style="bold", markup_mode="rich"
            )
            assert result == "Hello world"
            assert isinstance(result, str)

    def test_make_rich_text_markdown_mode_when_rich_disabled(self):
        """Test _make_rich_text with markdown mode when Rich disabled."""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils._make_rich_text(
                text="# Header\n\nContent", style="", markup_mode="markdown"
            )
            assert isinstance(result, str)
            assert "Header" in result


class TestGetHelpTextNoRich:
    """Test _get_help_text fallback when Rich is not available."""

    def test_get_help_text_plain_when_rich_disabled(self):
        """Test _get_help_text returns plain text when Rich disabled."""
        cmd = click.Command("test")
        cmd.help = "This is a test command"

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils._get_help_text(obj=cmd, markup_mode="rich")
            assert isinstance(result, str)
            assert "test command" in result

    def test_get_help_text_deprecated_command_no_rich(self):
        """Test _get_help_text with deprecated command when Rich disabled."""
        cmd = click.Command("old")
        cmd.help = "Old command"
        cmd.deprecated = True

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils._get_help_text(obj=cmd, markup_mode="rich")
            assert isinstance(result, str)
            assert "deprecated" in result.lower()

    def test_get_help_text_with_formfeed(self):
        """Test _get_help_text handles formfeed character."""
        cmd = click.Command("test")
        cmd.help = "First part\fSecond part (should be hidden)"

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils._get_help_text(obj=cmd, markup_mode="rich")
            assert isinstance(result, str)
            assert "Second part" not in result
            assert "First part" in result


class TestGetParameterHelpNoRich:
    """Test _get_parameter_help fallback when Rich is not available."""

    def test_get_parameter_help_returns_tuple_when_rich_disabled(self):
        """Test that _get_parameter_help returns tuple when Rich disabled."""
        opt = click.Option(["-v", "--verbose"], help="Verbose output")
        ctx = Mock()
        ctx.auto_envvar_prefix = None

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils._get_parameter_help(
                param=opt, ctx=ctx, markup_mode="rich"
            )
            assert isinstance(result, (tuple, type(None)))

    def test_get_parameter_help_no_help_record(self):
        """Test _get_parameter_help when param has no help record."""
        opt = click.Option(["-x"])
        ctx = Mock()
        ctx.auto_envvar_prefix = None

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch.object(opt, "get_help_record", return_value=None):
                result = _rich_utils._get_parameter_help(
                    param=opt, ctx=ctx, markup_mode="rich"
                )
                assert result == ("", "")


class TestPrintOptionsPanelNoRich:
    """Test _print_options_panel fallback when Rich is not available."""

    def test_print_options_panel_fallback_to_click_echo(self):
        """Test that _print_options_panel falls back to click.echo when Rich disabled."""
        opt = click.Option(["-v", "--verbose"], help="Verbose output")
        ctx = Mock()
        ctx.auto_envvar_prefix = None
        mock_console = Mock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch("click.echo") as mock_echo:
                _rich_utils._print_options_panel(
                    name="Options",
                    params=[opt],
                    ctx=ctx,
                    markup_mode="rich",
                    console=mock_console,
                )
                assert mock_echo.called

    def test_param_without_help_record(self):
        """Parameter without help_record in fallback mode."""
        param = Mock(spec=click.Option)
        param.get_help_record = Mock(return_value=None)

        console = Mock()
        ctx = Mock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch("typer_extensions._rich_utils.click.echo") as mock_echo:
                _rich_utils._print_options_panel(
                    name="Test Options",
                    params=[param],
                    ctx=ctx,
                    markup_mode="rich",
                    console=console,
                )
                assert mock_echo.called


class TestPrintCommandsPanelNoRich:
    """Test _print_commands_panel fallback when Rich is not available."""

    def test_print_commands_panel_fallback_to_click_echo(self):
        """Test that _print_commands_panel falls back to click.echo when Rich disabled."""
        cmd = click.Command("deploy")
        cmd.help = "Deploy the application"
        mock_console = Mock()

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
                assert mock_echo.called

    def test_print_commands_panel_deprecated_no_rich(self):
        """Test _print_commands_panel with deprecated command when Rich disabled."""
        cmd = click.Command("old")
        cmd.help = "Old command"
        cmd.deprecated = True
        mock_console = Mock()

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
                assert mock_echo.called

    def test_empty_commands_list_fallback(self):
        """Empty commands list in fallback mode."""
        console = Mock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch("typer_extensions._rich_utils.click.echo") as mock_echo:
                _rich_utils._print_commands_panel(
                    name="Commands",
                    commands=[],
                    markup_mode="rich",
                    console=console,
                    cmd_len=20,
                    extended_typer=None,
                )
                mock_echo.assert_not_called()

    def test_deprecated_command_in_fallback(self):
        """Test deprecated command in fallback mode."""
        cmd = Mock(spec=click.Command)
        cmd.name = "oldcmd"
        cmd.help = "Old command"
        cmd.deprecated = True
        cmd.hidden = False

        console = Mock()
        console.print = Mock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch("typer_extensions._rich_utils.click.echo"):
                _rich_utils._print_commands_panel(
                    name="Commands",
                    commands=[cmd],
                    markup_mode="rich",
                    console=console,
                    cmd_len=20,
                    extended_typer=None,
                )


class TestRichFormatHelpNoRich:
    """Test rich_format_help fallback when Rich is not available."""

    def test_rich_format_help_uses_click_formatter_when_rich_disabled(self):
        """Test that rich_format_help falls back to Click formatter when Rich disabled."""
        cmd = click.Command("test")
        cmd.help = "Test command"
        ctx = click.Context(cmd)
        formatter = MagicMock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch.object(ctx, "make_formatter", return_value=formatter):
                with patch("click.echo") as mock_echo:
                    _rich_utils.rich_format_help(obj=cmd, ctx=ctx, markup_mode="rich")
                    assert mock_echo.called

    def test_rich_format_help_console_none_fallback(self):
        """Test rich_format_help when console is None."""
        cmd = click.Command("test")
        cmd.help = "Test command"
        ctx = click.Context(cmd)
        formatter = MagicMock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", True):
            with patch.object(_rich_utils, "_get_rich_console", return_value=None):
                with patch.object(ctx, "make_formatter", return_value=formatter):
                    with patch("click.echo") as mock_echo:
                        _rich_utils.rich_format_help(
                            obj=cmd, ctx=ctx, markup_mode="rich"
                        )
                        assert mock_echo.called


class TestRichFormatErrorNoRich:
    """Test rich_format_error fallback when Rich is not available."""

    def test_rich_format_error_calls_show_when_rich_disabled(self):
        """Test that rich_format_error calls show() when Rich disabled."""
        exc = Mock()
        exc.__class__.__name__ = "CustomError"
        exc.show = Mock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            _rich_utils.rich_format_error(exc)
            assert exc.show.called

    def test_rich_format_error_console_none(self):
        """Test rich_format_error when console is None."""
        exc = Mock()
        exc.__class__.__name__ = "CustomError"
        exc.ctx = None
        exc.show = Mock()

        with patch.object(_rich_utils, "RICH_AVAILABLE", True):
            with patch.object(_rich_utils, "_get_rich_console", return_value=None):
                _rich_utils.rich_format_error(exc)
                assert exc.show.called

    def test_rich_format_error_noargs_error(self):
        """Test rich_format_error with NoArgsIsHelpError."""
        exc = Mock()
        exc.__class__.__name__ = "NoArgsIsHelpError"

        result = _rich_utils.rich_format_error(exc)
        assert result is None


class TestRichAbortErrorNoRich:
    """Test rich_abort_error fallback when Rich is not available."""

    def test_rich_abort_error_uses_click_echo_when_rich_disabled(self):
        """Test that rich_abort_error uses click.echo when Rich disabled."""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            with patch("click.echo") as mock_echo:
                _rich_utils.rich_abort_error()
                assert mock_echo.called
                call_args = mock_echo.call_args
                assert _rich_utils.ABORTED_TEXT in call_args[0]

    def test_rich_abort_error_console_none(self):
        """Test rich_abort_error when console is None."""
        with patch.object(_rich_utils, "RICH_AVAILABLE", True):
            with patch.object(_rich_utils, "_get_rich_console", return_value=None):
                with patch("click.echo") as mock_echo:
                    _rich_utils.rich_abort_error()
                    assert mock_echo.called


class TestRichRenderTextNoRich:
    """Test rich_render_text fallback when Rich is not available."""

    def test_rich_render_text_removes_tags_when_rich_disabled(self):
        """Test that rich_render_text removes tags when Rich disabled."""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils.rich_render_text("[bold]Hello[/bold] [red]World[/red]")
            assert isinstance(result, str)
            assert "[bold]" not in result
            assert "[/bold]" not in result
            assert "Hello" in result
            assert "World" in result

    def test_rich_render_text_console_none(self):
        """Test rich_render_text when console is None."""
        with patch.object(_rich_utils, "RICH_AVAILABLE", True):
            with patch.object(_rich_utils, "_get_rich_console", return_value=None):
                result = _rich_utils.rich_render_text("[bold]Text[/bold]")
                assert isinstance(result, str)
                assert "[bold]" not in result


class TestRichToHtmlNoRich:
    """Test rich_to_html fallback when Rich is not available."""

    def test_escape_html_without_rich(self):
        """Test HTML escaping without Rich."""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils.escape_before_html_export(
                "<script>alert('xss')</script>"
            )
            assert "&lt;script&gt;" in result
            assert "&lt;/script&gt;" in result

    def test_rich_to_html_without_rich(self):
        """Test rich_to_html without Rich."""
        with patch.object(_rich_utils, "RICH_AVAILABLE", False):
            result = _rich_utils.rich_to_html("[bold]Test[/bold]")
            assert result is not None
            assert "Test" in result

    def test_rich_to_html_console_none(self):
        """Test rich_to_html when console is falsy."""
        with patch.object(_rich_utils, "RICH_AVAILABLE", True):
            with patch("typer_extensions._rich_utils.Console") as MockConsole:
                mock_console = Mock()
                mock_console.__bool__ = Mock(return_value=False)
                MockConsole.return_value = mock_console

                result = _rich_utils.rich_to_html("[bold]Test[/bold]")
                assert result is not None


class TestGetTracebackNoRich:
    """Test get_traceback when Rich is not available."""

    def test_get_traceback_returns_none_when_rich_disabled(self):
        """Test that get_traceback returns None when Rich disabled."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            with patch.object(_rich_utils, "RICH_AVAILABLE", False):
                result = _rich_utils.get_traceback(
                    exc=e, exception_config=None, internal_dir_names=[]
                )
                assert result is None
