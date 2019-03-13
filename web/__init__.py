import os

from flask import Flask
from flask_talisman import Talisman
from web.blueprints.main import main
from web.blueprints.authentication import authentication



def create_app():
    application = Flask(__name__)
    Talisman(application)
    application.config.from_object(os.environ['APP_SETTINGS'])
    application.register_blueprint(main)
    application.register_blueprint(authentication)

    return application
