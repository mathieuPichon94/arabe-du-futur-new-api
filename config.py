import os

basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE_URL = os.getenv("DATABASE_URL")  # or other relevant config var
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = "this-really-needs-to-be-changed"
    SQLALCHEMY_DATABASE_URI = DATABASE_URL



class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
