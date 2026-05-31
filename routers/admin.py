from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import User, MonthlyDiary
from routers.auth import get_current_user, admin_required

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/users")
def list_users(request: Request, db: Session = Depends(get_db), _=Depends(admin_required)):
    user = get_current_user(request, db)
    users = db.query(User).order_by(User.name).all()
    return templates.TemplateResponse("admin_users.html", {
        "request": request, "user": user, "users": users,
    })


@router.get("/diaries")
def all_diaries(request: Request, db: Session = Depends(get_db), _=Depends(admin_required)):
    user = get_current_user(request, db)
    diaries = db.query(MonthlyDiary).order_by(MonthlyDiary.year.desc(), MonthlyDiary.month.desc()).all()
    return templates.TemplateResponse("admin_diaries.html", {
        "request": request, "user": user, "diaries": diaries,
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
