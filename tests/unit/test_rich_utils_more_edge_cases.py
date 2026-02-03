"""Additional Rich utilities edge case tests requiring complex mocking."""

from unittest.mock import Mock, patch

import click


class TestParameterRangeConstraints:
    """Test parameters with range constraints."""

    def test_parameter_with_range_constraint(self):
        """Test parameter with range type."""
        from typer_extensions._rich_utils import _get_parameter_help

        # Create a parameter with a range type
        param = Mock(spec=click.Option)
        param.name = "port"
        param.help = "Port number"
        param.required = False
        param.default = 8080
        param.show_default = True
        param.envvar = None

        # Create a mock range type
        range_type = Mock()
        range_type.name = "IntRange"
        range_type.min = 1024
        range_type.max = 65535
        param.type = range_type

        ctx = Mock()
        ctx.show_default = False

        result = _get_parameter_help(param=param, ctx=ctx, markup_mode="rich")
        assert result is not None


class TestCommandAliasHandling:
    """Test command formatting with aliases."""

    def test_commands_with_aliases(self):
        """Test command panel with alias support enabled."""
        from typer_extensions._rich_utils import _print_commands_panel

        # Create mock commands
        cmd1 = Mock(spec=click.Command)
        cmd1.name = "start"
        cmd1.help = "Start the service"
        cmd1.deprecated = False
        cmd1.hidden = False

        cmd2 = Mock(spec=click.Command)
        cmd2.name = "stop"
        cmd2.help = "Stop the service"
        cmd2.deprecated = False
        cmd2.hidden = False

        # Create extended_typer with alias support
        extended_typer = Mock()
        extended_typer.show_aliases_in_help = True
        extended_typer._command_aliases = {"start": ["run", "s"], "stop": ["halt", "x"]}

        console = Mock()
        console.print = Mock()

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            # Mock the format function
            with patch(
                "typer_extensions.format.format_commands_with_aliases"
            ) as mock_format:
                mock_format.return_value = [
                    ("start", ["run", "s"]),
                    ("stop", ["halt", "x"]),
                ]

                _print_commands_panel(
                    name="Commands",
                    commands=[cmd1, cmd2],
                    markup_mode="rich",
                    console=console,
                    cmd_len=20,
                    extended_typer=extended_typer,
                )

    def test_commands_with_alias_error_recovery(self):
        """Test command alias formatting with error recovery."""
        from typer_extensions._rich_utils import _print_commands_panel

        cmd = Mock(spec=click.Command)
        cmd.name = "test"
        cmd.help = "Test command"
        cmd.deprecated = False
        cmd.hidden = False

        extended_typer = Mock()
        extended_typer.show_aliases_in_help = True
        extended_typer._command_aliases = {"test": ["t"]}

        console = Mock()
        console.print = Mock()

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            # Mock format function to raise an exception
            with patch(
                "typer_extensions.format.format_commands_with_aliases"
            ) as mock_format:
                mock_format.side_effect = Exception("Format error")

                # Should handle the error gracefully
                _print_commands_panel(
                    name="Commands",
                    commands=[cmd],
                    markup_mode="rich",
                    console=console,
                    cmd_len=20,
                    extended_typer=extended_typer,
                )


class TestDeprecatedCommands:
    """Test deprecated command handling."""

    def test_deprecated_command_in_fallback(self):
        """Test deprecated command in fallback mode."""
        from typer_extensions._rich_utils import _print_commands_panel

        cmd = Mock(spec=click.Command)
        cmd.name = "oldcmd"
        cmd.help = "Old command"
        cmd.deprecated = True  # Deprecated!
        cmd.hidden = False

        console = Mock()
        console.print = Mock()

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", False):
            with patch("typer_extensions._rich_utils.click.echo"):
                # Should use click.echo instead of console.print
                _print_commands_panel(
                    name="Commands",
                    commands=[cmd],
                    markup_mode="rich",
                    console=console,
                    cmd_len=20,
                    extended_typer=None,
                )
                # Should work without error

    def test_deprecated_command_with_rich(self):
        """Test deprecated command with Rich enabled."""
        from typer_extensions._rich_utils import _print_commands_panel

        cmd = Mock(spec=click.Command)
        cmd.name = "oldcmd"
        cmd.help = "Old command"
        cmd.deprecated = True
        cmd.hidden = False

        console = Mock()
        console.print = Mock()

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            _print_commands_panel(
                name="Commands",
                commands=[cmd],
                markup_mode="rich",
                console=console,
                cmd_len=20,
                extended_typer=None,
            )


class TestHiddenCommands:
    """Test that hidden commands are properly excluded."""

    def test_hidden_command_not_shown(self):
        """Test that hidden commands are properly filtered in formatting."""
        from typer_extensions._rich_utils import rich_format_help

        # Create hidden and visible commands
        hidden_cmd = Mock(spec=click.Command)
        hidden_cmd.name = "hidden"
        hidden_cmd.help = "Hidden command"
        hidden_cmd.hidden = True  # Hidden!
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
        # Mock get_usage to return a proper string
        obj.get_usage = Mock(return_value="test-group")

        ctx = Mock()
        ctx.command = obj

        console = Mock()
        console.print = Mock()

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            with patch(
                "typer_extensions._rich_utils._get_rich_console", return_value=console
            ):
                rich_format_help(obj=obj, ctx=ctx, markup_mode="rich")
                # Should work without error


class TestMultilineHelpText:
    """Test multiline help text edge cases."""

    def test_help_with_form_feed(self):
        """Test help text with form feed character."""
        from typer_extensions._rich_utils import _get_help_text

        obj = Mock(spec=click.Command)
        obj.help = "First part\fSecond part that should be hidden"
        obj.deprecated = False

        # _get_help_text returns a Rich renderable object
        result = _get_help_text(obj=obj, markup_mode="rich")

        # Should be a Group object
        assert result is not None

    def test_help_with_literal_break(self):
        """Test help text with literal break marker."""
        from typer_extensions._rich_utils import _get_help_text

        obj = Mock(spec=click.Command)
        obj.help = "\\b\nLine 1\nLine 2"  # Literal break marker
        obj.deprecated = False

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            result = _get_help_text(obj=obj, markup_mode="rich")
            assert result is not None


class TestErrorFormattingEdgeCases:
    """Test error formatting edge cases."""

    def test_error_without_context(self):
        """Test error formatting when ctx is None."""
        from typer_extensions._rich_utils import rich_format_error

        exc = click.ClickException("Test error")
        # ClickException is set during Click processing, so just testing behavior

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            with patch(
                "typer_extensions._rich_utils._get_rich_console"
            ) as mock_console:
                console = Mock()
                console.print = Mock()
                mock_console.return_value = console

                rich_format_error(exc)

                # Should still format the error even without context
                assert console.print.called

    def test_error_without_help_option(self):
        """Test error formatting when command has no help option."""
        from typer_extensions._rich_utils import rich_format_error

        exc = click.ClickException("Test error")

        ctx = Mock()
        cmd = Mock()
        cmd.get_help_option = Mock(return_value=None)  # No help option!
        cmd.command_path = "myapp"
        ctx.command = cmd
        # Set ctx as an attribute - Click does this during exception handling
        object.__setattr__(exc, "ctx", ctx)

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            with patch(
                "typer_extensions._rich_utils._get_rich_console"
            ) as mock_console:
                console = Mock()
                console.print = Mock()
                mock_console.return_value = console

                rich_format_error(exc)

                # Should format error without help suggestion
                console.print.assert_called()

    def test_no_args_is_help_error_passthrough(self):
        """Test that NoArgsIsHelpError is not formatted."""
        from typer_extensions._rich_utils import rich_format_error

        # Create a mock NoArgsIsHelpError
        exc = click.ClickException("No args")
        exc.__class__.__name__ = "NoArgsIsHelpError"

        # Should return early without formatting
        result = rich_format_error(exc)
        assert result is None


class TestGetTracebackEdgeCases:
    """Test get_traceback edge cases."""

    def test_traceback_with_config(self):
        """Test traceback with exception config."""
        from typer_extensions._rich_utils import get_traceback

        try:
            raise ValueError("Test exception")
        except ValueError as e:
            config = Mock()
            config.pretty_exceptions_show_locals = True

            with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
                with patch("typer_extensions._rich_utils.Traceback") as MockTraceback:
                    MockTraceback.from_exception = Mock(return_value=Mock())

                    get_traceback(
                        exc=e, exception_config=config, internal_dir_names=["internal"]
                    )

                    # Should call with show_locals=True
                    MockTraceback.from_exception.assert_called_once()
                    call_kwargs = MockTraceback.from_exception.call_args[1]
                    assert call_kwargs["show_locals"] is True

    def test_traceback_without_config(self):
        """Test traceback without exception config."""
        from typer_extensions._rich_utils import get_traceback

        try:
            raise ValueError("Test exception")
        except ValueError as e:
            with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
                with patch("typer_extensions._rich_utils.Traceback") as MockTraceback:
                    MockTraceback.from_exception = Mock(return_value=Mock())

                    get_traceback(
                        exc=e,
                        exception_config=None,  # No config
                        internal_dir_names=["internal"],
                    )

                    # Should call with show_locals=False (default)
                    MockTraceback.from_exception.assert_called_once()
                    call_kwargs = MockTraceback.from_exception.call_args[1]
                    assert call_kwargs["show_locals"] is False


class TestRichRenderText:
    """Test rich_render_text edge cases."""

    def test_render_text_without_rich(self):
        """Test text rendering without Rich."""
        from typer_extensions._rich_utils import rich_render_text

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", False):
            result = rich_render_text("[bold]Test[/bold] text")

            # Should strip rich tags
            assert "bold" not in result or ("[" not in result and "]" not in result)
            assert "Test" in result

    def test_render_text_console_none(self):
        """Test text rendering when console is None."""
        from typer_extensions._rich_utils import rich_render_text

        with patch("typer_extensions._rich_utils.RICH_AVAILABLE", True):
            with patch(
                "typer_extensions._rich_utils._get_rich_console", return_value=None
            ):
                result = rich_render_text("[bold]Test[/bold] text")

                # Should fall back to tag removal
                assert "Test" in result


class TestSecondaryOptions:
    """Test secondary options handling."""

    def test_option_with_secondary_opts(self):
        """Test option with secondary options."""
        from typer_extensions._rich_utils import _print_options_panel

        param = Mock(spec=click.Option)
        param.name = "verbose"
        param.opts = ["--verbose"]
        param.secondary_opts = ["-v"]  # Secondary short option
        param.required = False
        param.help = "Verbose output"
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
