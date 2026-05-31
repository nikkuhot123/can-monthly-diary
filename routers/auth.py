"""
Auth routes — Google-only login via Firebase.
Replaces old staff_no/password flow.

Routes:
  GET  /auth/login          — Login page with Google Sign-In button
  POST /auth/google-login   — Verify Firebase token, create JWT or return needs_setup
  GET  /auth/setup          — First-time setup form
  POST /auth/google-setup   — Link Google account to staff_no
  GET  /auth/logout         — Clear session
  GET  /auth/profile        — View profile
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from database.db import get_db
from database.models import User
from config import settings, FIREBASE, ADMIN_EMAILS

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Return User object from JWT cookie, or None."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except JWTError:
        return None


def login_required(request: Request, db: Session = Depends(get_db)):
    """Dependency: any authenticated user."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=302, detail="Login required")
    return user


def admin_required(request: Request, db: Session = Depends(get_db)):
    """Dependency: admin-only access. Checks SQLite user.is_admin field."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=302, detail="Login required")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/login")
def login_page(request: Request):
    """Show Google Sign-In login page."""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "firebase_config": {
            "apiKey": FIREBASE.get("api_key", ""),
            "authDomain": FIREBASE.get("auth_domain", ""),
            "projectId": FIREBASE.get("project_id", ""),
            "storageBucket": FIREBASE.get("storage_bucket", ""),
            "messagingSenderId": FIREBASE.get("messaging_sender_id", ""),
            "appId": FIREBASE.get("app_id", ""),
        },
    })


@router.post("/google-login")
def google_login(
    request: Request,
    id_token: str = Form(...),
    db: Session = Depends(get_db),
):
    """Verify Firebase ID token, create JWT session, or return needs_setup."""
    from services.firebase_service import verify_google_token, get_user_link

    try:
        decoded = verify_google_token(id_token)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=401)
    except RuntimeError as e:
        return JSONResponse({"error": "Service unavailable: Firebase not configured"}, status_code=503)

    google_uid = decoded["uid"]
    google_email = decoded.get("email", "")

    # Check if this Google account is already linked
    try:
        user_link = get_user_link(google_uid)
    except Exception as e:
        import traceback
        print(f"[WARN] Firestore get_user_link failed: {e}\n{traceback.format_exc()}")
        user_link = None

    if not user_link:
        # Firestore may have failed or this is a first-time login.
        # Try to find user by email in SQLite as fallback.
        sqlite_user = db.query(User).filter(User.email == google_email).first()
        if sqlite_user:
            # Email matched — log in directly without Firestore
            is_admin = google_email in (e.strip() for e in ADMIN_EMAILS) or sqlite_user.is_admin
            token = create_access_token({
                "user_id": sqlite_user.id,
                "staff_no": sqlite_user.staff_no,
                "is_admin": is_admin,
            })
            response = JSONResponse({"redirect": "/attendance/dashboard"})
            response.set_cookie(key="access_token", value=token, httponly=True, max_age=86400 * 30)
            return response

        # Genuine first-time login — redirect to setup
        temp_token = create_access_token({
            "google_uid": google_uid,
            "google_email": google_email,
            "temp_setup": True,
        })
        return JSONResponse({
            "needs_setup": True,
            "temp_token": temp_token,
            "email": google_email,
        })

    # User is linked — find SQLite user by staff_no
    sqlite_user = db.query(User).filter(User.staff_no == user_link["staff_no"]).first()
    if not sqlite_user:
        return JSONResponse({
            "error": "User account not found in system. Contact your administrator."
        }, status_code=404)

    # Create JWT session
    token = create_access_token({
        "user_id": sqlite_user.id,
        "staff_no": sqlite_user.staff_no,
        "is_admin": user_link.get("is_admin", False),
    })
    response = JSONResponse({"redirect": "/attendance/dashboard"})
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=86400 * 30)
    return response


@router.get("/setup")
def setup_page(request: Request):
    """Show account setup form for first-time Google login."""
    return templates.TemplateResponse("setup_account.html", {
        "request": request,
        "error": "",
        "email": request.query_params.get("email", ""),
    })


@router.post("/google-setup")
def google_setup(
    request: Request,
    temp_token: str = Form(...),
    staff_no: str = Form(...),
    mobile: str = Form(...),
    db: Session = Depends(get_db),
):
    """First-time setup: link Google account to staff_no.

    Flow:
    1. Decode temp_token to get Google identity
    2. Look up staff_no in SQLite
    3. If not found -> show error
    4. If found + mobile mismatch -> warning (allow proceed)
    5. Check email whitelist for admin status
    6. Save user_link to Firestore
    7. Update sqlite_user.is_admin if applicable
    8. Create JWT session, redirect
    """
    from services.firebase_service import save_user_link

    # Decode the temp token to get Google identity
    try:
        payload = jwt.decode(temp_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return templates.TemplateResponse("setup_account.html", {
            "request": request,
            "error": "Your setup session has expired. Please login again.",
            "email": "",
        })

    google_uid = payload.get("google_uid")
    google_email = payload.get("google_email", "")

    if not google_uid:
        return templates.TemplateResponse("setup_account.html", {
            "request": request,
            "error": "Setup session expired. Please login again.",
            "email": "",
        })

    # Lookup the staff_no in SQLite
    sqlite_user = db.query(User).filter(User.staff_no == staff_no).first()
    if not sqlite_user:
        return templates.TemplateResponse("setup_account.html", {
            "request": request,
            "error": f"Staff No {staff_no} not found. Contact your administrator.",
            "email": google_email,
        })

    # Determine admin status from configured whitelist
    is_admin = google_email in (email.strip() for email in ADMIN_EMAILS)

    # Update SQLite user is_admin if applicable
    if is_admin and not sqlite_user.is_admin:
        sqlite_user.is_admin = True
        db.commit()

    # Save user_link to Firestore — non-fatal if it fails
    try:
        save_user_link(google_uid, google_email, staff_no, mobile, is_admin)
    except Exception as e:
        import traceback
        print(f"[WARN] Firestore save_user_link failed: {e}\n{traceback.format_exc()}")
        # Proceed anyway — JWT session still works without Firestore link

    # Create JWT session
    token = create_access_token({
        "user_id": sqlite_user.id,
        "staff_no": sqlite_user.staff_no,
        "is_admin": is_admin,
    })
    response = RedirectResponse(url="/attendance/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=86400 * 30)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("access_token")
    return response


@router.get("/profile")
def profile_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    return templates.TemplateResponse("profile.html", {
        "request": request, "user": user
    })


@router.get("/profile/edit")
def profile_edit_page(request: Request, db: Session = Depends(get_db)):
    """Show profile edit form with personal detail fields."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    return templates.TemplateResponse("profile_edit.html", {
        "request": request, "user": user
    })


@router.post("/profile/edit")
def profile_edit_save(
    request: Request,
    db: Session = Depends(get_db),
    address_line1: str = Form(""),
    address_line2: str = Form(""),
    city_pin: str = Form(""),
    bank_name: str = Form(""),
    bank_account_no: str = Form(""),
    ta_id: str = Form(""),
):
    """Save personal detail fields to the user record."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")

    user.address_line1 = address_line1.strip() or None
    user.address_line2 = address_line2.strip() or None
    user.city_pin = city_pin.strip() or None
    user.bank_name = bank_name.strip() or None
    user.bank_account_no = bank_account_no.strip() or None
    user.ta_id = ta_id.strip() or None
    db.commit()

    return RedirectResponse(url="/auth/profile", status_code=302)


@router.post("/profile/clear-field")
def profile_clear_field(
    request: Request,
    db: Session = Depends(get_db),
    field: str = Form(...),
):
    """Clear a single personal detail field."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")

    allowed_fields = {"address_line1", "address_line2", "city_pin", "bank_name", "bank_account_no", "ta_id"}
    if field not in allowed_fields:
        return JSONResponse({"error": "Invalid field"}, status_code=400)

    setattr(user, field, None)
    db.commit()
    return RedirectResponse(url="/auth/profile", status_code=302)


@router.post("/profile/clear-all")
def profile_clear_all(request: Request, db: Session = Depends(get_db)):
    """Clear all personal detail fields."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")

    user.address_line1 = None
    user.address_line2 = None
    user.city_pin = None
    user.bank_name = None
    user.bank_account_no = None
    user.ta_id = None
    db.commit()

    return RedirectResponse(url="/auth/profile", status_code=302)
