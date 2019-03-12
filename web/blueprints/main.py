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
        if not twitch.validate_token(session['twitch_token']):
            session.pop('twitch_token')
            session.pop('twitch_refresh_token')
        # elif 'twitch_refresh_token' in session:
        #     json = twitch.refresh_token(session['twitch_refresh_token'])
        #     if json is None:
        #         session.pop('twitch_token')
        #         session.pop('twitch_refresh_token')
        #     else:
        #         session['twitch_token'] = (json['access_token'])
        #         session['twitch_refresh_token'] = (json['refresh_token'])
