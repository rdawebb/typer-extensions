"""Core ExtendedTyper class extending typer.Typer with alias support"""

import re
from typing import Any, Callable, Optional, Protocol, Union, cast

import typer
import typer.main
from click import Command, Group
from click.core import Context
from typer.core import TyperGroup


_ALIAS_PATTERN = re.compile(r"^[\w\-]+$", re.UNICODE)


class HasName(Protocol):
    """Protocol for objects that have a name attribute"""

    __name__: str


class ExtendedGroup(TyperGroup):
    """Custom Typer Group that handles command aliases"""

    def __init__(
        self,
        *args: Any,
        extended_typer: Optional["ExtendedTyper"] = None,
        **kwargs: Any,
    ) -> None:
        """Initialise the ExtendedGroup

        Args:
            extended_typer: Reference to the ExtendedTyper instance for alias resolution
            *args, **kwargs: Arguments passed to Typer Group
        """
        super().__init__(*args, **kwargs)
        self._extended_typer = extended_typer

    def get_command(self, ctx: Context, cmd_name: str) -> Optional[Command]:
        """Override Click's get_command to support aliases

        Args:
            ctx: The Click context
            cmd_name: The name of the command

        Returns:
            The command if found, None otherwise
        """
        if self._extended_typer is None:
            return super().get_command(ctx, cmd_name)

        # Try to resolve as an active alias first
        primary_cmd = self._extended_typer._resolve_alias(cmd_name)
        if primary_cmd is not None:
            cmd_name = primary_cmd

        return super().get_command(ctx, cmd_name)


# Store original function
_original_get_group_from_info = typer.main.get_group_from_info


def _extended_get_group_from_info(
    typer_info: Any,
    **kwargs: Any,
) -> Union[ExtendedGroup, TyperGroup]:
    """Custom version of get_group_from_info that returns ExtendedGroup for ExtendedTyper instances

    Args:
        typer_info: The TyperInfo instance containing information about the Typer instance
        **kwargs: Additional keyword arguments

    Returns:
        An ExtendedGroup if the Typer instance is an ExtendedTyper, otherwise a standard TyperGroup
    """
    # Call original function to get standard TyperGroup
    group = _original_get_group_from_info(typer_info, **kwargs)

    # If Typer instance is ExtendedTyper, wrap it in an ExtendedGroup
    if isinstance(typer_info.typer_instance, ExtendedTyper):
        extended_typer = typer_info.typer_instance

        if not extended_typer._alias_to_command:
            return group  # No aliases registered, return standard group

        typer_group_kwargs = {
            "name": group.name,
            "callback": group.callback,
            "params": group.params,
            "help": group.help,
            "epilog": group.epilog,
            "short_help": group.short_help,
            "options_metavar": group.options_metavar,
            "subcommand_metavar": group.subcommand_metavar,
            "chain": group.chain,
            "result_callback": group.result_callback,
            "context_settings": group.context_settings,
        }

        if hasattr(group, "__dict__"):
            if "rich_markup_mode" in group.__dict__:
                typer_group_kwargs["rich_markup_mode"] = group.__dict__[
                    "rich_markup_mode"
                ]
            if "rich_help_panel" in group.__dict__:
                typer_group_kwargs["rich_help_panel"] = group.__dict__[
                    "rich_help_panel"
                ]

        extended_group = ExtendedGroup(
            **typer_group_kwargs,
            extended_typer=extended_typer,
        )

        extended_group.commands = group.commands

        return extended_group

    # Standard TyperGroup
    return group


# Apply monkey-patch to Typer's group creation function
typer.main.get_group_from_info = _extended_get_group_from_info  # type: ignore[assignment]


class Context(typer.Context):
    """Context for ExtendedTyper commands."""

    pass


class ExtendedTyper(typer.Typer):
    """Typer application with alias support"""

    # Expose Typer's Argument and Option
    Argument = staticmethod(typer.Argument)
    Option = staticmethod(typer.Option)

    # Expose common Typer utility functions
    echo = staticmethod(typer.echo)
    echo_via_pager = staticmethod(typer.echo_via_pager)
    secho = staticmethod(typer.secho)
    style = staticmethod(typer.style)
    prompt = staticmethod(typer.prompt)
    confirm = staticmethod(typer.confirm)
    getchar = staticmethod(typer.getchar)
    clear = staticmethod(typer.clear)
    pause = staticmethod(typer.pause)
    progressbar = staticmethod(typer.progressbar)
    launch = staticmethod(typer.launch)
    open_file = staticmethod(typer.open_file)
    get_app_dir = staticmethod(typer.get_app_dir)
    get_terminal_size = staticmethod(typer.get_terminal_size)
    run = staticmethod(typer.run)

    _alias_case_sensitive: bool

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
        """Initialise ExtendedTyper

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
        super().__init__(*args, **kwargs)

        # Sync with Typer's case_sensitive setting if not explicitly set
        if alias_case_sensitive is None:
            context_settings: dict[str, Any] = kwargs.get("context_settings") or {}
            typer_case_sensitive = context_settings.get("case_sensitive", True)
            self._alias_case_sensitive = typer_case_sensitive
        else:
            self._alias_case_sensitive = alias_case_sensitive

        self.show_aliases_in_help = show_aliases_in_help
        self.alias_display_format = alias_display_format
        self.alias_separator = alias_separator
        self.max_num_aliases = max_num_aliases

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

        if not _ALIAS_PATTERN.match(alias):
            raise ValueError(
                "Alias must only contain alphanumeric characters, dashes, and underscores (Unicode allowed)"
            )

        normalised_alias = self._normalise_name(alias)
        normalised_cmd = self._normalise_name(command_name)

        if normalised_alias == normalised_cmd:
            raise ValueError(
                f"Alias '{alias}' cannot be the same as command name '{command_name}'"
            )

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
            The registered command function

        Raises:
            ValueError: If any aliases conflict with existing commands/aliases
        """
        aliases = aliases or []

        cmd = super().command(name, **kwargs)(func)

        for alias in aliases:
            self._register_alias(name, alias)

        return cmd

    def _resolve_alias(self, name: str) -> Optional[str]:
        """Resolve a command/alias name to its primary command name

        Args:
            name: The command/alias name to resolve

        Returns:
            The primary command name if found, or None if not found or removed
        """
        normalised_name = self._normalise_name(name)

        return self._alias_to_command.get(normalised_name)

    def _get_command(self, ctx: Context, cmd_name: str) -> Optional[Command]:
        """Programmatically retrieve a command by its name/alias

        Args:
            ctx: The context in which the command is being invoked
            cmd_name: The name or alias of the command to retrieve

        Returns:
            The command if found, else None
        """
        if getattr(self, "_group", None) is None:
            if getattr(self, "_command", None) is None:
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

    def command(
        self,
        name: Optional[Union[str, Callable[..., Any]]] = None,
        *,
        aliases: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], Command]:
        """Decorator to register a command with the specified name and optional aliases.

        Overrides the default behavior of Typer's @app.command decorator.

        Args:
            name: The name of the command - if not provided, inferred from the function name
            aliases: A list of aliases for the command
            **kwargs: Additional keyword arguments for command registration
                (e.g. help, hidden, deprecated, context_settings, etc.)

        Returns:
            A decorator that registers the command with the specified name and aliases
        """
        if callable(name):
            func = name

            return self._register_command_with_aliases(
                func, name=cast(HasName, func).__name__, aliases=None, **kwargs
            )

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

    def add_command(
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
        """List all aliased commands and their aliases

        Only includes commands with aliases and returns a copy, so modifications won't affect the original

        Returns:
            A dictionary mapping command names to their aliases, or an empty dictionary if no commands have aliases
        """
        return {cmd: aliases.copy() for cmd, aliases in self._command_aliases.items()}
