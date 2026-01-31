# dacli-mcp Test Report

**Date:** 2026-01-31
**Version Tested:** 0.4.20
**Tester:** Automated test script + manual edge case testing

## Executive Summary

The dacli-mcp server was tested for functionality, edge cases, and error handling. **4 bugs** were identified, ranging from cosmetic to potentially document-corrupting issues.

## Test Environment

- **Platform:** Linux
- **Python:** 3.12
- **Test Documents:** Custom AsciiDoc and Markdown files with various edge cases (special characters, unicode, empty sections, deeply nested structures, HTML comments)

## Test Categories

### 1. Basic Functionality Tests

All 9 MCP tools were tested for basic functionality:

| Tool | Status | Notes |
|------|--------|-------|
| `get_structure` | PASS | max_depth validation works correctly |
| `get_section` | PASS | Path resolution, error handling OK |
| `get_sections_at_level` | PASS | Level validation works (1-based) |
| `search` | PASS | Full-text search, query validation OK |
| `get_elements` | PASS | Type filtering, recursive flag work |
| `update_section` | PASS | Basic updates work, hash locking works |
| `insert_content` | PASS | All positions work (before/after/append) |
| `get_metadata` | PASS | Project and section metadata OK |
| `validate_structure` | PASS | Detects broken includes |

### 2. Input Validation Tests

All negative parameter validation works correctly:

- `get_structure(max_depth=-1)` raises ValueError
- `get_sections_at_level(level=0)` raises ValueError
- `get_sections_at_level(level=-1)` raises ValueError
- `search(query="")` raises ValueError
- `search(query="   ")` raises ValueError
- `search(max_results=-1)` raises ValueError
- `get_elements(content_limit=-1)` raises ValueError

### 3. Edge Case Tests

| Test Case | Status | Notes |
|-----------|--------|-------|
| Document with only title | PASS | Correctly returns empty content |
| Document with emoji in path/title | PASS | Unicode handled correctly |
| Empty sections | PASS | Returns minimal content |
| Deeply nested paths (5 levels) | PASS | All levels accessible |
| Unicode search (Umlauts) | PASS | Search finds unicode content |
| Special characters in paths | PASS | Slugification works |
| Non-existent paths | PASS | Returns PATH_NOT_FOUND with suggestions |
| Leading slash in paths | PASS | Correctly normalized |

### 4. Error Handling Tests

| Test Case | Status | Notes |
|-----------|--------|-------|
| Non-existent section update | PASS | Returns error, not exception |
| Invalid insert position | PASS | Returns descriptive error |
| Wrong expected_hash | PASS | Hash conflict properly detected |
| Broken include detection | PASS | validate_structure reports error |

## Bugs Found

### Bug 1: Markdown Document Level Inconsistency (Severity: Medium)

**Description:** Markdown documents use level 1 for their root document, while AsciiDoc documents use level 0. This creates an inconsistency when working with mixed documentation projects.

**Steps to Reproduce:**
1. Create an AsciiDoc file with `= Title`
2. Create a Markdown file with `# Title`
3. Call `get_structure()`
4. Observe: AsciiDoc root has `level: 0`, Markdown root has `level: 1`

**Expected:** Both formats should use the same level for root documents.

**Impact:** Makes it difficult to consistently query sections across mixed format projects using `get_sections_at_level`.

---

### Bug 2: Missing Blank Line After insert_content (Severity: Low)

**Description:** When using `insert_content` with `position="after"`, the inserted content may not have a blank line before the next heading, which can cause rendering issues in AsciiDoc/Markdown.

**Steps to Reproduce:**
1. Insert content after a section that is followed by another heading
2. The inserted content ends with a paragraph (not a heading)
3. Observe: No blank line between inserted content and next heading

**Expected:** A blank line should be inserted to maintain proper document structure.

**Impact:** Cosmetic/rendering issue, may cause parsing problems in some renderers.

---

### Bug 3: update_section with Level Change Can Corrupt Hierarchy (Severity: High)

**Description:** When using `update_section` with `preserve_title=False` and providing content with a different heading level, the document hierarchy can be corrupted.

**Steps to Reproduce:**
1. Get a level 2 section (e.g., `=== Goals`)
2. Update it with `preserve_title=False` and level 1 content (`== New Title`)
3. The section becomes level 1, potentially making sibling sections appear as children

**Example:**
```
Before:
== Introduction
=== Goals          <- Level 2
=== Non-Goals      <- Level 2 (sibling)

After update_section("introduction.goals", "== New Title\n...", preserve_title=False):
== Introduction
== New Title       <- Now Level 1!
=== Non-Goals      <- Appears as child of "New Title"
```

**Expected:** Either:
- Warn/prevent level changes
- Automatically adjust heading level to match original
- Document this behavior clearly

**Impact:** Can silently corrupt document structure.

---

### Bug 4: Markdown Headings with Inline HTML Comments Not Parsed (Severity: Medium)

**Description:** Markdown headings that contain inline HTML comments are not recognized as headings by the parser.

**Steps to Reproduce:**
1. Create a Markdown file with: `## Heading <!-- comment -->`
2. Call `get_structure()`
3. The heading is not recognized; content is merged into previous section

**Expected:** The heading should be recognized, with or without stripping the comment.

**Impact:** Loss of document structure in Markdown files with inline HTML comments (common in documentation with notes).

---

## Test Coverage Summary

| Category | Tests Run | Passed | Failed |
|----------|-----------|--------|--------|
| Basic Functionality | 50+ | 50+ | 0 |
| Edge Cases | 15 | 15 | 0 |
| Bug Discovery | 10+ | N/A | 4 bugs found |

## Recommendations

1. **High Priority:** Fix Bug 3 (level change corruption) - add validation or level adjustment
2. **Medium Priority:** Fix Bug 1 (Markdown level consistency) and Bug 4 (HTML comments in headings)
3. **Low Priority:** Fix Bug 2 (blank line handling) for cleaner output

## Conclusion

The dacli-mcp server is generally robust and handles most common use cases well. The validation for negative parameters is comprehensive. However, the identified bugs, particularly Bug 3, could cause data corruption in production use cases and should be addressed before wider deployment.
