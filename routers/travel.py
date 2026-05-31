from datetime import datetime
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import TravelLeg, MonthlyDiary
from routers.auth import get_current_user, admin_required
from config import settings, get_state_from_gstin

router = APIRouter(dependencies=[Depends(admin_required)])
templates = Jinja2Templates(directory="templates")


@router.get("/list/{diary_id}")
def list_travel(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)
    legs = db.query(TravelLeg).filter(TravelLeg.diary_id == diary_id, TravelLeg.user_id == user.id).order_by(TravelLeg.date_start.desc()).all()
    return templates.TemplateResponse("list_travel.html", {
        "request": request, "user": user, "diary": diary, "legs": legs,
    })


@router.get("/add/{diary_id}")
def add_travel_page(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("add_travel.html", {
        "request": request, "user": user, "diary": diary,
        "gst_rates": settings.GST_RATES, "now": datetime.utcnow(),
    })


@router.post("/add/{diary_id}")
def add_travel(
    request: Request, diary_id: int,
    from_place: str = Form(...), to_place: str = Form(...),
    date_start: str = Form(...), time_start: str = Form(""),
    date_arrival: str = Form(""), time_arrival: str = Form(""),
    mode: str = Form("Train"), travel_class: str = Form(""),
    distance_km: float = Form(0.0),
    claimed_amount_exc_gst: float = Form(0.0),
    gst_percent: float = Form(0.0),
    vendor_gstin: str = Form(""), ticket_no: str = Form(""),
    invoice_date: str = Form(""), invoice_number: str = Form(""),
    no_bill: bool = Form(False),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)

    gst = gst_percent if gst_percent > 0 else settings.GST_RATES.get(mode, 0)
    claimed_gst = round(claimed_amount_exc_gst * gst / 100, 2)
    total_amount = claimed_amount_exc_gst + claimed_gst
    vendor_state = get_state_from_gstin(vendor_gstin)

    leg = TravelLeg(
        user_id=user.id, diary_id=diary_id,
        from_place=from_place, to_place=to_place,
        date_start=datetime.strptime(date_start, "%Y-%m-%d").date(),
        time_start=time_start,
        date_arrival=datetime.strptime(date_arrival, "%Y-%m-%d").date() if date_arrival else None,
        time_arrival=time_arrival,
        mode=mode, travel_class=travel_class,
        distance_km=distance_km,
        claimed_amount_exc_gst=claimed_amount_exc_gst,
        gst_percent=gst, claimed_gst=claimed_gst,
        non_taxable=0.0, total_amount=total_amount,
        vendor_gstin=vendor_gstin, vendor_state=vendor_state,
        bank_state=diary.bank_state, bank_gstin=diary.bank_gstin,
        ticket_no=ticket_no,
        invoice_date=datetime.strptime(invoice_date, "%Y-%m-%d").date() if invoice_date else None,
        invoice_number=invoice_number, no_bill=no_bill,
    )
    db.add(leg)
    db.commit()
    return RedirectResponse(url=f"/travel/list/{diary_id}", status_code=302)


@router.get("/edit/{leg_id}")
def edit_travel_page(request: Request, leg_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    leg = db.query(TravelLeg).filter(TravelLeg.id == leg_id, TravelLeg.user_id == user.id).first()
    if not leg:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("edit_travel.html", {
        "request": request, "user": user, "leg": leg,
        "gst_rates": settings.GST_RATES,
    })


@router.post("/edit/{leg_id}")
def edit_travel(
    request: Request, leg_id: int,
    from_place: str = Form(...), to_place: str = Form(...),
    date_start: str = Form(...), time_start: str = Form(""),
    date_arrival: str = Form(""), time_arrival: str = Form(""),
    mode: str = Form("Train"), travel_class: str = Form(""),
    distance_km: float = Form(0.0),
    claimed_amount_exc_gst: float = Form(0.0),
    gst_percent: float = Form(0.0),
    vendor_gstin: str = Form(""), ticket_no: str = Form(""),
    invoice_date: str = Form(""), invoice_number: str = Form(""),
    no_bill: bool = Form(False),
    sanctioned_amount_exc_gst: float = Form(0.0),
    sanctioned_gst: float = Form(0.0),
    remarks: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)

    leg = db.query(TravelLeg).filter(TravelLeg.id == leg_id, TravelLeg.user_id == user.id).first()
    if not leg:
        raise HTTPException(status_code=404)

    gst = gst_percent if gst_percent > 0 else settings.GST_RATES.get(mode, 0)
    claimed_gst = round(claimed_amount_exc_gst * gst / 100, 2)
    total_amount = claimed_amount_exc_gst + claimed_gst

    leg.from_place = from_place; leg.to_place = to_place
    leg.date_start = datetime.strptime(date_start, "%Y-%m-%d").date()
    leg.time_start = time_start
    leg.date_arrival = datetime.strptime(date_arrival, "%Y-%m-%d").date() if date_arrival else None
    leg.time_arrival = time_arrival
    leg.mode = mode; leg.travel_class = travel_class
    leg.distance_km = distance_km
    leg.claimed_amount_exc_gst = claimed_amount_exc_gst
    leg.gst_percent = gst; leg.claimed_gst = claimed_gst
    leg.total_amount = total_amount
    leg.vendor_gstin = vendor_gstin
    leg.vendor_state = get_state_from_gstin(vendor_gstin)
    leg.ticket_no = ticket_no
    leg.invoice_date = datetime.strptime(invoice_date, "%Y-%m-%d").date() if invoice_date else None
    leg.invoice_number = invoice_number
    leg.no_bill = no_bill
    leg.sanctioned_amount_exc_gst = sanctioned_amount_exc_gst
    leg.sanctioned_gst = sanctioned_gst
    leg.amount_approved = sanctioned_amount_exc_gst + sanctioned_gst if sanctioned_amount_exc_gst else 0
    leg.remarks = remarks
    db.commit()
    return RedirectResponse(url=f"/travel/list/{leg.diary_id}", status_code=302)


@router.post("/delete/{leg_id}")
def delete_travel(leg_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    leg = db.query(TravelLeg).filter(TravelLeg.id == leg_id, TravelLeg.user_id == user.id).first()
    if not leg:
        raise HTTPException(status_code=404)
    diary_id = leg.diary_id
    db.delete(leg)
    db.commit()
    return RedirectResponse(url=f"/travel/list/{diary_id}", status_code=302)
