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

        # FALLBACK: For single-line format "Name: message" or "- Name: message",
        # sender_line is empty and body contains the full line. Try to extract sender.
        if not sender_line and not sender_mobile and body:
            colon_match = re.match(r"^\s*(?:[-–—]+\s*)?(.+?)\s*:\s*", body)
            if colon_match:
                potential = colon_match.group(1).strip()
                # Remove leading dash/space
                potential = re.sub(r"^[-–—]+\s*", "", potential).strip()
                if potential:
                    # Check if it's a phone number
                    phone_check = re.match(r"^\s*\+?91[\s\-]?\d[\d\s]{8,11}$", potential)
                    if phone_check:
                        sender_mobile = normalize_mobile(potential)
                        sender_name = ""
                    else:
                        sender_name = potential
                        # Remove sender prefix from body
                        body = body[colon_match.end():].strip()

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
    from database.models import User, MonthlyDiary, AttendanceRecord
    from services.calendar_utils import is_bank_holiday, get_bank_holiday_reason
    from sqlalchemy import func
    from calendar import monthrange

    # 1. Parse ALL messages from the WhatsApp chat
    all_messages = split_messages(file_content)
    if not all_messages:
        return {"total_messages": 0, "total_new": 0, "total_duplicates": 0,
                "total_leaves": 0, "total_review": 0, "total_users": 0,
                "results_by_user": {}}

    # 2. Get the admin's diary to know target month/year/bank_state
    admin_diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id).first()
    if not admin_diary:
        return {"total_messages": 0, "total_new": 0, "total_duplicates": 0,
                "total_leaves": 0, "total_review": 0, "total_users": 0,
                "results_by_user": {}}

    target_month = admin_diary.month
    target_year = admin_diary.year

    # 3. Group messages by sender
    sender_groups: Dict[str, List[Dict]] = {}
    for msg in all_messages:
        sender_key = msg.get("sender_name") or msg.get("sender_mobile") or "unknown"
        sender_groups.setdefault(sender_key, []).append(msg)

    total_new = 0
    total_duplicates = 0
    total_leaves = 0
    total_review = 0
    total_month_mismatch = 0
    results_by_user: Dict[str, dict] = {}
    processed_diaries: Dict[int, set] = {}  # diary_id -> set of existing dates

    # 4. Process each sender group
    for sender_key, msgs in sender_groups.items():
        # Try to find a matching User in DB
        target_user = None
        sample = msgs[0]
        sender_mobile = sample.get("sender_mobile", "")
        sender_name = sample.get("sender_name", "")

        # PRIMARY: Match by staff_no found in message bodies
        all_text = " ".join(
            m.get("body", "") + " " + m.get("full_text", "")
            for m in msgs[:100]  # Check first 100 messages
        )
        found_staffs = set(re.findall(r'\b(\d{6})\b', all_text))
        for sid in sorted(found_staffs):
            target_user = db.query(User).filter(User.staff_no == sid).first()
            if target_user:
                break

        # SECONDARY: Match by mobile number
        if not target_user and sender_mobile:
            norm_mobile = normalize_mobile(sender_mobile)
            if norm_mobile:
                target_user = db.query(User).filter(
                    User.mobile.like(f"%{norm_mobile}")
                ).first()

        # TERTIARY: Match by name tokens
        if not target_user and sender_name:
            sender_words = [w.lower() for w in re.split(r'[\s,/:;]+', sender_name)
                           if len(w) > 2 and w.lower() not in ('the', 'for', 'and', 'with', 'from', 'this', 'that')]
            for word in sender_words:
                target_user = db.query(User).filter(
                    func.lower(User.name).contains(word)
                ).first()
                if target_user:
                    break

        # Skip senders who don't match any User
        if not target_user:
            continue

        # Get or create MonthlyDiary for this user
        target_diary = db.query(MonthlyDiary).filter(
            MonthlyDiary.user_id == target_user.id,
            MonthlyDiary.month == target_month,
            MonthlyDiary.year == target_year,
        ).first()
        if not target_diary:
            target_diary = MonthlyDiary(
                user_id=target_user.id,
                month=target_month,
                year=target_year,
                bank_state=admin_diary.bank_state,
                bank_gstin=admin_diary.bank_gstin,
                status="draft",
            )
            db.add(target_diary)
            db.flush()

        # Get existing dates for this diary
        if target_diary.id not in processed_diaries:
            existing_dates = {r.duty_date for r in db.query(AttendanceRecord).filter(
                AttendanceRecord.diary_id == target_diary.id,
            ).all()}
            processed_diaries[target_diary.id] = existing_dates
        existing_dates = processed_diaries[target_diary.id]

        user_new = 0
        user_duplicates = 0
        user_leaves = 0
        user_review = 0

        # Parse each message in the group
        for msg in msgs:
            parsed = parse_attendance_record(msg)
            if not parsed:
                continue

            duty_date = parsed.get("duty_date")
            if not duty_date:
                continue

            # Skip dates outside the target month/year
            if duty_date.year != target_year or duty_date.month != target_month:
                total_month_mismatch += 1
                continue

            # Skip duplicates
            if duty_date in existing_dates:
                total_duplicates += 1
                user_duplicates += 1
                continue

            bh_reason = get_bank_holiday_reason(duty_date)
            wd = duty_date.weekday()

            record = AttendanceRecord(
                user_id=target_user.id,
                diary_id=target_diary.id,
                duty_date=duty_date,
                branch_name=parsed.get("branch_name", ""),
                dp_code=parsed.get("dp_code", ""),
                audit_type=parsed.get("audit_type", ""),
                place=parsed.get("place", ""),
                mandays_sanctioned=parsed.get("mandays_sanctioned", 0),
                mandays_pending=parsed.get("mandays_pending", 0),
                mandays_utilised=parsed.get("mandays_utilised", 0),
                executive_mandays=parsed.get("executive_mandays", 0),
                date_of_commencement=parsed.get("date_of_commencement"),
                is_holiday=(bh_reason is not None),
                is_leave=parsed.get("is_leave", False),
                is_weekend=(wd >= 5 and bh_reason is None),
                source="whatsapp",
                raw_message=parsed.get("raw_message", ""),
                is_duplicate=False,
                needs_review=parsed.get("needs_review", False),
                review_note=parsed.get("review_note", ""),
            )
            db.add(record)
            existing_dates.add(duty_date)
            total_new += 1
            user_new += 1
            if record.is_leave:
                total_leaves += 1
                user_leaves += 1
            if record.needs_review:
                total_review += 1
                user_review += 1

        # Fill missing weekdays as leave for this user's diary
        user_leaves_filled = 0
        _, dim = monthrange(target_year, target_month)
        for day_num in range(1, dim + 1):
            d = date(target_year, target_month, day_num)
            if d in existing_dates:
                continue
            if is_bank_holiday(d):
                continue
            if d.weekday() >= 5:
                continue
            db.add(AttendanceRecord(
                user_id=target_user.id,
                diary_id=target_diary.id,
                duty_date=d,
                source="auto",
                is_leave=True,
                needs_review=False,
            ))
            existing_dates.add(d)
            total_leaves += 1
            user_leaves_filled += 1

        results_by_user[sender_key] = {
            "user_name": target_user.name,
            "staff_no": target_user.staff_no,
            "new": user_new,
            "duplicates": user_duplicates,
            "leaves": user_leaves_filled,
            "needs_review": user_review,
        }

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "total_messages": len(all_messages),
        "total_new": total_new,
        "total_duplicates": total_duplicates,
        "total_leaves": total_leaves,
        "total_review": total_review,
        "total_users": len(results_by_user),
        "results_by_user": results_by_user,
    }
