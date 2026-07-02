import calendar
import traceback
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import User, MonthlyDiary, AttendanceRecord
from routers.auth import get_current_user, admin_required, permission_required
from services.whatsapp_parser import process_whatsapp_upload
from services.calendar_utils import get_bank_holidays_for_month, is_bank_holiday, get_bank_holiday_reason, build_month_calendar
from services.holiday_service import get_holiday

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_or_create_diary(db: Session, user_id: int, month: int, year: int,
                        bank_state: str = "Maharashtra"):
    diary = db.query(MonthlyDiary).filter(
        MonthlyDiary.user_id == user_id,
        MonthlyDiary.month == month,
        MonthlyDiary.year == year,
    ).first()
    if not diary:
        from config import get_bank_gstin
        diary = MonthlyDiary(
            user_id=user_id, month=month, year=year,
            bank_state=bank_state,
            bank_gstin=get_bank_gstin(bank_state),
            status="draft",
        )
        db.add(diary)
        db.commit()
        db.refresh(diary)
    return diary


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    now = datetime.utcnow()
    diaries = db.query(MonthlyDiary).filter(
        MonthlyDiary.user_id == user.id
    ).order_by(MonthlyDiary.year.desc(), MonthlyDiary.month.desc()).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "user": user, "diaries": diaries, "now": now,
    })


@router.post("/new-month")
def new_month(
    request: Request,
    month: int = Form(...),
    year: int = Form(...),
    bank_state: str = Form("Maharashtra"),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    diary = get_or_create_diary(db, user.id, month, year, bank_state)
    return RedirectResponse(url=f"/attendance/calendar?diary_id={diary.id}", status_code=302)


@router.get("/calendar")
def calendar_view(
    request: Request,
    diary_id: int = None,
    month: int = None,
    year: int = None,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")

    if diary_id:
        q = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id)
        if not user.is_admin:
            q = q.filter(MonthlyDiary.user_id == user.id)
        diary = q.first()
        if not diary:
            raise HTTPException(status_code=404, detail="Diary not found")
        month = diary.month
        year = diary.year
    else:
        if not month or not year:
            now = datetime.utcnow()
            month = now.month
            year = now.year
        diary = get_or_create_diary(db, user.id, month, year)

    _, days_in_month = calendar.monthrange(year, month)
    # Convert Mon=0 (Python) to Sun=0 (calendar template column order)
    first_weekday = (calendar.weekday(year, month, 1) + 1) % 7

    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.diary_id == diary.id
    ).all()

    # Ensure dates are date objects (sometimes SQLite returns them as strings if not handled by ORM properly)
    record_map = {}
    attendance_map = {}
    for r in records:
        d = r.duty_date
        if isinstance(d, str):
            from datetime import date
            d = date.fromisoformat(d)
        record_map[d] = r
        attendance_map[d] = {
            "is_leave": r.is_leave,
            "is_holiday": r.is_holiday,
            "is_weekend": r.is_weekend,
            "needs_review": r.needs_review,
            "branch_name": r.branch_name,
            "audit_type": r.audit_type,
        }

    bh = get_bank_holidays_for_month(year, month)
    day_rows = build_month_calendar(year, month, attendance_map)

    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weeks = []
    week = [None] * first_weekday
    for row in day_rows:
        d = row["date"]
        att = row["attendance"]
        status = row["status"]
        reason = row["holiday_reason"]

        if status == "sunday" or status == "bank_holiday" or status == "public_holiday" or status == "manual_holiday":
            css_class = "cell-holiday"
            day_type = "Holiday" if status == "manual_holiday" else status.replace("_", " ").title()
        elif status == "leave":
            css_class = "cell-leave"
            day_type = "Leave"
        elif status == "present":
            css_class = "cell-present" if not (att and att.get("needs_review")) else "cell-review"
            day_type = "Review" if (att and att.get("needs_review")) else "Present"
        else:
            css_class = "cell-missing"
            day_type = "Missing"

        week.append({
            "day": d.day, "record": record_map.get(d),
            "css": css_class, "date": d,
            "holiday": reason, "day_type": day_type,
        })
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        week.extend([None] * (7 - len(week)))
        weeks.append(week)

    return templates.TemplateResponse("calendar.html", {
        "request": request, "user": user, "diary": diary,
        "month": month, "year": year,
        "month_name": calendar.month_name[month],
        "weeks": weeks, "days_in_month": days_in_month,
    })


@router.get("/upload-whatsapp")
def upload_whatsapp_page(
    request: Request, diary_id: int,
    db: Session = Depends(get_db),
    _=Depends(permission_required("whatsapp")),
):
    user = get_current_user(request, db)
    diary = db.query(MonthlyDiary).filter(
        MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id
    ).first()
    if not diary:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("upload_whatsapp.html", {
        "request": request, "user": user, "diary": diary,
    })


@router.post("/upload-whatsapp")
async def upload_whatsapp(
    request: Request,
    diary_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(permission_required("whatsapp")),
):
    user = get_current_user(request, db)
    diary = db.query(MonthlyDiary).filter(
        MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id
    ).first()
    if not diary:
        raise HTTPException(status_code=404)

    content = await file.read()
    text = content.decode("utf-8", errors="ignore")

    try:
        result = process_whatsapp_upload(
            db, user.id, diary.id, text,
            staff_no=user.staff_no,
            mobile_no=user.mobile or "",
            name_keywords=[user.name, user.staff_no],
        )
    except Exception as exc:
        db.rollback()
        print("WhatsApp upload failed:")
        print(traceback.format_exc())
        return templates.TemplateResponse("upload_whatsapp.html", {
            "request": request, "user": user, "diary": diary,
            "error": f"Could not import this WhatsApp file: {exc}",
        })

    return templates.TemplateResponse("upload_whatsapp.html", {
        "request": request, "user": user, "diary": diary, "result": result,
    })


@router.get("/edit/{record_id}")
def edit_attendance(request: Request, record_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.id == record_id, AttendanceRecord.user_id == user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("edit_attendance.html", {
        "request": request, "user": user, "record": record,
        "error": request.query_params.get("error")
    })


@router.post("/edit/{record_id}")
def update_attendance(
    request: Request, record_id: int,
    duty_date: str = Form(...),
    branch_name: str = Form(""),
    dp_code: str = Form(""),
    audit_type: str = Form(""),
    place: str = Form(""),
    mandays_sanctioned: int = Form(0),
    mandays_pending: int = Form(0),
    mandays_utilised: int = Form(0),
    executive_mandays: int = Form(0),
    is_holiday: bool = Form(False),
    is_leave: bool = Form(False),
    duty_from_time: str = Form("09:00"),
    duty_to_time: str = Form("18:00"),
    db: Session = Depends(get_db),
):
    try:
        user = get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/auth/login")
        
        record = db.query(AttendanceRecord).filter(
            AttendanceRecord.id == record_id, AttendanceRecord.user_id == user.id
        ).first()
        if not record:
            raise HTTPException(status_code=404)

        diary_id = record.diary_id
        diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id).first()
        
        try:
            duty_date_obj = datetime.strptime(duty_date, "%Y-%m-%d").date()
        except ValueError:
            duty_date_obj = datetime.strptime(duty_date[:10], "%Y-%m-%d").date()

        # Update fields
        record.duty_date = duty_date_obj
        record.branch_name = branch_name
        record.dp_code = dp_code
        record.audit_type = audit_type
        record.place = place
        record.mandays_sanctioned = mandays_sanctioned
        record.mandays_pending = mandays_pending
        record.mandays_utilised = mandays_utilised
        record.executive_mandays = executive_mandays
        record.is_leave = is_leave
        record.duty_from_time = duty_from_time
        record.duty_to_time = duty_to_time
        
        # Recalculate holiday status
        if diary and diary.bank_state:
            holiday = get_holiday(db, duty_date_obj, diary.bank_state)
            record.is_holiday = is_holiday or (holiday is not None)
        else:
            record.is_holiday = is_holiday

        record.needs_review = False
        record.review_note = ""
        
        db.commit()
        return RedirectResponse(url=f"/attendance/calendar?diary_id={diary_id}", status_code=302)
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "UNIQUE constraint failed" in error_msg:
            return RedirectResponse(
                url=f"/attendance/edit/{record_id}?error=A+record+already+exists+for+this+date.+Please+delete+or+change+the+other+record+first.",
                status_code=302
            )
        import traceback
        tb = traceback.format_exc()
        print(f"Error in update_attendance: {tb}")
        return HTMLResponse(content=f"<h3>Error saving record: {error_msg}</h3><pre>{tb}</pre>", status_code=500)


@router.get("/add/{diary_id}")
def add_attendance_page(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    diary = db.query(MonthlyDiary).filter(
        MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id
    ).first()
    if not diary:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("add_attendance.html", {
        "request": request, "user": user, "diary": diary,
        "error": request.query_params.get("error"),
        "prefill_date": request.query_params.get("date", ""),
    })


@router.post("/add/{diary_id}")
def add_attendance(
    request: Request, diary_id: int,
    duty_date: str = Form(...),
    branch_name: str = Form(""),
    dp_code: str = Form(""),
    audit_type: str = Form(""),
    place: str = Form(""),
    mandays_sanctioned: int = Form(0),
    mandays_pending: int = Form(0),
    mandays_utilised: int = Form(0),
    executive_mandays: int = Form(0),
    is_holiday: bool = Form(False),
    is_leave: bool = Form(False),
    duty_from_time: str = Form("09:00"),
    duty_to_time: str = Form("18:00"),
    db: Session = Depends(get_db),
):
    try:
        user = get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/auth/login")

        diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id).first()
        duty_date_obj = datetime.strptime(duty_date, "%Y-%m-%d").date()
        
        holiday = get_holiday(db, duty_date_obj, diary.bank_state) if diary else None
        actual_is_holiday = is_holiday or (holiday is not None)

        record = AttendanceRecord(
            user_id=user.id, diary_id=diary_id,
            duty_date=duty_date_obj,
            branch_name=branch_name, dp_code=dp_code,
            audit_type=audit_type, place=place,
            mandays_sanctioned=mandays_sanctioned,
            mandays_pending=mandays_pending,
            mandays_utilised=mandays_utilised,
            executive_mandays=executive_mandays,
            is_holiday=actual_is_holiday, is_leave=is_leave,
            duty_from_time=duty_from_time, duty_to_time=duty_to_time,
            source="manual",
        )
        db.add(record)
        db.commit()
        return RedirectResponse(url=f"/attendance/calendar?diary_id={diary_id}", status_code=302)
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "UNIQUE constraint failed" in error_msg:
            return RedirectResponse(
                url=f"/attendance/add/{diary_id}?error=A+record+already+exists+for+this+date.",
                status_code=302
            )
        return HTMLResponse(content=f"<h3>Error adding record: {error_msg}</h3>", status_code=500)


@router.post("/delete/{record_id}")
def delete_attendance(
    record_id: int, request: Request,
    db: Session = Depends(get_db),
    _=Depends(permission_required("users")),
):
    user = get_current_user(request, db)
    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.id == record_id, AttendanceRecord.user_id == user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404)
    diary_id = record.diary_id
    db.delete(record)
    db.commit()
    return RedirectResponse(url=f"/attendance/calendar?diary_id={diary_id}", status_code=302)


@router.get("/edit-diary/{diary_id}")
def edit_diary_page(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    diary = db.query(MonthlyDiary).filter(
        MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id
    ).first()
    if not diary:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("edit_diary.html", {
        "request": request, "user": user, "diary": diary,
        "now": datetime.utcnow(),
    })


@router.post("/edit-diary/{diary_id}")
def edit_diary(
    request: Request, diary_id: int,
    month: int = Form(...),
    year: int = Form(...),
    bank_state: str = Form("Maharashtra"),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    diary = db.query(MonthlyDiary).filter(
        MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id
    ).first()
    if not diary:
        raise HTTPException(status_code=404)

    from config import get_bank_gstin
    diary.month = month
    diary.year = year
    diary.bank_state = bank_state
    diary.bank_gstin = get_bank_gstin(bank_state)
    db.commit()
    return RedirectResponse(url="/attendance/dashboard", status_code=302)


@router.post("/compute-leaves/{diary_id}")
def compute_leaves(
    diary_id: int, request: Request,
    db: Session = Depends(get_db),
    _=Depends(permission_required("whatsapp")),
):
    user = get_current_user(request, db)
    diary = db.query(MonthlyDiary).filter(
        MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id
    ).first()
    if not diary:
        raise HTTPException(status_code=404)

    from calendar import monthrange
    from services.calendar_utils import is_bank_holiday

    existing_dates = {r.duty_date for r in db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == user.id,
        AttendanceRecord.diary_id == diary_id,
    ).all()}

    _, dim = monthrange(diary.year, diary.month)
    filled = 0
    for day_num in range(1, dim + 1):
        d = date(diary.year, diary.month, day_num)
        if d in existing_dates:
            continue
        if d.weekday() >= 5:
            continue
        if is_bank_holiday(d):
            continue
        db.add(AttendanceRecord(
            user_id=user.id, diary_id=diary_id,
            duty_date=d, source="auto",
            is_leave=True, needs_review=False,
        ))
        filled += 1

    db.commit()
    return RedirectResponse(
        url=f"/attendance/calendar?diary_id={diary_id}&success=Leaves+computed:+{filled}",
        status_code=302,
    )


@router.post("/delete-diary/{diary_id}")
def delete_diary(diary_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    diary = db.query(MonthlyDiary).filter(
        MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id
    ).first()
    if not diary:
        raise HTTPException(status_code=404)
    db.delete(diary)
    db.commit()
    return RedirectResponse(url="/attendance/dashboard", status_code=302)
