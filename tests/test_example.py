"""Example test file demonstrating test patterns for dacli.

This test file serves as a template for creating new tests.
"""

import pytest


class TestExample:
    """Example test class."""

    def test_basic_assertion(self):
        """Test that basic assertions work."""
        assert 1 + 1 == 2

    def test_string_operations(self):
        """Test string operations."""
        text = "dacli"
        assert text.upper() == "DACLI"
        assert len(text) == 5

    def test_list_operations(self):
        """Test list operations."""
        items = [1, 2, 3]
        assert len(items) == 3
        assert sum(items) == 6


class TestPathNotation:
    """Test path notation conventions used in dacli."""

    def test_empty_path_for_root(self):
        """Level 0 (document title) has empty path."""
        root_path = ""
        assert root_path == ""

    def test_slug_path_for_level_1(self):
        """Level 1 sections use slug only."""
        chapter_path = "introduction"
        assert "." not in chapter_path

    def test_dot_notation_for_nested(self):
        """Level 2+ sections use parent.slug notation."""
        nested_path = "introduction.goals"
        parts = nested_path.split(".")
        assert len(parts) == 2
        assert parts[0] == "introduction"
        assert parts[1] == "goals"
