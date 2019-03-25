import os

import redis
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    SECRET_KEY = os.environ['SECRET_KEY']
    TWITCH_STATE = os.environ['TWITCH_STATE']
    TWITCH_CLIENT_ID = os.environ['TWITCH_CLIENT_ID']
    TWITCH_SECRET = os.environ['TWITCH_SECRET']
    SQLALCHEMY_DATABASE_URI = DATABASE_URL = os.environ['DATABASE_URL']

    REDIS = redis.Redis.from_url(os.environ['REDIS_URL'])
    TWITCH_BOT_USERNAME = os.environ['TWITCH_BOT_USERNAME']
    TWITCH_BOT_TOKEN = os.environ['TWITCH_BOT_TOKEN']


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
    SQLALCHEMY_DATABASE_URI = DATABASE_URL = 'sqlite:///:memory:'
