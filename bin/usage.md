# whenwords for Python

Human-friendly time formatting and parsing.

## Installation

Copy `whenwords.py` to your project and import the functions:

```python
from whenwords import timeago, duration, parse_duration, human_date, date_range
```

## Quick start

```python
from whenwords import timeago, duration, parse_duration, human_date, date_range
from datetime import datetime

# Relative time
timeago(1704049200, reference=1704067200)  # "5 hours ago"

# Format durations
duration(3661)                              # "1 hour, 1 minute"
duration(3661, {'compact': True})          # "1h 1m"

# Parse durations
parse_duration("2h 30m")                   # 9000 (seconds)

# Contextual dates
human_date(1705190400, reference=1705276800)  # "Yesterday"

# Date ranges
date_range(1705276800, 1705881600)         # "January 15–22, 2024"
```

## Functions

### timeago(timestamp, reference?) → str

Returns a human-readable relative time string like "3 hours ago" or "in 2 days".

**Parameters:**
- `timestamp`: Unix timestamp (int/float), ISO 8601 string, or datetime object
- `reference`: Optional reference time (defaults to timestamp, returns "just now")

**Examples:**
```python
# Past times
timeago(1704067170, reference=1704067200)  # "just now" (30 seconds ago)
timeago(1704049200, reference=1704067200)  # "5 hours ago"
timeago(1703462400, reference=1704067200)  # "7 days ago"

# Future times
timeago(1704067260, reference=1704067200)  # "in 1 minute"
timeago(1704078000, reference=1704067200)  # "in 3 hours"

# With datetime objects
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
past = datetime(2024, 1, 1, tzinfo=timezone.utc)
timeago(past, now)  # "X days ago" (depends on current date)
```

### duration(seconds, options?) → str

Formats a duration as a human-readable string. Not relative to now.

**Parameters:**
- `seconds`: Non-negative number of seconds (int or float)
- `options`: Optional dict with:
  - `compact`: bool (default False) - use "2h 30m" style instead of "2 hours, 30 minutes"
  - `max_units`: int (default 2) - maximum number of time units to display

**Examples:**
```python
# Standard format
duration(3661)                    # "1 hour, 1 minute"
duration(9000)                    # "2 hours, 30 minutes"
duration(0)                       # "0 seconds"

# Compact format
duration(3661, {'compact': True})              # "1h 1m"
duration(93600, {'compact': True})             # "1d 2h"

# Limit units
duration(3661, {'max_units': 1})               # "1 hour"
duration(93661, {'max_units': 3})              # "1 day, 2 hours, 1 minute"
duration(9000, {'compact': True, 'max_units': 1})  # "3h"
```

### parse_duration(string) → int

Parses a human-written duration string into seconds.

**Parameters:**
- `string`: Duration string in various formats

**Returns:** Total seconds as an integer

**Supported formats:**
- Compact: "2h30m", "2h 30m", "2h, 30m"
- Verbose: "2 hours 30 minutes", "2 hours and 30 minutes"
- Decimal: "2.5 hours", "1.5h"
- Single unit: "90 minutes", "90m", "90min"
- Colon notation: "2:30" (h:mm), "1:30:00" (h:mm:ss)

**Unit aliases:**
- seconds: s, sec, secs, second, seconds
- minutes: m, min, mins, minute, minutes
- hours: h, hr, hrs, hour, hours
- days: d, day, days
- weeks: w, wk, wks, week, weeks

**Examples:**
```python
parse_duration("2h30m")                    # 9000
parse_duration("2 hours 30 minutes")       # 9000
parse_duration("2.5 hours")                # 9000
parse_duration("2:30")                     # 9000
parse_duration("1 day, 2 hours, and 30 minutes")  # 95400
parse_duration("1w")                       # 604800
```

### human_date(timestamp, reference?) → str

Returns a contextual date string based on proximity to the reference date.

**Parameters:**
- `timestamp`: The date to format (Unix timestamp, ISO 8601 string, or datetime)
- `reference`: The reference date for comparison (defaults to timestamp)

**Returns:** A contextual string like "Today", "Yesterday", "Last Friday", or "March 5"

**Examples:**
```python
# Same day
human_date(1705276800, reference=1705276800)    # "Today"

# Adjacent days
human_date(1705190400, reference=1705276800)    # "Yesterday"
human_date(1705363200, reference=1705276800)    # "Tomorrow"

# Recent weekdays
human_date(1705104000, reference=1705276800)    # "Last Saturday" (2 days ago)
human_date(1705449600, reference=1705276800)    # "This Wednesday" (2 days future)

# Dates in same year
human_date(1709251200, reference=1705276800)    # "March 1"

# Different years
human_date(1672531200, reference=1705276800)    # "January 1, 2023"
```

### date_range(start, end) → str

Formats a date range with smart abbreviation to avoid repetition.

**Parameters:**
- `start`: Start timestamp (Unix seconds, ISO 8601 string, or datetime)
- `end`: End timestamp (automatically swapped if start > end)

**Returns:** A formatted date range string

**Examples:**
```python
# Same day
date_range(1705276800, 1705276800)          # "January 15, 2024"

# Same month
date_range(1705276800, 1705881600)          # "January 15–22, 2024"

# Same year, different months
date_range(1705276800, 1707955200)          # "January 15 – February 15, 2024"

# Different years
date_range(1703721600, 1705276800)          # "December 28, 2023 – January 15, 2024"

# Auto-corrects swapped dates
date_range(1705881600, 1705276800)          # "January 15–22, 2024"
```

## Error handling

All functions raise `ValueError` with descriptive messages for invalid inputs:

```python
# Invalid inputs
duration(-100)                  # ValueError: Duration must be non-negative and finite
parse_duration("")              # ValueError: Duration string cannot be empty
parse_duration("-5 hours")      # ValueError: Negative durations are not allowed
timeago("invalid")              # ValueError: Invalid timestamp format
```

Catch errors using standard Python exception handling:

```python
try:
    result = parse_duration(user_input)
except ValueError as e:
    print(f"Invalid duration: {e}")
```

## Accepted types

**Timestamp parameters** (timeago, human_date, date_range) accept:
- Unix timestamps: `1704067200` (int or float, interpreted as seconds since 1970-01-01 UTC)
- ISO 8601 strings: `"2024-01-01T00:00:00Z"`
- Python datetime objects: `datetime(2024, 1, 1, tzinfo=timezone.utc)`

**Duration parameters** accept:
- `duration()`: int or float (seconds)
- `parse_duration()`: string

**Options** are passed as dictionaries:
```python
duration(3661, {'compact': True, 'max_units': 1})
```

## Timezone notes

All calendar functions (`human_date`, `date_range`) interpret timestamps in UTC by default. For timezone-aware datetimes, pass datetime objects with tzinfo set:

```python
from datetime import datetime, timezone

# UTC (recommended)
dt_utc = datetime(2024, 1, 1, tzinfo=timezone.utc)

# The library converts all datetime objects to Unix timestamps for processing
human_date(dt_utc)
```

Relative functions (`timeago`, `duration`, `parse_duration`) work with durations between timestamps and are timezone-agnostic.
