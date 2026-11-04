"""Unit tests for formatters module."""

import pytest

from typer_extensions.format import (
    calculate_width,
    format_commands_with_aliases,
    truncate_aliases,
)


@pytest.mark.parametrize(
    ("aliases", "max_num", "kwargs", "expected"),
    [
        ([], 3, {}, ""),
        (["only"], 3, {}, "only"),
        (["a", "b"], 3, {}, "a, b"),
        (["a", "b", "c"], 3, {}, "a, b, c"),
        (["a", "b", "c", "d"], 2, {}, "a, b, +2 more"),
        (["a", "b", "c"], 3, {"separator": " | "}, "a | b | c"),
        (["a", "b", "c", "d"], 2, {"separator": "; "}, "a; b; +2 more"),
        (["a", "b"], 0, {}, "+2 more"),
        (["a", "b"], -1, {}, "+2 more"),
    ],
)
def test_truncate_aliases(aliases, max_num, kwargs, expected) -> None:
    """Test aliases are joined, and truncated with +N more past the limit."""
    assert truncate_aliases(aliases, max_num, **kwargs) == expected


class TestFormatCommandsWithAliases:
    """Tests for format_commands_with_aliases function."""

    def test_no_commands(self) -> None:
        """Test empty command list."""
        assert format_commands_with_aliases([], {}) == []

    def test_commands_without_aliases(self) -> None:
        """Test commands without any aliases."""
        names = ["list", "delete"]

        assert format_commands_with_aliases(names, {"other": ["o"]}) == names

    def test_unaliased_names_are_not_padded(self) -> None:
        """Test only aliased names are padded, whatever the order."""
        result = format_commands_with_aliases(["short", "longest"], {"short": ["s"]})

        assert result == ["short     (s)", "longest"]

    def test_all_commands_with_aliases(self) -> None:
        """Test all commands have aliases."""
        aliases = {"list": ["ls", "l"], "delete": ["rm"]}
        result = format_commands_with_aliases(["list", "delete"], aliases)

        assert result == ["list     (ls, l)", "delete   (rm)   "]

    def test_mixed_aliased_and_non_aliased(self) -> None:
        """Test mix of commands with and without aliases."""
        aliases = {"list": ["ls"], "delete": ["rm"]}
        result = format_commands_with_aliases(["list", "delete", "create"], aliases)

        assert result == ["list     (ls)", "delete   (rm)", "create"]

    @pytest.mark.parametrize(
        ("options", "expected"),
        [
            ({"display_format": "[{aliases}]"}, "[a, b, c]"),
            ({"display_format": "<{aliases}>"}, "<a, b, c>"),
            ({"separator": " | "}, "(a | b | c)"),
            ({"max_num": 1}, "(a, +2 more)"),
            (
                {"display_format": "[{aliases}]", "separator": " / ", "max_num": 2},
                "[a / b / +1 more]",
            ),
        ],
    )
    def test_custom_options(self, options, expected) -> None:
        """Test custom display format, separator and max_num are applied."""
        aliases = {"cmd": ["a", "b", "c"]}
        result = format_commands_with_aliases(["cmd"], aliases, **options)

        assert result == [f"cmd   {expected}"]

    def test_wide_characters_pad_by_display_width(self) -> None:
        """Test wide aliases are padded by terminal width, not len()."""
        aliases = {"list": ["列表"], "delete": ["rm"]}
        result = format_commands_with_aliases(["list", "delete"], aliases)

        assert result == ["list     (列表)", "delete   (rm)  "]
        assert len({calculate_width(name) for name in result}) == 1

    def test_preserves_command_order(self) -> None:
        """Test that command order is preserved."""
        aliases = {"zzz": ["z"], "aaa": ["a"]}
        result = format_commands_with_aliases(["zzz", "aaa", "mmm"], aliases)

        assert result == ["zzz   (z)", "aaa   (a)", "mmm"]


def test_calculate_width_falls_back_to_len_for_non_printable() -> None:
    """wcswidth returns -1 for control chars; calculate_width falls back to len()."""
    assert calculate_width("a\x07b") == 3
