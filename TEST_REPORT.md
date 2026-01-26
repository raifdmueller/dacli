# dacli Test Report

**Version:** 0.3.2
**Test Date:** 2026-01-26
**Tester:** Claude (Automated Testing)

---

## Executive Summary

dacli is a well-designed CLI and MCP server tool for navigating and querying documentation projects. The tool is functional and stable for its core use cases. Testing revealed mostly minor issues and some areas for improvement.

**Overall Rating:** 4/5 - Good, with minor issues

| Category | Rating | Notes |
|----------|--------|-------|
| Installation | 5/5 | Flawless with uv |
| Core Functionality | 4.5/5 | All features work as documented |
| Error Handling | 4/5 | Good error messages, some edge cases could be improved |
| Documentation | 4/5 | Comprehensive but some CLI quirks undocumented |
| Performance | 5/5 | Fast indexing and queries |

---

## Test Environment

- **Platform:** Linux 4.4.0
- **Python:** 3.12.3
- **Package Manager:** uv
- **Test Documents:** AsciiDoc and Markdown files

---

## Functional Tests

### Installation & Setup

| Test | Result | Notes |
|------|--------|-------|
| `uv sync` | PASS | 88 packages installed correctly |
| `dacli --version` | PASS | Returns "dacli, version 0.3.2" |
| `dacli --help` | PASS | Comprehensive help output |
| `dacli-mcp --help` | PASS | MCP server options documented |

### CLI Commands

#### Structure Command
| Test | Result | Notes |
|------|--------|-------|
| `dacli structure` | PASS | Returns hierarchical YAML |
| `dacli --format json structure` | PASS | JSON format works |
| `dacli --format yaml structure` | PASS | YAML format works |
| `dacli --pretty structure` | PASS | Pretty output for JSON |

#### Section Command
| Test | Result | Notes |
|------|--------|-------|
| Read existing section | PASS | Content, location, format returned |
| Read nested section | PASS | Dot-notation paths work |
| Read non-existent section | PASS | Returns PATH_NOT_FOUND error with exit code 3 |
| Read with special characters (Umlauts) | PASS | ü, ä, ö in paths work correctly |

#### Search Command
| Test | Result | Notes |
|------|--------|-------|
| Basic search | PASS | Returns scored results |
| Search with special characters | PASS | "München" finds correct section |
| Search with `--scope` | PASS | Scope filtering works |
| Search with `--max-results` | PASS | Limits results correctly |
| Empty search query | ISSUE | Returns all sections with score 1.0 (see Issues) |

#### Elements Command
| Test | Result | Notes |
|------|--------|-------|
| Get all elements | PASS | Returns code, table, image elements |
| Filter by type `--type code` | PASS | Only code blocks returned |
| Invalid type | ISSUE | Silently returns 0 results (see Issues) |

#### Sections-at-Level Command
| Test | Result | Notes |
|------|--------|-------|
| Level 1 | PASS | Returns all chapter-level sections |
| Level 99 (non-existent) | PASS | Returns empty list, no error |
| Level -1 | ISSUE | Parsed as option, confusing error (see Issues) |

#### Update Command
| Test | Result | Notes |
|------|--------|-------|
| Basic update | PASS | Content updated, hash returned |
| Preserve title | PASS | Original heading preserved |
| Optimistic locking success | PASS | Update succeeds with correct hash |
| Optimistic locking conflict | PASS | Fails with hash conflict error |

#### Insert Command
| Test | Result | Notes |
|------|--------|-------|
| Insert after | PASS | Content inserted correctly |
| Insert before | PASS | Content inserted correctly |
| Invalid position | PASS | Clear error message |

#### Validate Command
| Test | Result | Notes |
|------|--------|-------|
| Valid documents | PASS | Returns `valid: True` |
| Unclosed code block | PASS | Detected as warning |
| Orphaned files | PASS | Detected as warning |

#### Metadata Command
| Test | Result | Notes |
|------|--------|-------|
| Project metadata | PASS | Returns file count, word count, formats |
| Section metadata | PASS | Returns section details |

### MCP Server

| Test | Result | Notes |
|------|--------|-------|
| Server startup | PASS | FastMCP banner displayed, starts on stdio |
| All 10 tools registered | PASS | Verified in source code |

### Document Format Support

| Format | Parsing | Elements | Update | Notes |
|--------|---------|----------|--------|-------|
| AsciiDoc | PASS | PASS | PASS | Full support |
| Markdown | PASS | PASS | PASS | Full support |
| Mixed docs | PASS | PASS | PASS | Both formats in same root |

---

## Issues Found

### Issue 1: Empty Search Query Returns All Sections (Minor)

**Severity:** Low
**Command:** `dacli search ""`
**Behavior:** Returns all sections with score 1.0
**Expected:** Either return an error or return 0 results
**Impact:** Confusing behavior, wastes bandwidth for LLMs

### Issue 2: Invalid Element Type Silently Returns 0 Results (Minor)

**Severity:** Low
**Command:** `dacli elements --type invalid`
**Behavior:** Returns `count: 0` silently
**Expected:** Warning message about unknown type
**Impact:** User might think there are no elements when they misspelled the type

### Issue 3: Negative Level Parsed as Option (Minor)

**Severity:** Low
**Command:** `dacli sections-at-level -1`
**Behavior:** Error: "No such option: -1"
**Expected:** Either accept negative (return empty) or clear error about positive integers
**Workaround:** Use `--` before arguments: `dacli sections-at-level -- -1`
**Impact:** Confusing for edge case testing

### Issue 4: Global Options Must Come Before Subcommand (Documentation)

**Severity:** Low
**Example:**
- Works: `dacli --format json section "path"`
- Fails: `dacli section "path" --format json`
**Impact:** Undocumented CLI behavior, users might get confused

### Issue 5: Test Failures in Root Environment (Test Infrastructure)

**Severity:** Low (Test-only)
**Tests:** 3 file permission tests fail when running as root
**Reason:** Root bypasses file permissions
**Impact:** CI environments running as root will see these failures

---

## Strengths

1. **Clean Architecture:** Well-separated concerns, clear data models
2. **Robust Parser:** Handles AsciiDoc includes, circular detection, source mapping
3. **Good Error Messages:** PATH_NOT_FOUND includes suggestions
4. **Optimistic Locking:** Hash-based conflict detection for concurrent edits
5. **Multiple Output Formats:** JSON, YAML, text output with pretty-print option
6. **Validation:** Detects structural issues like unclosed blocks, orphaned files
7. **Unicode Support:** Full support for special characters in content and paths
8. **MCP Integration:** Clean FastMCP implementation with all tools

---

## Recommendations

### High Priority

1. **Input Validation for Search:** Reject or warn on empty search queries
2. **Element Type Validation:** Warn on unknown element types

### Medium Priority

1. **CLI Option Ordering:** Document that global options must precede subcommand
2. **Negative Number Handling:** Use `--` convention or validate positively

### Low Priority

1. **Test Environment Detection:** Skip permission tests when running as root
2. **Search Limit Option:** The `--limit` alias would be clearer than `--max-results`

---

## Test Statistics

| Metric | Value |
|--------|-------|
| Unit Tests Run | 456 |
| Unit Tests Passed | 453 |
| Unit Tests Failed | 3 (permission tests, root environment) |
| Manual CLI Tests | 35+ |
| Edge Cases Tested | 15+ |
| Critical Bugs Found | 0 |
| Minor Issues Found | 5 |

---

## Conclusion

dacli is a well-implemented tool that accomplishes its stated purpose effectively. The core functionality for documentation navigation, search, and manipulation works reliably. The issues found are minor and do not impact the primary use cases.

**Recommendation:** Ready for production use. The identified issues should be addressed in future releases but do not block current adoption.

---

*Report generated by automated testing session*
