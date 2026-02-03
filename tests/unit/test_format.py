"""Unit tests for formatters module."""

from unittest.mock import patch

from typer_extensions.format import (
    format_commands_with_aliases,
    truncate_aliases,
)


class TestTruncateAliases:
    """Tests for truncate_aliases function."""

    def test_empty_list(self):
        """Test that empty list returns empty string."""
        result = truncate_aliases([], 3)
        assert result == ""

    def test_within_limit(self):
        """Test aliases within limit show all."""
        result = truncate_aliases(["a", "b"], 3)
        assert result == "a, b"

    def test_at_exact_limit(self):
        """Test aliases at exact limit show all."""
        result = truncate_aliases(["a", "b", "c"], 3)
        assert result == "a, b, c"

    def test_over_limit(self):
        """Test aliases over limit truncate with +N more."""
        result = truncate_aliases(["a", "b", "c", "d"], 2)
        assert result == "a, b, +2 more"

    def test_custom_separator(self):
        """Test custom separator between aliases."""
        result = truncate_aliases(["a", "b", "c"], 3, separator=" | ")
        assert result == "a | b | c"

    def test_truncate_with_custom_separator(self):
        """Test truncation with custom separator."""
        result = truncate_aliases(["a", "b", "c", "d"], 2, separator="; ")
        assert result == "a; b; +2 more"

    def test_single_alias(self):
        """Test single alias returns just that alias."""
        result = truncate_aliases(["only"], 3)
        assert result == "only"

    def test_many_aliases_truncated(self):
        """Test many aliases show correct count."""
        aliases = ["a", "b", "c", "d", "e", "f"]
        result = truncate_aliases(aliases, 2)
        assert result == "a, b, +4 more"


class TestFormatCommandsWithAliases:
    """Tests for format_commands_with_aliases function."""

    def test_no_commands(self):
        """Test empty command list."""
        result, max_len = format_commands_with_aliases([], {})

        assert result == []
        assert max_len == 0

    def test_commands_without_aliases(self):
        """Test commands without any aliases."""
        commands = [("list", "List items"), ("delete", "Delete items")]
        result, max_len = format_commands_with_aliases(commands, {})

        assert result == commands

    def test_single_command_with_alias(self):
        """Test single command with alias."""
        commands = [("list", "List items")]
        aliases = {"list": ["ls"]}
        result, max_len = format_commands_with_aliases(commands, aliases)

        assert len(result) == 1
        assert result[0][0].startswith("list")
        assert result[0][1] == "List items"

    def test_all_commands_with_aliases(self):
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

    def test_mixed_aliased_and_non_aliased(self):
        """Test mix of commands with and without aliases."""
        commands = [
            ("list", "List items"),
            ("delete", "Delete items"),
            ("create", "Create item"),
        ]
        aliases = {"list": ["ls"], "delete": ["rm"]}
        result, max_len = format_commands_with_aliases(commands, aliases)

        assert len(result) == 3
        assert result[0][0].startswith("list")
        assert result[1][0].startswith("delete")
        assert result[2][0] == "create"

    def test_custom_display_format_square(self):
        """Test custom display format with square brackets."""
        commands = [("list", "List items")]
        aliases = {"list": ["ls", "l"]}
        result, max_len = format_commands_with_aliases(
            commands, aliases, display_format="[{aliases}]"
        )

        assert "[ls, l]" in result[0][0]

    def test_custom_display_format_arrow(self):
        """Test custom display format with arrows."""
        commands = [("list", "List items")]
        aliases = {"list": ["ls", "l"]}
        result, max_len = format_commands_with_aliases(
            commands, aliases, display_format="<{aliases}>"
        )

        assert "<ls, l>" in result[0][0]

    def test_custom_separator(self):
        """Test custom separator is applied."""
        commands = [("list", "List items")]
        aliases = {"list": ["ls", "l"]}
        result, max_len = format_commands_with_aliases(
            commands, aliases, separator=" | "
        )

        assert "ls | l" in result[0][0]

    def test_custom_max_num(self):
        """Test custom max_num is applied."""
        commands = [("list", "List items")]
        aliases = {"list": ["ls", "l"]}
        result, max_len = format_commands_with_aliases(commands, aliases, max_num=1)

        assert "(ls, +1 more)" in result[0][0]

    def test_combined_custom_params(self):
        """Test combined custom parameters are applied."""
        commands = [("cmd", "Command")]
        aliases = {"cmd": ["a", "b", "c"]}
        result, max_len = format_commands_with_aliases(
            commands, aliases, display_format="[{aliases}]", separator=" / ", max_num=2
        )

        assert "[a / b / +1 more]" in result[0][0]

    def test_alignment_padding(self):
        """Test that commands are properly aligned with padding."""
        commands = [("a", "Short"), ("verylongname", "Long help text")]
        aliases = {"a": ["x"], "verylongname": ["vln"]}
        result, max_len = format_commands_with_aliases(commands, aliases)

        # Should be padded to the same length
        assert len(result[0][0]) == len(result[1][0])

    def test_long_command_name(self):
        """Test long command name is handled properly."""
        commands = [("verylongcommandname", "Long help text")]
        aliases = {"verylongcommandname": ["vlcn"]}
        result, max_len = format_commands_with_aliases(commands, aliases)

        assert "verylongcommandname" in result[0][0]
        assert "(vlcn)" in result[0][0]

    def test_unicode_aliases(self):
        """Test handling of unicode characters in aliases."""
        commands = [("list", "List items")]
        aliases = {"list": ["ls", "列表"]}
        result, max_len = format_commands_with_aliases(commands, aliases)

        assert "ls" in result[0][0]
        assert "列表" in result[0][0]

    def test_none_help_text(self):
        """Test commands with None help text."""
        commands = [("list", None), ("delete", "Delete items")]
        aliases = {"list": ["ls"]}
        result, max_len = format_commands_with_aliases(commands, aliases)

        assert result[0][1] is None
        assert result[1][1] == "Delete items"

    def test_preserves_command_order(self):
        """Test that command order is preserved."""
        commands = [
            ("zzz", "Last alphabetically"),
            ("aaa", "First alphabetically"),
            ("mmm", "Middle"),
        ]
        aliases = {"zzz": ["z"], "aaa": ["a"]}
        result, max_len = format_commands_with_aliases(commands, aliases)

        # Order should be preserved, not alphabetised
        assert result[0][0].startswith("zzz")
        assert result[1][0].startswith("aaa")
        assert result[2][0] == "mmm"

    def test_formatted_max_length_returned(self):
        """Test that the formatted max length is correctly returned."""
        commands = [("short", "Short"), ("verylongcommand", "Long")]
        aliases = {"short": ["s"], "verylongcommand": ["vlc"]}
        result, max_len = format_commands_with_aliases(commands, aliases)

        # Should be the length of longest formatted command
        assert max_len == len(result[0][0])
        assert max_len == len(result[1][0])


class TestFormattersEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_very_long_alias_list(self):
        """Test with very long list of aliases."""
        aliases = [f"alias{i}" for i in range(100)]
        result = truncate_aliases(aliases, 3)
        assert result == "alias0, alias1, alias2, +97 more"

    def test_alias_with_spaces(self):
        """Test aliases containing spaces."""
        commands = [("cmd", "Command")]
        aliases = {"cmd": ["alias one", "alias two"]}
        result, max_len = format_commands_with_aliases(commands, aliases)

        assert "alias one" in result[0][0]
        assert "alias two" in result[0][0]

    def test_alias_with_special_chars(self):
        """Test aliases with special characters."""
        commands = [("cmd", "Command")]
        aliases = {"cmd": ["alias@one", "alias#two", "alias$three"]}
        result, max_len = format_commands_with_aliases(commands, aliases)

        assert "alias@one" in result[0][0]
        assert "alias#two" in result[0][0]
        assert "alias$three" in result[0][0]

    def test_empty_string_alias(self):
        """Test handling of empty string in alias list."""
        # Should be prevented in practice, but tested defensively
        result = truncate_aliases(["a", "", "b"], 3)
        assert result == "a, , b"

    def test_max_num_zero(self):
        """Test max_num of 0 shows +N more immediately."""
        result = truncate_aliases(["a", "b"], 0)
        assert result == "+2 more"

    def test_max_num_negative(self):
        """Test negative max_num (edge case, treat as 0)."""
        result = truncate_aliases(["a", "b"], -1)
        # Should return empty, so only +N more
        assert "+2 more" in result

    def test_calculate_width_import_error_fallback(self):
        """Test calculate_width fallback when wcswidth raises ImportError

        Covers lines 52-54: ImportError exception handler
        """
        from typer_extensions import format

        # Patch wcswidth to raise ImportError
        with patch(
            "typer_extensions.format.wcswidth", side_effect=ImportError("Mock error")
        ):
            # Should fall back to len()
            result = format.calculate_width("test string")
            assert result == len("test string")
