from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Security and session management
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expires = db.Column(db.DateTime)
    
    # Rate limiting
    last_request = db.Column(db.DateTime)
    request_count = db.Column(db.Integer, default=0)
    
    # Relationships
    pastes = relationship('Paste', back_populates='user', lazy='dynamic')
    owned_pastes = relationship('Paste', back_populates='owner', foreign_keys='Paste.owner_id', lazy='dynamic')
    sessions = relationship('UserSession', back_populates='user', lazy='dynamic')
    
    __table_args__ = (
        db.Index('idx_user_username_admin', 'username', 'is_admin'),
        db.Index('idx_user_reset_token', 'reset_token'),
    )
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def create_user(cls, username, password, is_admin=False):
        user = cls(username=username, is_admin=is_admin)
        user.password = password
        db.session.add(user)
        db.session.commit()
        return user

    def record_login(self, success, ip_address=None):
        """Record login attempt and handle security measures."""
        if success:
            self.failed_login_attempts = 0
            self.last_login = datetime.utcnow()
            self.locked_until = None
        else:
            self.failed_login_attempts += 1
            if self.failed_login_attempts >= 5:
                self.locked_until = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()
        
        # Log the attempt
        LoginAttempt.create(
            user_id=self.id,
            success=success,
            ip_address=ip_address
        )

class UserSession(db.Model):
    """Track user sessions for security monitoring"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), index=True)
    token = db.Column(db.String(255), unique=True, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, index=True)
    revoked = db.Column(db.Boolean, default=False, index=True)
    
    user = relationship('User', back_populates='sessions')

class Paste(db.Model):
    __tablename__ = 'pastes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    public = db.Column(db.Boolean, default=True, index=True)
    burn = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # New fields
    expires_at = db.Column(db.DateTime, index=True)
    language = db.Column(db.String(50))
    size = db.Column(db.Integer)  # Size in bytes
    version = db.Column(db.Integer, default=1)
    file_path = db.Column(db.String(255))  # For file attachments
    paste_metadata = db.Column(db.Text)  # JSON field for flexible metadata
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), index=True)
    
    # Relationships
    user = relationship('User', back_populates='pastes', foreign_keys=[user_id])
    owner = relationship('User', back_populates='owned_pastes', foreign_keys=[owner_id])
    audits = relationship('Audit', back_populates='paste', lazy='dynamic', cascade='all, delete-orphan')
    versions = relationship('PasteVersion', back_populates='paste', lazy='dynamic')
    
    __table_args__ = (
        db.Index('idx_paste_public_created', 'public', 'created_at'),
        db.Index('idx_paste_user_created', 'user_id', 'created_at'),
        db.Index('idx_paste_owner_public', 'owner_id', 'public'),
        db.Index('idx_paste_expiry', 'expires_at'),
    )
    
    def set_metadata(self, data):
        """Store additional metadata as JSON"""
        self.paste_metadata = json.dumps(data)
    
    def get_metadata(self):
        """Retrieve metadata as dictionary"""
        return json.loads(self.paste_metadata) if self.paste_metadata else {}

    @classmethod
    def create_paste(cls, title, content, user_id, public=True, burn=False, 
                    language=None, metadata=None, expires_at=None, file_path=None):
        """Create a new paste with the given parameters."""
        paste = cls(
            title=title,
            content=content,
            user_id=user_id,
            owner_id=user_id,
            public=public,
            burn=burn,
            language=language,
            size=len(content.encode('utf-8')),
            file_path=file_path,
            expires_at=expires_at
        )
        
        if metadata:
            paste.set_metadata(metadata)
            
        # Create initial version
        version = PasteVersion(
            paste=paste,
            content=content,
            version=1
        )
        
        db.session.add(paste)
        db.session.add(version)
        db.session.commit()
        
        # Log the creation
        Audit.log_action(paste.id, user_id, 'create')
        
        return paste

class PasteVersion(db.Model):
    """Track paste version history"""
    __tablename__ = 'paste_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    paste_id = db.Column(db.Integer, db.ForeignKey('pastes.id', ondelete='CASCADE'), index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    version = db.Column(db.Integer, nullable=False)
    
    paste = relationship('Paste', back_populates='versions')

class Audit(db.Model):
    __tablename__ = 'audits'
    
    id = db.Column(db.Integer, primary_key=True)
    paste_id = db.Column(db.Integer, db.ForeignKey('pastes.id', ondelete='CASCADE'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), index=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45))
    
    # New fields for better security tracking
    user_agent = db.Column(db.String(255))
    request_headers = db.Column(db.Text)  # JSON
    graphql_operation = db.Column(db.String(100))
    operation_type = db.Column(db.String(20))  # query, mutation, subscription
    security_level = db.Column(db.String(20))  # info, warning, critical
    
    # Relationships
    paste = relationship('Paste', back_populates='audits')
    user = relationship('User')
    
    __table_args__ = (
        db.Index('idx_audit_paste_time', 'paste_id', 'timestamp'),
        db.Index('idx_audit_user_time', 'user_id', 'timestamp'),
        db.Index('idx_audit_security', 'security_level', 'timestamp'),
    )
    
    @classmethod
    def log_action(cls, paste_id, user_id, action, ip_address=None):
        audit = cls(
            paste_id=paste_id,
            user_id=user_id,
            action=action,
            ip_address=ip_address
        )
        db.session.add(audit)
        db.session.commit()
        return audit

class LoginAttempt(db.Model):
    """Track login attempts for security monitoring"""
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    success = db.Column(db.Boolean, default=False, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    
    @classmethod
    def create(cls, user_id, success, ip_address=None, user_agent=None):
        attempt = cls(
            user_id=user_id,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(attempt)
        db.session.commit()
        return attempt

class ServerMode(db.Model):
    """Controls the application's security mode and configuration"""
    __tablename__ = 'server_mode'
    
    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.String(10), nullable=False, default='easy', index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # Security settings
    rate_limit = db.Column(db.Integer, default=100)  # Requests per minute
    max_paste_size = db.Column(db.Integer, default=1048576)  # 1MB in bytes
    max_file_size = db.Column(db.Integer, default=5242880)  # 5MB in bytes
    allowed_file_types = db.Column(db.String(255), default='txt,pdf,png,jpg')
    log_level = db.Column(db.String(20), default='INFO')
    
    # Configuration as JSON
    security_config = db.Column(db.Text)  # JSON field for flexible security settings
    
    @classmethod
    def get_mode(cls):
        mode = cls.query.first()
        return mode.mode if mode else 'easy'
    
    @classmethod
    def set_mode(cls, mode):
        if mode not in ['easy', 'hard']:
            raise ValueError("Mode must be 'easy' or 'hard'")
        
        server_mode = cls.query.first()
        if server_mode:
            server_mode.mode = mode
        else:
            server_mode = cls(mode=mode)
            db.session.add(server_mode)
        
        db.session.commit()
        return server_mode

# Event listeners for audit logging
@db.event.listens_for(Paste, 'after_update')
def paste_update_listener(mapper, connection, target):
    Audit.log_action(target.id, target.user_id, 'update')

@db.event.listens_for(Paste, 'after_delete')
def paste_delete_listener(mapper, connection, target):
    Audit.log_action(target.id, target.user_id, 'delete') 