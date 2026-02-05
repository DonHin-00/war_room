from flask import Flask, render_template
from .config import Config
from .core.db import db
from .routes.auth import auth_bp
from .routes.banking import banking_bp
from .routes.admin import admin_bp
from .core.extensions import limiter, csrf
from flask_talisman import Talisman
from irondome.dlp import DLPScanner
from irondome.firewall import is_blocked
from flask import request, abort
import logging
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Security Extensions
    csrf.init_app(app)
    limiter.init_app(app)

    # CSP Policy
    csp = {
        'default-src': '\'self\'',
        'script-src': '\'self\'',
        'style-src': '\'self\'',
        'img-src': '\'self\''
    }
    Talisman(app, content_security_policy=csp, force_https=False) # force_https=False for localhost simulation

    dlp = DLPScanner()

    @app.before_request
    def check_firewall():
        if is_blocked(request.remote_addr):
            abort(403, description="Your IP has been flagged by IronDome Security.")

    @app.after_request
    def scan_response(response):
        try:
            # Scan text content
            if response.mimetype and 'text' in response.mimetype:
                dlp.inspect_traffic(request.path, response.get_data(as_text=True))
        except: pass
        return response

    # Ensure instance folder exists if using sqlite relative path
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)

    # Initialize DB
    db.init_app(app)

    # Logging
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(filename=os.path.join(log_dir, 'app.log'), level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(banking_bp, url_prefix='/banking')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        return render_template('base.html')

    with app.app_context():
        db.create_all()

    return app
