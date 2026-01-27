"""whenwords - Human-friendly time formatting and parsing.

A library for converting timestamps to readable strings like "3 hours ago"
and parsing duration strings like "2h 30m" into seconds.

All functions are pure - no side effects, no I/O, no system clock access.
"""

import re
import math
from datetime import datetime, timezone as dt_timezone
from typing import Union, Optional, Dict, Any
from zoneinfo import ZoneInfo


def _to_timestamp(value: Union[int, float, str, datetime]) -> float:
    """Convert various timestamp formats to Unix seconds."""
    if isinstance(value, (int, float)):
        return float(value)
    elif isinstance(value, str):
        # Parse ISO 8601 string
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return dt.timestamp()
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid timestamp format: {value}")
    elif isinstance(value, datetime):
        return value.timestamp()
    else:
        raise ValueError(f"Invalid timestamp type: {type(value)}")


def timeago(timestamp: Union[int, float, str, datetime],
            reference: Optional[Union[int, float, str, datetime]] = None) -> str:
    """Return a human-readable relative time string.

    Args:
        timestamp: The time to format (Unix seconds, ISO 8601 string, or datetime)
        reference: The reference time (defaults to timestamp, returns "just now")

    Returns:
        A string like "3 hours ago" or "in 2 days"

    Examples:
        >>> timeago(1704067170, 1704067200)
        'just now'
        >>> timeago(1704049200, 1704067200)
        '5 hours ago'
    """
    ts = _to_timestamp(timestamp)
    ref = _to_timestamp(reference) if reference is not None else ts

    diff = ref - ts  # Positive if timestamp is in the past
    abs_diff = abs(diff)
    is_future = diff < 0

    # Thresholds and formatting
    if abs_diff < 45:
        return "just now"
    elif abs_diff < 90:
        unit = "minute"
        n = 1
    elif abs_diff < 45 * 60:
        unit = "minutes"
        n = round(abs_diff / 60)
    elif abs_diff < 90 * 60:
        unit = "hour"
        n = 1
    elif abs_diff < 22 * 3600:
        unit = "hours"
        n = round(abs_diff / 3600)
    elif abs_diff < 36 * 3600:
        unit = "day"
        n = 1
    elif abs_diff < 26 * 86400:
        unit = "days"
        n = round(abs_diff / 86400)
    elif abs_diff < 46 * 86400:
        unit = "month"
        n = 1
    elif abs_diff < 320 * 86400:
        unit = "months"
        n = round(abs_diff / (30 * 86400))
    elif abs_diff < 548 * 86400:
        unit = "year"
        n = 1
    else:
        unit = "years"
        n = round(abs_diff / (365 * 86400))

    # Format output
    if n == 1 and unit[-1] == 's':
        unit = unit[:-1]  # Remove plural

    if is_future:
        return f"in {n} {unit}"
    else:
        return f"{n} {unit} ago"


def duration(seconds: Union[int, float],
             options: Optional[Dict[str, Any]] = None) -> str:
    """Format a duration as a human-readable string.

    Args:
        seconds: Non-negative number of seconds
        options: Optional dict with:
            - compact: bool (default False) - use "2h 34m" style
            - max_units: int (default 2) - maximum units to show

    Returns:
        A formatted duration string

    Examples:
        >>> duration(3661)
        '1 hour, 1 minute'
        >>> duration(3661, {'compact': True})
        '1h 1m'
        >>> duration(3661, {'max_units': 1})
        '1 hour'
    """
    if seconds < 0 or math.isnan(seconds) or math.isinf(seconds):
        raise ValueError("Duration must be non-negative and finite")

    options = options or {}
    compact = options.get('compact', False)
    max_units = options.get('max_units', 2)

    if seconds == 0:
        return "0s" if compact else "0 seconds"

    # Unit definitions (from largest to smallest)
    units = [
        ('year', 'y', 365 * 86400),
        ('month', 'mo', 30 * 86400),
        ('day', 'd', 86400),
        ('hour', 'h', 3600),
        ('minute', 'm', 60),
        ('second', 's', 1),
    ]

    remaining = seconds
    parts = []

    for unit_name, unit_abbr, unit_seconds in units:
        if remaining >= unit_seconds:
            count = int(remaining / unit_seconds)
            remaining = remaining % unit_seconds

            if compact:
                parts.append(f"{count}{unit_abbr}")
            else:
                plural = unit_name if count == 1 else f"{unit_name}s"
                parts.append(f"{count} {plural}")

            if len(parts) >= max_units:
                # Round the last unit if there's remaining time
                if remaining >= unit_seconds / 2:
                    count += 1
                    if compact:
                        parts[-1] = f"{count}{unit_abbr}"
                    else:
                        plural = unit_name if count == 1 else f"{unit_name}s"
                        parts[-1] = f"{count} {plural}"
                break

    if compact:
        return " ".join(parts)
    else:
        return ", ".join(parts)


def parse_duration(duration_str: str) -> int:
    """Parse a human-written duration string into seconds.

    Args:
        duration_str: A duration string like "2h30m", "2 hours 30 minutes", or "2:30"

    Returns:
        Total seconds as an integer

    Raises:
        ValueError: If the string is empty, unparseable, or results in negative duration

    Examples:
        >>> parse_duration("2h30m")
        9000
        >>> parse_duration("2 hours 30 minutes")
        9000
        >>> parse_duration("2:30")
        9000
    """
    if not duration_str or not duration_str.strip():
        raise ValueError("Duration string cannot be empty")

    duration_str = duration_str.strip()

    # Check for negative values first
    if '-' in duration_str:
        raise ValueError("Negative durations are not allowed")

    # Check for colon notation (h:mm or h:mm:ss)
    colon_match = re.match(r'^(\d+):(\d+)(?::(\d+))?$', duration_str)
    if colon_match:
        hours = int(colon_match.group(1))
        minutes = int(colon_match.group(2))
        seconds = int(colon_match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds

    # Unit mappings
    unit_map = {
        's': 1, 'sec': 1, 'secs': 1, 'second': 1, 'seconds': 1,
        'm': 60, 'min': 60, 'mins': 60, 'minute': 60, 'minutes': 60,
        'h': 3600, 'hr': 3600, 'hrs': 3600, 'hour': 3600, 'hours': 3600,
        'd': 86400, 'day': 86400, 'days': 86400,
        'w': 604800, 'wk': 604800, 'wks': 604800, 'week': 604800, 'weeks': 604800,
    }

    # Parse duration components
    # Pattern: optional number (int or float) followed by unit
    pattern = r'([\d.]+)\s*([a-zA-Z]+)'
    matches = re.findall(pattern, duration_str, re.IGNORECASE)

    if not matches:
        raise ValueError(f"No parseable duration found in: {duration_str}")

    total_seconds = 0
    for value_str, unit in matches:
        value = float(value_str)
        if value < 0:
            raise ValueError("Negative durations are not allowed")

        unit_lower = unit.lower()
        if unit_lower not in unit_map:
            raise ValueError(f"Unknown unit: {unit}")

        total_seconds += value * unit_map[unit_lower]

    if total_seconds < 0:
        raise ValueError("Negative durations are not allowed")

    return int(total_seconds)


def human_date(timestamp: Union[int, float, str, datetime],
               reference: Optional[Union[int, float, str, datetime]] = None,
               timezone: Optional[str] = None) -> str:
    """Return a contextual date string.

    Args:
        timestamp: The date to format
        reference: The reference date for comparison (defaults to timestamp)
        timezone: IANA timezone name (e.g., "America/New_York", "Europe/London").
                  If None, uses UTC (default).

    Returns:
        A string like "Today", "Yesterday", "Last Friday", or "March 5"

    Examples:
        >>> human_date(1705276800, 1705276800)
        'Today'
        >>> human_date(1705190400, 1705276800)
        'Yesterday'
        >>> human_date(1721950200, 1721952000, timezone="America/New_York")
        'Today'
    """
    ts = _to_timestamp(timestamp)
    ref = _to_timestamp(reference) if reference is not None else ts

    # Determine timezone to use
    if timezone is None:
        tz = dt_timezone.utc
    else:
        try:
            tz = ZoneInfo(timezone)
        except Exception as e:
            raise ValueError(f"Invalid timezone name: {timezone}") from e

    # Convert to datetime objects in specified timezone
    dt = datetime.fromtimestamp(ts, tz=tz)
    ref_dt = datetime.fromtimestamp(ref, tz=tz)

    # Get date components (ignoring time)
    dt_date = dt.date()
    ref_date = ref_dt.date()

    # Calculate day difference
    day_diff = (dt_date - ref_date).days

    # Same day
    if day_diff == 0:
        return "Today"

    # Yesterday
    if day_diff == -1:
        return "Yesterday"

    # Tomorrow
    if day_diff == 1:
        return "Tomorrow"

    # Within past 7 days (2-6 days ago)
    if -6 <= day_diff <= -2:
        weekday = dt.strftime("%A")
        return f"Last {weekday}"

    # Within next 7 days (2-6 days future)
    if 2 <= day_diff <= 6:
        weekday = dt.strftime("%A")
        return f"This {weekday}"

    # Same year
    if dt.year == ref_dt.year:
        return dt.strftime("%B %-d")

    # Different year
    return dt.strftime("%B %-d, %Y")


def date_range(start: Union[int, float, str, datetime],
               end: Union[int, float, str, datetime],
               timezone: Optional[str] = None) -> str:
    """Format a date range with smart abbreviation.

    Args:
        start: Start timestamp
        end: End timestamp
        timezone: IANA timezone name (e.g., "America/New_York", "Europe/London").
                  If None, uses UTC (default).

    Returns:
        A formatted date range string

    Examples:
        >>> date_range(1705276800, 1705276800)
        'January 15, 2024'
        >>> date_range(1705276800, 1705881600)
        'January 15–22, 2024'
        >>> date_range(1721950200, 1721955600, timezone="America/New_York")
        'July 25, 2024'
    """
    start_ts = _to_timestamp(start)
    end_ts = _to_timestamp(end)

    # Auto-correct if swapped
    if start_ts > end_ts:
        start_ts, end_ts = end_ts, start_ts

    # Determine timezone to use
    if timezone is None:
        tz = dt_timezone.utc
    else:
        try:
            tz = ZoneInfo(timezone)
        except Exception as e:
            raise ValueError(f"Invalid timezone name: {timezone}") from e

    # Convert to datetime objects in specified timezone
    start_dt = datetime.fromtimestamp(start_ts, tz=tz)
    end_dt = datetime.fromtimestamp(end_ts, tz=tz)

    # Get date components
    start_date = start_dt.date()
    end_date = end_dt.date()

    # Same day
    if start_date == end_date:
        return start_dt.strftime("%B %-d, %Y")

    # Same month and year
    if start_dt.month == end_dt.month and start_dt.year == end_dt.year:
        return f"{start_dt.strftime('%B %-d')}–{end_dt.strftime('%-d, %Y')}"

    # Same year, different months
    if start_dt.year == end_dt.year:
        return f"{start_dt.strftime('%B %-d')} – {end_dt.strftime('%B %-d, %Y')}"

    # Different years
    return f"{start_dt.strftime('%B %-d, %Y')} – {end_dt.strftime('%B %-d, %Y')}"
