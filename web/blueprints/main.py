from flask import (
    Blueprint, render_template, session
)

import web.twitch as twitch
from web.models import User

main = Blueprint('main', __name__)


@main.route('/')
def index():
    user = None
    if 'twitch_user_id' in session:
        user = User.get_user_by_twitch_id(session['twitch_user_id'])
    return render_template('home.html', user=user)


@main.before_request
def validate_token():
    if 'twitch_token' in session:
        validation_json = twitch.validate_token(session['twitch_token'])
        if not validation_json:
            session.clear()
