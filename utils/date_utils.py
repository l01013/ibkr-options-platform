"""Trading calendar and date utilities."""

from datetime import date, datetime, timedelta
import pandas as pd


def get_trading_days(start: date, end: date) -> list[date]:
    """Return US market trading days between start and end (inclusive)."""
    bdays = pd.bdate_range(start=start, end=end, freq="B")
    # Exclude common US holidays (simplified)
    holidays = _us_market_holidays(start.year, end.year)
    return [d.date() for d in bdays if d.date() not in holidays]


def _us_market_holidays(start_year: int, end_year: int) -> set[date]:
    """Approximate US market holidays. For production use exchange calendar."""
    holidays = set()
    for year in range(start_year, end_year + 1):
        holidays.add(date(year, 1, 1))    # New Year
        holidays.add(date(year, 7, 4))    # Independence Day
        holidays.add(date(year, 12, 25))  # Christmas
        # MLK Day: 3rd Monday of January
        holidays.add(_nth_weekday(year, 1, 0, 3))
        # Presidents Day: 3rd Monday of February
        holidays.add(_nth_weekday(year, 2, 0, 3))
        # Memorial Day: last Monday of May
        holidays.add(_last_weekday(year, 5, 0))
        # Labor Day: 1st Monday of September
        holidays.add(_nth_weekday(year, 9, 0, 1))
        # Thanksgiving: 4th Thursday of November
        holidays.add(_nth_weekday(year, 11, 3, 4))
    return holidays


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """Get the nth occurrence of a weekday in a month (1-indexed)."""
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (n - 1))


def _last_weekday(year: int, month: int, weekday: int) -> date:
    """Get the last occurrence of a weekday in a month."""
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    offset = (last_day.weekday() - weekday) % 7
    return last_day - timedelta(days=offset)


def dte(expiry: date, from_date: date | None = None) -> int:
    """Calculate days to expiration."""
    if from_date is None:
        from_date = date.today()
    return (expiry - from_date).days


def parse_ib_date(date_str: str) -> datetime:
    """Parse IBKR date format (YYYYMMDD or YYYYMMDD HH:MM:SS)."""
    date_str = date_str.strip()
    if len(date_str) == 8:
        return datetime.strptime(date_str, "%Y%m%d")
    return datetime.strptime(date_str, "%Y%m%d %H:%M:%S")
