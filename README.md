# 📋 Audit Diary System

A web-based **Monthly Diary & TA Bill management system** for bank auditors. Built with FastAPI, Firebase Auth, and SQLite.

---

## ✨ Features

### 👥 Authentication
- **Google Sign-In** only (no passwords) via Firebase Auth
- Admin and regular user roles
- Admin whitelist via email configuration
- First-time Google login → staff number linking

### 📅 Attendance & Calendar
- **WhatsApp message parsing** — auto-extract attendance from forwarded messages
- Manual attendance entry with holiday/leave marking
- Color-coded calendar view (Present, Leave, Holiday, Weekend)
- Holiday calendar with bank/public/restricted holidays

### 📊 Excel Generation
- Generate **Monthly Diary-cum-TA Bill** in Excel format
- Auto-populates: attendance, travel, hotel, local conveyance, other expenses
- Personal details (address, bank account, TA ID) saved per user
- HRMS export format

### 💰 Expense Management
- **Travel**: Multi-leg journeys with mode, class, distance, GST
- **Hotels**: Lodging, boarding, halting allowance, GST
- **Local Conveyance**: Mode, distance, fares
- **Other Expenses**: Miscellaneous claims
- **Bills**: Upload receipts (PDF/image), OCR text extraction

### 👑 Admin Features
- User management (activate/deactivate, toggle admin)
- View all user diaries
- Linked Google account management
- Compute leaves and attendance validation

### 👤 Personal Profile
- View/edit personal details (address, bank account, TA ID)
- Details auto-populated in Excel generation

### 🎨 UI
- **Navy + Gold** design system
- Responsive (works on mobile)
- Card-based layouts
- Dark header with gold accents

---

## 🏗️ Tech Stack

| Layer      | Technology                             |
| ---------- | -------------------------------------- |
| Backend    | Python 3.10+, FastAPI                  |
| Database   | SQLite (via SQLAlchemy)                |
| Auth       | Firebase Auth (Google Sign-In)         |
| Auth State | Firestore (user_links collection)      |
| Templates  | Jinja2 + Bootstrap 5.3                |
| Styling    | Custom CSS (Navy + Gold design system) |
| Fonts      | Inter (Google Fonts)                   |
| OCR        | Tesseract + pdfplumber                |
| Excel      | openpyxl                               |
| PDF        | pdfplumber                             |

---

## 📁 Project Structure

```
audit-report/
├── main.py                  # FastAPI app entry point
├── config.py                # Settings & Firebase config
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git)
├── deploy.sh                # One-click VPS deployment script
│
├── database/
│   ├── db.py                # SQLAlchemy engine & session
│   ├── models.py            # All ORM models (User, Diary, etc.)
│   └── __init__.py
│
├── routers/
│   ├── auth.py              # Google sign-in, profile management
│   ├── attendance.py        # Calendar, attendance CRUD, preview
│   ├── admin.py             # Admin user/list/link management
│   ├── travel.py            # Travel expense routes
│   ├── hotel.py             # Hotel expense routes
│   ├── local.py             # Local conveyance routes
│   ├── other.py             # Other expense routes
│   └── bills.py             # Bill upload & OCR routes
│
├── services/
│   ├── firebase_service.py  # Firebase Admin SDK wrapper
│   └── calendar_utils.py    # Calendar builder logic
│
├── generators/
│   └── diary_excel.py       # Excel TA bill generator
│
├── templates/               # Jinja2 HTML templates (30+)
│   ├── base.html            # Base layout (nav, footer)
│   ├── login.html           # Google sign-in page
│   ├── dashboard.html       # Monthly diary list
│   ├── calendar.html        # Monthly calendar view
│   ├── preview_diary.html   # Diary preview with all expenses
│   ├── profile.html         # User profile view
│   ├── profile_edit.html    # Edit personal details
│   └── ...                  # Admin, forms, list pages
│
├── static/
│   └── style.css            # Navy + Gold design system
│
├── docs/
│   └── superpowers/
│       ├── specs/           # Design documents
│       └── plans/           # Implementation plans
│
├── template.xlsx            # Excel template (clean, universal)
├── seed.py                  # Seed initial user data
└── seed_holidays.py         # Seed holiday calendar
```

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.10+
- Tesseract OCR ([Download](https://github.com/UB-Mannheim/tesseract/wiki))
- Firebase project (see setup below)

### Installation

```bash
# Clone the repo
git clone https://github.com/nikkuhot123/can-monthly-diary.git
cd can-monthly-diary

# Create virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com) → Create a project
2. Enable **Google Sign-In** under Authentication → Sign-in method
3. Register a **Web app** → copy the config values
4. Go to Project Settings → Service Accounts → **Generate new private key**
   - Save as `firebase-service-account.json` in project root

### Configuration

Copy `.env` (template in repo) and fill in:

```ini
SECRET_KEY=your-secret-key-change-this
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MSG_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id
ADMIN_EMAILS=admin@gmail.com
```

### Run

```bash
uvicorn main:app --reload --port 9931
```

Visit: http://localhost:9931

> ⚠️ Add `localhost` and `127.0.0.1` to Firebase authorized domains (Authentication → Settings)

---

## 🖥️ Deployment

See **[DEPLOY.md](DEPLOY.md)** for complete deployment guide.

**One-command deploy:**
```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/nikkuhot123/can-monthly-diary/main/deploy.sh)"
```

---

## 👑 Roles & Permissions

| Role  | Access                                                               |
| ----- | -------------------------------------------------------------------- |
| Admin | Full access: Upload WhatsApp, Compute Leaves, all expenses, user mgmt |
| User  | Calendar view, holidays, preview, add manual attendance               |

Admin is determined by:
- **Staff number 861198** (hardcoded)
- Email in `ADMIN_EMAILS` env variable

---

## 📄 Excel Template

The `template.xlsx` file generates the **Monthly Diary-cum-TA Bill**. It contains:
- **Sheet1**: Attendance register, duty groups, leave/holiday summary
- **Sheet2**: Daily breakdown with travel, hotel, local conveyance
- **Sheet3**: Summary with cross-sheet formulas
- **Sheet4**: Empty placeholder

Personal details (address, bank, TA ID) are saved per-user and auto-populated on generation.

---

## 🔐 Environment Variables

| Variable                  | Required | Description                     |
| ------------------------- | -------- | ------------------------------- |
| `SECRET_KEY`                | ✅       | JWT signing secret              |
| `FIREBASE_API_KEY`          | ✅       | Firebase Web API key            |
| `FIREBASE_AUTH_DOMAIN`      | ✅       | Firebase auth domain            |
| `FIREBASE_PROJECT_ID`       | ✅       | Firebase project ID             |
| `FIREBASE_STORAGE_BUCKET`   | ✅       | Firebase storage bucket         |
| `FIREBASE_MSG_SENDER_ID`    | ✅       | Firebase sender ID              |
| `FIREBASE_APP_ID`           | ✅       | Firebase app ID                 |
| `ADMIN_EMAILS`              | ✅       | Comma-separated admin emails    |
| `DATABASE_URL`              | ❌       | SQLite path (default: `sqlite:///./audit_diary.db`) |
| `OCR_TESSERACT_CMD`         | ❌       | Tesseract executable path       |
| `APP_PORT`                  | ❌       | Port (default: 9931)            |

---

## 🧪 Key Commands

```bash
# Run in development
uvicorn main:app --reload --host 0.0.0.0 --port 9931

# Seed initial data
python seed.py
python seed_holidays.py

# Run database migration
python -c "
import sqlalchemy as sa
from database.db import engine
conn = engine.connect()
result = conn.execute(sa.text('PRAGMA table_info(users)'))
existing = {row[1] for row in result.fetchall()}
for col, typ in {'address_line1':'VARCHAR(200)','address_line2':'VARCHAR(200)','city_pin':'VARCHAR(100)','bank_name':'VARCHAR(100)','bank_account_no':'VARCHAR(50)','ta_id':'VARCHAR(50)'}.items():
    if col not in existing:
        conn.execute(sa.text(f'ALTER TABLE users ADD COLUMN {col} {typ}'))
conn.commit()
conn.close()
"
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add some feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📝 License

This project is for internal use.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Firebase for authentication
- Tesseract OCR for bill text extraction
- Bootstrap 5 for base UI framework
- Inter font by Rasmus Andersson
