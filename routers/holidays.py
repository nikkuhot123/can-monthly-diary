import re
from datetime import date, datetime
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import User, Holiday
from routers.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def holiday_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")

    state_filter = request.query_params.get("state", "")
    year_filter = request.query_params.get("year", "")

    query = db.query(Holiday)
    if state_filter:
        query = query.filter(Holiday.state == state_filter)
    if year_filter:
        try:
            y = int(year_filter)
            query = query.filter(
                Holiday.holiday_date >= date(y, 1, 1),
                Holiday.holiday_date <= date(y, 12, 31),
            )
        except ValueError:
            pass

    holidays = query.order_by(Holiday.holiday_date.desc()).all()
    states = [r[0] for r in db.query(Holiday.state).distinct().all()]

    return templates.TemplateResponse("holidays.html", {
        "request": request, "user": user,
        "holidays": holidays, "states": states,
        "state_filter": state_filter, "year_filter": year_filter,
        "now": datetime.utcnow(),
    })


@router.post("/add")
def add_holiday(
    request: Request,
    holiday_date: str = Form(...),
    state: str = Form("Maharashtra"),
    description: str = Form(""),
    holiday_type: str = Form("public"),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")

    try:
        d = datetime.strptime(holiday_date, "%Y-%m-%d").date()
    except ValueError:
        return RedirectResponse(url="/holidays/", status_code=302)

    existing = db.query(Holiday).filter(
        Holiday.holiday_date == d, Holiday.state == state
    ).first()

    if not existing:
        db.add(Holiday(
            holiday_date=d, state=state,
            description=description, holiday_type=holiday_type,
        ))
        db.commit()

    return RedirectResponse(url="/holidays/", status_code=302)


@router.post("/refresh")
def refresh_holidays(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")

    referer = request.headers.get("referer", "")
    is_admin_flow = "/admin/" in referer
    redirect_target = "/admin/holidays" if is_admin_flow else "/holidays/"

    try:
        import httpx
        from bs4 import BeautifulSoup
        resp = httpx.get("https://www.bankbazaar.com/indian-holiday/rbi-holidays.html", timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        tables = soup.find_all("table")
        added = 0
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    date_text = cols[0].get_text(strip=True)
                    desc_text = cols[2].get_text(strip=True)
                    states_text = cols[3].get_text(strip=True)
                    for fmt in ["%d %B %Y", "%d %b %Y"]:
                        try:
                            d = datetime.strptime(re.sub(r"\s+", " ", date_text).strip(), fmt).date()
                            break
                        except ValueError:
                            continue
                    else:
                        continue
                    for s in [s.strip() for s in states_text.split(",")]:
                        existing = db.query(Holiday).filter(
                            Holiday.holiday_date == d,
                            Holiday.state == s,
                        ).first()
                        if not existing:
                            db.add(Holiday(
                                holiday_date=d, state=s,
                                description=desc_text, holiday_type="bank",
                            ))
                            added += 1
        db.commit()
        from urllib.parse import quote_plus
        return RedirectResponse(url=f"{redirect_target}?success={quote_plus(f'Added {added} new holidays')}", status_code=303)
    except Exception as e:
        from urllib.parse import quote_plus
        return RedirectResponse(url=f"{redirect_target}?error={quote_plus(f'Refresh failed: {str(e)}')}", status_code=303)


@router.post("/delete/{holiday_id}")
def delete_holiday(
    holiday_id: int, request: Request, db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login")

    h = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if h:
        db.delete(h)
        db.commit()

    return RedirectResponse(url="/holidays/", status_code=302)
