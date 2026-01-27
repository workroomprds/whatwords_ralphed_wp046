# Technical Decisions

This document records significant technical decisions made during whenwords implementation across different languages.

## Python Implementation (2026-01-27)

### Date Formatting with `strftime`
**Decision**: Use `strftime` with `%-d` format for day-of-month without leading zeros.

**Rationale**: The SPEC.md requires date outputs like "January 8" not "January 08". Python's `strftime` supports platform-specific flags: `%-d` on Linux/Unix removes leading zeros. This is simpler than manual string manipulation.

**Trade-offs**: The `%-d` flag is platform-specific (Windows uses `%#d`). However, since this implementation targets a Linux environment and the spec tests expect this format, we prioritized simplicity. A more portable version would detect the platform or strip leading zeros manually.

### Negative Duration Detection
**Decision**: Check for minus sign in input string before regex parsing in `parse_duration()`.

**Rationale**: The regex pattern `([\d.]+)` only matches digits and decimals, not minus signs. Initially, negative values weren't caught until after parsing units. Adding an early check for `-` in the input string provides clearer error messages and prevents partial parsing.

**Alternative considered**: Modify regex to `([+-]?[\d.]+)` to capture sign, then validate. Rejected because it complicates the parsing logic and we want to fail fast on invalid input.

### Weekday Range for `human_date()`
**Decision**: "Last/This [Weekday]" applies to 2-6 days away, not 1-7 days.

**Rationale**: Initial implementation used `if -7 <= day_diff < -1` which incorrectly included 7 days. The SPEC.md tests clarified that exactly 7 days should display as a date ("January 8"), not "Last Monday". The boundary conditions are:
- Yesterday: -1 day
- Last [Weekday]: -2 to -6 days
- Date format: -7+ days
- Tomorrow: +1 day
- This [Weekday]: +2 to +6 days
- Date format: +7+ days

This creates clearer transitions and avoids ambiguity (e.g., "Last Monday" when today is Monday).

### Timestamp Normalization Strategy
**Decision**: Create a single `_to_timestamp()` helper that converts all timestamp types (Unix seconds, ISO 8601, datetime objects) to float.

**Rationale**: Multiple functions accept flexible timestamp types. Centralizing conversion logic ensures consistency and reduces code duplication. The helper handles three cases:
1. `int/float` → pass through as float
2. `str` → parse as ISO 8601
3. `datetime` → convert via `.timestamp()`

**Trade-offs**: Adds a function call overhead, but improves maintainability. Alternative would be inline conversion in each function.

### Duration Rounding with `max_units`
**Decision**: Round the last displayed unit when `max_units` truncates output.

**Rationale**: When displaying fewer units than available, rounding the smallest shown unit provides more accurate representations. For example, `duration(3690, max_units=1)` shows "1 hour" because 90 seconds rounds up to 2 minutes, but we only show hours, which remains 1. This prevents misleading outputs like showing "1 hour" for 3659 seconds (which is nearly 1 hour 1 minute).

**Implementation**: After collecting units, if we've reached `max_units` and there's remaining time, check if remaining >= half of the current unit size to decide whether to round up.

### Test Generation Approach
**Decision**: Hand-write test functions rather than dynamically generating them from YAML.

**Rationale**: While we could write a test generator that reads YAML and creates tests dynamically, hand-written tests are:
- More debuggable (clear stack traces with function names)
- Compatible with pytest's test discovery
- Easier to understand without knowing the generator logic
- More maintainable for humans reviewing the code

The trade-off is initial effort, but since tests are generated once and rarely change, explicitness wins.

### Error Handling: `ValueError` for All Cases
**Decision**: Raise `ValueError` for all error conditions (invalid timestamps, negative durations, unparseable strings).

**Rationale**: Python convention is to use `ValueError` when a function receives an argument of correct type but inappropriate value. This is idiomatic and expected by Python developers. More specific exceptions (like custom `InvalidTimestamp` or `ParseError` classes) would add complexity without clear benefit for a small library.

**Consistency**: All five functions use the same error type, simplifying error handling for library users.

---

## Daylight Saving Time Support Planning (2026-01-27)

### Scope: Calendar Functions Only
**Decision**: Add timezone support only to `human_date()` and `date_range()`. Do not add timezone parameters to `timeago()`, `duration()`, or `parse_duration()`.

**Rationale**:
- `timeago()` calculates relative time between two absolute moments. The difference between Unix timestamps inherently accounts for DST—no timezone parameter needed.
- `duration()` and `parse_duration()` work with elapsed time (seconds), not wall-clock time. A duration of 3600 seconds is always 1 hour of elapsed time, regardless of DST.
- `human_date()` and `date_range()` determine which calendar *day* a timestamp falls on, which depends on timezone. A timestamp at midnight UTC is "Today" in London but "Yesterday" in California.

**Example**: The time from UK 2026-03-29 00:30 to 02:30 spans the spring-forward transition. The elapsed duration is 1 hour (3600 seconds), even though the wall-clock shows a 2-hour difference. The `duration()` function correctly returns "1 hour" because it measures elapsed time.

### API Design: Optional Timezone Parameter
**Decision**: Add optional `timezone` parameter to `human_date()` and `date_range()`. When omitted, default to UTC (preserving backwards compatibility).

**Rationale**:
- Additive API change—no breaking changes to existing code
- Explicit is better than implicit—users must specify timezone when needed
- UTC default is safe and matches current behavior
- Follows Python convention of optional parameters with sensible defaults

**Signature changes**:
```python
human_date(timestamp, reference=None, timezone=None)
date_range(start, end, timezone=None)
```

**Alternative considered**: Always require timezone parameter for accuracy. Rejected because it breaks backwards compatibility and adds friction for UTC-only use cases.

### Timezone Format: IANA Names Only
**Decision**: Accept only IANA timezone names (e.g., "Europe/London", "America/New_York"). Use Python's `zoneinfo` module (stdlib in Python 3.9+).

**Rationale**:
- IANA names are unambiguous and comprehensive
- `zoneinfo` is standard library (no external dependencies)
- Handles all DST transitions automatically via timezone database
- Cross-platform and well-maintained

**Rejected alternatives**:
- Timezone abbreviations (e.g., "GMT", "PST"): Ambiguous (PST could be Pacific or Philippine Standard Time)
- UTC offsets (e.g., "+01:00"): Don't account for DST transitions
- Custom timezone objects: Unnecessary complexity

**Trade-off**: Requires Python 3.9+. Document this as a requirement. For Python 3.8 and earlier, users must install `backports.zoneinfo` package.

### Non-Existent Times: Let Python Raise Errors
**Decision**: When users try to create a datetime during a spring-forward transition (non-existent hour), let Python's `datetime` raise an exception. Document this behavior clearly but don't try to handle it automatically.

**Rationale**:
- Non-existent times are genuinely ambiguous—no "correct" interpretation exists
- Attempting to guess (e.g., rounding to nearest valid time) could silently introduce bugs
- Python's error message is clear: "NonExistentTimeError" (or similar depending on version)
- Forces users to be explicit about their intent

**Example**: UK 2026-03-29 01:30 doesn't exist (clocks jump from 00:59:59 to 02:00:00). If a user tries `datetime(2026, 3, 29, 1, 30, tzinfo=ZoneInfo("Europe/London"))`, Python will raise an error. This is correct behavior.

**Documentation requirement**: Provide clear guidance in `usage.md` about DST transitions and how to avoid non-existent times.

### Ambiguous Times: Support Python's `fold` Parameter
**Decision**: Document that users should use Python's `fold` parameter to disambiguate times during fall-back transitions. The `whenwords` library will accept timezone-aware datetime objects with `fold` set appropriately.

**Rationale**:
- Python's `fold` parameter (PEP 495) is the standard way to handle ambiguous times
- `fold=0` means first occurrence (e.g., 01:30 BST)
- `fold=1` means second occurrence (e.g., 01:30 GMT after clocks fall back)
- This puts the responsibility on the caller, which is appropriate since they have the context

**Example**: UK 2026-10-25 01:30 happens twice. Users create:
- `datetime(2026, 10, 25, 1, 30, tzinfo=ZoneInfo("Europe/London"), fold=0)` for first occurrence
- `datetime(2026, 10, 25, 1, 30, tzinfo=ZoneInfo("Europe/London"), fold=1)` for second occurrence

**Alternative considered**: Add our own disambiguation parameter (e.g., `dst=True/False`). Rejected because Python already solves this problem—no need to reinvent it.

### Duration Calculations: Remain DST-Agnostic
**Decision**: `duration()` and `parse_duration()` continue to work with seconds of elapsed time. They remain completely unaware of timezones and DST.

**Rationale**:
- These functions measure elapsed time, not wall-clock time
- Unix timestamps already encode DST information—the difference between two timestamps is correct
- Mixing elapsed time with wall-clock time would be confusing and error-prone

**Key insight**: There's a fundamental difference between:
- **Elapsed time**: "3600 seconds passed" (what `duration()` measures)
- **Wall-clock time**: "the clock showed 2 hours difference" (display artifact of DST)

Users who need wall-clock duration (e.g., "2pm to 4pm is 2 hours, even if DST made it 1 hour of elapsed time") should calculate this themselves by converting to local datetimes and comparing wall-clock values. This is a specialized use case that shouldn't be the default.

**Example clarification**:
```python
# UK 2026-03-29: clocks spring forward at 01:00 → 02:00
start = datetime(2026, 3, 29, 0, 30, tzinfo=ZoneInfo("Europe/London"))
end = datetime(2026, 3, 29, 2, 30, tzinfo=ZoneInfo("Europe/London"))

elapsed = end.timestamp() - start.timestamp()  # 3600 seconds
duration(elapsed)  # "1 hour" ✓ correct (elapsed time)

# Wall-clock shows 00:30 → 02:30 (2 hours difference on display)
# But only 1 hour actually elapsed (01:00-01:59 didn't exist)
```

### Test Format: Unix Timestamps + Timezone Field
**Decision**: Add optional `timezone` field to test cases in `tests.yaml`. Unix timestamps remain the input format, but timezone field specifies how to interpret them for calendar functions.

**Rationale**:
- Unix timestamps are unambiguous (no DST confusion)
- Language-agnostic test format (any language can read Unix timestamps)
- Timezone field makes test intent clear without complex datetime parsing
- Backwards compatible—tests without timezone field default to UTC

**Format**:
```yaml
human_date:
  - name: "UK timezone displays different day"
    input: { timestamp: 1704063600, reference: 1704067200, timezone: "Europe/London" }
    output: "Yesterday"
```

**Alternative considered**: Use ISO 8601 strings with timezone offsets. Rejected because offsets don't account for future DST changes (the test suite should remain valid across years).

### Backwards Compatibility: Non-Negotiable
**Decision**: All 123 existing tests must pass without modification. Default behavior (no timezone parameter) must remain UTC.

**Rationale**:
- Breaking existing implementations is unacceptable for a stable library
- Users should be able to adopt new timezone support gradually
- UTC-only use cases shouldn't pay any cost (performance or complexity)

**Verification approach**: Run existing test suite after each change to ensure no regressions.

### DST Test Validation Strategy
**Decision**: Test DST transitions using carefully calculated Unix timestamps rather than attempting to construct non-existent or ambiguous local times directly.

**Rationale**:
- Unix timestamps are unambiguous and always valid—they represent a single point in absolute time
- Python's ZoneInfo automatically applies correct DST offsets when converting timestamps to local times
- Testing the conversion process (timestamp → local datetime → formatted output) validates DST handling
- Avoids complexity of trying to create non-existent times (which should raise errors anyway)
- Tests prove that the same timestamp displays correctly in different timezones with DST applied

**Implementation approach**:
- Calculate exact Unix timestamps for moments before/during/after DST transitions using Python with ZoneInfo
- Add these timestamps to tests.yaml with appropriate timezone field
- Verify output reflects correct local time with DST offset applied
- Document timestamps with comments showing both UTC and local time interpretations

**Example**: UK spring forward test uses timestamp 1774747800 = 2026-03-29 02:30:00 BST (01:30 UTC). This proves the implementation correctly interprets a timestamp falling after the 01:00→02:00 clock skip as being in BST (UTC+1).

**Validation result**: All 8 DST test cases pass without code changes, confirming that ZoneInfo handles DST transitions correctly and the implementation requires no special DST logic.
