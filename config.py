import os

# Web server configuration
WEB_HOST = os.environ.get('WEB_HOST', '127.0.0.1')
WEB_PORT = int(os.environ.get('WEB_PORT', 5013))

# Security settings
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = 604800  # 1 week

# Database settings
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dvga.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Application settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
TESTING = os.environ.get('TESTING', 'False').lower() == 'true' 