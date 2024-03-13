from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate
from config import config_by_name
from celery import Celery, Task
from flask_mailman import Mail

db = SQLAlchemy()
mail = Mail()

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app():
    app = Flask(__name__)

    config_name = os.getenv('FLASK_CONFIG') or 'dev'

    # Load configuration from a configuration file
    app.config.from_object(config_by_name[config_name])

    # Initialize the database with the Flask app
    db.init_app(app)

    # Initialize mail with the Flask app 
    mail.init_app(app)

    # Initialize migrate command
    migrate = Migrate(app, db)

    # Celery configuration 
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)

    # Register the blueprints for your API routes
    from app.controllers.login_controller import login_api
    from app.controllers.main_controller import main_api
    app.register_blueprint(login_api)
    app.register_blueprint(main_api)

    # Importing database models from models.py
    from app.models.admin import Admin
    from app.models.all_models import Ticket, Train

    # Create the database (if it doesn't exist)
    with app.app_context():
        db.create_all()

    return app
