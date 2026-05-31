from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.db import get_db
from database.models import User, MonthlyDiary, AttendanceRecord
from routers.auth import get_current_user, admin_required

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/users")
def list_users(request: Request, db: Session = Depends(get_db), _=Depends(admin_required)):
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
    })


@router.get("/diaries")
def all_diaries(request: Request, staff: str = None, db: Session = Depends(get_db), _=Depends(admin_required)):
    user = get_current_user(request, db)
    q = db.query(MonthlyDiary).join(User, MonthlyDiary.user_id == User.id)
    if staff:
        q = q.filter(User.staff_no == staff)
    diaries = q.order_by(User.staff_no, MonthlyDiary.year.desc(), MonthlyDiary.month.desc()).all()
    # Attach record counts
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
def toggle_admin(user_id: int, request: Request, db: Session = Depends(get_db), _=Depends(admin_required)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404)
    target.is_admin = not target.is_admin
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)


@router.post("/toggle-active/{user_id}")
def toggle_active(user_id: int, request: Request, db: Session = Depends(get_db), _=Depends(admin_required)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404)
    target.is_active = not target.is_active
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)


@router.get("/links")
def list_links(request: Request, db: Session = Depends(get_db), _=Depends(admin_required)):
    """View all Google account links stored in Firestore."""
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
def unlink_user(google_uid: str, request: Request, db: Session = Depends(get_db), _=Depends(admin_required)):
    """Remove a Google account link from Firestore."""
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
