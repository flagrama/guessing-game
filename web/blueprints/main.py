from flask import (
    Blueprint, render_template, session
)

from web.twitch import Twitch

main = Blueprint('main', __name__)


@main.route('/')
def hello():
    return render_template('home.html')


@main.before_request
def validate_token():
    if 'twitch_token' in session:
        if not Twitch().validate_token(session['twitch_token']):
            session.pop('twitch_token')
