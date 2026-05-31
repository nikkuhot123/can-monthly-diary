"""
Indian Banking Calendar Utility
Rules:
  - All Sundays = Holiday
  - 2nd Saturday of month = Holiday
  - 4th Saturday of month = Holiday
  - 1st, 3rd, 5th Saturdays = Working day
  - Public holidays = Holiday (Maharashtra)
  - Everything else = Working day
"""
import calendar
from datetime import date, timedelta
from typing import List, Dict, Optional


PUBLIC_HOLIDAYS: Dict[str, str] = {
    "2026-01-01": "New Year's Day",
    "2026-01-26": "Republic Day",
    "2026-02-19": "Chhatrapati Shivaji Maharaj Jayanti",
    "2026-02-26": "Maha Shivaratri",
    "2026-03-03": "Holi",
    "2026-03-20": "Ugadi",
    "2026-03-21": "Idul Fitr",
    "2026-03-27": "Ram Navami",
    "2026-03-31": "Mahavir Jayanti",
    "2026-04-03": "Good Friday",
    "2026-04-14": "Dr. Ambedkar Jayanti",
    "2026-05-01": "Maharashtra Day / Labour Day",
    "2026-06-26": "Muharram",
    "2026-08-15": "Independence Day",
    "2026-08-16": "Parsi New Year",
    "2026-08-27": "Ganesh Chaturthi",
    "2026-08-25": "Milad-un-Nabi",
    "2026-10-02": "Gandhi Jayanti",
    "2026-10-20": "Dussehra",
    "2026-11-04": "Diwali (Lakshmi Puja)",
    "2026-11-05": "Diwali (Balipratipada)",
    "2026-11-24": "Guru Nanak Jayanti",
    "2026-12-25": "Christmas Day",
    "2025-01-26": "Republic Day",
    "2025-02-19": "Chhatrapati Shivaji Maharaj Jayanti",
    "2025-03-14": "Holi",
    "2025-05-01": "Maharashtra Day",
    "2025-08-15": "Independence Day",
    "2025-08-16": "Parsi New Year",
    "2025-08-27": "Ganesh Chaturthi",
    "2025-10-01": "Gandhi Jayanti",
    "2025-10-20": "Diwali",
    "2025-11-05": "Guru Nanak Jayanti",
    "2025-12-25": "Christmas",
}


def get_nth_saturday(year: int, month: int, n: int) -> Optional[date]:
    """Return the nth Saturday of given month. n=1,2,3,4,5. Returns None if doesn't exist."""
    first_day = date(year, month, 1)
    days_until_saturday = (5 - first_day.weekday()) % 7
    first_saturday = first_day + timedelta(days=days_until_saturday)
    target = first_saturday + timedelta(weeks=(n - 1))
    if target.month != month:
        return None
    return target


def get_bank_holidays_for_month(year: int, month: int) -> Dict[date, str]:
    """
    Returns dict of {date: reason} for all bank holidays in given month.
    Includes: All Sundays, 2nd & 4th Saturdays, Public Holidays.
    """
    holidays: Dict[date, str] = {}
    _, days_in_month = calendar.monthrange(year, month)

    sat2 = get_nth_saturday(year, month, 2)
    sat4 = get_nth_saturday(year, month, 4)

    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        wd = d.weekday()

        if wd == 6:
            holidays[d] = "Sunday"
            continue

        if wd == 5 and sat2 and d == sat2:
            holidays[d] = "2nd Saturday"
            continue
        if wd == 5 and sat4 and d == sat4:
            holidays[d] = "4th Saturday"
            continue

        date_str = d.strftime("%Y-%m-%d")
        if date_str in PUBLIC_HOLIDAYS:
            holidays[d] = PUBLIC_HOLIDAYS[date_str]

    return holidays


def is_bank_holiday(d: date) -> bool:
    """True if date is a bank holiday (Sunday, 2nd/4th Sat, or public holiday)."""
    return d in get_bank_holidays_for_month(d.year, d.month)


def get_bank_holiday_reason(d: date) -> Optional[str]:
    """Return reason if bank holiday, else None."""
    holidays = get_bank_holidays_for_month(d.year, d.month)
    return holidays.get(d)


def is_working_day(d: date) -> bool:
    """True if date is a bank working day."""
    return not is_bank_holiday(d)


def count_month_days(year: int, month: int) -> Dict[str, int]:
    """Returns counts: total, working, holidays breakdown."""
    _, days_in_month = calendar.monthrange(year, month)
    bh = get_bank_holidays_for_month(year, month)

    sundays = sum(1 for r in bh.values() if r == "Sunday")
    bank_sats = sum(1 for r in bh.values() if "Saturday" in r)
    pub_hols = sum(1 for d, r in bh.items() if r not in ("Sunday",) and "Saturday" not in r)
    working = days_in_month - len(bh)

    return {
        "total_days": days_in_month,
        "working_days": working,
        "sundays": sundays,
        "bank_saturdays": bank_sats,
        "public_holidays": pub_hols,
        "total_holidays": len(bh),
    }


def build_month_calendar(year: int, month: int, attendance_map: Dict[date, dict]) -> List[dict]:
    """
    Build full month calendar list.
    attendance_map: {date: record_dict}
    Returns list of dicts per day with status/holiday_reason/attendance.
    """
    bh = get_bank_holidays_for_month(year, month)
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    result = []

    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        d = date(year, month, day)
        att = attendance_map.get(d)

        if d in bh:
            reason = bh[d]
            if reason == "Sunday":
                status = "sunday"
            elif "Saturday" in reason:
                status = "bank_holiday"
            else:
                status = "public_holiday"
        elif att and att.get("is_holiday"):
            status = "manual_holiday"
        elif att and att.get("is_leave"):
            status = "leave"
        elif att:
            status = "present"
        else:
            status = "missing"

        result.append({
            "date": d,
            "day_no": day,
            "weekday_name": weekday_names[d.weekday()],
            "is_working_day": d not in bh,
            "status": status,
            "holiday_reason": bh.get(d),
            "attendance": att,
        })
    return result