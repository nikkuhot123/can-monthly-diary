import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from database.db import engine
from database import models
from config import settings
from routers import auth, attendance, bills, travel, hotel, local, other, generate, admin, holidays

models.Base.metadata.create_all(bind=engine)

# Schema migrations for columns added after initial deploy
def _run_migrations():
    import sqlalchemy as sa
    with engine.connect() as conn:
        existing = {row[1] for row in conn.execute(sa.text("PRAGMA table_info(users)")).fetchall()}
        pending = {
            "google_uid": "VARCHAR(128)",
        }
        for col, typ in pending.items():
            if col not in existing:
                conn.execute(sa.text(f"ALTER TABLE users ADD COLUMN {col} {typ}"))
                print(f"[migration] Added column users.{col}")
        conn.commit()

_run_migrations()

for folder in ["uploads/whatsapp", "uploads/bills", "uploads/generated"]:
    os.makedirs(folder, exist_ok=True)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(auth.router,       prefix="/auth",       tags=["auth"])
app.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
app.include_router(bills.router,      prefix="/bills",      tags=["bills"])
app.include_router(travel.router,     prefix="/travel",     tags=["travel"])
app.include_router(hotel.router,      prefix="/hotel",      tags=["hotel"])
app.include_router(local.router,      prefix="/local",      tags=["local"])
app.include_router(other.router,      prefix="/other",      tags=["other"])
app.include_router(generate.router,   prefix="/generate",   tags=["generate"])
app.include_router(admin.router,      prefix="/admin",      tags=["admin"])
app.include_router(holidays.router,   prefix="/holidays",   tags=["holidays"])


@app.get("/")
def root():
    return RedirectResponse(url="/auth/login")


@app.get("/dashboard")
def dashboard(request: Request):
    return RedirectResponse(url="/attendance/dashboard")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
