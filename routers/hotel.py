from datetime import datetime, date
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import HotelStay, MonthlyDiary
from routers.auth import get_current_user, login_required
from config import settings, get_state_from_gstin, get_ha_rate

router = APIRouter(dependencies=[Depends(login_required)])
templates = Jinja2Templates(directory="templates")


def nights_between(checkin: date, checkout: date) -> int:
    return (checkout - checkin).days


@router.get("/list/{diary_id}")
def list_hotels(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)
    stays = db.query(HotelStay).filter(HotelStay.diary_id == diary_id, HotelStay.user_id == user.id).order_by(HotelStay.checkin_date.desc()).all()
    return templates.TemplateResponse("list_hotels.html", {
        "request": request, "user": user, "diary": diary, "stays": stays,
    })


@router.get("/add/{diary_id}")
def add_hotel_page(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("add_hotel.html", {
        "request": request, "user": user, "diary": diary,
        "hotel_gst_rates": settings.HOTEL_GST_RATES,
        "now": datetime.utcnow(),
    })


@router.post("/add/{diary_id}")
def add_hotel(
    request: Request, diary_id: int,
    checkin_date: str = Form(...), checkin_time: str = Form("12:00"),
    checkout_date: str = Form(...), checkout_time: str = Form("12:00"),
    city: str = Form(""), hotel_name: str = Form(""),
    hotel_type: str = Form("ThreeStar"),
    lodging_amount: float = Form(0.0), boarding_amount: float = Form(0.0),
    gst_percent: float = Form(0.0),
    vendor_gstin: str = Form(""), invoice_date: str = Form(""),
    invoice_number: str = Form(""), no_bill: bool = Form(False),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)

    ci = datetime.strptime(checkin_date, "%Y-%m-%d").date()
    co = datetime.strptime(checkout_date, "%Y-%m-%d").date()
    nights = nights_between(ci, co)
    total_lb = lodging_amount + boarding_amount
    gst = gst_percent if gst_percent > 0 else settings.HOTEL_GST_RATES.get(hotel_type, 12)
    claimed_gst = round(total_lb * gst / 100, 2)
    ha_rate = get_ha_rate(city)
    halting_allowance = nights * ha_rate
    total_claimed = total_lb + halting_allowance

    stay = HotelStay(
        user_id=user.id, diary_id=diary_id,
        checkin_date=ci, checkin_time=checkin_time,
        checkout_date=co, checkout_time=checkout_time,
        city=city, hotel_name=hotel_name, hotel_type=hotel_type,
        lodging_amount=lodging_amount, boarding_amount=boarding_amount,
        total_lb=total_lb, gst_percent=gst, claimed_gst=claimed_gst,
        vendor_gstin=vendor_gstin, vendor_state=get_state_from_gstin(vendor_gstin),
        bank_state=diary.bank_state, bank_gstin=diary.bank_gstin,
        invoice_date=datetime.strptime(invoice_date, "%Y-%m-%d").date() if invoice_date else None,
        invoice_number=invoice_number, no_bill=no_bill,
        halting_allowance=halting_allowance,
        total_claimed_exc_gst=total_claimed,
    )
    db.add(stay)
    db.commit()
    return RedirectResponse(url=f"/hotel/list/{diary_id}", status_code=302)


@router.get("/edit/{stay_id}")
def edit_hotel_page(request: Request, stay_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    stay = db.query(HotelStay).filter(HotelStay.id == stay_id, HotelStay.user_id == user.id).first()
    if not stay:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("edit_hotel.html", {
        "request": request, "user": user, "stay": stay,
        "hotel_gst_rates": settings.HOTEL_GST_RATES,
    })


@router.post("/edit/{stay_id}")
def edit_hotel(
    request: Request, stay_id: int,
    checkin_date: str = Form(...), checkin_time: str = Form("12:00"),
    checkout_date: str = Form(...), checkout_time: str = Form("12:00"),
    city: str = Form(""), hotel_name: str = Form(""),
    hotel_type: str = Form("ThreeStar"),
    lodging_amount: float = Form(0.0), boarding_amount: float = Form(0.0),
    gst_percent: float = Form(0.0),
    vendor_gstin: str = Form(""), invoice_date: str = Form(""),
    invoice_number: str = Form(""), no_bill: bool = Form(False),
    declaration_amount: float = Form(0.0), declaration_text: str = Form(""),
    sanctioned_amount: float = Form(0.0), sanctioned_gst: float = Form(0.0),
    remarks: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)

    stay = db.query(HotelStay).filter(HotelStay.id == stay_id, HotelStay.user_id == user.id).first()
    if not stay:
        raise HTTPException(status_code=404)

    ci = datetime.strptime(checkin_date, "%Y-%m-%d").date()
    co = datetime.strptime(checkout_date, "%Y-%m-%d").date()
    total_lb = lodging_amount + boarding_amount
    gst = gst_percent if gst_percent > 0 else settings.HOTEL_GST_RATES.get(hotel_type, 12)
    claimed_gst = round(total_lb * gst / 100, 2)
    ha_rate = get_ha_rate(city)
    halting_allowance = nights_between(ci, co) * ha_rate

    stay.checkin_date = ci; stay.checkin_time = checkin_time
    stay.checkout_date = co; stay.checkout_time = checkout_time
    stay.city = city; stay.hotel_name = hotel_name
    stay.hotel_type = hotel_type
    stay.lodging_amount = lodging_amount; stay.boarding_amount = boarding_amount
    stay.total_lb = total_lb; stay.gst_percent = gst; stay.claimed_gst = claimed_gst
    stay.vendor_gstin = vendor_gstin
    stay.vendor_state = get_state_from_gstin(vendor_gstin)
    stay.invoice_date = datetime.strptime(invoice_date, "%Y-%m-%d").date() if invoice_date else None
    stay.invoice_number = invoice_number; stay.no_bill = no_bill
    stay.halting_allowance = halting_allowance
    stay.total_claimed_exc_gst = total_lb + halting_allowance
    stay.declaration_amount = declaration_amount; stay.declaration_text = declaration_text
    stay.sanctioned_amount = sanctioned_amount; stay.sanctioned_gst = sanctioned_gst
    stay.remarks = remarks
    db.commit()
    return RedirectResponse(url=f"/hotel/list/{stay.diary_id}", status_code=302)


@router.post("/delete/{stay_id}")
def delete_hotel(stay_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    stay = db.query(HotelStay).filter(HotelStay.id == stay_id, HotelStay.user_id == user.id).first()
    if not stay:
        raise HTTPException(status_code=404)
    diary_id = stay.diary_id
    db.delete(stay)
    db.commit()
    return RedirectResponse(url=f"/hotel/list/{diary_id}", status_code=302)
