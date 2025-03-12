import os
import json
import logging
from datetime import datetime, timedelta
from .models import (
    db, User, ServerMode, Paste, UserSession,
    LoginAttempt, Audit, PasteVersion
)

# Set up logging
logger = logging.getLogger(__name__)

def create_database():
    """Create all database tables and set up initial data."""
    try:
        # Drop all existing tables
        logger.info("Dropping all existing tables...")
        db.drop_all()
        
        # Create all tables fresh
        logger.info("Creating all tables...")
        db.create_all()
        
        # Create default admin user
        logger.info("Creating default admin user...")
        admin = User.create_user(
            username='admin',
            password=os.getenv('DVGA_ADMIN_PASSWORD', 'dvga_admin_password'),
            is_admin=True
        )
        
        # Create default server mode
        logger.info("Setting default server mode...")
        ServerMode.set_mode('easy')
        
        # Create sample vulnerable paste if in development
        if os.getenv('FLASK_ENV') == 'development':
            logger.info("Creating sample vulnerable paste...")
            Paste.create_paste(
                title='Example SQL Injection',
                content='SELECT * FROM users WHERE id = ${user_input}',
                user_id=admin.id,
                public=True,
                metadata={
                    'language': 'sql',
                    'vulnerability': 'sql_injection',
                    'severity': 'high'
                }
            )
        
        logger.info("Database creation completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        db.session.rollback()
        raise

def reset_database():
    """Reset the database to its initial state."""
    try:
        logger.info("Starting database reset...")
        # Drop everything
        db.drop_all()
        
        # Recreate from scratch
        success = create_database()
        
        if success:
            logger.info("Database reset completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        db.session.rollback()
        raise

def setup_database(app, reset=False):
    """Initialize database with application context."""
    logger.info(f"Setting up database (reset={reset})...")
    db.init_app(app)
    
    try:
        with app.app_context():
            if reset:
                return reset_database()
            else:
                return create_database()
                
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        raise

def cleanup_database():
    """Cleanup old data and reset security-sensitive information."""
    logger.info("Starting database cleanup...")
    try:
        with db.session.begin():
            # Remove expired sessions
            deleted = UserSession.query.filter(
                UserSession.expires_at < datetime.utcnow()
            ).delete()
            logger.info(f"Deleted {deleted} expired sessions")
            
            # Remove expired pastes
            deleted = Paste.query.filter(
                Paste.expires_at < datetime.utcnow()
            ).delete()
            logger.info(f"Deleted {deleted} expired pastes")
            
            # Remove old audit logs (older than 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            deleted = Audit.query.filter(
                Audit.timestamp < thirty_days_ago
            ).delete()
            logger.info(f"Deleted {deleted} old audit logs")
            
            # Remove old login attempts
            deleted = LoginAttempt.query.filter(
                LoginAttempt.timestamp < thirty_days_ago
            ).delete()
            logger.info(f"Deleted {deleted} old login attempts")
            
            # Reset rate limiting counters
            updated = User.query.update({
                User.request_count: 0,
                User.last_request: None
            })
            logger.info(f"Reset rate limiting for {updated} users")
            
            # Reset server mode to 'easy'
            ServerMode.set_mode('easy')
            logger.info("Reset server mode to 'easy'")
            
            logger.info("Database cleanup completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error during database cleanup: {str(e)}")
        db.session.rollback()
        raise 