"""Smoke tests for basic package functionality"""

import typer_extensions


def test_package_imports():
    """Test that package imports successfully"""
    assert hasattr(typer_extensions, "ExtendedTyper")
    assert hasattr(typer_extensions, "__version__")


def test_version_format():
    """Test that version string is properly formatted"""
    version = typer_extensions.__version__
    assert isinstance(version, str)
    assert len(version.split(".")) == 3  # semantic versioning


def test_aliased_typer_instantiation():
    """Test that ExtendedTyper can be instantiated"""
    app = typer_extensions.ExtendedTyper()
    assert isinstance(app, typer_extensions.ExtendedTyper)

    # Verify it's also a Typer instance
    import typer

    assert isinstance(app, typer.Typer)


def test_aliased_typer_has_core_methods():
    """Test that ExtendedTyper has core methods"""
    app = typer_extensions.ExtendedTyper()
    assert hasattr(app, "_register_alias")
    assert hasattr(app, "_register_command_with_aliases")
    assert hasattr(app, "_resolve_alias")
    assert hasattr(app, "_get_command")


def test_aliased_typer_config():
    """Test that ExtendedTyper stores configuration"""
    app = typer_extensions.ExtendedTyper(
        alias_case_sensitive=False, show_aliases_in_help=False
    )
    assert app._alias_case_sensitive is False
    assert app.show_aliases_in_help is False


def test_aliased_typer_has_argument_and_option():
    """Test that ExtendedTyper exposes Typer's Argument and Option"""
    import typer

    app = typer_extensions.ExtendedTyper()

    # Should be accessible as class attributes
    assert hasattr(app, "Argument")
    assert hasattr(app, "Option")

    # Should match Typer's
    assert app.Argument == typer.Argument
    assert app.Option == typer.Option


def test_getattr_fallback_to_typer():
    """Test that __getattr__ provides forward compatibility with Typer"""
    import typer

    # Test accessing Typer attributes through typer_extensions
    assert typer_extensions.Typer == typer.Typer
    assert typer_extensions.Exit == typer.Exit
    assert typer_extensions.Abort == typer.Abort


def test_getattr_raises_for_nonexistent_attribute():
    """Test that __getattr__ raises AttributeError for non-existent attributes"""
    import pytest

    with pytest.raises(AttributeError):
        _ = typer_extensions.NonExistentAttribute


def test_context_exported():
    """Test that Context is properly exported from the package"""
    from typer_extensions import Context

    assert Context is not None
    assert hasattr(Context, "__init__")
