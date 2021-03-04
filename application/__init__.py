from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        from application import routes
        db.create_all()

        return app