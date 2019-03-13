import os

from flask import Flask
from flask_talisman import Talisman
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app(config):
    application = Flask(__name__)
    application.config.from_object(config)
    if not application.config['TESTING']:
        Talisman(application)
    db.init_app(application)
    migrate.init_app(application, db)

    from web.blueprints.main import main
    application.register_blueprint(main)
    from web.blueprints.authentication import authentication
    application.register_blueprint(authentication)

    return application


from web import models
