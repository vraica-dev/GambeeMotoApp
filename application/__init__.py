from datetime import date, datetime
from typing import Any, Optional

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def _http_error_page(error: Exception) -> tuple:
    code = getattr(error, "code", 500)
    return render_template(f"{code}.html"), code


def _human_date(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return value.strftime("%d %b %Y")
    return str(value)


def init_app() -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config.DevConfig)  # dev
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY is not set. Define it in .env (see config.py).")
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login_page"
    login_manager.session_protection = "strong"
    csrf.init_app(app)

    with app.app_context():
        from application.admin import admin_bp
        from application.auth import auth_bp
        from application.events import events_bp
        from application.main import main_bp
        from application.pics import pics_bp
        from application.trips import trips_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(trips_bp)
        app.register_blueprint(events_bp)
        app.register_blueprint(pics_bp)
        app.register_blueprint(admin_bp)

        for code in (403, 404, 405, 429, 500):
            app.register_error_handler(code, _http_error_page)
        app.add_template_filter(_human_date, "human_date")

        from application.models import Riders

        @login_manager.user_loader
        def load_user(user_id: str) -> Optional[Riders]:
            try:
                return Riders.query.filter_by(id=int(user_id)).first()
            except (ValueError, TypeError):
                return Riders.query.filter_by(email=user_id).first()

        return app
