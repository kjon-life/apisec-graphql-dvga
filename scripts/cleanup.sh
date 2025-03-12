#!/bin/bash
set -e

# Configuration
APP_NAME="dvga"
APP_DIR="$HOME/apps/${APP_NAME}"
VENV_DIR="${APP_DIR}/.venv"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"
DB_FILE="${APP_DIR}/dvga.db"

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "Please run with sudo"
fi

# Stop the service
log "Stopping DVGA service..."
systemctl stop ${APP_NAME} || true

# Remove database
log "Removing database..."
rm -f ${DB_FILE} || true

# Remove temporary files
log "Cleaning temporary files..."
find ${APP_DIR} -type f -name "*.pyc" -delete
find ${APP_DIR} -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Clean virtual environment
log "Cleaning virtual environment..."
rm -rf ${VENV_DIR}

# Reset git repository to clean state
log "Resetting git repository..."
cd ${APP_DIR}
git reset --hard HEAD
git clean -fdx

log "Cleanup completed successfully!"
log "To redeploy the application, run: ./scripts/deploy.sh" 