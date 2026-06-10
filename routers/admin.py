import re
from datetime import datetime
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.db import get_db
from database.models import User, MonthlyDiary, AttendanceRecord, Holiday
from routers.auth import (
    get_current_user, admin_required, super_admin_required,
    permission_required, is_super_admin, ALL_ADMIN_PERMISSIONS, SUPER_ADMIN_STAFF_NO,
)
from config import settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/users")
def list_users(request: Request, db: Session = Depends(get_db), _=Depends(permission_required("users"))):
    user = get_current_user(request, db)
    users = db.query(User).order_by(User.staff_no).all()
    diary_counts = dict(
        db.query(MonthlyDiary.user_id, func.count(MonthlyDiary.id))
        .group_by(MonthlyDiary.user_id)
        .all()
    )
    for u in users:
        u.diary_count = diary_counts.get(u.id, 0)
    return templates.TemplateResponse("admin_users.html", {
        "request": request, "user": user, "users": users,
        "is_super_admin": is_super_admin(user),
    })


@router.get("/diaries")
def all_diaries(request: Request, staff: str = None, db: Session = Depends(get_db), _=Depends(permission_required("diaries"))):
    user = get_current_user(request, db)
    q = db.query(MonthlyDiary).join(User, MonthlyDiary.user_id == User.id)
    if staff:
        q = q.filter(User.staff_no == staff)
    diaries = q.order_by(User.staff_no, MonthlyDiary.year.desc(), MonthlyDiary.month.desc()).all()
    counts = dict(
        db.query(AttendanceRecord.diary_id, func.count(AttendanceRecord.id))
        .group_by(AttendanceRecord.diary_id)
        .all()
    )
    for d in diaries:
        d.record_count = counts.get(d.id, 0)
    user_count = db.query(func.count(func.distinct(MonthlyDiary.user_id))).scalar()
    return templates.TemplateResponse("admin_diaries.html", {
        "request": request, "user": user, "diaries": diaries, "user_count": user_count,
    })


@router.post("/toggle-admin/{user_id}")
def toggle_admin(user_id: int, request: Request, db: Session = Depends(get_db), _=Depends(super_admin_required)):
    """Only super admin can promote/demote admins."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404)
    if target.staff_no == SUPER_ADMIN_STAFF_NO:
        raise HTTPException(status_code=403, detail="Cannot demote super admin")
    target.is_admin = not target.is_admin
    if not target.is_admin:
        target.admin_permissions = ""
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)


@router.post("/toggle-active/{user_id}")
def toggle_active(user_id: int, request: Request, db: Session = Depends(get_db), _=Depends(permission_required("users"))):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404)
    if target.staff_no == SUPER_ADMIN_STAFF_NO:
        raise HTTPException(status_code=403, detail="Cannot deactivate super admin")
    target.is_active = not target.is_active
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)


@router.get("/links")
def list_links(request: Request, db: Session = Depends(get_db), _=Depends(permission_required("links"))):
    from services.firebase_service import list_all_user_links
    user = get_current_user(request, db)
    try:
        links = list_all_user_links()
    except Exception as e:
        return templates.TemplateResponse("admin_links.html", {
            "request": request, "user": user,
            "links": [], "error": f"Could not fetch links: {e}",
        })
    return templates.TemplateResponse("admin_links.html", {
        "request": request, "user": user,
        "links": links, "error": "",
    })


@router.post("/unlink/{google_uid}")
def unlink_user(google_uid: str, request: Request, db: Session = Depends(get_db), _=Depends(permission_required("links"))):
    from services.firebase_service import delete_user_link
    user = get_current_user(request, db)
    try:
        delete_user_link(google_uid)
    except Exception as e:
        return templates.TemplateResponse("admin_links.html", {
            "request": request, "user": user,
            "links": [], "error": f"Failed to unlink: {e}",
        })
    return RedirectResponse(url="/admin/links", status_code=302)


# ── User edit ─────────────────────────────────────────────────────────────────

_ALL_STATES = sorted(settings.CANARA_BANK_GSTIN.keys())


@router.get("/users/{user_id}/edit")
def edit_user_page(user_id: int, request: Request, db: Session = Depends(get_db), _=Depends(permission_required("users"))):
    admin = get_current_user(request, db)
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("admin_user_edit.html", {
        "request": request, "user": admin, "target": target,
        "all_states": _ALL_STATES, "error": "", "success": "",
        "all_permissions": ALL_ADMIN_PERMISSIONS,
        "is_super_admin": is_super_admin(admin),
        "target_perms": set(p.strip() for p in (target.admin_permissions or "").split(",") if p.strip()),
    })


@router.post("/users/{user_id}/edit")
def edit_user_save(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _=Depends(permission_required("users")),
    name: str = Form(""),
    staff_no: str = Form(""),
    mobile: str = Form(""),
    email: str = Form(""),
    designation: str = Form(""),
    designation_code: str = Form(""),
    dp_code: str = Form(""),
    section: str = Form(""),
    zone: str = Form(""),
    basic_pay: str = Form(""),
    home_state: str = Form(""),
    city_category: str = Form(""),
    address_line1: str = Form(""),
    address_line2: str = Form(""),
    city_pin: str = Form(""),
    bank_name: str = Form(""),
    bank_account_no: str = Form(""),
    ta_id: str = Form(""),
):
    admin = get_current_user(request, db)
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404)

    # staff_no uniqueness check
    if staff_no.strip() and staff_no.strip() != target.staff_no:
        conflict = db.query(User).filter(User.staff_no == staff_no.strip(), User.id != user_id).first()
        if conflict:
            return templates.TemplateResponse("admin_user_edit.html", {
                "request": request, "user": admin, "target": target,
                "all_states": _ALL_STATES,
                "error": f"Staff No {staff_no} already used by {conflict.name}.", "success": "",
            })

    if name.strip():
        target.name = name.strip()
    if staff_no.strip():
        target.staff_no = staff_no.strip()
    if mobile.strip():
        nm = re.sub(r'\D', '', mobile)
        if nm.startswith('91') and len(nm) == 12:
            nm = nm[2:]
        target.mobile = nm[-10:] if nm else target.mobile
    if email.strip():
        target.email = email.strip()
    target.designation = designation.strip() or None
    target.designation_code = designation_code.strip() or None
    target.dp_code = dp_code.strip() or None
    target.section = section.strip() or None
    target.zone = zone.strip() or None
    try:
        target.basic_pay = float(basic_pay) if basic_pay.strip() else target.basic_pay
    except ValueError:
        pass
    if home_state.strip():
        target.home_state = home_state.strip()
    if city_category.strip():
        target.city_category = city_category.strip()
    target.address_line1 = address_line1.strip() or None
    target.address_line2 = address_line2.strip() or None
    target.city_pin = city_pin.strip() or None
    target.bank_name = bank_name.strip() or None
    target.bank_account_no = bank_account_no.strip() or None
    target.ta_id = ta_id.strip() or None
    db.commit()
    db.refresh(target)

    return templates.TemplateResponse("admin_user_edit.html", {
        "request": request, "user": admin, "target": target,
        "all_states": _ALL_STATES, "error": "", "success": "User updated successfully.",
        "all_permissions": ALL_ADMIN_PERMISSIONS,
        "is_super_admin": is_super_admin(admin),
        "target_perms": set(p.strip() for p in (target.admin_permissions or "").split(",") if p.strip()),
    })


@router.post("/users/{user_id}/permissions")
def save_user_permissions(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _=Depends(super_admin_required),
    permissions: list[str] = Form(default=[]),
):
    """Super admin sets which permissions an admin user has."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404)
    if target.staff_no == SUPER_ADMIN_STAFF_NO:
        raise HTTPException(status_code=403, detail="Cannot restrict super admin")
    valid = set(ALL_ADMIN_PERMISSIONS)
    granted = [p for p in permissions if p in valid]
    target.admin_permissions = ",".join(granted)
    db.commit()
    db.refresh(target)
    admin = get_current_user(request, db)
    return templates.TemplateResponse("admin_user_edit.html", {
        "request": request, "user": admin, "target": target,
        "all_states": _ALL_STATES, "error": "", "success": "Permissions updated.",
        "all_permissions": ALL_ADMIN_PERMISSIONS,
        "is_super_admin": True,
        "target_perms": set(granted),
    })


# ── Admin holidays ─────────────────────────────────────────────────────────────

@router.get("/holidays")
def admin_holidays_page(request: Request, db: Session = Depends(get_db), _=Depends(permission_required("holidays"))):
    admin = get_current_user(request, db)
    holidays = db.query(Holiday).order_by(Holiday.holiday_date.desc()).limit(60).all()
    return templates.TemplateResponse("admin_holidays.html", {
        "request": request, "user": admin,
        "holidays": holidays, "all_states": _ALL_STATES,
        "error": "", "success": "",
    })


@router.post("/holidays/add")
def admin_add_holiday(
    request: Request,
    db: Session = Depends(get_db),
    _=Depends(permission_required("holidays")),
    holiday_date: str = Form(...),
    state: str = Form("Maharashtra"),
    description: str = Form(""),
    holiday_type: str = Form("public"),
    apply_to_attendance: str = Form("yes"),
):
    admin = get_current_user(request, db)

    try:
        d = datetime.strptime(holiday_date, "%Y-%m-%d").date()
    except ValueError:
        holidays = db.query(Holiday).order_by(Holiday.holiday_date.desc()).limit(60).all()
        return templates.TemplateResponse("admin_holidays.html", {
            "request": request, "user": admin,
            "holidays": holidays, "all_states": _ALL_STATES,
            "error": "Invalid date format.", "success": "",
        })

    existing = db.query(Holiday).filter(
        Holiday.holiday_date == d, Holiday.state == state
    ).first()
    if not existing:
        db.add(Holiday(
            holiday_date=d, state=state,
            description=description.strip(),
            holiday_type=holiday_type,
        ))
        db.commit()

    updated_count = 0
    if apply_to_attendance == "yes":
        rows = db.query(AttendanceRecord).filter(AttendanceRecord.duty_date == d).all()
        for rec in rows:
            rec.is_holiday = True
            rec.is_leave = False
            updated_count += 1
        if rows:
            db.commit()

    holidays = db.query(Holiday).order_by(Holiday.holiday_date.desc()).limit(60).all()
    msg = f"Holiday added for {state} on {d.strftime('%d %b %Y')}."
    if updated_count:
        msg += f" Marked {updated_count} attendance records as holiday."
    return templates.TemplateResponse("admin_holidays.html", {
        "request": request, "user": admin,
        "holidays": holidays, "all_states": _ALL_STATES,
        "error": "", "success": msg,
    })


@router.post("/holidays/delete/{holiday_id}")
def admin_delete_holiday(
    holiday_id: int, request: Request,
    db: Session = Depends(get_db), _=Depends(permission_required("holidays")),
):
    h = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if h:
        db.delete(h)
        db.commit()
    return RedirectResponse(url="/admin/holidays", status_code=302)
