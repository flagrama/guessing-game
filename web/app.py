from flask import Flask
from flask_talisman import Talisman
from web.blueprints.main import main
from web.blueprints.authentication import authentication


def create_app(config='dev'):
    app = Flask(__name__)
    if not config == 'testing':
        Talisman(app)
    app.register_blueprint(main)
    app.register_blueprint(authentication)
    app.secret_key = 'development'

    return app


if __name__ == '__main__':
    create_app().run()
