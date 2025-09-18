import pytest
from pathlib import Path
from mcp_server.components.parser import parse_document
from mcp_server.models.document import Document, Section

# Define the path to the fixtures directory
FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"

def test_parse_simple_document():
    """Tests parsing of a simple document with nested sections."""
    doc_path = str(FIXTURE_DIR / "simple.adoc")
    document = parse_document(doc_path)

    assert isinstance(document, Document)
    assert document.filepath == doc_path
    assert len(document.sections) == 2

    # Check first top-level section
    assert document.sections[0].title == "Level 1 Title"
    assert document.sections[0].level == 2
    assert "Some content in level 1.\n" in document.sections[0].content
    assert len(document.sections[0].subsections) == 1

    # Check subsection
    subsection = document.sections[0].subsections[0]
    assert subsection.title == "Level 2 Title"
    assert subsection.level == 3
    assert "Some content in level 2.\n" in subsection.content
    assert len(subsection.subsections) == 0

    # Check second top-level section
    assert document.sections[1].title == "Another Level 1 Title"
    assert document.sections[1].level == 2
    assert len(document.sections[1].content) == 0 # Should be empty
    assert len(document.sections[1].subsections) == 0

def test_parse_empty_document():
    """Tests that parsing an empty file results in an empty Document."""
    doc_path = str(FIXTURE_DIR / "empty.adoc")
    document = parse_document(doc_path)

    assert isinstance(document, Document)
    assert len(document.sections) == 0

def test_parse_document_with_no_sections():
    """Tests that a file with content but no section headers is parsed correctly."""
    doc_path = str(FIXTURE_DIR / "no_sections.adoc")
    document = parse_document(doc_path)

    # The current parser implementation only adds content to a section after a title is found.
    # Therefore, a file with no section titles will result in a document with no sections.
    assert isinstance(document, Document)
    assert len(document.sections) == 0

def test_parse_nonexistent_document():
    """Tests that a FileNotFoundError is raised for a non-existent file."""
    with pytest.raises(FileNotFoundError):
        parse_document("nonexistent_file.adoc")

def test_parser_handles_simple_include():
    """Tests that the parser correctly handles a simple 'include::[]' directive."""
    doc_path = str(FIXTURE_DIR / "include_main.adoc")
    document = parse_document(doc_path)

    assert len(document.sections) == 1
    main_section = document.sections[0]
    assert main_section.title == "Main Document Section"
    
    # This is the part that will fail
    assert len(main_section.subsections) == 1
    included_section = main_section.subsections[0]
    assert included_section.title == "Included Section"
    assert "This content comes from the partial file.\n" in included_section.content
