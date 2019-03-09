from flask import (
    Flask, Blueprint, render_template, redirect, session
)
from flask_talisman import Talisman

main = Blueprint('app_main', __name__)


@main.route('/')
def hello():
    return render_template('home.html')


@main.route('/login')
def login():
    session['twitch_token'] = True
    return redirect('/')


def create_app(config='dev'):
    app = Flask(__name__)
    if not config == 'testing':
        Talisman(app)
    app.register_blueprint(main)
    app.secret_key = 'development'

    return app


if __name__ == '__main__':
    create_app().run()
