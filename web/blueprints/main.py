from flask import (
    Blueprint, render_template, session
)

import web.twitch as twitch

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if 'twitch_display_name' not in session and 'twitch_token' in session:
        new_token, new_refresh_token, user = (
            twitch.get_users(
                session['twitch_token'],
                session['twitch_refresh_token'],
                session['twitch_login'])
        )
        if new_token and new_token != session['twitch_token']:
            session['twitch_token'] = new_token
        if new_refresh_token and new_refresh_token != session['twitch_refresh_token']:
            session['twitch_refresh_token'] = new_refresh_token
        if user:
            session['twitch_display_name'] = user['data'][0]['display_name']
    return render_template('home.html')


@main.before_request
def validate_token():
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
