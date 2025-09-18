import re
from pathlib import Path
from typing import List
from mcp_server.models.document import Document, Section

# Regex to find AsciiDoc section titles (e.g., == Title, === Sub-title)
SECTION_TITLE_REGEX = re.compile(r'^(={2,5})\s+(.*)')
INCLUDE_REGEX = re.compile(r'^include::([^\[]+)\[\]')

def parse_document(file_path: str) -> Document:
    """
    Parses a single AsciiDoc file and builds a hierarchical structure of its sections.
    This version handles `include::[]` directives by pre-processing them.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Document not found at: {file_path}")

    # Pre-process file to handle includes
    all_lines = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            include_match = INCLUDE_REGEX.match(line)
            if include_match:
                include_filename = include_match.group(1).strip()
                include_path = path.parent / include_filename
                if include_path.is_file():
                    with open(include_path, 'r', encoding='utf-8') as include_f:
                        all_lines.extend(include_f.readlines())
                else:
                    # If include file not found, keep the include directive as content
                    all_lines.append(line)
            else:
                all_lines.append(line)

    document = Document(filepath=str(path))
    section_stack: List[Section] = []

    for line in all_lines:
        match = SECTION_TITLE_REGEX.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            
            new_section = Section(title=title, level=level)

            while section_stack and section_stack[-1].level >= level:
                section_stack.pop()

            if not section_stack:
                document.sections.append(new_section)
            else:
                section_stack[-1].subsections.append(new_section)
            
            section_stack.append(new_section)
        elif section_stack:
            section_stack[-1].content.append(line)

    return document
