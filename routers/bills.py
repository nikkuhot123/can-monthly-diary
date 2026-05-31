import os
from datetime import timedelta
from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Bill, HotelStay, MonthlyDiary
from routers.auth import get_current_user, admin_required
from config import get_ha_rate, get_state_from_gstin, settings
from services.bill_parser import parse_hotel_bill
import aiofiles

router = APIRouter(dependencies=[Depends(admin_required)])
templates = Jinja2Templates(directory="templates")


def _create_hotel_stay_from_bill(db: Session, user, diary: MonthlyDiary, bill: Bill, parsed) -> bool:
    if not parsed.raw_text.strip():
        return False
    if not parsed.hotel_name or not (parsed.lodging_amount or parsed.total_amount):
        return False

    checkin_date = parsed.checkin_date or parsed.invoice_date
    if not checkin_date:
        return False

    checkout_date = parsed.checkout_date or (checkin_date + timedelta(days=1))
    if checkout_date <= checkin_date:
        checkout_date = checkin_date + timedelta(days=1)

    city = parsed.city or user.section or "NASHIK"
    hotel_name = parsed.hotel_name or "Hotel Bill"
    lodging_amount = parsed.lodging_amount or max(parsed.total_amount - parsed.gst_amount, 0.0)
    boarding_amount = parsed.boarding_amount or 0.0
    total_lb = lodging_amount + boarding_amount
    gst_percent = parsed.gst_percent
    if not gst_percent and total_lb and parsed.gst_amount:
        gst_percent = round(parsed.gst_amount * 100 / total_lb, 2)

    nights = max((checkout_date - checkin_date).days, 1)
    halting_allowance = nights * get_ha_rate(city)

    stay = HotelStay(
        user_id=user.id,
        diary_id=diary.id,
        bill_id=bill.id,
        checkin_date=checkin_date,
        checkin_time="12:00",
        checkout_date=checkout_date,
        checkout_time="12:00",
        city=city,
        hotel_name=hotel_name,
        hotel_type="FiveStar" if gst_percent >= 18 else "ThreeStar" if gst_percent >= 12 else "Budget",
        lodging_amount=lodging_amount,
        boarding_amount=boarding_amount,
        total_lb=total_lb,
        gst_percent=gst_percent or 0.0,
        claimed_gst=parsed.gst_amount or 0.0,
        vendor_gstin=parsed.vendor_gstin,
        vendor_state=get_state_from_gstin(parsed.vendor_gstin),
        bank_state=diary.bank_state,
        bank_gstin=diary.bank_gstin,
        invoice_date=parsed.invoice_date,
        invoice_number=parsed.invoice_number,
        no_bill=False,
        halting_allowance=halting_allowance,
        total_claimed_exc_gst=total_lb + halting_allowance,
    )
    db.add(stay)
    return True


@router.get("/upload/{diary_id}")
def upload_bill_page(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(
        MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id
    ).first()
    if not diary:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("upload_bill.html", {
        "request": request, "user": user, "diary": diary,
    })


@router.post("/upload/{diary_id}")
async def upload_bill(
    request: Request, diary_id: int,
    bill_category: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(
        MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id
    ).first()
    if not diary:
        raise HTTPException(status_code=404)

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "pdf"
    upload_dir = os.path.join(settings.UPLOAD_DIR, "bills")
    os.makedirs(upload_dir, exist_ok=True)

    fname = f"user_{user.id}_diary_{diary_id}_{file.filename}"
    fpath = os.path.join(upload_dir, fname)
    async with aiofiles.open(fpath, "wb") as f:
        content = await file.read()
        await f.write(content)

    bill = Bill(
        user_id=user.id, diary_id=diary_id,
        file_name=file.filename, file_path=fpath,
        file_type=ext, bill_category=bill_category,
    )
    db.add(bill)
    db.flush()

    if bill_category == "hotel":
        parsed = parse_hotel_bill(fpath, ext)
        bill.ocr_raw_text = parsed.raw_text
        bill.vendor_name = parsed.hotel_name
        bill.invoice_date = parsed.invoice_date
        bill.invoice_number = parsed.invoice_number
        bill.vendor_gstin = parsed.vendor_gstin
        bill.vendor_state = get_state_from_gstin(parsed.vendor_gstin)
        bill.amount_exc_gst = (parsed.lodging_amount or 0) + (parsed.boarding_amount or 0)
        bill.gst_amount = parsed.gst_amount
        bill.gst_percent = parsed.gst_percent
        bill.total_amount = parsed.total_amount or (bill.amount_exc_gst + bill.gst_amount)
        bill.is_verified = bool(parsed.raw_text.strip())
        bill.is_matched = _create_hotel_stay_from_bill(db, user, diary, bill, parsed)

    db.commit()
    db.refresh(bill)

    return RedirectResponse(url=f"/bills/list/{diary_id}", status_code=302)


@router.get("/list/{diary_id}")
def list_bills(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(
        MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id
    ).first()
    if not diary:
        raise HTTPException(status_code=404)
    bills = db.query(Bill).filter(
        Bill.diary_id == diary_id, Bill.user_id == user.id
    ).order_by(Bill.uploaded_at.desc()).all()
    return templates.TemplateResponse("list_bills.html", {
        "request": request, "user": user, "diary": diary, "bills": bills,
    })


@router.post("/delete/{bill_id}")
def delete_bill(bill_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    bill = db.query(Bill).filter(
        Bill.id == bill_id, Bill.user_id == user.id
    ).first()
    if not bill:
        raise HTTPException(status_code=404)
    diary_id = bill.diary_id
    if os.path.exists(bill.file_path):
        os.remove(bill.file_path)
    db.delete(bill)
    db.commit()
    return RedirectResponse(url=f"/bills/list/{diary_id}", status_code=302)
