from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate
from config import config_by_name
from werkzeug.security import generate_password_hash  

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    config_name = os.getenv('FLASK_CONFIG') or 'dev'

    print(os.getenv('FLASK_CONFIG'))
    # Load configuration from a configuration file
    app.config.from_object(config_by_name[config_name])

    # Initialize the database with the Flask app
    db.init_app(app)

    # Initialize migrate command
    migrate = Migrate(app, db)

    # Register the blueprints for your API routes
    from app.controllers.login_controller import login_api
    from app.controllers.main_controller import main_api
    app.register_blueprint(login_api)
    app.register_blueprint(main_api)

    # Importing database models from models.py
    from app.models.admin import Admin
    # from app.models.transactions import Transaction

    # Custom CLI command to create an admin user

    # Create the database (if it doesn't exist)
    with app.app_context():
        db.create_all()

    return app

