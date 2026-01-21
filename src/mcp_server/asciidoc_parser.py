"""AsciiDoc Parser for MCP Documentation Server.

This module provides the AsciidocParser class for parsing AsciiDoc documents.
It extracts sections, elements, cross-references, and handles includes.

Current implementation focuses on section extraction (AC-ADOC-01).
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from mcp_server.models import (
    CrossReference,
    Document,
    Section,
    SourceLocation,
)

# Regex patterns from specification
SECTION_PATTERN = re.compile(r"^(={1,6})\s+(.+?)(?:\s+=*)?$")
ATTRIBUTE_PATTERN = re.compile(r"^:([a-zA-Z0-9_-]+):\s*(.*)$")


def _title_to_slug(title: str) -> str:
    """Convert a section title to a URL-friendly slug.

    Args:
        title: The section title

    Returns:
        A lowercase slug with spaces replaced by dashes
    """
    # Remove special characters, convert to lowercase, replace spaces with dashes
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


@dataclass
class IncludeInfo:
    """Information about a resolved include directive.

    Attributes:
        source_location: Where the include directive was found
        target_path: The resolved path to the included file
        options: Include options (leveloffset, lines, etc.)
    """

    source_location: SourceLocation
    target_path: Path
    options: dict[str, str] = field(default_factory=dict)


@dataclass
class AsciidocDocument(Document):
    """A parsed AsciiDoc document.

    Extends Document with AsciiDoc-specific fields.

    Attributes:
        attributes: Document attributes (:attr: value)
        cross_references: List of cross-references found
        includes: List of resolved includes
    """

    attributes: dict[str, str] = field(default_factory=dict)
    cross_references: list[CrossReference] = field(default_factory=list)
    includes: list[IncludeInfo] = field(default_factory=list)


class AsciidocParser:
    """Parser for AsciiDoc documents.

    Parses AsciiDoc files and extracts structure, elements, and references.
    Currently implements section extraction (AC-ADOC-01).

    Attributes:
        base_path: Base path for resolving relative file paths
        max_include_depth: Maximum depth for nested includes (default: 20)
    """

    def __init__(self, base_path: Path, max_include_depth: int = 20):
        """Initialize the parser.

        Args:
            base_path: Base path for resolving relative file paths
            max_include_depth: Maximum depth for nested includes
        """
        self.base_path = base_path
        self.max_include_depth = max_include_depth

    def parse_file(self, file_path: Path) -> AsciidocDocument:
        """Parse an AsciiDoc file.

        Args:
            file_path: Path to the AsciiDoc file

        Returns:
            Parsed AsciidocDocument

        Raises:
            FileNotFoundError: If the file does not exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Parse attributes first (they can be used in sections)
        attributes = self._parse_attributes(lines)

        # Parse sections with attribute substitution
        sections, title = self._parse_sections(lines, file_path, attributes)

        return AsciidocDocument(
            file_path=file_path,
            title=title,
            sections=sections,
            elements=[],
            attributes=attributes,
            cross_references=[],
            includes=[],
        )

    def _parse_attributes(self, lines: list[str]) -> dict[str, str]:
        """Parse document attributes from lines.

        Attributes are defined as :name: value at the start of the document.

        Args:
            lines: Document lines

        Returns:
            Dictionary of attribute name to value
        """
        attributes: dict[str, str] = {}

        for line in lines:
            match = ATTRIBUTE_PATTERN.match(line)
            if match:
                name = match.group(1)
                value = match.group(2).strip()
                attributes[name] = value
            elif line.strip() and not line.startswith(":"):
                # Stop parsing attributes when we hit non-attribute content
                # (but continue through empty lines)
                if SECTION_PATTERN.match(line):
                    break

        return attributes

    def _substitute_attributes(self, text: str, attributes: dict[str, str]) -> str:
        """Substitute attribute references in text.

        Replaces {attribute} with the attribute value.

        Args:
            text: Text with potential attribute references
            attributes: Dictionary of attribute name to value

        Returns:
            Text with attribute references substituted
        """
        result = text
        for name, value in attributes.items():
            result = result.replace(f"{{{name}}}", value)
        return result

    def _parse_sections(
        self,
        lines: list[str],
        file_path: Path,
        attributes: dict[str, str] | None = None,
    ) -> tuple[list[Section], str]:
        """Parse sections from document lines.

        Args:
            lines: Document lines
            file_path: Path to the source file
            attributes: Document attributes for substitution

        Returns:
            Tuple of (list of top-level sections, document title)
        """
        if not lines:
            return [], ""

        if attributes is None:
            attributes = {}

        sections: list[Section] = []
        section_stack: list[Section] = []
        document_title = ""

        for line_num, line in enumerate(lines, start=1):
            match = SECTION_PATTERN.match(line)
            if match:
                equals = match.group(1)
                raw_title = match.group(2).strip()
                # Substitute attribute references in title
                title = self._substitute_attributes(raw_title, attributes)
                level = len(equals) - 1  # = is level 0, == is level 1, etc.

                # Create section
                section = Section(
                    title=title,
                    level=level,
                    path="",  # Will be set below
                    source_location=SourceLocation(file=file_path, line=line_num),
                    children=[],
                    anchor=None,
                )

                # Document title (level 0)
                if level == 0:
                    document_title = title
                    section.path = _title_to_slug(title)
                    sections.append(section)
                    section_stack = [section]
                else:
                    # Find parent section
                    while section_stack and section_stack[-1].level >= level:
                        section_stack.pop()

                    if section_stack:
                        parent = section_stack[-1]
                        section.path = f"{parent.path}.{_title_to_slug(title)}"
                        parent.children.append(section)
                    else:
                        # No parent found, add as top-level
                        section.path = _title_to_slug(title)
                        sections.append(section)

                    section_stack.append(section)

        return sections, document_title
