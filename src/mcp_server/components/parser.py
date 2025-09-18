import re
from pathlib import Path
from typing import List
from mcp_server.models.document import Document, Section

# Regex to find AsciiDoc section titles (e.g., == Title, === Sub-title)
SECTION_TITLE_REGEX = re.compile(r'^(={2,5})\s+(.*)')

def parse_document(file_path: str) -> Document:
    """
    Parses a single AsciiDoc file and builds a hierarchical structure of its sections.

    NOTE: This is a basic implementation and does not handle 'include::[]' directives yet.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Document not found at: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    document = Document(filepath=str(path))
    # A stack to keep track of the current parent section for nesting
    section_stack: List[Section] = []

    for line in lines:
        match = SECTION_TITLE_REGEX.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            
            new_section = Section(title=title, level=level)

            # Adjust the stack to find the correct parent
            while section_stack and section_stack[-1].level >= level:
                section_stack.pop()

            if not section_stack:
                # This is a top-level section
                document.sections.append(new_section)
            else:
                # This is a subsection of the last section on the stack
                section_stack[-1].subsections.append(new_section)
            
            section_stack.append(new_section)
        elif section_stack:
            # Add content to the current section on the top of the stack
            section_stack[-1].content.append(line)

    return document
