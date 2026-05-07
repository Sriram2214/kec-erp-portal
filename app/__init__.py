import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["2000 per day", "500 per hour"])
from flask_compress import Compress
from flask_cors import CORS
compress = Compress()
cors = CORS()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app(config_class=Config):
    from flask import Flask

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Session Security
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = False  # Set True in Prod with HTTPS
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)
    compress.init_app(app)
    cors.init_app(app, supports_credentials=True)


    # Exclude API from CSRF if using Bearer tokens, but since we use sessions,
    # we might need to handle it or exempt temporarily for dev.
    # We will exempt the api blueprint for now to avoid breaking the frontend.

    from flask_talisman import Talisman

    is_prod = os.environ.get('VERCEL') == '1'
    Talisman(app, 
             content_security_policy=None, 
             force_https=is_prod,
             strict_transport_security=is_prod)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.route("/api/health")
    def health():
        return {"status": "ok", "service": "kec_erp", "database": "connected"}

    from app.api import api as api_bp
    app.register_blueprint(api_bp)
    csrf.exempt(api_bp)
    limiter.exempt(api_bp)
    
    from app.api.init import init_bp
    app.register_blueprint(init_bp)

    from app.core import core_bp
    app.register_blueprint(core_bp)

    from app.errors import register_error_handlers
    register_error_handlers(app)

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request, jsonify, redirect, url_for
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Unauthorized'}), 401
        return redirect(url_for('auth.login'))

    @app.before_request
    def log_request_info():
        from flask import request

        print(f"REQUEST: {request.method} {request.url}")

    return app
