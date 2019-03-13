import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    SECRET_KEY = os.environ['SECRET_KEY']
    TWITCH_CLIENT_ID = os.environ['TWITCH_CLIENT_ID']
    TWITCH_SECRET = os.environ['TWITCH_SECRET']


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
