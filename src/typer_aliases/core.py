"""Core AliasedTyper class extending typer.Typer with alias support"""

import re
from typing import Any, Callable, Optional, Protocol, Union, cast

import typer
import typer.main
from click import Command, Context, Group
from typer.core import TyperGroup


class HasName(Protocol):
    """Protocol for objects that have a name attribute"""

    __name__: str


class AliasedGroup(TyperGroup):
    """Custom Click Group that handles command aliases"""

    def __init__(
        self,
        *args: Any,
        aliased_typer: Optional["AliasedTyper"] = None,
        **kwargs: Any,
    ) -> None:
        """Initialise the AliasedGroup

        Args:
            aliased_typer: Reference to the AliasedTyper instance for alias resolution
            *args, **kwargs: Arguments passed to Click Group
        """
        super().__init__(*args, **kwargs)
        self.aliased_typer = aliased_typer

    def get_command(self, ctx: Context, cmd_name: str) -> Optional[Command]:
        """Override Click's get_command to support aliases

        Args:
            ctx: The Click context
            cmd_name: The name of the command

        Returns:
            The command if found, None otherwise
        """
        if self.aliased_typer is None:
            return super().get_command(ctx, cmd_name)

        # Try to resolve as an active alias first
        primary_cmd = self.aliased_typer._resolve_alias(cmd_name)
        if primary_cmd is not None:
            return super().get_command(ctx, primary_cmd)

        cmd = super().get_command(ctx, cmd_name)
        if cmd is not None:
            return cmd

        return None

    def format_help(self, ctx: Context, formatter: Any) -> None:
        """Override TyperGroup's format_help to inject aliases into Rich output

        Args:
            ctx: The Click context
            formatter: The Click HelpFormatter instance
        """
        # Check if Rich formatting is enabled
        if not hasattr(self, "rich_markup_mode") or self.rich_markup_mode is None:
            return super().format_help(ctx, formatter)

        from typer import rich_utils

        # Store original _print_commands_panel
        original_print = rich_utils._print_commands_panel

        def custom_print_commands_panel(
            *,
            name: str,
            commands: list[Command],
            markup_mode: Any,
            console: Any,
            cmd_len: int,
        ) -> None:
            """Wrapper that modifies command names to include aliases

            Args:
                name: The name of the command group
                commands: The list of commands in the group
                markup_mode: The markup mode for the console output
                console: The console instance for output
                cmd_len: The length of the longest command name
            """
            modified_commands = []
            max_len = cmd_len

            for command in commands:
                if (
                    self.aliased_typer
                    and self.aliased_typer._show_aliases_in_help
                    and command.name in self.aliased_typer._command_aliases
                ):
                    from .format import format_command_with_aliases

                    formatted_name = format_command_with_aliases(
                        command.name,
                        self.aliased_typer._command_aliases[command.name],
                        display_format=self.aliased_typer._alias_display_format,
                        max_num=self.aliased_typer._max_num_aliases,
                        separator=self.aliased_typer._alias_separator,
                    )

                    # Longest formatted name for correct column width
                    max_len = max(max_len, len(formatted_name))

                    # Temporary command object with the formatted name
                    cmd_copy = command
                    cmd_copy.name = formatted_name

                    modified_commands.append(cmd_copy)
                else:
                    modified_commands.append(command)

            # Call the original with modified commands & cmd_len
            original_print(
                name=name,
                commands=modified_commands,
                markup_mode=markup_mode,
                console=console,
                cmd_len=max_len,
            )

        # Temporarily replace the function
        rich_utils._print_commands_panel = custom_print_commands_panel  # type: ignore[assignment]
        try:
            # Call parent's format_help with custom_print_commands_panel
            super().format_help(ctx, formatter)
        finally:
            # Restore original function
            rich_utils._print_commands_panel = original_print  # type: ignore[assignment]


# Store original function
_original_get_group_from_info = typer.main.get_group_from_info


def _aliased_get_group_from_info(
    typer_info: "typer.main.TyperInfo",
    **kwargs: Any,
) -> Union[AliasedGroup, TyperGroup]:
    """Custom version of get_group_from_info that returns AliasedGroup for AliasedTyper instances

    Args:
        typer_info: The TyperInfo instance containing information about the Typer instance
        **kwargs: Additional keyword arguments

    Returns:
        An AliasedGroup if the Typer instance is an AliasedTyper, otherwise a standard TyperGroup
    """
    # Call original function to get standard TyperGroup
    group = _original_get_group_from_info(typer_info, **kwargs)

    # If Typer instance is AliasedTyper, wrap it in an AliasedGroup
    if isinstance(typer_info.typer_instance, AliasedTyper):
        aliased_typer = typer_info.typer_instance
        aliased_group = AliasedGroup(
            name=group.name,
            callback=group.callback,
            params=group.params,
            help=group.help,
            epilog=group.epilog,
            short_help=group.short_help,
            options_metavar=group.options_metavar,
            subcommand_metavar=group.subcommand_metavar,
            chain=group.chain,
            result_callback=group.result_callback,
            context_settings=group.context_settings,
            aliased_typer=aliased_typer,
            rich_markup_mode=group.rich_markup_mode,
            rich_help_panel=group.rich_help_panel,
        )

        for name, cmd in group.commands.items():
            aliased_group.add_command(cmd, name=name)

        return aliased_group

    # Standard TyperGroup
    return group


# Apply monkey-patch to Typer's group creation function
typer.main.get_group_from_info = _aliased_get_group_from_info  # type: ignore[assignment]


class AliasedTyper(typer.Typer):
    """Typer application with alias support"""

    # Expose Typer's Argument and Option
    Argument = staticmethod(typer.Argument)
    Option = staticmethod(typer.Option)

    def __init__(
        self,
        *args: Any,
        alias_case_sensitive: Optional[bool] = None,
        show_aliases_in_help: bool = True,
        alias_display_format: str = "({aliases})",
        alias_separator: str = ", ",
        max_num_aliases: int = 3,
        **kwargs: Any,
    ) -> None:
        """Initialise AliasedTyper

        Args:
            *args: Positional arguments for Typer
            alias_case_sensitive: Whether aliases are case sensitive. If None (default), will match
                Typer's case_sensitive setting from context_settings (defaults to True)
            show_aliases_in_help: Whether to show aliases in help
            alias_display_format: Format string for displaying aliases in help
                Must include the placeholder '{aliases}'
            alias_separator: Separator for displaying aliases in help (default: ', ')
            max_num_aliases: Maximum number of aliases to display before truncating with '+ N more'
            **kwargs: Keyword arguments for Typer
        """
        kwargs.setdefault("rich_markup_mode", "rich")
        kwargs.setdefault("rich_help_panel", True)
        super().__init__(*args, **kwargs)

        # Sync with Typer's case_sensitive setting if not explicitly set
        if alias_case_sensitive is None:
            context_settings = kwargs.get("context_settings") or {}
            typer_case_sensitive = context_settings.get("case_sensitive", True)
            self._alias_case_sensitive = typer_case_sensitive
        else:
            self._alias_case_sensitive = alias_case_sensitive

        self._show_aliases_in_help = show_aliases_in_help
        self._alias_display_format = alias_display_format
        self._alias_separator = alias_separator
        self._max_num_aliases = max_num_aliases

        # Mapping of command names to aliases (O(1) lookup)
        self._command_aliases: dict[str, list[str]] = {}
        self._alias_to_command: dict[str, str] = {}

    def _normalise_name(self, name: str) -> str:
        """Normalise command/alias name based on case sensitivity

        Args:
            name: The command/alias name to normalise

        Returns:
            The normalised command/alias name (lowercase if case insensitive)
        """
        return name.lower() if not self._alias_case_sensitive else name

    def _register_alias(self, command_name: str, alias: str) -> None:
        """Register an alias for a command

        Args:
            command_name: The name of the command
            alias: The alias to register

        Raises:
            ValueError: If the alias conflicts with an existing command/alias
        """
        if not alias or not isinstance(alias, str):
            raise ValueError("Alias must be a non-empty string")

        if any(c.isspace() for c in alias):
            raise ValueError("Alias cannot contain whitespace")

        if not re.match(r"^[\w\-]+$", alias, re.UNICODE):
            raise ValueError(
                "Alias must only contain alphanumeric characters, dashes, and underscores (Unicode allowed)"
            )

        normalised_alias = self._normalise_name(alias)
        normalised_cmd = self._normalise_name(command_name)

        # Check if alias is the same as command name
        if normalised_alias == normalised_cmd:
            raise ValueError(
                f"Alias '{alias}' cannot be the same as command name '{command_name}'"
            )

        # Check if alias is already registered
        if normalised_alias in self._alias_to_command:
            existing_cmd = self._alias_to_command[normalised_alias]
            raise ValueError(
                f"Alias '{alias}' is already registered for command '{existing_cmd}'"
            )

        # Register the alias
        self._alias_to_command[normalised_alias] = command_name

        # Add alias to command mapping
        if command_name not in self._command_aliases:
            self._command_aliases[command_name] = []
        self._command_aliases[command_name].append(alias)

    def _register_command_with_aliases(
        self,
        func: Callable[..., Any],
        name: str,
        aliases: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Command:
        """Register a command with aliases

        Args:
            func: The command function
            name: The command name
            aliases: List of aliases for the command
            **kwargs: Additional keyword arguments for command registration

        Returns:
            The registered Click Command object

        Raises:
            ValueError: If any aliases conflict with existing commands/aliases
        """
        aliases = aliases or []

        self.command(name, **kwargs)(func)

        for alias in aliases:
            self._register_alias(name, alias)

        click_obj = typer.main.get_command(self)
        if isinstance(click_obj, Group):
            command = click_obj.commands[name]
        else:
            command = click_obj

        return command

    def _resolve_alias(self, name: str) -> Optional[str]:
        """Resolve a command/alias name to its primary command name

        Args:
            name: The command/alias name to resolve

        Returns:
            The primary command name if found, or None if not found or removed
        """
        normalised_name = self._normalise_name(name)

        return self._alias_to_command.get(normalised_name)

    def get_command(self, ctx: Context, cmd_name: str) -> Optional[Command]:
        """Programmatically retrieve a command by its name/alias

        Args:
            ctx: The context in which the command is being invoked
            cmd_name: The name or alias of the command to retrieve

        Returns:
            The command if found, else None
        """
        if not hasattr(self, "_group") or self._group is None:
            if not hasattr(self, "_command") or self._command is None:
                # Trigger CLI build
                click_obj = typer.main.get_command(self)

                if hasattr(click_obj, "commands"):
                    self._group = click_obj
                else:
                    self._command = click_obj

        primary_cmd = self._resolve_alias(cmd_name)
        effective_name = primary_cmd if primary_cmd is not None else cmd_name

        # Single command apps
        if hasattr(self, "_command"):
            command = self._command
            if command.name == effective_name:
                return command
            return None

        # Multi-command apps
        group = cast(Group, self._group)
        if effective_name in group.commands:
            return group.commands[effective_name]
        return group.get_command(ctx, effective_name)

    def command_with_aliases(
        self,
        name: Optional[Union[str, Callable[..., Any]]] = None,
        *,
        aliases: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], Command]:
        """Decorator to register a command with aliases, similar to Typer's @app.command decorator

        Args:
            name: The name of the command - if not provided, inferred from the function name
            aliases: A list of aliases for the command
            **kwargs: Additional keyword arguments for command registration
                (e.g. help, hidden, deprecated, context_settings, etc.)

        Returns:
            A decorator that registers the command with the specified name and aliases
        """
        # Decorator used without parentheses (name inferred)
        if callable(name):
            func = name

            return self._register_command_with_aliases(
                func, name=cast(HasName, func).__name__, aliases=None, **kwargs
            )

        # Standard decorator with parentheses
        def decorator(func: Callable[..., Any]) -> Command:
            """Decorator to register a command with aliases

            Args:
                func: The command function

            Returns:
                The registered Click Command object
            """
            if isinstance(name, str) and name:
                command_name = name
            else:
                command_name = cast(HasName, func).__name__

            return self._register_command_with_aliases(
                func, name=command_name, aliases=aliases, **kwargs
            )

        return decorator

    def add_aliased_command(
        self,
        func: Callable[..., Any],
        name: Optional[str] = None,
        aliases: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Command:
        """Programmatically register a command with aliases

        Args:
            func: The command function
            name: The name of the command - if not provided, inferred from the function name
            aliases: A list of aliases for the command
            **kwargs: Additional keyword arguments for command registration

        Returns:
            The registered Click Command object

        Raises:
            ValueError: If any alias conflicts with existing commands/aliases
        """
        if isinstance(name, str) and name:
            command_name = name
        else:
            command_name = cast(HasName, func).__name__

        return self._register_command_with_aliases(
            func, name=command_name, aliases=aliases, **kwargs
        )

    def add_alias(self, command_name: str, alias: str) -> None:
        """Programmatically add an alias to an existing command

        This does not allow adding aliases to single-command applications, in line with Typer's design principle of treating single-commands apps as the default command, making aliases redundant

        Args:
            command_name: The name of the existing command
            alias: The alias to add

        Raises:
            ValueError: If the command doesn't exist, is a single-command app, or the alias conflicts with existing commands/aliases
        """
        # Get the underlying Click group
        click_obj = typer.main.get_command(self)

        if not isinstance(click_obj, Group):
            raise ValueError("Cannot add aliases to single-command applications")

        existing_command = click_obj.get_command(Context(click_obj), command_name)
        if existing_command is None:
            raise ValueError(f"Command '{command_name}' does not exist")

        self._register_alias(command_name, alias)

    def remove_alias(self, alias: str) -> bool:
        """Programmatically remove an alias from an existing command

        Args:
            alias: The alias to remove

        Returns:
            True if the alias was removed, False if it doesn't exist
        """
        normalised_alias = self._normalise_name(alias)

        if normalised_alias not in self._alias_to_command:
            return False

        primary_name = self._alias_to_command[normalised_alias]
        del self._alias_to_command[normalised_alias]

        if primary_name in self._command_aliases:
            try:
                self._command_aliases[primary_name].remove(alias)

                if not self._command_aliases[primary_name]:
                    del self._command_aliases[primary_name]

            except ValueError:
                pass

        return True

    def get_aliases(self, command_name: str) -> list[str]:
        """Retrieve the list of aliases for a given command

        Args:
            command_name: The name of the command

        Returns:
            A list of aliases for the command, or an empty list if no aliases or command doesn't exist
        """
        if command_name in self._command_aliases:
            return self._command_aliases[command_name].copy()
        return []

    def list_commands_with_aliases(self) -> dict[str, list[str]]:
        """List all commands and their aliases

        Returns a dictionary mapping command names to their aliases - only includes commands with aliases and returns a copy, so modifications won't affect the original

        Returns:
            A dictionary mapping command names to their aliases, or an empty dictionary if no commands have aliases
        """
        return {cmd: aliases.copy() for cmd, aliases in self._command_aliases.items()}
