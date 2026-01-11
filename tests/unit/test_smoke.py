"""Smoke tests for basic package functionality"""

import typer_aliases


def test_package_imports():
    """Test that package imports successfully"""
    assert hasattr(typer_aliases, "AliasedTyper")
    assert hasattr(typer_aliases, "__version__")


def test_version_format():
    """Test that version string is properly formatted"""
    version = typer_aliases.__version__
    assert isinstance(version, str)
    assert len(version.split(".")) == 3  # semantic versioning


def test_aliased_typer_instantiation():
    """Test that AliasedTyper can be instantiated"""
    app = typer_aliases.AliasedTyper()
    assert isinstance(app, typer_aliases.AliasedTyper)

    # Verify it's also a Typer instance
    import typer

    assert isinstance(app, typer.Typer)


def test_aliased_typer_has_core_methods():
    """Test that AliasedTyper has core methods"""
    app = typer_aliases.AliasedTyper()
    assert hasattr(app, "_register_alias")
    assert hasattr(app, "_register_command_with_aliases")
    assert hasattr(app, "_resolve_alias")
    assert hasattr(app, "get_command")


def test_aliased_typer_config():
    """Test that AliasedTyper stores configuration"""
    app = typer_aliases.AliasedTyper(
        alias_case_sensitive=False, show_aliases_in_help=False
    )
    assert app._alias_case_sensitive is False
    assert app._show_aliases_in_help is False


def test_aliased_typer_has_argument_and_option():
    """Test that AliasedTyper exposes Typer's Argument and Option"""
    import typer

    app = typer_aliases.AliasedTyper()

    # Should be accessible as class attributes
    assert hasattr(app, "Argument")
    assert hasattr(app, "Option")

    # Should match Typer's
    assert app.Argument == typer.Argument
    assert app.Option == typer.Option
