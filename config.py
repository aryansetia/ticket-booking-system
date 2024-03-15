import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'ujwrawjhdf'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT =  os.environ.get('MAIL_PORT')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD =  os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = False 
    MAIL_USE_SSL = True 


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    'dev':DevelopmentConfig,
    'test':TestingConfig,
    'prod':ProductionConfig
}