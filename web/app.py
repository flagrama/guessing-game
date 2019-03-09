from flask import (
    Flask, Blueprint, render_template
)
from flask_talisman import Talisman

main = Blueprint('app_main', __name__)


@main.route('/')
def hello():
    return render_template('home.html')


def create_app(config='dev'):
    app = Flask(__name__)
    if not config == 'testing':
        Talisman(app)
    app.register_blueprint(main)

    return app


if __name__ == '__main__':
    create_app().run()
