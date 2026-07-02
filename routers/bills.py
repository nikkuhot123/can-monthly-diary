import os
from datetime import timedelta, date
from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Bill, HotelStay, MonthlyDiary, TravelLeg, LocalConveyance, OtherExpense
from routers.auth import get_current_user, login_required
from config import get_ha_rate, get_state_from_gstin, settings
from services.bill_parser import parse_bill
import aiofiles

router = APIRouter(dependencies=[Depends(login_required)])
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


def _create_travel_leg_from_bill(db: Session, user, diary: MonthlyDiary, bill: Bill, parsed) -> bool:
    if not parsed.raw_text.strip():
        return False
    
    travel_date = parsed.invoice_date or parsed.checkin_date or date.today()
    from_place = parsed.city or "MUMBAI"
    to_place = "NASHIK"
    
    raw_lower = parsed.raw_text.lower()
    if "railway" in raw_lower or "irctc" in raw_lower or "train" in raw_lower:
        mode = "Train"
        travel_class = "AC III"
    elif "flight" in raw_lower or "indigo" in raw_lower or "boarding pass" in raw_lower or "air" in raw_lower:
        mode = "Flight"
        travel_class = "Economy"
    else:
        mode = "Bus"
        travel_class = "Regular"

    claimed_amount_exc_gst = max(parsed.total_amount - parsed.gst_amount, 0.0)
    
    leg = TravelLeg(
        user_id=user.id,
        diary_id=diary.id,
        bill_id=bill.id,
        from_place=from_place,
        to_place=to_place,
        date_start=travel_date,
        time_start="10:00",
        date_arrival=travel_date,
        time_arrival="14:00",
        mode=mode,
        travel_class=travel_class,
        distance_km=0.0,
        claimed_amount_exc_gst=claimed_amount_exc_gst,
        gst_percent=parsed.gst_percent,
        claimed_gst=parsed.gst_amount,
        non_taxable=0.0,
        total_amount=parsed.total_amount,
        vendor_state=get_state_from_gstin(parsed.vendor_gstin),
        vendor_gstin=parsed.vendor_gstin,
        bank_state=diary.bank_state,
        bank_gstin=diary.bank_gstin,
        ticket_no=parsed.invoice_number or "AUTO",
        invoice_date=parsed.invoice_date,
        invoice_number=parsed.invoice_number,
        no_bill=False,
        sanctioned_amount_exc_gst=claimed_amount_exc_gst,
        sanctioned_gst=parsed.gst_amount,
        amount_approved=parsed.total_amount,
    )
    db.add(leg)
    return True


def _create_local_conveyance_from_bill(db: Session, user, diary: MonthlyDiary, bill: Bill, parsed) -> bool:
    if not parsed.raw_text.strip():
        return False
    
    travel_date = parsed.invoice_date or parsed.checkin_date or date.today()
    from_place = parsed.city or "Local"
    
    raw_lower = parsed.raw_text.lower()
    if "taxi" in raw_lower or "cab" in raw_lower or "uber" in raw_lower or "ola" in raw_lower:
        mode = "Taxi"
    else:
        mode = "Auto"

    amount_exc_gst = max(parsed.total_amount - parsed.gst_amount, 0.0)
    
    item = LocalConveyance(
        user_id=user.id,
        diary_id=diary.id,
        bill_id=bill.id,
        travel_date=travel_date,
        from_place=from_place,
        to_place="Local",
        mode=mode,
        amount=amount_exc_gst,
        gst_percent=parsed.gst_percent,
        gst_amount=parsed.gst_amount,
        total_amount=parsed.total_amount,
        vendor_gstin=parsed.vendor_gstin,
        vendor_state=get_state_from_gstin(parsed.vendor_gstin),
        bank_state=diary.bank_state,
        bank_gstin=diary.bank_gstin,
        invoice_date=parsed.invoice_date,
        invoice_number=parsed.invoice_number,
        no_bill=False,
        sanctioned_amount=amount_exc_gst,
        sanctioned_gst=parsed.gst_amount,
    )
    db.add(item)
    return True


def _create_other_expense_from_bill(db: Session, user, diary: MonthlyDiary, bill: Bill, parsed) -> bool:
    if not parsed.raw_text.strip():
        return False
    
    expense_description = parsed.hotel_name or "Miscellaneous Expense"
    amount_exc_gst = max(parsed.total_amount - parsed.gst_amount, 0.0)
    
    item = OtherExpense(
        user_id=user.id,
        diary_id=diary.id,
        bill_id=bill.id,
        expense_description=expense_description,
        claimed_amount_exc_gst=amount_exc_gst,
        gst_percent=parsed.gst_percent,
        claimed_gst=parsed.gst_amount,
        total_amount=parsed.total_amount,
        vendor_gstin=parsed.vendor_gstin,
        vendor_state=get_state_from_gstin(parsed.vendor_gstin),
        bank_state=diary.bank_state,
        bank_gstin=diary.bank_gstin,
        invoice_date=parsed.invoice_date,
        invoice_number=parsed.invoice_number,
        no_bill=False,
        sanctioned_amount=amount_exc_gst,
        sanctioned_gst=parsed.gst_amount,
    )
    db.add(item)
    return True
@router.post("/upload/{diary_id}")
async def upload_bill(
    request: Request, diary_id: int,
    bill_category: str = Form("auto"),
    file: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(
        MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id
    ).first()
    if not diary:
        raise HTTPException(status_code=404)

    warnings_list = []
    for upload_file in file:
        if not upload_file.filename:
            continue

        ext = upload_file.filename.rsplit(".", 1)[-1].lower() if "." in upload_file.filename else "pdf"
        upload_dir = os.path.join(settings.UPLOAD_DIR, "bills")
        os.makedirs(upload_dir, exist_ok=True)

        fname = f"user_{user.id}_diary_{diary_id}_{upload_file.filename}"
        fpath = os.path.join(upload_dir, fname)
        async with aiofiles.open(fpath, "wb") as out_file:
            content = await upload_file.read()
            await out_file.write(content)

        # Parse using generalized bill parser (runs pre-processing, OCR, and classification)
        parsed = parse_bill(fpath, ext)

        if parsed.warnings:
            warnings_list.extend(parsed.warnings)

        # Use auto-detected category if 'auto' was chosen
        category = parsed.category if bill_category == "auto" else bill_category

        # Create the Bill record in the DB
        bill = Bill(
            user_id=user.id,
            diary_id=diary_id,
            file_name=upload_file.filename,
            file_path=fpath,
            file_type=ext,
            bill_category=category,
            ocr_raw_text=parsed.raw_text,
            vendor_name=parsed.hotel_name,
            invoice_date=parsed.invoice_date,
            invoice_number=parsed.invoice_number,
            vendor_gstin=parsed.vendor_gstin,
            vendor_state=get_state_from_gstin(parsed.vendor_gstin),
            amount_exc_gst=parsed.lodging_amount + parsed.boarding_amount if category == "hotel" else max(parsed.total_amount - parsed.gst_amount, 0.0),
            gst_amount=parsed.gst_amount,
            gst_percent=parsed.gst_percent,
            total_amount=parsed.total_amount or (parsed.lodging_amount + parsed.boarding_amount + parsed.gst_amount),
            is_verified=bool(parsed.raw_text.strip()),
        )
        db.add(bill)
        db.flush()  # Generate DB ID

        # Auto-match / create the corresponding expense logs
        if category == "hotel":
            bill.is_matched = _create_hotel_stay_from_bill(db, user, diary, bill, parsed)
        elif category == "travel":
            bill.is_matched = _create_travel_leg_from_bill(db, user, diary, bill, parsed)
        elif category == "local":
            bill.is_matched = _create_local_conveyance_from_bill(db, user, diary, bill, parsed)
        else:  # other
            bill.is_matched = _create_other_expense_from_bill(db, user, diary, bill, parsed)

    db.commit()
    return RedirectResponse(url=f"/bills/list/{diary_id}", status_code=302)


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
