from flask import Flask, session
from flaskext.csrf import csrf
from flask_login import LoginManager
from flask_talisman import Talisman
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from web import twitch

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config):
    application = Flask(__name__)
    application.config.from_object(config)
    if not application.config['TESTING'] and not application.config['DB_ONLY']:
        Talisman(application)
    db.init_app(application)
    if not application.config['DB_ONLY']:
        migrate.init_app(application, db)
        login_manager.login_view = 'authentication.login'
        login_manager.login_message = None
        login_manager.init_app(application)
        csrf(application)

        from web.blueprints.main import main
        application.register_blueprint(main)
        from web.blueprints.authentication import authentication
        application.register_blueprint(authentication)
        from web.blueprints.bot import bot
        application.register_blueprint(bot)
        from web.blueprints.guessable import guessable
        application.register_blueprint(guessable, url_prefix="/guessables")
        from web.blueprints.results import results
        application.register_blueprint(results, url_prefix="/results")

        @application.before_request
        def validate_token():
            if 'twitch_token' in session:
                validation_json = twitch.validate_token(session['twitch_token'])
                if not validation_json:
                    session.clear()

    return application


from web import models


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))
