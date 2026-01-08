"""Core AliasedTyper class extending typer.Typer with alias support"""

from typing import Any, Callable, Optional, Protocol, cast

import typer
import typer.main
from click import Command, Context, Group
from typer.core import TyperGroup


class HasName(Protocol):
    """Protocol for objects that have a name attribute"""

    __name__: str


class AliasedGroup(Group):
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
        cmd = super().get_command(ctx, cmd_name)
        if cmd is not None:
            return cmd

        # Resolve alias if command not found
        if self.aliased_typer is not None:
            primary_cmd = self.aliased_typer._resolve_alias(cmd_name)
            if primary_cmd is not None:
                return super().get_command(ctx, primary_cmd)

        return None


# Store original function
_original_get_group_from_info = typer.main.get_group_from_info


def _aliased_get_group_from_info(
    typer_info: "typer.main.TyperInfo",
    **kwargs: Any,
) -> AliasedGroup | TyperGroup:
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
        )

        for name, cmd in group.commands.items():
            aliased_group.add_command(cmd, name=name)

        return aliased_group

    return group


# Apply monkey-patch to Typer's group creation function
typer.main.get_group_from_info = _aliased_get_group_from_info  # type: ignore[assignment]


class AliasedTyper(typer.Typer):
    """Typer application with alias support"""

    def __init__(
        self,
        *args: Any,
        alias_case_sensitive: bool = True,
        show_aliases_in_help: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialise AliasedTyper

        Args:
            *args: Positional arguments for Typer
            alias_case_sensitive: Whether aliases are case sensitive
            show_aliases_in_help: Whether to show aliases in help
            **kwargs: Keyword arguments for Typer
        """
        super().__init__(*args, **kwargs)

        self._alias_case_sensitive = alias_case_sensitive
        self._show_aliases_in_help = show_aliases_in_help

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

        command = self.command(name, **kwargs)(func)

        for alias in aliases:
            self._register_alias(name, alias)
            alias_kwargs = kwargs.copy()
            alias_kwargs["hidden"] = True
            self.command(alias, **alias_kwargs)(func)

        return command

    def _resolve_alias(self, name: str) -> Optional[str]:
        """Resolve a command/alias name to its primary command name

        Args:
            name: The command/alias name to resolve

        Returns:
            The primary command name if found, else None
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
        if hasattr(self, "_command") and self._command is not None:
            command = self._command
            if command.name == effective_name:
                return command
            return None

        # Multi-command apps
        if hasattr(self, "_group") and self._group is not None:
            group = cast(Group, self._group)
            if effective_name in group.commands:
                return group.commands[effective_name]
            return group.get_command(ctx, effective_name)

        return None

    def command_with_aliases(
        self,
        name: Optional[str | Callable[..., Any]] = None,
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
