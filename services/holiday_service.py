from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from database.models import Holiday


def get_holiday(db: Session, d: date, state: str) -> Optional[Holiday]:
    return db.query(Holiday).filter(
        Holiday.holiday_date == d,
        Holiday.state == state,
    ).first()


def get_holidays_for_month(db: Session, year: int, month: int, state: str) -> list[Holiday]:
    from calendar import monthrange
    first = date(year, month, 1)
    last = date(year, month, monthrange(year, month)[1])
    return db.query(Holiday).filter(
        Holiday.holiday_date >= first,
        Holiday.holiday_date <= last,
        Holiday.state == state,
    ).all()


def get_holiday_description(db: Session, d: date, state: str) -> Optional[str]:
    h = get_holiday(db, d, state)
    return h.description if h else None


def get_saturday_ordinal(d: date) -> int:
    """Return which Saturday of the month: 1,2,3,4,5 or 0 if not Saturday"""
    if d.weekday() != 5:
        return 0
    count = 0
    for day in range(1, d.day + 1):
        if date(d.year, d.month, day).weekday() == 5:
            count += 1
    return count


def is_bank_holiday(d: date, db: Session = None, state: str = "") -> bool:
    """Check if date is a bank holiday (2nd/4th Saturday or seeded holiday)"""
    sat_ord = get_saturday_ordinal(d)
    if sat_ord in (2, 4):
        return True
    if db and state:
        return get_holiday(db, d, state) is not None
    return False


def get_bank_holiday_description(d: date, db: Session = None, state: str = "") -> Optional[str]:
    """Get description of bank holiday"""
    sat_ord = get_saturday_ordinal(d)
    if sat_ord in (2, 4):
        return "2nd Saturday" if sat_ord == 2 else "4th Saturday"
    if db and state:
        h = get_holiday(db, d, state)
        if h:
            return h.description
    return None
