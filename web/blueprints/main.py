from flask import (
    Blueprint, render_template, session
)

import web.twitch as twitch

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('home.html')


@main.before_request
def validate_token():
    if 'twitch_token' in session:
        validation_json = twitch.validate_token(session['twitch_token'])
        if not validation_json:
            session.clear()
