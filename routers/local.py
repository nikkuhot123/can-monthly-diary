from datetime import datetime
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import LocalConveyance, MonthlyDiary
from routers.auth import get_current_user, admin_required
from config import settings, get_state_from_gstin

router = APIRouter(dependencies=[Depends(admin_required)])
templates = Jinja2Templates(directory="templates")


@router.get("/list/{diary_id}")
def list_local(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)
    items = db.query(LocalConveyance).filter(LocalConveyance.diary_id == diary_id, LocalConveyance.user_id == user.id).order_by(LocalConveyance.travel_date.desc()).all()
    return templates.TemplateResponse("list_local.html", {
        "request": request, "user": user, "diary": diary, "items": items,
    })


@router.get("/add/{diary_id}")
def add_local_page(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("add_local.html", {
        "request": request, "user": user, "diary": diary,
        "gst_rates": settings.GST_RATES, "now": datetime.utcnow(),
    })


@router.post("/add/{diary_id}")
def add_local(
    request: Request, diary_id: int,
    travel_date: str = Form(...),
    from_place: str = Form(...), to_place: str = Form(...),
    mode: str = Form("Taxi"), distance_km: float = Form(0.0),
    claimed_amount_exc_gst: float = Form(0.0),
    gst_percent: float = Form(0.0),
    vendor_gstin: str = Form(""),
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

    item = LocalConveyance(
        user_id=user.id, diary_id=diary_id,
        travel_date=datetime.strptime(travel_date, "%Y-%m-%d").date(),
        from_place=from_place, to_place=to_place,
        mode=mode, distance_km=distance_km,
        claimed_amount_exc_gst=claimed_amount_exc_gst,
        gst_percent=gst, claimed_gst=claimed_gst,
        vendor_gstin=vendor_gstin, vendor_state=get_state_from_gstin(vendor_gstin),
        bank_state=diary.bank_state, bank_gstin=diary.bank_gstin,
        invoice_date=datetime.strptime(invoice_date, "%Y-%m-%d").date() if invoice_date else None,
        invoice_number=invoice_number, no_bill=no_bill,
    )
    db.add(item)
    db.commit()
    return RedirectResponse(url=f"/local/list/{diary_id}", status_code=302)


@router.get("/edit/{item_id}")
def edit_local_page(request: Request, item_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    item = db.query(LocalConveyance).filter(LocalConveyance.id == item_id, LocalConveyance.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("edit_local.html", {
        "request": request, "user": user, "item": item,
        "gst_rates": settings.GST_RATES,
    })


@router.post("/edit/{item_id}")
def edit_local(
    request: Request, item_id: int,
    travel_date: str = Form(...),
    from_place: str = Form(...), to_place: str = Form(...),
    mode: str = Form("Taxi"), distance_km: float = Form(0.0),
    claimed_amount_exc_gst: float = Form(0.0),
    gst_percent: float = Form(0.0),
    vendor_gstin: str = Form(""),
    invoice_date: str = Form(""), invoice_number: str = Form(""),
    no_bill: bool = Form(False),
    sanctioned_amount: float = Form(0.0), sanctioned_gst: float = Form(0.0),
    remarks: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)

    item = db.query(LocalConveyance).filter(LocalConveyance.id == item_id, LocalConveyance.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404)

    gst = gst_percent if gst_percent > 0 else settings.GST_RATES.get(mode, 0)
    claimed_gst = round(claimed_amount_exc_gst * gst / 100, 2)

    item.travel_date = datetime.strptime(travel_date, "%Y-%m-%d").date()
    item.from_place = from_place; item.to_place = to_place
    item.mode = mode; item.distance_km = distance_km
    item.claimed_amount_exc_gst = claimed_amount_exc_gst
    item.gst_percent = gst; item.claimed_gst = claimed_gst
    item.vendor_gstin = vendor_gstin
    item.vendor_state = get_state_from_gstin(vendor_gstin)
    item.invoice_date = datetime.strptime(invoice_date, "%Y-%m-%d").date() if invoice_date else None
    item.invoice_number = invoice_number; item.no_bill = no_bill
    item.sanctioned_amount = sanctioned_amount; item.sanctioned_gst = sanctioned_gst
    item.remarks = remarks
    db.commit()
    return RedirectResponse(url=f"/local/list/{item.diary_id}", status_code=302)


@router.post("/delete/{item_id}")
def delete_local(item_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    item = db.query(LocalConveyance).filter(LocalConveyance.id == item_id, LocalConveyance.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404)
    diary_id = item.diary_id
    db.delete(item)
    db.commit()
    return RedirectResponse(url=f"/local/list/{diary_id}", status_code=302)
