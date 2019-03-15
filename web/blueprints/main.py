from flask import (
    Blueprint, render_template, session, redirect, url_for
)

import web.twitch as twitch
from web.models import User

main = Blueprint('main', __name__)


@main.route('/')
def index():
    user = None
    if 'twitch_user_id' in session:
        user = User.get_user_by_twitch_id(session['twitch_user_id'])
        if not user:
            return redirect(url_for('authentication.logout'))
    return render_template('home.html', user=user)


@main.before_request
def validate_token():
    if 'twitch_token' in session:
        validation_json = twitch.validate_token(session['twitch_token'])
        if not validation_json:
            session.clear()
