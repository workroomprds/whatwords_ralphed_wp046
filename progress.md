# Progress Log

A narrative history of whenwords implementations and milestones.

---

## Python Implementation - January 27, 2026

Successfully implemented the complete whenwords library in Python following SPEC.md v0.1.0.

**What was built:**
- `whenwords.py` (350 lines) - Core library implementing all five functions
- `test_whenwords.py` (639 lines) - Complete test suite with all 123 test cases from tests.yaml
- `usage.md` (233 lines) - Comprehensive documentation with examples

**Test results:**
All 123 tests pass, covering:
- 36 timeago tests (past/future times, edge cases)
- 22 duration tests (formatting options, units, compact mode)
- 34 parse_duration tests (multiple formats, error handling)
- 21 human_date tests (contextual dates, weekday handling)
- 10 date_range tests (range formatting, auto-correction)

**Implementation highlights:**
- Pure functions with no side effects or system clock dependencies
- Accepts Unix timestamps, ISO 8601 strings, and Python datetime objects
- Proper error handling with descriptive ValueError messages
- Smart pluralization and formatting
- UTC-based calendar operations with clear timezone handling
- Flexible duration parsing supporting multiple input formats (compact, verbose, colon notation)

**Challenges resolved:**
1. Initial human_date implementation incorrectly included 7-day boundaries in "Last/This [Weekday]" format. Fixed to use 2-6 day ranges per spec.
2. parse_duration regex didn't catch negative values before parsing. Added early minus-sign detection.
3. Date formatting required platform-specific strftime flags (`%-d` vs `%#d`) for leading zero removal.

**Development process:**
The implementation followed a test-driven approach:
1. Read and understood SPEC.md requirements
2. Parsed tests.yaml and generated Python test file
3. Implemented core functions iteratively
4. Ran tests, debugged failures, refined implementation
5. Achieved 100% test pass rate

Total development time was efficient thanks to the comprehensive specification and clear test cases. The YAML-based test format made it easy to verify behavior across all edge cases.

**Files committed:**
- Commit `24453e4`: Added Python implementation (1,222 lines)
- Location: `~/whenwords/bin/`
- All dependencies: Python 3.x standard library only (no external packages required for library; pytest only for testing)

The Python implementation demonstrates the effectiveness of the "library without code" approach—a complete, production-ready library generated entirely from specifications and tests.

---

## Daylight Saving Time Support - Planning Phase - January 27, 2026

**Motivation**: The current implementation uses UTC for all calendar operations, which sidesteps DST but limits real-world usage. Real applications need to display dates and times in user timezones, which requires handling DST transitions.

**User scenario**: In the UK, clocks spring forward on 2026-03-29 (01:00 becomes 02:00) and fall back on 2026-10-25 (02:00 becomes 01:00). The time between 2026-03-29 00:59 and 01:01 is 1 hour 2 minutes (not 2 minutes), because 01:00 doesn't exist. Similarly, 2 minutes after 2026-10-25 01:59 (first occurrence) is 02:01, but 2 minutes after 01:59 (second occurrence) is 01:01.

**Planning approach**: Created `implementation_plan.md` with phased approach to add timezone support without breaking existing functionality. Documented all design decisions in `decisions.md` before starting implementation.

**Key decisions made**:

1. **Scope limitation**: Only add timezone support to `human_date()` and `date_range()`. Functions working with elapsed time (`timeago`, `duration`, `parse_duration`) remain DST-agnostic because Unix timestamp differences already account for DST.

2. **API design**: Add optional `timezone` parameter (defaults to UTC for backwards compatibility). Use IANA timezone names via Python's `zoneinfo` module.

3. **DST edge cases**:
   - Non-existent times (spring forward): Let Python raise errors, document clearly
   - Ambiguous times (fall back): Support Python's `fold` parameter
   - Duration calculations: Remain based on elapsed time, not wall-clock time

4. **Test approach**: Extend `tests.yaml` with timezone-aware test cases while keeping all 123 existing tests passing.

**Implementation plan phases**:
1. Phase 1: Design and documentation (update SPEC.md, design test cases)
2. Phase 2: Test definition (extend tests.yaml with DST cases)
3. Phase 3: Implementation (add timezone parameter to calendar functions)
4. Phase 4: Documentation (update usage.md with timezone examples)
5. Phase 5: Validation and cleanup

**Status**: Planning complete. Ready to begin Phase 1 (documentation updates).

**Files created**:
- `implementation_plan.md` - Detailed phased implementation guide
- Updated `decisions.md` - DST design decisions
- Updated `progress.md` - This entry

**Next steps**: Update SPEC.md to include timezone parameter specification and DST behavior documentation.

---

## Basic Timezone Support for human_date() - January 27, 2026

Successfully added optional timezone parameter to `human_date()` function, enabling dates to be displayed in different timezones while maintaining full backwards compatibility.

**What was implemented:**
- Added `timezone` parameter to `human_date()` signature (optional, defaults to UTC)
- Integrated Python's `zoneinfo` module for IANA timezone support
- Error handling for invalid timezone names (raises ValueError)
- Imported timezone module as `dt_timezone` to avoid name collision with parameter
- 4 new test cases demonstrating timezone functionality

**Test results:**
All 127 tests pass (123 original + 4 new):
- UTC timezone explicit test (baseline)
- America/New_York showing different day than UTC for same timestamp
- Europe/London (BST) test verifying UTC+1 offset
- Backwards compatibility test confirming None defaults to UTC

**Key insight from testing:**
Initial test expectation for Europe/London was incorrect. The timestamp 2024-07-25 23:30 UTC becomes 2024-07-26 00:30 BST (British Summer Time is UTC+1), putting it on the same day as reference 2024-07-26 00:00 UTC (01:00 BST). This demonstrates how timezone-aware date display differs from UTC.

**Implementation approach:**
Followed test-first workflow:
1. Added 4 timezone test cases to tests.yaml
2. Generated corresponding test functions in test_whenwords.py
3. Ran tests and confirmed 3 failures (timezone parameter didn't exist)
4. Modified whenwords.py to add timezone parameter and ZoneInfo logic
5. Fixed one test expectation error (Europe/London)
6. Verified all 127 tests pass

**Changes committed:**
- Commit `0791e98`: "Add timezone support to human_date() function"
- Modified: bin/whenwords.py, bin/test_whenwords.py, tests.yaml
- 62 insertions, 7 deletions

**Remaining work:**
- Phase 2: Add DST transition test cases (spring forward, fall back)
- Phase 3: Add timezone support to date_range() function
- Phase 4: Update usage.md with timezone examples and DST guidance
- Update SPEC.md with timezone parameter documentation

---

## Timezone Support for date_range() - January 27, 2026

Completed timezone support for `date_range()` function, finishing Phase 3 of the timezone implementation plan. Both calendar functions now support optional timezone parameters with consistent behavior.

**What was implemented:**
- Added `timezone` parameter to `date_range()` signature (optional, defaults to UTC)
- Used same ZoneInfo integration pattern as `human_date()`
- Error handling for invalid timezone names
- Full backwards compatibility maintained
- 4 new test cases proving timezone functionality

**Test results:**
All 131 tests pass (127 previous + 4 new):
- UTC timezone test showing two-day range (baseline)
- America/New_York (EDT = UTC-4) collapsing same two timestamps to single day
- Europe/London (BST = UTC+1) collapsing to single day on different date
- Backwards compatibility test confirming None defaults to UTC

**Key demonstration:**
Timestamps 1721950200 (2024-07-25 23:30 UTC) to 1721955600 (2024-07-26 01:00 UTC):
- In UTC: "July 25–26, 2024" (spans two days)
- In America/New_York: "July 25, 2024" (19:30–21:00, same day)
- In Europe/London: "July 26, 2024" (00:30–02:00 BST, same day)

This clearly shows how timezone context affects date range display—the same time interval can represent different calendar days depending on the observer's timezone.

**Implementation approach:**
Followed strict TDD workflow as specified:
1. Added 4 timezone test cases to tests.yaml
2. Manually added corresponding test functions to test_whenwords.py
3. Ran tests and confirmed failures (timezone parameter didn't exist)
4. Modified `date_range()` in whenwords.py following `human_date()` pattern
5. Verified all 131 tests pass

**Changes committed:**
- Commit `b8f7e0e`: "Add timezone support to date_range() function"
- Modified: bin/whenwords.py, bin/test_whenwords.py, tests.yaml
- 59 insertions, 4 deletions

**Phase 3 status:** ✅ COMPLETE
Both `human_date()` and `date_range()` now support timezone parameters.

**Remaining work:**
- Phase 1: Update SPEC.md with timezone parameter documentation
- Phase 2: Add comprehensive DST transition test cases (spring forward, fall back)
- Phase 4: Update usage.md with timezone examples and DST guidance
- Phase 5: Validation and cleanup
