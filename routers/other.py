from datetime import datetime
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import OtherExpense, MonthlyDiary
from routers.auth import get_current_user, login_required
from config import settings, get_state_from_gstin

router = APIRouter(dependencies=[Depends(login_required)])
templates = Jinja2Templates(directory="templates")


@router.get("/list/{diary_id}")
def list_other(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)
    items = db.query(OtherExpense).filter(OtherExpense.diary_id == diary_id, OtherExpense.user_id == user.id).order_by(OtherExpense.created_at.desc()).all()
    return templates.TemplateResponse("list_other.html", {
        "request": request, "user": user, "diary": diary, "items": items,
    })


@router.get("/add/{diary_id}")
def add_other_page(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("add_other.html", {
        "request": request, "user": user, "diary": diary,
        "now": datetime.utcnow(),
    })


@router.post("/add/{diary_id}")
def add_other(
    request: Request, diary_id: int,
    expense_description: str = Form(...),
    claimed_amount_exc_gst: float = Form(0.0),
    gst_percent: float = Form(0.0),
    declaration_amount: float = Form(0.0),
    vendor_gstin: str = Form(""),
    invoice_date: str = Form(""), invoice_number: str = Form(""),
    no_bill: bool = Form(False),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)

    diary = db.query(MonthlyDiary).filter(MonthlyDiary.id == diary_id, MonthlyDiary.user_id == user.id).first()
    if not diary:
        raise HTTPException(status_code=404)

    claimed_gst = round(claimed_amount_exc_gst * gst_percent / 100, 2)

    item = OtherExpense(
        user_id=user.id, diary_id=diary_id,
        expense_description=expense_description,
        claimed_amount_exc_gst=claimed_amount_exc_gst,
        gst_percent=gst_percent, claimed_gst=claimed_gst,
        declaration_amount=declaration_amount,
        vendor_gstin=vendor_gstin, vendor_state=get_state_from_gstin(vendor_gstin),
        bank_state=diary.bank_state, bank_gstin=diary.bank_gstin,
        invoice_date=datetime.strptime(invoice_date, "%Y-%m-%d").date() if invoice_date else None,
        invoice_number=invoice_number, no_bill=no_bill,
    )
    db.add(item)
    db.commit()
    return RedirectResponse(url=f"/other/list/{diary_id}", status_code=302)


@router.get("/edit/{item_id}")
def edit_other_page(request: Request, item_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    item = db.query(OtherExpense).filter(OtherExpense.id == item_id, OtherExpense.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("edit_other.html", {
        "request": request, "user": user, "item": item,
    })


@router.post("/edit/{item_id}")
def edit_other(
    request: Request, item_id: int,
    expense_description: str = Form(...),
    claimed_amount_exc_gst: float = Form(0.0),
    gst_percent: float = Form(0.0),
    declaration_amount: float = Form(0.0),
    vendor_gstin: str = Form(""),
    invoice_date: str = Form(""), invoice_number: str = Form(""),
    no_bill: bool = Form(False),
    sanctioned_amount: float = Form(0.0), sanctioned_gst: float = Form(0.0),
    remarks: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)

    item = db.query(OtherExpense).filter(OtherExpense.id == item_id, OtherExpense.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404)

    claimed_gst = round(claimed_amount_exc_gst * gst_percent / 100, 2)

    item.expense_description = expense_description
    item.claimed_amount_exc_gst = claimed_amount_exc_gst
    item.gst_percent = gst_percent; item.claimed_gst = claimed_gst
    item.declaration_amount = declaration_amount
    item.vendor_gstin = vendor_gstin
    item.vendor_state = get_state_from_gstin(vendor_gstin)
    item.invoice_date = datetime.strptime(invoice_date, "%Y-%m-%d").date() if invoice_date else None
    item.invoice_number = invoice_number; item.no_bill = no_bill
    item.sanctioned_amount = sanctioned_amount; item.sanctioned_gst = sanctioned_gst
    item.remarks = remarks
    db.commit()
    return RedirectResponse(url=f"/other/list/{item.diary_id}", status_code=302)


@router.post("/delete/{item_id}")
def delete_other(item_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    item = db.query(OtherExpense).filter(OtherExpense.id == item_id, OtherExpense.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404)
    diary_id = item.diary_id
    db.delete(item)
    db.commit()
    return RedirectResponse(url=f"/other/list/{diary_id}", status_code=302)
