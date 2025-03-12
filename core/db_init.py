from .models import db, User, ServerMode

def init_db():
    """Initialize the database, creating tables and default data."""
    # Create all tables
    db.create_all()
    
    # Check if we need to create default admin user
    if not User.query.filter_by(username='admin').first():
        User.create_user(
            username='admin',
            password='dvga_admin_password',  # This should be changed after first login
            is_admin=True
        )
    
    # Initialize server mode if not exists
    if not ServerMode.query.first():
        ServerMode.set_mode('easy')

def reset_db():
    """Reset the database, dropping all tables and recreating them."""
    db.drop_all()
    init_db()

def create_test_data():
    """Create sample data for testing purposes."""
    # Create test users
    test_user = User.create_user(
        username='test_user',
        password='test_password',
        is_admin=False
    )
    
    # Create some test pastes
    from .models import Paste
    test_pastes = [
        {
            'title': 'Public Test Paste',
            'content': 'This is a public test paste',
            'public': True,
            'burn': False
        },
        {
            'title': 'Private Test Paste',
            'content': 'This is a private test paste',
            'public': False,
            'burn': False
        },
        {
            'title': 'Burn After Reading',
            'content': 'This paste will be deleted after reading',
            'public': False,
            'burn': True
        }
    ]
    
    for paste_data in test_pastes:
        Paste.create_paste(
            title=paste_data['title'],
            content=paste_data['content'],
            user_id=test_user.id,
            public=paste_data['public'],
            burn=paste_data['burn']
        )

def setup_db(app, create_test_data=False):
    """Setup database with application context."""
    db.init_app(app)
    
    with app.app_context():
        init_db()
        
        if create_test_data:
            create_test_data() 