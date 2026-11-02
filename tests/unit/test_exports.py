"""Tests for the public API of typer_extensions"""

import pytest
import typer

import typer_extensions
from typer_extensions import ExtendedTyper

TYPER_EXPORTS = (
    "Abort",
    "Argument",
    "BadParameter",
    "CallbackParam",
    "Exit",
    "FileBinaryRead",
    "FileBinaryWrite",
    "FileText",
    "FileTextWrite",
    "Option",
    "confirm",
    "echo",
    "format_filename",
    "get_app_dir",
    "get_binary_stream",
    "get_terminal_size",
    "get_text_stream",
    "getchar",
    "launch",
    "progressbar",
    "prompt",
    "run",
    "secho",
    "style",
)


def test_all_lists_the_public_api() -> None:
    """Test that '__all__' is exactly the documented API, so nothing drops out unnoticed"""
    assert set(typer_extensions.__all__) == {
        "Context",
        "ExtendedTyper",
        "__version__",
        *TYPER_EXPORTS,
    }


@pytest.mark.parametrize("name", TYPER_EXPORTS)
def test_typer_export_matches_typer(name) -> None:
    """Test that each name matches Typer's own object, on the package and on the class"""
    expected = getattr(typer, name)
    assert getattr(typer_extensions, name) is expected
    assert getattr(ExtendedTyper, name) is expected


def test_extended_typer_is_a_typer() -> None:
    """Test that ExtendedTyper is a subclass of typer.Typer"""
    assert issubclass(ExtendedTyper, typer.Typer)


def test_context_is_a_typer_context() -> None:
    """Test that Context is a subclass of typer.Context"""
    assert issubclass(typer_extensions.Context, typer.Context)


def test_version_is_semantic() -> None:
    """Test that the package version follows semantic versioning"""
    assert len(typer_extensions.__version__.split(".")) == 3


def test_getattr_forwards_names_outside_all() -> None:
    """Test that any imports outside of '__all__' are forwarded to Typer"""
    assert typer_extensions.Typer is typer.Typer


def test_getattr_raises_for_unknown_names() -> None:
    """Test that an AttributeError is raised for unknown inports"""
    with pytest.raises(AttributeError):
        _ = typer_extensions.DoesNotExist
