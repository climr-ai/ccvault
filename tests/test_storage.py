"""Tests for storage functionality."""

import pytest
from pathlib import Path

from dnd_manager.storage.yaml_store import YAMLStore


class TestFilenameSanitization:
    """Tests for filename sanitization security."""

    def test_basic_name(self):
        """Test basic name sanitization."""
        assert YAMLStore._sanitize_filename("Thorin") == "thorin"
        assert YAMLStore._sanitize_filename("My Character") == "my_character"

    def test_spaces_to_underscores(self):
        """Test that spaces become underscores."""
        assert YAMLStore._sanitize_filename("Iron Man") == "iron_man"
        assert YAMLStore._sanitize_filename("a b c") == "a_b_c"

    def test_removes_special_characters(self):
        """Test that special characters are removed."""
        assert YAMLStore._sanitize_filename("Thorin!@#$%") == "thorin"
        assert YAMLStore._sanitize_filename("Test<>:\"") == "test"
        assert YAMLStore._sanitize_filename("Name|?*") == "name"

    def test_allows_hyphens_underscores(self):
        """Test that hyphens and underscores are preserved."""
        assert YAMLStore._sanitize_filename("my-character") == "my-character"
        assert YAMLStore._sanitize_filename("my_character") == "my_character"
        assert YAMLStore._sanitize_filename("my-char_name") == "my-char_name"

    def test_path_traversal_prevention(self):
        """Test that path traversal attacks are prevented."""
        # Forward slash - converted to underscore, then dots stripped
        result = YAMLStore._sanitize_filename("../../../etc/passwd")
        assert "/" not in result
        assert ".." not in result
        # The actual result is safe - no path components can escape

        # Backslash - converted to underscore
        result = YAMLStore._sanitize_filename("..\\..\\windows\\system32")
        assert "\\" not in result
        assert ".." not in result

        # Mixed - slashes become underscores
        assert YAMLStore._sanitize_filename("foo/bar\\baz") == "foo_bar_baz"

        # Ensure result stays within storage directory
        for malicious in ["../secret", "..\\secret", "/etc/passwd", "C:\\Windows"]:
            result = YAMLStore._sanitize_filename(malicious)
            assert "/" not in result
            assert "\\" not in result
            assert ".." not in result

    def test_empty_name_returns_unnamed(self):
        """Test that empty names return 'unnamed'."""
        assert YAMLStore._sanitize_filename("") == "unnamed"
        assert YAMLStore._sanitize_filename("   ") == "unnamed"
        assert YAMLStore._sanitize_filename("!!!") == "unnamed"

    def test_none_returns_unnamed(self):
        """Test that None returns 'unnamed'."""
        assert YAMLStore._sanitize_filename(None) == "unnamed"

    def test_max_length_enforced(self):
        """Test that maximum filename length is enforced."""
        long_name = "a" * 300
        result = YAMLStore._sanitize_filename(long_name)
        assert len(result) <= YAMLStore.MAX_FILENAME_LENGTH

    def test_leading_trailing_chars_stripped(self):
        """Test that leading/trailing underscores and hyphens are stripped."""
        assert YAMLStore._sanitize_filename("_test_") == "test"
        assert YAMLStore._sanitize_filename("-test-") == "test"
        assert YAMLStore._sanitize_filename("__test__") == "test"

    def test_multiple_underscores_collapsed(self):
        """Test that multiple underscores are collapsed."""
        assert YAMLStore._sanitize_filename("a   b") == "a_b"
        assert YAMLStore._sanitize_filename("a___b") == "a_b"

    def test_unicode_handling(self):
        """Test that unicode characters are handled safely.

        Note: Python's isalnum() considers unicode letters as alphanumeric,
        which is acceptable for filenames on modern filesystems. The key
        security concern is path traversal, not unicode support.
        """
        # Unicode letters are preserved (isalnum returns True for them)
        # This is safe - they can't enable path traversal
        result = YAMLStore._sanitize_filename("Thorïn")
        assert "/" not in result
        assert "\\" not in result

        # CJK characters are also alphanumeric to Python
        result = YAMLStore._sanitize_filename("名前")
        assert "/" not in result
        assert "\\" not in result
        # Either preserved or becomes 'unnamed' depending on implementation

        # Accented characters preserved
        result = YAMLStore._sanitize_filename("Émile")
        assert "/" not in result
        assert "\\" not in result

    def test_numbers_preserved(self):
        """Test that numbers are preserved."""
        assert YAMLStore._sanitize_filename("Character123") == "character123"
        assert YAMLStore._sanitize_filename("42") == "42"

    def test_realistic_names(self):
        """Test realistic D&D character names."""
        assert YAMLStore._sanitize_filename("Gandalf the Grey") == "gandalf_the_grey"
        assert YAMLStore._sanitize_filename("Drizzt Do'Urden") == "drizzt_dourden"
        assert YAMLStore._sanitize_filename("Bob (Level 5)") == "bob_level_5"
        assert YAMLStore._sanitize_filename("Sir Reginald III") == "sir_reginald_iii"

    def test_case_insensitivity(self):
        """Test that names are lowercased."""
        assert YAMLStore._sanitize_filename("THORIN") == "thorin"
        assert YAMLStore._sanitize_filename("ThOrIn") == "thorin"

    def test_dot_files_safe(self):
        """Test that dot filenames are safe."""
        # Dots are removed, so hidden files can't be created
        assert YAMLStore._sanitize_filename(".hidden") == "hidden"
        assert YAMLStore._sanitize_filename("..") == "unnamed"
        assert YAMLStore._sanitize_filename("...") == "unnamed"
