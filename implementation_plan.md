# Daylight Saving Time Support - Implementation Plan

**Goal**: Add timezone support to whenwords calendar functions to handle DST transitions correctly while maintaining backwards compatibility.

**Date**: 2026-01-27

**Status**: IN PROGRESS
- ✅ Basic timezone support for `human_date()` completed (commit 0791e98)
- ✅ Basic timezone support for `date_range()` completed (commit b8f7e0e)
- ⏳ DST transition handling pending

---

## Overview

Currently, whenwords uses UTC for all calendar operations, which sidesteps DST entirely. This works but limits real-world usage. This plan adds timezone awareness to calendar functions while keeping duration functions DST-agnostic (as they work with elapsed time).

---

## Phase 1: Design and Documentation

**Status**: ✅ COMPLETE (design decisions documented, SPEC.md update pending)

**Goal**: Finalize design decisions and update SPEC.md without touching code or tests.

### Tasks:

1. ✅ **Document design decisions** → `decisions.md`
   - Which functions get timezone support (only `human_date` and `date_range`)
   - API design (optional `timezone` parameter)
   - Error handling approach for non-existent times
   - Ambiguous time handling using `fold` parameter
   - Duration calculation behavior (remains DST-agnostic)

2. ⏳ **Update SPEC.md** (PENDING)
   - Add timezone parameter to `human_date()` signature
   - Add timezone parameter to `date_range()` signature
   - Document timezone format (IANA names like "Europe/London")
   - Clarify DST behavior in "Timezone Handling" section
   - Add error conditions for invalid timezone names
   - Document non-existent and ambiguous time handling

3. ⏳ **Design test cases** → DST test cases pending
   - Basic timezone tests added (4 tests for human_date)
   - UK spring forward (2026-03-29): clocks jump 01:00 → 02:00 - PENDING
   - UK fall back (2026-10-25): 01:00-01:59 happens twice - PENDING
   - US spring forward (2026-03-08): different dates than UK - PENDING
   - US fall back (2026-11-01): different dates than UK - PENDING
   - Boundary cases: timestamps at exact transition moments - PENDING
   - Same timestamp, different timezones → different days - DONE

**Checkpoint**: Design decisions documented. Basic implementation complete. SPEC.md update and DST test design pending.

---

## Phase 2: Test Definition

**Status**: 🔄 PARTIALLY COMPLETE (basic timezone tests done, DST tests pending)

**Goal**: Add DST test cases to tests.yaml while keeping all existing tests passing.

### Tasks:

1. ✅ **Add timezone field to test schema**
   - Tests without `timezone` field default to UTC (backwards compatible)
   - Tests with `timezone: "Europe/London"` interpret timestamps in that zone
   - 4 basic timezone tests added to tests.yaml

2. ⏳ **Add DST test cases to tests.yaml** (PENDING)

   For `human_date`:
   - ✅ Same timestamp, different timezones → different day labels (done with America/New_York test)
   - ⏳ Timestamps during UK spring forward transition
   - ⏳ Timestamps during UK fall back transition
   - ⏳ Timestamps during US DST transitions (verify different dates work)
   - ⏳ Midnight in one timezone = different day in another

   For `date_range`:
   - ⏳ Ranges that span DST transitions
   - ⏳ Same timestamp pair, different timezones → different date strings
   - ⏳ Verify date boundaries respect timezone

3. ✅ **Validate test design**
   - ✅ Run existing tests to ensure backwards compatibility (all 123 pass)
   - ✅ Calculate expected outputs for basic timezone tests manually
   - ✅ Document test timestamps with comments showing local times

**Checkpoint**: Basic timezone tests added (4 tests). All 127 tests passing. DST-specific test cases pending.

---

## Phase 3: Implementation

**Status**: ✅ COMPLETE

**Goal**: Modify Python implementation to support timezone parameter.

### Tasks:

1. ✅ **Add dependency on `zoneinfo`**
   - Python 3.9+ standard library module
   - Document Python version requirement
   - Add import and error handling for invalid timezone names
   - Imported as `from zoneinfo import ZoneInfo`
   - Aliased timezone module as `dt_timezone` to avoid parameter name collision

2. ✅ **Modify `human_date()`**
   - ✅ Add optional `timezone` parameter (default: None)
   - ✅ When timezone=None, use UTC (current behavior, backwards compatible)
   - ✅ When timezone provided, convert timestamp using `ZoneInfo`
   - ✅ Update datetime creation: `datetime.fromtimestamp(ts, tz=ZoneInfo(timezone))`
   - ✅ Raise `ValueError` for invalid timezone names
   - ✅ Updated docstring with timezone parameter and example

3. ✅ **Modify `date_range()`**
   - ✅ Add optional `timezone` parameter (default: None)
   - ✅ Apply same timezone conversion logic as `human_date()`
   - ✅ Ensure both start and end use same timezone
   - ✅ Updated docstring with timezone parameter and example
   - ✅ Added 4 timezone test cases demonstrating same timestamps → different date ranges

4. ✅ **Update `_to_timestamp()` if needed**
   - Current implementation handles timezone-aware datetime objects
   - Verified it correctly converts to Unix timestamps
   - No changes needed (datetime.timestamp() already handles this)

5. ✅ **Run test suite**
   - ✅ All 123 existing tests pass (backwards compatibility maintained)
   - ✅ All 4 new human_date timezone tests pass (commit 0791e98)
   - ✅ All 4 new date_range timezone tests pass (commit b8f7e0e)
   - ✅ Total: 131 tests passing

**Checkpoint**: ✅ Phase 3 complete! Both `human_date()` and `date_range()` now support timezone parameters with full backwards compatibility.

---

## Phase 4: Documentation Updates

**Goal**: Update user-facing documentation with timezone examples and DST guidance.

### Tasks:

1. **Update `usage.md`**
   - Add timezone examples to `human_date()` section
   - Add timezone examples to `date_range()` section
   - Show same timestamp in different timezones
   - Document Python version requirement (3.9+)

2. **Add DST guidance section to `usage.md`**
   - Explain non-existent times (spring forward)
   - Explain ambiguous times (fall back) and `fold` parameter
   - Show how to safely create timezone-aware datetimes
   - Clarify that duration functions remain DST-agnostic
   - Provide example: elapsed time vs. wall-clock time

3. **Create DST examples**
   - Show UK spring forward behavior
   - Show UK fall back behavior
   - Demonstrate the example from user: "2026-03-29 00:59 to 2026-03-29 01:01 is 1 hour 2 minutes"
   - Show how same timestamp displays differently in different timezones

**Checkpoint**: Documentation complete, users have clear guidance on DST behavior.

---

## Phase 5: Validation and Cleanup

**Goal**: Final verification and cleanup of temporary files.

### Tasks:

1. **Run full test suite**
   - Verify all 123+ tests pass
   - Check backwards compatibility explicitly
   - Test with different Python versions if possible

2. **Manual testing**
   - Test with real DST transition dates
   - Verify UK clocks-go-forward example: 2026-03-29
   - Verify UK clocks-go-back example: 2026-10-25
   - Test edge case: midnight at timezone boundaries

3. **Update `progress.md`**
   - Document DST support completion
   - Note any challenges encountered
   - Record final test count

4. **Clean up**
   - Remove temporary `test_design.md` file
   - Ensure all docs are consistent
   - Verify SPEC.md and implementation match

**Checkpoint**: Implementation complete, validated, and documented.

---

## Rollback Plan

Each phase is designed to be reversible:

- **Phase 1**: Only doc changes → revert with git
- **Phase 2**: Tests extended but code unchanged → can pause here safely
- **Phase 3**: Code changes isolated to timezone parameter → can revert to Phase 2
- **Phase 4**: Documentation only → can revert independently

---

## Success Criteria

- [ ] SPEC.md includes timezone parameter specification
- [x] tests.yaml includes basic timezone test cases (8 tests added: 4 for human_date, 4 for date_range; DST tests pending)
- [x] All existing tests pass (backwards compatibility) - all 123 original tests pass
- [x] All new timezone tests pass (8/8 passing)
- [x] `human_date()` accepts timezone parameter (✅ commit 0791e98)
- [x] `date_range()` accepts timezone parameter (✅ commit b8f7e0e)
- [x] Invalid timezone names raise `ValueError`
- [x] Default behavior (no timezone param) remains UTC
- [ ] usage.md documents timezone usage with examples
- [ ] DST edge cases clearly documented
- [ ] User's example scenarios work correctly (DST transitions not yet tested)

---

## Non-Goals (Out of Scope)

- Adding timezone support to `timeago()` (not needed for relative times)
- Adding timezone support to `duration()` or `parse_duration()` (work with elapsed time)
- Handling non-existent times automatically (let Python raise errors, document clearly)
- Timezone abbreviation support (e.g., "PST" → use full IANA names only)
- Automatic timezone detection (user must specify explicitly)
- Historical timezone data handling (rely on Python's zoneinfo database)

---

## Estimated Complexity

**Low risk, moderate effort**:
- API change is additive (optional parameter)
- Backwards compatibility maintained throughout
- Python's `zoneinfo` handles DST complexity
- Test-driven approach reduces implementation risk

**Key risks**:
- Platform differences in zoneinfo data (mitigated: document requirement)
- Edge cases at exact transition moments (mitigated: comprehensive tests)
- User confusion about DST behavior (mitigated: clear documentation)
