# GitHub Issues for dacli

The following bugs were discovered during comprehensive testing of the dacli-mcp server.

---

## Issue 1: Markdown and AsciiDoc documents have inconsistent root levels

### Title
Markdown documents have level 1 root while AsciiDoc has level 0

### Labels
`bug`, `parser`, `markdown`

### Description

When mixing Markdown and AsciiDoc documents in the same project, the root document level is inconsistent:
- AsciiDoc documents (`= Title`) have `level: 0`
- Markdown documents (`# Title`) have `level: 1`

This inconsistency makes it difficult to use `get_sections_at_level` consistently across mixed-format projects.

### Steps to Reproduce

1. Create test files:

**test.adoc:**
```asciidoc
= AsciiDoc Document

== Chapter
Content
```

**test.md:**
```markdown
# Markdown Document

## Chapter
Content
```

2. Start the MCP server and call `get_structure()`

3. Observe the levels:
```json
{
  "sections": [
    {"path": "test", "title": "AsciiDoc Document", "level": 0, ...},
    {"path": "test_md", "title": "Markdown Document", "level": 1, ...}
  ]
}
```

### Expected Behavior

Both document types should use the same level for their root document (preferably level 0 for consistency with AsciiDoc convention, since `=` in AsciiDoc and `#` in Markdown are semantically equivalent).

### Actual Behavior

AsciiDoc roots are level 0, Markdown roots are level 1.

### Impact

- `get_sections_at_level(level=1)` returns Markdown roots but AsciiDoc chapters
- Makes cross-format queries inconsistent
- Users cannot reliably get "all top-level documents" with a single call

### Suggested Fix

In the Markdown parser, adjust the level calculation so that `# Title` produces `level: 0` (matching AsciiDoc's `= Title`).

---

## Issue 2: insert_content "after" position missing blank line before next heading

### Title
insert_content with position="after" doesn't add blank line before following heading

### Labels
`bug`, `mcp-tools`, `low-priority`

### Description

When using `insert_content` with `position="after"`, if the content being inserted ends with a non-heading line and is followed by a heading in the document, no blank line is inserted between them. This violates AsciiDoc/Markdown conventions and may cause rendering issues.

### Steps to Reproduce

1. Create a test document:
```asciidoc
= Test

== Chapter One
Content

== Chapter Two
Content
```

2. Call:
```python
insert_content(
    path="test:chapter-one",
    position="after",
    content="Inserted paragraph content.\n"
)
```

3. Result:
```asciidoc
= Test

== Chapter One
Content

Inserted paragraph content.
== Chapter Two      <- No blank line before heading!
Content
```

### Expected Behavior

```asciidoc
Inserted paragraph content.

== Chapter Two      <- Blank line before heading
```

### Actual Behavior

No blank line is added between the inserted content and the following heading.

### Impact

- May cause rendering issues in some parsers
- Violates common AsciiDoc/Markdown conventions
- Users need to manually add trailing newlines

### Suggested Fix

In `insert_content`, after inserting content with `position="after"`, check if the next line is a heading and insert a blank line if needed.

---

## Issue 3: update_section with preserve_title=False can corrupt document hierarchy

### Title
update_section allows level changes that corrupt document hierarchy

### Labels
`bug`, `mcp-tools`, `high-priority`, `data-corruption`

### Description

When using `update_section` with `preserve_title=False` and providing content with a different heading level than the original section, the document hierarchy can be silently corrupted. This is a data-integrity issue.

### Steps to Reproduce

1. Create a test document:
```asciidoc
= Document

== Introduction

=== Goals
Original goals content

=== Non-Goals
Original non-goals content

== Other Chapter
```

2. Call:
```python
update_section(
    path="document:introduction.goals",
    content="== Changed To Level 1\n\nNew content",
    preserve_title=False
)
```

3. Result - the document structure is corrupted:
```asciidoc
= Document

== Introduction

== Changed To Level 1    <- Was level 3 (===), now level 2 (==)
New content

=== Non-Goals            <- Now appears as CHILD of "Changed To Level 1"!
Original non-goals content

== Other Chapter
```

4. The structure index now shows:
```
document
├── introduction
├── changed-to-level-1
│   └── non-goals        <- WRONG! Was sibling, now child
└── other-chapter
```

### Expected Behavior

One of the following:
1. **Validation:** Raise an error if the new content has a different heading level
2. **Auto-adjustment:** Automatically adjust the heading level to match the original
3. **Warning:** Return a warning in the response about hierarchy changes

### Actual Behavior

The level change is silently applied, corrupting the document hierarchy.

### Impact

- **Data corruption:** Document structure is silently broken
- **Lost context:** Sibling sections become children
- **Difficult to detect:** No error or warning is raised

### Suggested Fix

Option A (Recommended): Validate heading level in new content and reject if different:
```python
if not preserve_title:
    new_level = extract_heading_level(content)
    if new_level != section.level:
        return {"success": False, "error": "Content heading level mismatch"}
```

Option B: Auto-adjust the heading level:
```python
if not preserve_title:
    content = adjust_heading_level(content, section.level)
```

---

## Issue 4: Markdown headings with inline HTML comments are not recognized

### Title
Markdown parser fails to recognize headings containing inline HTML comments

### Labels
`bug`, `parser`, `markdown`

### Description

When a Markdown heading contains an inline HTML comment, the parser fails to recognize it as a heading. The heading content is instead merged into the previous section.

### Steps to Reproduce

1. Create a test Markdown file:
```markdown
# Document

## Overview
Content here.

## Details
More content.

## Important <!-- TODO: review this section -->
This section has an inline comment in its heading.
```

2. Call `get_structure()` or `get_section(path="document")`

3. Observe that only "Overview" and "Details" are recognized as children:
```json
{
  "path": "document",
  "children": [
    {"path": "document:overview", "title": "Overview"},
    {"path": "document:details", "title": "Details"}
  ]
}
```

4. The "Important" section is completely missing; its content is merged into "Details"

### Expected Behavior

The heading should be recognized. The title could either:
- Include the comment: `"Important <!-- TODO: review this section -->"`
- Strip the comment: `"Important"`

### Actual Behavior

The heading is not recognized at all. Content is merged into the previous section.

### Impact

- **Lost structure:** Sections are not indexed
- **Common pattern:** Inline HTML comments are frequently used in documentation for TODOs, notes, etc.
- **Silent failure:** No error or warning is raised

### Suggested Fix

In the Markdown parser's heading regex or detection logic, handle inline HTML comments:

```python
# Current regex might be: r'^(#{1,6})\s+(.+)$'
# Should handle: r'^(#{1,6})\s+(.+?)(?:\s*<!--.*-->)?$'
```

Or strip HTML comments before parsing:
```python
line = re.sub(r'<!--.*?-->', '', line)
```

---

## Summary Table

| Issue | Severity | Component | Status |
|-------|----------|-----------|--------|
| #1 Markdown level inconsistency | Medium | Parser | New |
| #2 Missing blank line in insert | Low | MCP Tools | New |
| #3 Level change hierarchy corruption | High | MCP Tools | New |
| #4 HTML comments in Markdown headings | Medium | Parser | New |
