import os
from flask import Flask, render_template, make_response
from flask_sockets import Sockets
from core.models import db, ServerMode
from core.schema import schema
from flask_graphql import GraphQLView
from graphql.backend import GraphQLCoreBackend

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///dvga.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    WEB_HOST=os.environ.get('WEB_HOST', '127.0.0.1'),
    WEB_PORT=int(os.environ.get('WEB_PORT', 5013))
)

# Initialize extensions
db.init_app(app)
sockets = Sockets(app)

# Create database tables
with app.app_context():
    db.create_all()
    # Initialize default server mode if not exists
    if not ServerMode.query.first():
        ServerMode.set_mode('easy')

# Routes
@app.route('/')
def index():
    resp = make_response(render_template('index.html'))
    resp.set_cookie("env", "graphiql:disable")
    return resp

@app.route('/health')
def health_check():
    try:
        # Check database connection
        with app.app_context():
            db.session.execute('SELECT 1')
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500

# GraphQL endpoints
class CustomBackend(GraphQLCoreBackend):
    def __init__(self, executor=None):
        super().__init__(executor)
        self.execute_params['allow_subscriptions'] = True

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        backend=CustomBackend(),
        batch=True
    )
)

app.add_url_rule(
    '/graphiql',
    view_func=GraphQLView.as_view(
        'graphiql',
        schema=schema,
        backend=CustomBackend(),
        graphiql=True
    )
)

# WebSocket subscription endpoint
@sockets.route('/subscriptions')
def echo_socket(ws):
    from core.schema import subscription_server
    subscription_server.handle(ws)
    return []

if __name__ == '__main__':
    # Note: This file should be run using: uv run python app.py
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    
    server = pywsgi.WSGIServer(
        (app.config['WEB_HOST'], app.config['WEB_PORT']),
        app,
        handler_class=WebSocketHandler
    )
    print(f"Server running on {app.config['WEB_HOST']}:{app.config['WEB_PORT']}")
    server.serve_forever() 