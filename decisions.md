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

## Timezone and DST Support (2026-01-29)

### Delegating DST Complexity to `zoneinfo`
**Decision**: Rely entirely on Python's `zoneinfo` module for DST handling, with no custom DST logic in whenwords.

**Rationale**: DST rules are complex, vary by location, and change over time. Rather than implementing custom DST logic, we delegate to Python's standard library `zoneinfo`, which:
- Maintains the IANA timezone database with all historical and current DST rules
- Automatically handles offset changes during transitions
- Updates with OS timezone data, staying current with rule changes
- Has been thoroughly tested across many Python applications

**Validation**: Added 9 comprehensive DST test cases covering:
- UK spring forward (clocks jump 01:00 → 02:00 on 2026-03-29)
- UK fall back (clocks go back 02:00 → 01:00 on 2026-10-25)
- US Eastern time transitions (different dates than UK)
- Date ranges spanning DST transitions

All tests pass without any DST-specific code in whenwords. The implementation simply passes timezone names to `ZoneInfo()` and lets Python handle the rest.

**Trade-offs**:
- Requires Python 3.9+ (when `zoneinfo` was added to standard library)
- Depends on system timezone database being up-to-date
- Cannot customize DST behavior for edge cases

**Alternative considered**: Implementing custom DST logic or using third-party libraries like `pytz`. Rejected because:
- Custom logic would be error-prone and require extensive maintenance
- Standard library is sufficient and has no external dependencies
- `pytz` is deprecated in favor of `zoneinfo` for Python 3.9+
