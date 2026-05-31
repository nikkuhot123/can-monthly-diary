# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```powershell
# Start server (clears port 9931 first, then runs)
.\start_9931.ps1

# Or directly:
python main.py
# or: uvicorn main:app --reload --host 0.0.0.0 --port 9931

# Seed initial user data
python seed.py

# Seed holiday calendar
python seed_holidays.py
```

No test framework is configured. `test_parse.py` and `_t.py` are ad-hoc debug scripts, not a test suite.

No Alembic migrations are set up — schema changes are applied manually via raw `ALTER TABLE` SQL against `audit_diary.db`. Add new columns by running SQLite `ALTER TABLE` inline (see README for pattern).

## Architecture

**FastAPI + Jinja2 SSR app.** All routes return HTML via Jinja2 templates. No REST API or JS framework — form submits and page reloads.

**Auth:** Firebase Google Sign-In (client-side token) → `routers/auth.py` verifies token via Firebase Admin SDK (`services/firebase_service.py`) → stores user session in Starlette `SessionMiddleware`. Firestore `user_links` collection maps `google_uid` → `staff_no`. Admin is determined by staff_no `861198` or email in `ADMIN_EMAILS` env var.

**Database:** SQLite via SQLAlchemy. Single `audit_diary.db` file. No migrations — `models.Base.metadata.create_all()` at startup handles new tables. Manual `ALTER TABLE` for new columns on existing tables.

**Core data model:**
- `User` → has many `MonthlyDiary` (unique per user/month/year)
- `MonthlyDiary` → has many `AttendanceRecord`, `TravelLeg`, `HotelStay`, `LocalConveyance`, `OtherExpense`, `Bill`
- `Holiday` table — seeded via `seed_holidays.py`, queried by state + date

**Expense types** each have their own router (`travel`, `hotel`, `local`, `other`, `bills`) with standard list/add/edit/delete routes under `/travel/`, `/hotel/`, etc.

**Excel generation** (`generators/diary_excel.py`, `generators/hrms_excel.py`): fills `template.xlsx` with openpyxl. The template has 4 sheets — Sheet1 (attendance), Sheet2 (daily expenses), Sheet3 (summary with cross-sheet formulas), Sheet4 (empty). Generation triggered via `/generate/download-excel/{diary_id}`.

**Business config** is all in `config.py` `Settings` class as `ClassVar` dicts: GST rates by travel mode, hotel category, HA (halting allowance) rates by city category, state GSTIN codes for Canara Bank.

**WhatsApp import:** Admin uploads exported WhatsApp chat `.txt` → `services/whatsapp_parser.py` parses attendance messages and creates `AttendanceRecord` rows. Matches sender by staff_no or name.

**Holiday logic:** `services/calendar_utils.py` handles bank holidays (hardcoded), `services/holiday_service.py` queries the `Holiday` DB table. Saturdays 2nd/4th are bank holidays.

## Key patterns

- Auth check in every route: `user = get_current_user(request, db); if not user: return RedirectResponse("/auth/login")`
- Admin-only routes use `Depends(admin_required)` from `routers/auth.py`
- `get_or_create_diary()` in `routers/attendance.py` is the canonical way to get/create a `MonthlyDiary`
- `diary.bank_state` drives GSTIN lookups and holiday lookups — always set when creating a diary

## Environment

Required `.env` vars: `SECRET_KEY`, all `FIREBASE_*` vars, `ADMIN_EMAILS`. `firebase-service-account.json` must exist in project root. OCR (Tesseract) optional — set `OCR_TESSERACT_CMD` if not on PATH.
