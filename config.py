import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'ujwrawjhdf'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.fastmail.com'
    MAIL_PORT =  465
    MAIL_USERNAME = 'ticket_booking@fastmail.com'
    MAIL_PASSWORD =  '6jhcgxpy8gqzd6zr'
    MAIL_USE_TLS = False 
    MAIL_USE_SSL = True 


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    'dev':DevelopmentConfig,
    'test':TestingConfig,
    'prod':ProductionConfig
}