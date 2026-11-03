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
        result, max_len = format_commands_with_aliases([], {})

        assert result == []
        assert max_len == 0

    def test_commands_without_aliases(self) -> None:
        """Test commands without any aliases."""
        commands = [("list", "List items"), ("delete", "Delete items")]
        result, _ = format_commands_with_aliases(commands, {})

        assert result == commands

    def test_max_length_of_unaliased_commands(self) -> None:
        """Test the max length measures the longest name, not the last one.

        A panel can hold only unaliased commands while other panels supply the
        alias map, so the width must not depend on iteration order.
        """
        commands = [("longest", "Longest"), ("short", "Short")]
        result, max_len = format_commands_with_aliases(commands, {"other": ["o"]})

        assert result == commands
        assert max_len == len("longest")

    def test_all_commands_with_aliases(self) -> None:
        """Test all commands have aliases."""
        commands = [("list", "List items"), ("delete", "Delete items")]
        aliases = {"list": ["ls", "l"], "delete": ["rm"]}
        result, max_len = format_commands_with_aliases(commands, aliases)

        assert len(result) == 2
        assert result[0][0].startswith("list")
        assert "(ls, l)" in result[0][0]
        assert result[1][0].startswith("delete")
        assert "(rm)" in result[1][0]

        # Should be padded to the same length
        assert len(result[0][0]) == len(result[1][0])
        assert max_len == len(result[0][0])

    def test_mixed_aliased_and_non_aliased(self) -> None:
        """Test mix of commands with and without aliases."""
        commands = [
            ("list", "List items"),
            ("delete", "Delete items"),
            ("create", "Create item"),
        ]
        aliases = {"list": ["ls"], "delete": ["rm"]}
        result, _ = format_commands_with_aliases(commands, aliases)

        assert len(result) == 3
        assert result[0][0].startswith("list")
        assert result[1][0].startswith("delete")
        assert result[2][0] == "create"

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
        commands = [("cmd", "Command")]
        aliases = {"cmd": ["a", "b", "c"]}
        result, _ = format_commands_with_aliases(commands, aliases, **options)

        assert expected in result[0][0]

    def test_unicode_aliases(self) -> None:
        """Test handling of unicode characters in aliases."""
        commands = [("list", "List items")]
        aliases = {"list": ["ls", "列表"]}
        result, _ = format_commands_with_aliases(commands, aliases)

        assert "ls" in result[0][0]
        assert "列表" in result[0][0]

    def test_none_help_text(self) -> None:
        """Test commands with None help text."""
        commands = [("list", None), ("delete", "Delete items")]
        aliases = {"list": ["ls"]}
        result, _ = format_commands_with_aliases(commands, aliases)

        assert result[0][1] is None
        assert result[1][1] == "Delete items"

    def test_preserves_command_order(self) -> None:
        """Test that command order is preserved."""
        commands = [
            ("zzz", "Last alphabetically"),
            ("aaa", "First alphabetically"),
            ("mmm", "Middle"),
        ]
        aliases = {"zzz": ["z"], "aaa": ["a"]}
        result, _ = format_commands_with_aliases(commands, aliases)

        # Order should be preserved, not alphabetised
        assert result[0][0].startswith("zzz")
        assert result[1][0].startswith("aaa")
        assert result[2][0] == "mmm"


def test_calculate_width_falls_back_to_len_for_non_printable() -> None:
    """wcswidth returns -1 for control chars; calculate_width falls back to len()."""
    assert calculate_width("a\x07b") == 3
