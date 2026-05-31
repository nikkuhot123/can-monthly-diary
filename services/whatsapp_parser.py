"""
WhatsApp Chat Parser — Audit Diary System
==========================================
Primary identification: Staff No + Mobile Number
Rule: Only process messages that contain a Date field.
No auto-prefill. Every missing day stays MISSING for manual entry.
"""
import re
from datetime import date, datetime
from typing import List, Dict, Optional


DATE_FIELD_PATTERNS = [
    r"\bdate[\s\-:]+(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})",
    r"dt\.\s*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})",
    r"dated[\s\-:]+(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})",
]

FIELD_PATTERNS = {
    "branch_name": [
        r"branch\s+name[\s\-:]+(.+?)(?=\n|dp\s*code|type\s*of\s*audit|manday|executive|$)",
    ],
    "dp_code": [
        r"dp\s*code[\s\-:]+(\w+)",
        r"dpcode[\s\-:]+(\w+)",
    ],
    "audit_type": [
        r"type\s+of\s+audit[\s\-:]+(.+?)(?=\n|date|manday|commencement|$)",
        r"audit\s+type[\s\-:]+(.+?)(?=\n|date|manday|$)",
    ],
    "mandays_sanctioned": [
        r"mandays\s+sanction(?:ed)?[\s\-:]+(\d+)",
    ],
    "mandays_pending": [
        r"mandays\s+pending[\s\-:]+(\d+)",
    ],
    "mandays_utilised": [
        r"mandays\s+utilis(?:ed|e)[\s\-:]+(\d+)",
        r"running\s+mandays[\s\-:]+(\d+)",
    ],
    "executive_mandays": [
        r"executive\s+mandays[\s\-:]+(\d+)",
    ],
    "commencement_date": [
        r"(?:date\s+of\s+commencement|commencement\s+date)[\s\-:]+(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})",
    ],
}

LEAVE_KEYWORDS = [
    "unable to attend", "kindly grant me leave", "kindly permit",
    "on approved leave", "self sickness", "personal exigency",
    "medical exigency", "not feeling well", "am on leave",
    "grant me leave", "consider my leave", "leave for today",
    "leave for the day", "sick leave", "cannot attend",
    "family exigency", "on joining leave",
]

SKIP_PATTERNS = [
    r"^(media omitted|this message was deleted|this message was edited)",
    r"^(good night|good evening|ok sir|noted|thank you)$",
    r"(https://maps|maps\.google)",
    r"^rip\b", r"^om shanti", r"^very sad",
]


def parse_date_string(date_str: str) -> Optional[date]:
    date_str = date_str.strip()
    for fmt in ["%d.%m.%Y", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%y", "%d-%m-%y", "%d/%m/%y"]:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    if re.match(r"^\d{8}$", date_str):
        try:
            return datetime.strptime(date_str, "%d%m%Y").date()
        except ValueError:
            pass
    return None


def extract_date_field(text: str) -> Optional[date]:
    for pat in DATE_FIELD_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE | re.MULTILINE)
        if m:
            d = parse_date_string(m.group(1))
            if d:
                return d
    return None


def extract_field(text: str, field_key: str) -> Optional[str]:
    for pat in FIELD_PATTERNS.get(field_key, []):
        m = re.search(pat, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if m:
            v = m.group(1).strip()
            if v.upper() in ("NA", "TBD", "NIL", "N/A", ""):
                return None
            if field_key in ("mandays_sanctioned", "mandays_pending",
                             "mandays_utilised", "executive_mandays"):
                n = re.search(r"\d+", v)
                return n.group(0) if n else None
            return re.split(r"\n", v)[0].strip()
    return None


def is_leave_message(text: str) -> bool:
    return any(kw in text.lower() for kw in LEAVE_KEYWORDS)


def should_skip(text: str) -> bool:
    t = text.strip().lower()
    for p in SKIP_PATTERNS:
        if re.search(p, t):
            return True
    return False


def normalize_mobile(mobile: str) -> str:
    digits = re.sub(r"\D", "", mobile)
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    return digits[-10:] if len(digits) >= 10 else digits


def split_messages(raw_text: str) -> List[Dict]:
    messages = []
    # Robust regex for Android/iOS formats
    pattern = re.compile(
        r"(?:\[?(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?\s*(?:[apAP][mM])?)\]?\s*[-:]?\s*)(.*?)(?=\[?\d{1,2}[./-]\d{1,2}[./-]\d{2,4},\s*\d{1,2}:\d{2}|$)",
        re.DOTALL
    )
    for m in pattern.finditer(raw_text):
        msg_date = parse_date_string(m.group(1))
        if not msg_date:
            continue

        content = m.group(3).strip()
        lines = content.split("\n", 1)
        sender_line = lines[0].strip() if lines else ""
        body = lines[1].strip() if len(lines) > 1 else ""

        if not body:
            body = sender_line
            sender_line = ""

        phone_m = re.match(r"^\s*\+?91[\s\-]?\d[\d\s]{8,11}$", sender_line.strip())
        if phone_m:
            sender_mobile = normalize_mobile(sender_line.strip())
            sender_name = ""
        else:
            sender_mobile = ""
            sender_name = sender_line

        messages.append({
            "msg_date": msg_date,
            "sender_name": sender_name,
            "sender_mobile": sender_mobile,
            "body": body,
            "full_text": content,
        })
    return messages


def match_user_messages(
    messages: List[Dict],
    staff_no: str,
    mobile_no: str,
    name_keywords: List[str],
) -> List[Dict]:
    matched = []
    mobile_norm = normalize_mobile(mobile_no) if mobile_no else ""
    name_lower = [k.lower() for k in name_keywords]

    for msg in messages:
        body = msg["body"]
        sender_name_lower = msg["sender_name"].lower()

        if staff_no and staff_no in body:
            matched.append(msg)
            continue
        if mobile_norm and msg["sender_mobile"] == mobile_norm:
            matched.append(msg)
            continue
        if any(kw in sender_name_lower for kw in name_lower):
            matched.append(msg)
            continue

    return matched


def parse_attendance_record(msg: Dict) -> Optional[Dict]:
    full_text = msg["full_text"]

    duty_date = extract_date_field(full_text)
    if not duty_date:
        return None

    if should_skip(msg["body"]) and not extract_field(full_text, "branch_name"):
        return None

    on_leave = is_leave_message(full_text)

    rec = {
        "duty_date": duty_date,
        "is_leave": on_leave,
        "is_holiday": False,
        "is_weekend": False,
        "branch_name": "",
        "dp_code": "",
        "audit_type": "",
        "place": "",
        "mandays_sanctioned": 0,
        "mandays_pending": 0,
        "mandays_utilised": 0,
        "executive_mandays": 0,
        "date_of_commencement": None,
        "needs_review": False,
        "review_note": "",
        "source": "whatsapp",
        "raw_message": full_text,
    }

    rec["branch_name"]  = extract_field(full_text, "branch_name") or ""
    rec["dp_code"]       = extract_field(full_text, "dp_code") or ""
    rec["audit_type"]    = extract_field(full_text, "audit_type") or ""
    rec["mandays_sanctioned"] = int(extract_field(full_text, "mandays_sanctioned") or "0")
    rec["mandays_pending"]     = int(extract_field(full_text, "mandays_pending") or "0")
    rec["mandays_utilised"]    = int(extract_field(full_text, "mandays_utilised") or "0")
    rec["executive_mandays"]   = int(extract_field(full_text, "executive_mandays") or "0")

    cdate = extract_field(full_text, "commencement_date")
    if cdate:
        rec["date_of_commencement"] = parse_date_string(cdate)

    if not on_leave:
        if not rec["branch_name"]:
            rec["needs_review"] = True
            rec["review_note"] = "Missing: Branch Name"
        elif not rec["dp_code"]:
            rec["needs_review"] = True
            rec["review_note"] = "Missing: DP Code"

    return rec


def parse_whatsapp_message(text: str, staff_no: str, mobile_no: str = "",
                           name_keywords: List[str] = None) -> List[Dict]:
    if name_keywords is None:
        name_keywords = []

    all_messages = split_messages(text)
    user_messages = match_user_messages(all_messages, staff_no, mobile_no, name_keywords)

    records = []
    for msg in user_messages:
        parsed = parse_attendance_record(msg)
        if parsed:
            records.append(parsed)

    return records


def process_whatsapp_upload(
    db, user_id: int, diary_id: int, file_content: str,
    staff_no: str, mobile_no: str = "", name_keywords: List[str] = None,
) -> dict:
    from database.models import MonthlyDiary, AttendanceRecord
    from services.calendar_utils import is_bank_holiday, get_bank_holiday_reason

    if name_keywords is None:
        name_keywords = []

    parsed = parse_whatsapp_message(file_content, staff_no, mobile_no, name_keywords)
    new_count = 0
    duplicate_count = 0
    leave_count = 0
    review_count = 0
    month_mismatch_count = 0

    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id).first()
    if not diary:
        return {"total": 0, "new": 0, "duplicates": 0, "month_mismatch": 0,
                "leaves_detected": 0, "leaves_filled": 0}

    # Fetch existing dates into a set for fast lookup
    existing_dates = {r.duty_date for r in db.query(AttendanceRecord).filter(
        AttendanceRecord.diary_id == diary_id,
    ).all()}

    for data in parsed:
        duty_date = data.get("duty_date")
        if not duty_date:
            continue
        if duty_date.year != diary.year or duty_date.month != diary.month:
            month_mismatch_count += 1
            continue
        if duty_date in existing_dates:
            duplicate_count += 1
            continue

        bh_reason = get_bank_holiday_reason(duty_date)
        wd = duty_date.weekday()

        record = AttendanceRecord(
            user_id=user_id, diary_id=diary_id, duty_date=duty_date,
            branch_name=data.get("branch_name", ""),
            dp_code=data.get("dp_code", ""),
            audit_type=data.get("audit_type", ""),
            place=data.get("place", ""),
            mandays_sanctioned=data.get("mandays_sanctioned", 0),
            mandays_pending=data.get("mandays_pending", 0),
            mandays_utilised=data.get("mandays_utilised", 0),
            executive_mandays=data.get("executive_mandays", 0),
            date_of_commencement=data.get("date_of_commencement"),
            is_holiday=(bh_reason is not None),
            is_leave=data.get("is_leave", False),  # Respect the detected leave status
            is_weekend=(wd >= 5 and bh_reason is None),
            source="whatsapp",
            raw_message=data.get("raw_message", ""),
            is_duplicate=False,
            needs_review=data.get("needs_review", False),
            review_note=data.get("review_note", ""),
        )
        db.add(record)
        existing_dates.add(duty_date)
        new_count += 1
        if record.is_leave:
            leave_count += 1
        if record.needs_review:
            review_count += 1

    leaves_filled = 0
    from calendar import monthrange
    _, dim = monthrange(diary.year, diary.month)
    for day_num in range(1, dim + 1):
        d = date(diary.year, diary.month, day_num)
        if d in existing_dates:
            continue
        if is_bank_holiday(d):
            continue
        if d.weekday() >= 5:  # Skip Saturdays and Sundays
            continue
        db.add(AttendanceRecord(
            user_id=user_id, diary_id=diary_id, duty_date=d,
            source="auto", is_leave=True, needs_review=False,
        ))
        existing_dates.add(d)
        leaves_filled += 1

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "total": len(parsed),
        "new": new_count,
        "duplicates": duplicate_count,
        "month_mismatch": month_mismatch_count,
        "needs_review": review_count,
        "leaves_detected": leave_count,
        "leaves_filled": leaves_filled,
    }
