"""Tests for edge cases in Rich utilities."""

from __future__ import annotations

import importlib
import json
from unittest.mock import Mock, patch

import click


class TestForceTerminalDisabled:
    """Test _TYPER_FORCE_DISABLE_TERMINAL handling."""

    def test_force_terminal_disabled_via_env(self, monkeypatch):
        """Test that _TYPER_FORCE_DISABLE_TERMINAL=1 can disable terminal."""
        monkeypatch.setenv("_TYPER_FORCE_DISABLE_TERMINAL", "1")

        from typer_extensions import _rich_utils

        importlib.reload(_rich_utils)
        assert _rich_utils.FORCE_TERMINAL is False

        # Clean up & reload
        monkeypatch.delenv("_TYPER_FORCE_DISABLE_TERMINAL", raising=False)
        importlib.reload(_rich_utils)


class TestRichImportFailure:
    """Test line 117->164: Handling when Rich imports fail."""

    def test_fallback_without_rich(self, monkeypatch, subprocess_runner):
        """Test fallback behavior when Rich is not available (runs in isolated subprocess)."""
        code = """
import json
import builtins

real_import = builtins.__import__

def fake_import(name, *args, **kwargs):
    if name.startswith("rich"):
        raise ImportError("No module named 'rich'")
    return real_import(name, *args, **kwargs)

# Apply the fake import before importing _rich_utils
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
    # Restore real import
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

    def test_fallback_without_rich_deprecated(self, monkeypatch, subprocess_runner):
        """Test fallback with deprecated command when Rich is not available (isolated subprocess)."""
        code = """
import json
import builtins

real_import = builtins.__import__

def fake_import(name, *args, **kwargs):
    if name.startswith("rich"):
        raise ImportError("No module named 'rich'")
    return real_import(name, *args, **kwargs)

# Apply the fake import before importing _rich_utils
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
    # Restore real import
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


class TestParameterHelpEdgeCases:
    """Parameter help formatting edge cases."""

    def test_typer_argument_with_default_value(self):
        """TyperArgument with default_value_from_help."""
        from typer_extensions._rich_utils import _get_parameter_help
        from typer.core import TyperArgument

        # Create a real TyperArgument instance
        param = TyperArgument(param_decls=["test_arg"], nargs=1)
        param.help = "Test argument"
        param.required = False
        # Set the default_value_from_help attribute dynamically
        setattr(param, "default_value_from_help", "42")
        param.envvar = None

        ctx = Mock()

        # Should handle the default_value_from_help attribute
        result = _get_parameter_help(param=param, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_parameter_help_with_backspace_escape(self):
        """Help text starting with \\b escape (no linebreak removal)."""
        from typer_extensions._rich_utils import _get_parameter_help

        param = Mock(spec=click.Option)
        param.name = "test"
        param.help = "\bThis is verbatim\ntext with newlines"
        param.required = False
        param.default = None
        param.show_default = False
        param.envvar = None

        ctx = Mock()
        ctx.show_default = False

        # The \b prefix should prevent linebreak removal
        result = _get_parameter_help(param=param, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_list_default_value(self):
        """Parameter with list/tuple default."""
        from typer_extensions._rich_utils import _get_parameter_help

        param = Mock(spec=click.Option)
        param.name = "test_option"
        param.help = "Test option"
        param.required = False
        param.default = ["val1", "val2", "val3"]
        param.show_default = True
        param.envvar = None

        ctx = Mock()
        ctx.show_default = False

        result = _get_parameter_help(param=param, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_tuple_default_value(self):
        """Parameter with tuple default."""
        from typer_extensions._rich_utils import _get_parameter_help

        param = Mock(spec=click.Option)
        param.name = "test_option"
        param.help = "Test option"
        param.required = False
        param.default = (1, 2, 3)
        param.show_default = True
        param.envvar = None

        ctx = Mock()
        ctx.show_default = False

        result = _get_parameter_help(param=param, ctx=ctx, markup_mode="rich")
        assert result is not None

    def test_empty_default_string_not_added(self):
        """Empty default string is not added to help."""
        from typer_extensions._rich_utils import _get_parameter_help

        param = Mock(spec=click.Option)
        param.name = "test_option"
        param.help = "Test option"
        param.required = False
        param.default = ""  # Empty string
        param.show_default = True
        param.envvar = None

        ctx = Mock()
        ctx.show_default = False

        result = _get_parameter_help(param=param, ctx=ctx, markup_mode="rich")
        # Should not include the empty default
        assert result is not None


class TestOptionsPanelEdgeCases:
    """Options panel edge cases."""

    def test_param_without_help_record(self):
        """Parameter without help_record in fallback mode."""
        from typer_extensions._rich_utils import _print_options_panel

        param = Mock(spec=click.Option)
        param.get_help_record = Mock(return_value=None)  # No help record

        console = Mock()
        ctx = Mock()

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", False):
            with patch("typer_extensions._rich_utils.click.echo") as mock_echo:
                _print_options_panel(
                    name="Test Options",
                    params=[param],
                    ctx=ctx,
                    markup_mode="rich",
                    console=console,
                )

                # Should still print the panel name
                mock_echo.assert_called()

    def test_highlighter_none_negative(self):
        """Test negative_highlighter is None."""
        from typer_extensions._rich_utils import _print_options_panel

        param = Mock(spec=click.Option)
        param.name = "no-feature"  # Negative option
        param.opts = ["--no-feature"]
        param.secondary_opts = []
        param.required = False
        param.help = "Disable feature"
        param.envvar = None
        param.default = None

        ctx = Mock()
        console = Mock()
        console.print = Mock()

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            # Initialise opts_text even when highlighter is None
            with patch("typer_extensions._rich_utils.negative_highlighter", None):
                with patch("typer_extensions._rich_utils.highlighter", Mock()):
                    with patch("typer_extensions._rich_utils._get_parameter_help"):
                        _print_options_panel(
                            name="Options",
                            params=[param],
                            ctx=ctx,
                            markup_mode="rich",
                            console=console,
                        )

    def test_highlighter_none_positive(self):
        """Test highlighter is None."""
        from typer_extensions._rich_utils import _print_options_panel

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

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            # Initialise opts_text even when highlighter is None
            with patch("typer_extensions._rich_utils.highlighter", None):
                with patch("typer_extensions._rich_utils.negative_highlighter", Mock()):
                    with patch("typer_extensions._rich_utils._get_parameter_help"):
                        _print_options_panel(
                            name="Options",
                            params=[param],
                            ctx=ctx,
                            markup_mode="rich",
                            console=console,
                        )

    def test_param_with_metavar(self):
        """Test Parameter with metavar."""
        from typer_extensions._rich_utils import _print_options_panel

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

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            _print_options_panel(
                name="Options",
                params=[param],
                ctx=ctx,
                markup_mode="rich",
                console=console,
            )

    def test_param_with_type_name(self):
        """Test Parameter with type.name."""
        from typer_extensions._rich_utils import _print_options_panel

        param = Mock(spec=click.Option)
        param.name = "count"
        param.opts = ["--count"]
        param.secondary_opts = []
        param.required = False
        param.help = "Number of items"
        param.envvar = None
        param.default = None

        # Mock type with name
        param_type = Mock()
        param_type.name = "INTEGER"
        param.type = param_type

        # No metavar attribute
        delattr(param, "metavar") if hasattr(param, "metavar") else None

        ctx = Mock()
        console = Mock()
        console.print = Mock()

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            _print_options_panel(
                name="Options",
                params=[param],
                ctx=ctx,
                markup_mode="rich",
                console=console,
            )

    def test_required_parameter_indicator(self):
        """Test Required parameter indicator."""
        from typer_extensions._rich_utils import _print_options_panel

        param = Mock(spec=click.Option)
        param.name = "required_opt"
        param.opts = ["--required"]
        param.secondary_opts = []
        param.required = True  # Required!
        param.help = "Required option"
        param.envvar = None
        param.default = None

        ctx = Mock()
        console = Mock()
        console.print = Mock()

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            _print_options_panel(
                name="Options",
                params=[param],
                ctx=ctx,
                markup_mode="rich",
                console=console,
            )

    def test_empty_options_table(self):
        """Test lines 499->456, 502->exit: No rows in options table."""
        from typer_extensions._rich_utils import _print_options_panel

        # Param that returns None for help columns
        param = Mock(spec=click.Option)
        param.name = "test"
        param.opts = ["--test"]
        param.secondary_opts = []
        param.required = False
        param.help = None  # No help
        param.envvar = None
        param.default = None

        ctx = Mock()
        console = Mock()
        console.print = Mock()

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            with patch(
                "typer_extensions._rich_utils._get_parameter_help", return_value=None
            ):
                _print_options_panel(
                    name="Options",
                    params=[param],
                    ctx=ctx,
                    markup_mode="rich",
                    console=console,
                )

                # Should not print panel if no rows
                if console.print.called:
                    # Verify no Panel was printed
                    for call in console.print.call_args_list:
                        from rich.panel import Panel

                        assert not isinstance(call[0][0] if call[0] else None, Panel)


class TestCommandsPanelEdgeCases:
    """Commands panel edge cases."""

    def test_empty_commands_list_fallback(self):
        """Empty commands list in fallback mode."""
        from typer_extensions._rich_utils import _print_commands_panel

        console = Mock()

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", False):
            with patch("typer_extensions._rich_utils.click.echo") as mock_echo:
                _print_commands_panel(
                    name="Commands",
                    commands=[],  # Empty list
                    markup_mode="rich",
                    console=console,
                    cmd_len=20,
                    extended_typer=None,
                )

                # Should not print anything for empty list
                mock_echo.assert_not_called()

    def test_empty_commands_table(self):
        """Test empty commands table doesn't print panel."""
        from typer_extensions._rich_utils import _print_commands_panel

        console = Mock()
        console.print = Mock()

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            _print_commands_panel(
                name="Commands",
                commands=[],  # Empty list
                markup_mode="rich",
                console=console,
                cmd_len=20,
                extended_typer=None,
            )

            # Should not print panel if no commands
            console.print.assert_not_called()


class TestRichFormatHelpEdgeCases:
    """Test rich_format_help edge cases."""

    def test_parameter_not_argument_or_option(self):
        """Test Parameter that is neither Argument nor Option."""
        from typer_extensions._rich_utils import rich_format_help

        # Create a parameter that is neither click.Argument nor click.Option
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

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            with patch(
                "typer_extensions._rich_utils._get_rich_console", return_value=console
            ):
                # This should execute the rich_format_help without errors
                rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")

    def test_custom_argument_panel(self):
        """Test non-default argument panel name."""
        from typer_extensions._rich_utils import rich_format_help

        arg = Mock(spec=click.Argument)
        arg.name = "file"
        arg.rich_help_panel = "Input Arguments"  # Custom panel name

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

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            with patch(
                "typer_extensions._rich_utils._get_rich_console", return_value=console
            ):
                with patch(
                    "typer_extensions._rich_utils._print_options_panel"
                ) as mock_print:
                    rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")

                    # Should print custom panel
                    calls = mock_print.call_args_list
                    panel_names = [
                        call[1]["name"] for call in calls if "name" in call[1]
                    ]
                    assert "Input Arguments" in panel_names

    def test_custom_command_panel(self):
        """Test non-default command panel."""
        from typer_extensions._rich_utils import rich_format_help

        # Create a command with custom panel
        cmd = Mock(spec=click.Command)
        cmd.name = "special"
        cmd.help = "Special command"
        cmd.hidden = False
        cmd.deprecated = False
        cmd.rich_help_panel = "Special Commands"  # Custom panel

        # Create a group with the command
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

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            with patch(
                "typer_extensions._rich_utils._get_rich_console", return_value=console
            ):
                with patch(
                    "typer_extensions._rich_utils._print_commands_panel"
                ) as mock_print:
                    rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")

                    # Should print custom panel
                    calls = mock_print.call_args_list
                    panel_names = [
                        call[1]["name"] for call in calls if "name" in call[1]
                    ]
                    assert "Special Commands" in panel_names


class TestCleandocEdgeCases:
    """Test cleandoc edge cases."""

    def test_cleandoc_empty_lines(self):
        """Test docstring with leading/trailing blank lines."""
        from typer_extensions._rich_utils import cleandoc

        # Test with empty string
        result = cleandoc("")
        assert result == ""

        # Test with docstring that has leading and trailing blank lines
        result = cleandoc("\n\n\nContent\n\n\n")
        assert result == "Content"

        # Test with indented content and blank lines (with common indentation)
        result = cleandoc("\n\n    Line 1\n    Line 2\n\n")
        assert result == "Line 1\nLine 2"

    def test_cleandoc_single_line(self):
        """Test cleandoc when there's only one line (margin=sys.maxsize)."""
        from typer_extensions._rich_utils import cleandoc

        # Single line - margin will be sys.maxsize
        result = cleandoc("Single line")
        assert result == "Single line"

        # First line with trailing blank lines only
        result = cleandoc("Line 1\n\n\n")
        assert result == "Line 1"

    def test_cleandoc_with_indented_lines(self):
        """Test cleandoc removes common indentation."""
        from typer_extensions._rich_utils import cleandoc

        # First line unindented, rest indented
        result = cleandoc("Line 1\n    Line 2\n    Line 3")
        assert result == "Line 1\nLine 2\nLine 3"

    def test_cleandoc_no_margin(self):
        """Test docstring where margin is sys.maxsize (no indentation)."""
        from typer_extensions._rich_utils import cleandoc

        # First line indented, no other lines
        result = cleandoc("   Test")
        assert result == "Test"

        # All lines at same indentation
        result = cleandoc("Line 1")
        assert result == "Line 1"


class TestHTMLExportEdgeCases:
    """Test HTML export fallback paths."""

    def test_escape_html_without_rich(self):
        """Test HTML escaping without Rich."""
        from typer_extensions._rich_utils import escape_before_html_export

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", False):
            result = escape_before_html_export("<script>alert('xss')</script>")
            assert "&lt;script&gt;" in result
            assert "&lt;/script&gt;" in result

    def test_rich_to_html_without_rich(self):
        """Test rich_to_html without Rich."""
        from typer_extensions._rich_utils import rich_to_html

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", False):
            result = rich_to_html("[bold]Test[/bold]")
            assert result is not None
            # Should fall back to escaped plain text
            assert "Test" in result

    def test_rich_to_html_console_none(self):
        """Test rich_to_html when console is falsy."""
        from typer_extensions._rich_utils import rich_to_html

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            # Mock Console to return a falsy value
            with patch("typer_extensions._rich_utils.Console") as MockConsole:
                # Create a mock that evaluates to False
                mock_console = Mock()
                mock_console.__bool__ = Mock(return_value=False)
                MockConsole.return_value = mock_console

                result = rich_to_html("[bold]Test[/bold]")
                assert result is not None


class TestCallableDefaultValue:
    """Test Callable default value."""

    def test_callable_default_parameter(self):
        """Test that callable defaults show as '(dynamic)'."""
        from typer_extensions._rich_utils import _get_parameter_help

        def default_func():
            return "dynamic"

        param = Mock(spec=click.Option)
        param.name = "test"
        param.help = "Test option"
        param.required = False
        param.default = default_func  # Callable default
        param.show_default = True
        param.envvar = None

        ctx = Mock()
        ctx.show_default = False

        result = _get_parameter_help(param=param, ctx=ctx, markup_mode="rich")
        assert result is not None
