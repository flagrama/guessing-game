from flask import (
    Blueprint, render_template, session
)

import web.twitch as twitch

main = Blueprint('main', __name__)


@main.route('/')
def hello():
    return render_template('home.html')


@main.before_request
def validate_and_refresh_token():
    if 'twitch_token' in session:
        validation_json = twitch.validate_token(session['twitch_token'])
        if not validation_json:
            session.pop('twitch_token')
            session.pop('twitch_refresh_token')
            session.pop('twitch_login', None)
            session.pop('twitch_user_id', None)
        else:
            session['twitch_login'] = validation_json['login']
            session['twitch_user_id'] = validation_json['user_id']
        # elif 'twitch_refresh_token' in session:
        #     json = twitch.refresh_token(session['twitch_refresh_token'])
        #     if json is None:
        #         session.pop('twitch_token')
        #         session.pop('twitch_refresh_token')
        #     else:
        #         session['twitch_token'] = (json['access_token'])
        #         session['twitch_refresh_token'] = (json['refresh_token'])
