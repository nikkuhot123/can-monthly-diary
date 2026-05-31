# Deployment Guide

Deploy the Audit Diary System on a Linux VPS (Ubuntu 22.04+ / Debian 12+).

---

## Quick Deploy (One Command)

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/nikkuhot123/can-monthly-diary/main/deploy.sh)"
```

This will:
- Install all system dependencies (Python, Tesseract OCR, Nginx)
- Clone the repository
- Create an isolated Python virtual environment
- Prompt for Firebase configuration
- Set up a systemd service for auto-start
- Configure Nginx reverse proxy

---

## Manual Deploy (Step by Step)

### 1. Prerequisites

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3 python3-pip python3-venv tesseract-ocr git nginx
```

### 2. Clone the Repository

```bash
sudo mkdir -p /opt/audit-diary
sudo git clone https://github.com/nikkuhot123/can-monthly-diary.git /opt/audit-diary
sudo chown -R $USER:$USER /opt/audit-diary
```

### 3. Virtual Environment

```bash
cd /opt/audit-diary
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Firebase Configuration

Create the `.env` file:

```bash
nano /opt/audit-diary/.env
```

Paste the following and fill in your Firebase values:

```ini
SECRET_KEY=<generate with: openssl rand -hex 32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:///./audit_diary.db
UPLOAD_DIR=uploads
APP_NAME=Audit Diary System
APP_HOST=0.0.0.0
APP_PORT=9931
OCR_TESSERACT_CMD=/usr/bin/tesseract
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MSG_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
ADMIN_EMAILS=admin@gmail.com
```

### 5. Firebase Service Account

1. Go to [Firebase Console](https://console.firebase.google.com) → Project Settings → Service Accounts
2. Click **"Generate new private key"**
3. Save the JSON file locally, then upload to your VPS:

```bash
# From your local machine:
scp /path/to/firebase-service-account.json root@your-vps-ip:/opt/audit-diary/
```

### 6. Database Setup

```bash
cd /opt/audit-diary
source venv/bin/activate

# Run migration to add profile fields
python -c "
import sqlalchemy as sa
from database.db import engine
conn = engine.connect()
result = conn.execute(sa.text('PRAGMA table_info(users)'))
existing = {row[1] for row in result.fetchall()}
NEW_COLS = {
    'address_line1': 'VARCHAR(200)', 'address_line2': 'VARCHAR(200)',
    'city_pin': 'VARCHAR(100)', 'bank_name': 'VARCHAR(100)',
    'bank_account_no': 'VARCHAR(50)', 'ta_id': 'VARCHAR(50)',
}
for col_name, col_type in NEW_COLS.items():
    if col_name not in existing:
        conn.execute(sa.text(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}'))
        print(f'  + Added column: {col_name}')
conn.commit()
conn.close()
print('Migration complete.')
"
```

### 7. Seed Initial Data (Optional)

```bash
cd /opt/audit-diary
source venv/bin/activate
python seed.py          # Seed users
python seed_holidays.py # Seed holidays
```

### 8. Run the App

#### Option A: Direct (for testing)

```bash
cd /opt/audit-diary
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 9931
```

Visit: `http://your-vps-ip:9931`

#### Option B: Systemd Service (for production, runs on boot)

```bash
sudo nano /etc/systemd/system/audit-diary.service
```

```ini
[Unit]
Description=Audit Diary System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/audit-diary
ExecStart=/opt/audit-diary/venv/bin/uvicorn main:app --host 0.0.0.0 --port 9931
Restart=always
RestartSec=5
EnvironmentFile=/opt/audit-diary/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable audit-diary
sudo systemctl start audit-diary

# Check status
sudo systemctl status audit-diary

# View logs
sudo journalctl -u audit-diary -f
```

### 9. Nginx Reverse Proxy (Optional, for port 80)

```bash
sudo nano /etc/nginx/sites-available/audit-diary
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:9931;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/audit-diary/static/;
        expires 7d;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/audit-diary /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # remove default
sudo nginx -t
sudo systemctl restart nginx
```

### 10. SSL Certificate (HTTPS)

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Post-Deployment Checklist

- [ ] App accessible at `http://your-vps-ip:9931` (or your domain)
- [ ] Google Sign-In working (add VPS IP/domain to Firebase authorized domains)
- [ ] First-time login links staff account successfully
- [ ] Calendar and dashboard loading
- [ ] Excel generation working from preview page
- [ ] Bill upload processing multi-page PDFs

### Firebase Authorized Domains

1. Go to [Firebase Console](https://console.firebase.google.com) → Authentication → Settings
2. Add your VPS IP address and/or domain to **Authorized domains**

---

## Maintenance

### Update the App

```bash
cd /opt/audit-diary
sudo systemctl stop audit-diary
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl start audit-diary
```

### View Logs

```bash
sudo journalctl -u audit-diary -f
```

### Backup Database

```bash
cp /opt/audit-diary/audit_diary.db /opt/audit-diary/backups/audit_diary_$(date +%Y%m%d).db
```

---

## Troubleshooting

| Problem                          | Likely Fix                                              |
| -------------------------------- | ------------------------------------------------------- |
| "Firebase not configured"        | Place `firebase-service-account.json` in project root   |
| "unauthorized-domain"            | Add your IP/domain to Firebase authorized domains       |
| 502 Bad Gateway (Nginx)          | App not running: `sudo systemctl restart audit-diary`   |
| Permission denied on uploads     | `sudo chown -R root:root /opt/audit-diary/uploads`      |
| Tesseract not found              | `sudo apt-get install tesseract-ocr`                    |
| 500 error on bill upload         | Check logs: `sudo journalctl -u audit-diary -f`         |
