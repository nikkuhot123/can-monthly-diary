#!/usr/bin/env bash
# =============================================================================
# Audit Diary System — One-Click Deploy
# =============================================================================
# Usage:
#   bash deploy.sh                    # Interactive (prompts for Firebase config)
#   bash deploy.sh --auto             # Non-interactive (uses env vars or .env)
#
# Prerequisites:
#   - Ubuntu 22.04+ / Debian 12+
#   - Root or sudo access
#   - Git
#
# After deploy, place your Firebase service account at:
#   /opt/audit-diary/firebase-service-account.json
# =============================================================================

set -euo pipefail

# ── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; }

# ── Defaults ────────────────────────────────────────────────────────────────
APP_DIR="/opt/audit-diary"
REPO_URL="https://github.com/nikkuhot123/can-monthly-diary.git"
BRANCH="main"
APP_USER="audit"
APP_PORT=9931
PYTHON="python3"
VENV_DIR="${APP_DIR}/venv"
NGINX_SITE="audit-diary"

# Parse args
AUTO_MODE=false
for arg in "$@"; do
    [ "$arg" == "--auto" ] && AUTO_MODE=true
done

# ── Pre-flight checks ───────────────────────────────────────────────────────
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║        Audit Diary System — One-Click Deploy        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

if [ "$(id -u)" -ne 0 ]; then
    err "This script must be run as root (or with sudo)."
    exit 1
fi

# Detect OS
if ! command -v apt-get &>/dev/null; then
    err "This script currently supports Debian/Ubuntu only."
    exit 1
fi

# ── 1. System Dependencies ──────────────────────────────────────────────────
info "Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq \
    python3 python3-pip python3-venv \
    tesseract-ocr \
    git nginx \
    openssl curl || {
    err "Failed to install system packages."
    exit 1
}
ok "System dependencies installed."

# ── 2. Create system user ───────────────────────────────────────────────────
if ! id "$APP_USER" &>/dev/null; then
    useradd --system --no-create-home --shell /usr/sbin/nologin "$APP_USER"
    ok "Created system user: $APP_USER"
else
    ok "System user $APP_USER already exists."
fi

# ── 3. Clone / Update repository ────────────────────────────────────────────
if [ -d "$APP_DIR/.git" ]; then
    info "Updating existing repository..."
    cd "$APP_DIR"
    git fetch origin
    git reset --hard "origin/$BRANCH"
    ok "Repository updated."
else
    info "Cloning repository..."
    mkdir -p "$APP_DIR"
    git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
    ok "Repository cloned."
fi

# ── 4. Python virtual environment ──────────────────────────────────────────
info "Setting up Python virtual environment..."
"$PYTHON" -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip -q
pip install -r "${APP_DIR}/requirements.txt" -q
ok "Python dependencies installed."

# ── 5. Configuration (.env) ─────────────────────────────────────────────────
if [ "$AUTO_MODE" = true ]; then
    # Auto mode: expect env vars to be set
    if [ -z "${FIREBASE_API_KEY:-}" ]; then
        err "Auto mode requires FIREBASE_API_KEY env var."
        exit 1
    fi
    cat > "${APP_DIR}/.env" << EOF
SECRET_KEY=${SECRET_KEY:-$(openssl rand -hex 32)}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:///./audit_diary.db
UPLOAD_DIR=uploads
APP_NAME=Audit Diary System
APP_HOST=0.0.0.0
APP_PORT=${APP_PORT}
OCR_TESSERACT_CMD=/usr/bin/tesseract
FIREBASE_API_KEY=${FIREBASE_API_KEY}
FIREBASE_AUTH_DOMAIN=${FIREBASE_AUTH_DOMAIN}
FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
FIREBASE_STORAGE_BUCKET=${FIREBASE_STORAGE_BUCKET}
FIREBASE_MSG_SENDER_ID=${FIREBASE_MSG_SENDER_ID}
FIREBASE_APP_ID=${FIREBASE_APP_ID}
ADMIN_EMAILS=${ADMIN_EMAILS:-admin@gmail.com}
EOF
    ok "Configuration written from environment variables."
else
    # Interactive mode
    if [ ! -f "${APP_DIR}/.env" ]; then
        warn "No .env file found. Let's set up Firebase configuration."
        echo ""
        echo "Enter your Firebase Web App configuration values:"
        echo "(Press Enter to skip any field — you can edit .env later)"
        echo ""
        read -rp "FIREBASE_API_KEY: " FIREBASE_API_KEY
        read -rp "FIREBASE_AUTH_DOMAIN: " FIREBASE_AUTH_DOMAIN
        read -rp "FIREBASE_PROJECT_ID: " FIREBASE_PROJECT_ID
        read -rp "FIREBASE_STORAGE_BUCKET: " FIREBASE_STORAGE_BUCKET
        read -rp "FIREBASE_MSG_SENDER_ID: " FIREBASE_MSG_SENDER_ID
        read -rp "FIREBASE_APP_ID: " FIREBASE_APP_ID
        read -rp "ADMIN_EMAILS (comma-separated, default: admin@gmail.com): " ADMIN_EMAILS
        ADMIN_EMAILS=${ADMIN_EMAILS:-admin@gmail.com}

        cat > "${APP_DIR}/.env" << EOF
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:///./audit_diary.db
UPLOAD_DIR=uploads
APP_NAME=Audit Diary System
APP_HOST=0.0.0.0
APP_PORT=${APP_PORT}
OCR_TESSERACT_CMD=/usr/bin/tesseract
FIREBASE_API_KEY=${FIREBASE_API_KEY}
FIREBASE_AUTH_DOMAIN=${FIREBASE_AUTH_DOMAIN}
FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
FIREBASE_STORAGE_BUCKET=${FIREBASE_STORAGE_BUCKET}
FIREBASE_MSG_SENDER_ID=${FIREBASE_MSG_SENDER_ID}
FIREBASE_APP_ID=${FIREBASE_APP_ID}
ADMIN_EMAILS=${ADMIN_EMAILS}
EOF
        ok "Configuration written to .env"
    else
        ok ".env file already exists, keeping existing configuration."
    fi
fi

# ── 6. Create directories & set permissions ────────────────────────────────
mkdir -p "${APP_DIR}/uploads" "${APP_DIR}/static"
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"
ok "Directories and permissions set."

# ── 7. Run database migration (add profile columns) ────────────────────────
info "Running database migration..."
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
cd "$APP_DIR"
"$PYTHON" -c "
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
ok "Database migration complete."

# ── 8. Create systemd service ──────────────────────────────────────────────
info "Creating systemd service..."
cat > /etc/systemd/system/audit-diary.service << EOF
[Unit]
Description=Audit Diary System
After=network.target

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
ExecStart=${VENV_DIR}/bin/uvicorn main:app --host 0.0.0.0 --port ${APP_PORT}
Restart=always
RestartSec=5
EnvironmentFile=${APP_DIR}/.env

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable audit-diary
systemctl restart audit-diary
ok "systemd service created and started."

# ── 9. Configure Nginx reverse proxy ────────────────────────────────────────
info "Configuring Nginx reverse proxy..."
cat > "/etc/nginx/sites-available/${NGINX_SITE}" << EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:${APP_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias ${APP_DIR}/static/;
        expires 7d;
    }
}
EOF

if [ -f "/etc/nginx/sites-enabled/default" ]; then
    rm /etc/nginx/sites-enabled/default
fi

if [ ! -f "/etc/nginx/sites-enabled/${NGINX_SITE}" ]; then
    ln -s "/etc/nginx/sites-available/${NGINX_SITE}" "/etc/nginx/sites-enabled/"
fi

nginx -t && systemctl restart nginx
ok "Nginx configured and restarted."

# ── 10. Final instructions ──────────────────────────────────────────────────
EXTERNAL_IP=$(curl -4 -s ifconfig.me 2>/dev/null || echo "your-server-ip")

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✅  Deployment Complete!                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}App URL:${NC}      http://${EXTERNAL_IP}"
echo -e "  ${CYAN}Status:${NC}       sudo systemctl status audit-diary"
echo -e "  ${CYAN}Logs:${NC}         sudo journalctl -u audit-diary -f"
echo ""
echo -e "  ${YELLOW}⚠  IMPORTANT:${NC}"
echo -e "  ${YELLOW}1.${NC} Place your Firebase service account at:"
echo -e "     ${APP_DIR}/firebase-service-account.json"
echo -e "  ${YELLOW}2.${NC} Restart the app after placing the file:"
echo -e "     sudo systemctl restart audit-diary"
echo -e "  ${YELLOW}3.${NC} Add 'localhost' to Firebase authorized domains"
echo -e "     (for local dev) or add your VPS domain/IP for production."
echo ""
echo -e "  ${YELLOW}Need SSL?${NC} Run:"
echo -e "     sudo apt-get install -y certbot python3-certbot-nginx"
echo -e "     sudo certbot --nginx -d your-domain.com"
echo ""

# ── Check service status ────────────────────────────────────────────────────
sleep 2
if systemctl is-active --quiet audit-diary; then
    ok "Service is running."
else
    warn "Service may not have started. Check with: sudo systemctl status audit-diary"
fi
