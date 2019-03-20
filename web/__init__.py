from flask import Flask
from flask_login import LoginManager
from flask_talisman import Talisman
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config):
    application = Flask(__name__)
    application.config.from_object(config)
    if not application.config['TESTING']:
        Talisman(application)
    db.init_app(application)
    migrate.init_app(application, db)
    login_manager.login_view = 'authentication.login'
    login_manager.init_app(application)

    from web.blueprints.main import main
    application.register_blueprint(main)
    from web.blueprints.authentication import authentication
    application.register_blueprint(authentication)
    from web.blueprints.bot import bot
    application.register_blueprint(bot)

    return application


from web import models


@login_manager.user_loader
def load_user(id):
    return models.User.query.get(int(id))
