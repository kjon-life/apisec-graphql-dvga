#!/bin/bash
set -e

# Configuration
APP_NAME="dvga"
APP_DIR="$HOME/apps/${APP_NAME}"
VENV_DIR="${APP_DIR}/.venv"
REPO_URL="git@github.com:kjon-life/apisec-graphql-qa.git"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"
NGINX_CONF="/etc/nginx/conf.d/${APP_NAME}.conf"
APP_PORT=9071
DB_FILE="${APP_DIR}/dvga.db"

# Environment variables
export FLASK_ENV="production"
export SECRET_KEY=$(openssl rand -hex 32)
export DATABASE_URL="sqlite:///${DB_FILE}"
export WEB_PORT=${APP_PORT}
export WEB_HOST="127.0.0.1"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Create application directory
log "Creating application directory..."
mkdir -p "$APP_DIR"

# Clone/update repository
log "Cloning/updating repository..."
if [ -d "${APP_DIR}/.git" ]; then
    cd "$APP_DIR"
    git pull
else
    git clone "$REPO_URL" "$APP_DIR"
fi

# Set up virtual environment
log "Setting up virtual environment..."
cd "$APP_DIR"
# Set up project software versions w asdf
log "Setting up asdf versions..."
asdf set python 3.9.21
asdf set nodejs 23.9.0
asdf set uv 0.6.6
# create virtual environment
uv venv
source "${VENV_DIR}/bin/activate"

# Install dependencies
log "Installing dependencies..."
uv pip install -e .

# Initialize database
log "Initializing database..."
uv run python -c "
from app import app, db
with app.app_context():
    db.create_all()
    from core.models import ServerMode
    if not ServerMode.query.first():
        ServerMode.set_mode('easy')
"

# Create systemd service file (requires sudo)
log "Setting up systemd service..."
sudo tee "$SERVICE_FILE" > /dev/null << EOL
[Unit]
Description=Damn Vulnerable GraphQL Application
After=network.target

[Service]
User=$USER
WorkingDirectory=${APP_DIR}
Environment=PATH=${VENV_DIR}/bin:$PATH
Environment=FLASK_ENV=production
Environment=SECRET_KEY=${SECRET_KEY}
Environment=DATABASE_URL=${DATABASE_URL}
Environment=WEB_PORT=${APP_PORT}
Environment=WEB_HOST=${WEB_HOST}
ExecStart=${VENV_DIR}/bin/uv run python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Set up nginx configuration (requires sudo)
log "Setting up nginx configuration..."
sudo tee "$NGINX_CONF" > /dev/null << EOL
server {
    listen 80;
    server_name dvga.kjon.life;

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:${APP_PORT}/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # DVGA - Damn Vulnerable GraphQL Application (port ${APP_PORT})
    location / {
        proxy_pass http://localhost:${APP_PORT}/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /subscriptions {
        proxy_pass http://localhost:${APP_PORT}/subscriptions;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host \$host;
    }
}
EOL

# Set proper permissions
log "Setting permissions..."
sudo chmod 644 "$SERVICE_FILE"
sudo chmod 644 "$NGINX_CONF"

# Reload systemd and restart services (requires sudo)
log "Reloading systemd and restarting services..."
sudo systemctl daemon-reload
sudo systemctl enable "$APP_NAME"
sudo systemctl restart "$APP_NAME"
sudo systemctl reload nginx

log "Deployment completed successfully!"
log "Next steps:"
log "1. Configure AWS security group to allow traffic on port 80 (nginx handles routing to ${APP_PORT})"
log "2. Access the application at http://YOUR_DOMAIN/dvga/"
log "3. Check application health at http://YOUR_DOMAIN/health" 