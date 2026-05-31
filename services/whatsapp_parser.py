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
    "staff_no": [
        r"staff\s*(?:no|number|id)[\s\-:.]+(\d{5,7})",
        r"emp(?:loyee)?\s*(?:no|number|id|code)[\s\-:.]+(\d{5,7})",
        r"s\.?\s*no[\s\-:.]+(\d{5,7})",
        r"staff[\s\-:.]+(\d{5,7})",
    ],
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
        r"mandays\s+remaining[\s\-:]+(\d+)",
    ],
    "mandays_utilised": [
        r"mandays\s+utilis(?:ed|e)[\s\-:]+(\d+)",
        r"running\s+mandays[\s\-:]+(\d+)",
        r"mandays\s+used[\s\-:]+(\d+)",
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


def strip_formatting(text: str) -> str:
    """Remove WhatsApp bold/italic markers (*text*, _text_) so they don't block regex."""
    return re.sub(r'[*_~`]', '', text)


def extract_date_field(text: str) -> Optional[date]:
    clean = strip_formatting(text)
    for pat in DATE_FIELD_PATTERNS:
        m = re.search(pat, clean, re.IGNORECASE | re.MULTILINE)
        if m:
            d = parse_date_string(m.group(1))
            if d:
                return d
    return None


def extract_field(text: str, field_key: str) -> Optional[str]:
    text = strip_formatting(text)
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


NAME_FROM_BODY_PATTERNS = [
    r"name\s+of\s+io[\s\-:]+(.+?)(?=\n|staff|branch|dp|$)",
    r"name[\s\-:]+(.+?)(?=\n|staff|branch|dp|$)",
    r"io\s+name[\s\-:]+(.+?)(?=\n|staff|branch|dp|$)",
]


def extract_name_from_body(text: str) -> str:
    """Extract IO/employee name from message body for auto-create labelling."""
    clean = strip_formatting(text)
    for pat in NAME_FROM_BODY_PATTERNS:
        m = re.search(pat, clean, re.IGNORECASE)
        if m:
            name = m.group(1).strip().rstrip('.,;')
            if name and len(name) <= 80:
                return name
    return ""


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

        # WhatsApp format: "SENDER: message_body\nmore_body"
        # The sender and message start may be on the same line separated by ": "
        sender_name = ""
        sender_mobile = ""
        body = content

        colon_idx = content.find(": ")
        if colon_idx != -1:
            potential_sender = content[:colon_idx].strip()
            rest_body = content[colon_idx + 2:].strip()
            # Sender should be short (no colons inside, reasonable length)
            if potential_sender and "\n" not in potential_sender and len(potential_sender) <= 80:
                phone_m = re.match(r"^\+?91[\s\-]?\d[\d\s]{8,11}$", potential_sender)
                if phone_m:
                    sender_mobile = normalize_mobile(potential_sender)
                    body = rest_body
                else:
                    sender_name = potential_sender
                    body = rest_body

        # Fallback: if body is empty, use full content
        if not body:
            body = content

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
    from sqlalchemy import cast, Integer, func
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

    # 3. Resolve each message to a User (per-message, not per-sender-group)
    #    Priority: staff_no in body > sender mobile > sender name > auto-create
    _cache_by_staff:  Dict[str, Optional["User"]] = {}
    _cache_by_mobile: Dict[str, Optional["User"]] = {}
    _cache_by_name:   Dict[str, Optional["User"]] = {}
    _autocreated:     Dict[str, "User"] = {}  # sender_key -> auto-created User

    def _resolve_user(msg: Dict) -> Optional["User"]:
        body_text = msg.get("body", "") + " " + msg.get("full_text", "")
        sender_mobile = msg.get("sender_mobile", "")
        sender_name   = msg.get("sender_name", "")

        # PRIMARY: explicit staff_no / employee_id field in message body
        for pat in FIELD_PATTERNS["staff_no"]:
            m_sno = re.search(pat, body_text, re.IGNORECASE)
            if m_sno:
                sno = m_sno.group(1)
                if sno not in _cache_by_staff:
                    _cache_by_staff[sno] = db.query(User).filter(User.staff_no == sno).first()
                if _cache_by_staff[sno]:
                    return _cache_by_staff[sno]

        # SECONDARY: sender mobile number
        if sender_mobile:
            norm = normalize_mobile(sender_mobile)
            if norm not in _cache_by_mobile:
                _cache_by_mobile[norm] = db.query(User).filter(
                    User.mobile.like(f"%{norm}")
                ).first()
            if _cache_by_mobile[norm]:
                return _cache_by_mobile[norm]

        # TERTIARY: sender name
        if sender_name:
            words = [w.lower() for w in re.split(r'[\s,/:;]+', sender_name)
                     if len(w) > 2 and w.lower() not in ('the', 'for', 'and', 'with', 'from', 'this', 'that')]
            for word in words:
                if word not in _cache_by_name:
                    _cache_by_name[word] = db.query(User).filter(
                        func.lower(User.name).contains(word)
                    ).first()
                if _cache_by_name[word]:
                    return _cache_by_name[word]

        # AUTO-CREATE: use mobile as unique key if no name, extract name from body
        # Covers phone-number senders whose staff_no/mobile isn't in DB yet
        display_name = sender_name or extract_name_from_body(body_text) or sender_mobile
        if not display_name:
            return None

        autocreate_key = sender_mobile if sender_mobile else display_name.strip().lower()
        if autocreate_key not in _autocreated:
            max_staff = db.query(func.max(cast(User.staff_no, Integer))).scalar()
            new_staff_no = str((max_staff + 1) if max_staff else 900001)
            new_user = User(
                staff_no=new_staff_no,
                name=display_name,
                mobile=sender_mobile or "",
                hashed_password="AUTO_CREATED_WHATSAPP_USER",
                is_active=True,
                is_admin=False,
            )
            db.add(new_user)
            db.flush()
            _autocreated[autocreate_key] = new_user
            if sender_name:
                words = [w.lower() for w in re.split(r'[\s,/:;]+', sender_name)
                         if len(w) > 2 and w.lower() not in ('the', 'for', 'and', 'with', 'from', 'this', 'that')]
                for word in words:
                    _cache_by_name[word] = new_user
            if sender_mobile:
                _cache_by_mobile[normalize_mobile(sender_mobile)] = new_user
        return _autocreated[autocreate_key]

    # 4. Group resolved messages by user_id
    user_msgs: Dict[int, List[Dict]] = {}
    user_map:  Dict[int, "User"]     = {}
    autocreated_ids: set             = set()

    for msg in all_messages:
        u = _resolve_user(msg)
        if not u:
            continue
        user_msgs.setdefault(u.id, []).append(msg)
        user_map[u.id] = u

    for ac_user in _autocreated.values():
        autocreated_ids.add(ac_user.id)

    total_new = 0
    total_duplicates = 0
    total_leaves = 0
    total_review = 0
    total_month_mismatch = 0
    results_by_user: Dict[int, dict] = {}
    processed_diaries: Dict[int, set] = {}  # diary_id -> set of existing dates

    # 5. Process each user's messages
    for uid, msgs in user_msgs.items():
        target_user = user_map[uid]
        sender_mobile = msgs[0].get("sender_mobile", "")
        sender_name   = msgs[0].get("sender_name", "")

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

        if target_user.id not in results_by_user:
            results_by_user[target_user.id] = {
                "user_name": target_user.name,
                "staff_no": target_user.staff_no,
                "new": 0,
                "duplicates": 0,
                "leaves": 0,
                "needs_review": 0,
                "auto_created": target_user.id in autocreated_ids,
            }
        results_by_user[target_user.id]["new"] += user_new
        results_by_user[target_user.id]["duplicates"] += user_duplicates
        results_by_user[target_user.id]["leaves"] += user_leaves_filled
        results_by_user[target_user.id]["needs_review"] += user_review

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
