import os
import calendar
from datetime import datetime
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import MonthlyDiary, AttendanceRecord, TravelLeg, HotelStay, LocalConveyance, OtherExpense
from routers.auth import get_current_user
from config import settings
from generators.diary_excel import generate_diary_excel
from generators.hrms_excel import generate_hrms_excel

router = APIRouter()
templates = Jinja2Templates(directory="templates")
NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}


@router.get("/preview/{diary_id}")
def preview_diary(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)

    attendance = db.query(AttendanceRecord).filter(AttendanceRecord.diary_id == diary_id).order_by(AttendanceRecord.duty_date).all()
    travel = db.query(TravelLeg).filter(TravelLeg.diary_id == diary_id).order_by(TravelLeg.date_start).all()
    hotels = db.query(HotelStay).filter(HotelStay.diary_id == diary_id).order_by(HotelStay.checkin_date).all()
    local = db.query(LocalConveyance).filter(LocalConveyance.diary_id == diary_id).order_by(LocalConveyance.travel_date).all()
    other = db.query(OtherExpense).filter(OtherExpense.diary_id == diary_id).order_by(OtherExpense.created_at).all()

    return templates.TemplateResponse("preview_diary.html", {
        "request": request, "user": user, "diary": diary,
        "attendance": attendance, "travel": travel,
        "hotels": hotels, "local": local, "other": other,
        "month_name": calendar.month_name[diary.month] if diary.month else "",
        "now": datetime.utcnow(),
    })


@router.get("/download-excel/{diary_id}")
def download_diary_excel(diary_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)

    attendance = db.query(AttendanceRecord).filter(AttendanceRecord.diary_id == diary_id).order_by(AttendanceRecord.duty_date).all()
    travel = db.query(TravelLeg).filter(TravelLeg.diary_id == diary_id).order_by(TravelLeg.date_start).all()
    hotels = db.query(HotelStay).filter(HotelStay.diary_id == diary_id).order_by(HotelStay.checkin_date).all()
    local = db.query(LocalConveyance).filter(LocalConveyance.diary_id == diary_id).order_by(LocalConveyance.travel_date).all()
    other = db.query(OtherExpense).filter(OtherExpense.diary_id == diary_id).order_by(OtherExpense.created_at).all()

    output_dir = os.path.join(settings.UPLOAD_DIR, "generated", "diary_excel")
    os.makedirs(output_dir, exist_ok=True)
    fname = f"TA_Diary_{user.staff_no}_{diary.month}_{diary.year}.xlsx"
    fpath = os.path.join(output_dir, fname)

    generate_diary_excel(fpath, user, diary, attendance, travel, hotels, local, other)
    return FileResponse(fpath, filename=fname, headers=NO_CACHE_HEADERS)


@router.get("/download-hrms/{diary_id}")
def download_hrms_excel(diary_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)

    travel = db.query(TravelLeg).filter(TravelLeg.diary_id == diary_id).order_by(TravelLeg.date_start).all()
    hotels = db.query(HotelStay).filter(HotelStay.diary_id == diary_id).order_by(HotelStay.checkin_date).all()
    local = db.query(LocalConveyance).filter(LocalConveyance.diary_id == diary_id).order_by(LocalConveyance.travel_date).all()
    other = db.query(OtherExpense).filter(OtherExpense.diary_id == diary_id).order_by(OtherExpense.created_at).all()
    attendance = db.query(AttendanceRecord).filter(AttendanceRecord.diary_id == diary_id).order_by(AttendanceRecord.duty_date).all()

    output_dir = os.path.join(settings.UPLOAD_DIR, "generated", "hrms_excel")
    os.makedirs(output_dir, exist_ok=True)
    fname = f"HRMS_Bill_{user.staff_no}_{diary.month}_{diary.year}.xlsx"
    fpath = os.path.join(output_dir, fname)

    generate_hrms_excel(fpath, user, diary, travel, hotels, local, other, attendance)
    return FileResponse(fpath, filename=fname, headers=NO_CACHE_HEADERS)


@router.post("/submit/{diary_id}")
def submit_diary(diary_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")
    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)

    travel = db.query(TravelLeg).filter(TravelLeg.diary_id == diary_id).all()
    hotels = db.query(HotelStay).filter(HotelStay.diary_id == diary_id).all()
    local = db.query(LocalConveyance).filter(LocalConveyance.diary_id == diary_id).all()
    other = db.query(OtherExpense).filter(OtherExpense.diary_id == diary_id).all()

    diary.total_fare = sum(t.total_amount or 0 for t in travel)
    diary.total_lodging = sum(h.total_lb or 0 for h in hotels)
    diary.total_halting = sum(h.halting_allowance or 0 for h in hotels)
    diary.total_local = sum(l.claimed_amount_exc_gst + (l.claimed_gst or 0) for l in local)
    diary.total_other = sum(o.claimed_amount_exc_gst + (o.claimed_gst or 0) for o in other)
    diary.total_gst = sum(t.claimed_gst or 0 for t in travel) + sum(h.claimed_gst or 0 for h in hotels) + sum(l.claimed_gst or 0 for l in local) + sum(o.claimed_gst or 0 for o in other)
    diary.grand_total = sum(t.total_amount or 0 for t in travel) + sum(h.total_lb or 0 for h in hotels) + sum(h.halting_allowance or 0 for h in hotels) + sum(l.claimed_amount_exc_gst + (l.claimed_gst or 0) for l in local) + sum(o.claimed_amount_exc_gst + (o.claimed_gst or 0) for o in other)
    diary.status = "submitted"
    db.commit()

    return RedirectResponse(url=f"/generate/preview/{diary_id}", status_code=302)
