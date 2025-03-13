#!/bin/bash
set -e

# Configuration
APP_NAME="dvga"
APP_DIR="$HOME/apps/${APP_NAME}"
VENV_DIR="${APP_DIR}/.venv"
REPO_URL="git@github.com:kjon-life/apisec-graphql-dvga.git"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"
# Nginx conf is managed separately at /etc/nginx/conf.d/dvga.conf

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
    git fetch
    git checkout dvga-simplidfied
    git pull origin dvga-simplidfied
else
    git clone -b dvga-simplidfied "$REPO_URL" "$APP_DIR"
fi

# Set up virtual environment
log "Setting up virtual environment..."
cd "$APP_DIR"
log "Set up asdf versions..."
asdf set python 3.9.21 || error "Failed to set Python version"
asdf set nodejs 23.9.0 || error "Failed to set Node.js version"
asdf set uv 0.6.6 || error "Failed to set uv version"

# Create and activate virtual environment
log "Creating virtual environment..."
rm -rf "${VENV_DIR}"  # Clean existing venv if any
uv venv
. "${VENV_DIR}/bin/activate"
uv pip install -r requirements.txt

# Create systemd service file (requires sudo)
log "Setting up systemd service..."
sudo tee "$SERVICE_FILE" > /dev/null << EOL
[Unit]
Description=dvga API application
After=network.target

[Service]
User=$USER
WorkingDirectory=${APP_DIR}
Environment=PATH=${VENV_DIR}/bin:$PATH
ExecStart=${VENV_DIR}/bin/python app.py
Restart=always
# Add environment variables from config
Environment=WEB_HOST=0.0.0.0
Environment=WEB_PORT=9071

[Install]
WantedBy=multi-user.target
EOL

# Set proper permissions
log "Setting permissions..."
sudo chmod 644 "$SERVICE_FILE"

# Reload systemd and restart services (requires sudo)
log "Reloading systemd and restarting services..."
sudo systemctl daemon-reload
sudo systemctl enable "$APP_NAME"
sudo systemctl restart "$APP_NAME"

# Note: Nginx configuration is managed separately
log "Restarting nginx to pick up any changes..."
sudo systemctl restart nginx

log "Deployment completed successfully!"
log "Next steps:"
log "1. Configure AWS security group to allow traffic on port 9071"
log "2. Ensure nginx configuration exists at /etc/nginx/conf.d/dvga.conf"
log "3. Set up SSL certificate with Let's Encrypt" 