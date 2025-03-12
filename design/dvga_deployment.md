# DVGA (Damn Vulnerable GraphQL Application) Deployment Design

## Problem Statement
Deploy DVGA in a controlled, isolated environment on EC2 that can be easily started when needed for testing and completely rebuilt after each use for security purposes.

## Progress Update (March 12, 2024)
✅ Completed:
1. Project initialization and structure
2. Python environment setup with asdf (Python 3.9.21)
3. Dependencies configuration in pyproject.toml
4. Full GraphQL schema implementation including:
   - All types and interfaces
   - Queries and mutations
   - Subscriptions
   - Custom directives
   - Authentication system
5. Deployment script creation including:
   - asdf version management
   - Virtual environment setup
   - Systemd service configuration
   - Nginx configuration
6. Port allocation (9071) and nginx integration strategy

🔄 In Progress:
1. Core application implementation
2. Database models and schema setup
3. Testing deployment script

⏳ Next Steps:
1. Implement core application logic
2. Set up database and models
3. Implement authentication system
4. Create deployment scripts
5. Configure nginx and systemd
6. Test locally before EC2 deployment
Clarify versus:
1. Complete core application implementation
2. Test deployment script on EC2
3. Create cleanup/reset scripts
4. Document security procedures

## Security Considerations
⚠️ **IMPORTANT**: This application is intentionally vulnerable and should:
1. Only be running during active testing
2. Be rebuilt after each use
3. Be isolated from other applications
4. Not be exposed to the internet when not in use

## Requirements
1. Create separate project structure for isolated deployment ✅
2. Set up Python 3.9 environment (3.10 not supported) ✅
3. Configure systemd service for controlled start/stop ✅
4. Set up nginx reverse proxy on port 9071 ✅
5. Create scripts for:
   - Clean deployment ✅
   - Safe shutdown ⏳
   - Environment cleanup ⏳

## Technical Design

### 1. Project Structure
```bash
/home/$USER/apps/dvga/
├── core/               # Core application logic
│   ├── models.py      # SQLAlchemy models
│   └── schema.py      # GraphQL schema
├── static/            # Static assets
├── templates/         # HTML templates
├── scripts/
│   └── deploy.sh      # Deployment script
├── tests/             # Test suite
├── app.py            # Main application file
├── config.py         # Configuration settings
└── pyproject.toml    # Project dependencies
```

### 2. Environment Configuration
EC2 environment requirements:
- Python 3.9.21 (via asdf)
- Node.js 23.9.0 (via asdf)
- uv 0.6.6 (via asdf)
- Virtual environment per deployment

Dependencies (pyproject.toml):
```toml
dependencies = [
    "flask>=2.0.0",
    "flask-sqlalchemy>=3.0.0",
    "flask-sockets>=0.2.1",
    "flask-graphql>=2.0.1",
    "flask-jwt-extended>=4.5.3",
    "gevent>=22.10.2",
    "gevent-websocket>=0.10.1",
    "graphene>=3.3",
    "graphene-sqlalchemy>=3.0.0",
    "rx>=3.2.0"
]
```

### 3. GraphQL Schema
The schema implementation is complete and includes:
1. Core Types:
   - User
   - Paste
   - Owner
   - Audit
2. Operations:
   - Queries (system diagnostics, pastes, users, etc.)
   - Mutations (create/edit/delete pastes, user management)
   - Subscriptions (real-time paste updates)
3. Security Features:
   - Authentication system
   - Token-based access
   - Custom directives for network info

### 3. Systemd Service Configuration
```ini
[Unit]
Description=Damn Vulnerable GraphQL Application
After=network.target

[Service]
User=$USER
WorkingDirectory=/home/$USER/apps/dvga
Environment=PATH=/home/$USER/apps/dvga/.venv/bin:$PATH
Environment=WEB_PORT=9071
ExecStart=/home/$USER/apps/dvga/.venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Nginx Configuration
Separate configuration file for DVGA (/etc/nginx/conf.d/dvga.conf):
```nginx
server {
    listen 80;
    server_name dvga.kjon.life;

    location / {
        proxy_pass http://localhost:9071/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /subscriptions {
        proxy_pass http://localhost:9071/subscriptions;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

## Implementation Plan

### Phase 1: Core Application (Current)
1. Complete models.py implementation
2. Set up database initialization
3. Implement authentication system
4. Add GraphQL resolvers and mutations

### Phase 2: Deployment Testing
1. Test deployment script on EC2
2. Verify nginx configuration
3. Test WebSocket subscriptions
4. Create cleanup scripts

### Phase 3: Security Hardening
1. Add deployment logging
2. Create monitoring scripts
3. Document security procedures
4. Test isolation from other services

## Usage Instructions

1. Deploy application:
```bash
cd ~/apps/dvga
./scripts/deploy.sh
```

2. Start service (when needed):
```bash
sudo systemctl start dvga
```

3. Stop and cleanup after use:
```bash
./scripts/cleanup.sh
```

## Access Information
- Application URL: http://54.234.103.190:9071
- Default credentials: (as specified in DVGA documentation)

## Security Checklist
- ⬜ Verify application is stopped when not in use
- ⬜ Rebuild after each testing session
- ⬜ Check for no residual data after cleanup
- ⬜ Verify isolation from other applications
- ⬜ Monitor for unauthorized access attempts 

# DVGA Deployment Status

## Current Implementation Status

### Completed Components
1. **Database Models** (`core/models.py`)
   - ✅ User model with security features (password hashing, rate limiting, session tracking)
   - ✅ Paste model with versioning and metadata support
   - ✅ Audit logging system with security event tracking
   - ✅ Server mode configuration with security settings
   - ✅ All necessary indexes for performance optimization
   - ✅ Proper relationships and cascading deletes

2. **Database Migration** (`core/db_migrate.py`)
   - ✅ Database initialization with default admin user
   - ✅ Complete database reset functionality
   - ✅ Cleanup routines for expired data
   - ✅ Error handling and logging
   - ✅ Transaction management

### Validation Status
1. **Database Models**
   - Models follow SQLAlchemy best practices
   - All relationships are properly defined
   - Indexes are created for common query patterns
   - Security features (password hashing, session tracking) are implemented
   - Audit logging captures all necessary events

2. **Database Operations**
   - All database operations are wrapped in transactions
   - Error handling is implemented with proper rollbacks
   - Logging is implemented for all operations
   - Cleanup operations handle all temporary data

### Next Steps
1. **Authentication System**
   - Implement JWT token generation and validation
   - Add rate limiting middleware
   - Create login/logout routes

2. **GraphQL API**
   - Define GraphQL schema
   - Implement resolvers and mutations
   - Add security middleware

3. **Testing**
   - Write unit tests for models
   - Create integration tests for database operations
   - Add security testing scenarios

## Technical Details

### Database Schema
```sql
-- Key Tables
users
  - Security fields: password_hash, failed_login_attempts, locked_until
  - Rate limiting: request_count, last_request
  - Session management: reset_token, reset_token_expires

pastes
  - Version control: version, content
  - Security: public, burn, expires_at
  - Metadata: language, size, file_path

audits
  - Security tracking: action, ip_address, security_level
  - Request data: user_agent, headers, graphql_operation
```

### Security Features
1. **User Security**
   - Password hashing using Werkzeug's security functions
   - Account lockout after 5 failed attempts
   - Session tracking with IP and user agent
   - Rate limiting per user

2. **Data Security**
   - Paste versioning for change tracking
   - Audit logging for all operations
   - Automatic cleanup of expired data
   - File size and type restrictions

3. **Application Security**
   - Two security modes: 'easy' and 'hard'
   - Configurable rate limits and file restrictions
   - Comprehensive audit logging
   - Session management and cleanup

### Deployment Requirements
- Python 3.9.21
- SQLite database (configurable via SQLALCHEMY_DATABASE_URI)
- Environment variables:
  - DVGA_ADMIN_PASSWORD
  - FLASK_ENV
  - WEB_HOST
  - WEB_PORT

### Maintenance
- Automatic cleanup of expired sessions and pastes
- 30-day retention for audit logs and login attempts
- Rate limit counter resets
- Server mode management 