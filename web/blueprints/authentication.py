from flask import (
    Blueprint, url_for, session, redirect, flash, request
)
from flask import current_app as app
from flask_login import current_user, login_user, logout_user

from web import db
import web.twitch as twitch
from web.models import User

authentication = Blueprint('authentication', __name__)


@authentication.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    session['next_url'] = request.args.get('next')
    redirect_uri = url_for('authentication.authorized', _external=True)
    return redirect(twitch.authorize(redirect_uri, app.config['TWITCH_STATE']))


@authentication.route('/login/authorized')
def authorized():
    redirect_uri = url_for('authentication.authorized', _external=True)
    authorization_code = request.args.get('code')
    csrf_state = request.args.get('state')
    if csrf_state != app.config['TWITCH_STATE']:
        flash('Access denied')
        return redirect('/')
    if authorization_code:
        create_json = twitch.create_token(authorization_code, redirect_uri)
        if create_json is None:
            flash('Access denied')
        else:
            session['twitch_token'] = (create_json['access_token'])
            session['twitch_refresh_token'] = (create_json['refresh_token'])
            result = __login_user(session['twitch_token'], session['twitch_refresh_token'])
            if not result:
                twitch.revoke_token(create_json['access_token'])
                session.clear()
    redirect_url = session.pop('next_url') if session['next_url'] else '/'
    return redirect(redirect_url)


@authentication.route('/logout')
def logout():
    logout_user()
    twitch.revoke_token(session.pop('twitch_token', None))
    session.clear()
    return redirect('/')


def __login_user(token, refresh_token):
    validation_json = twitch.validate_token(token)
    twitch_login = validation_json['login']
    new_token, new_refresh_token, twitch_user = (
        twitch.get_users(token, refresh_token, twitch_login))
    if new_token and new_token != token:
        session['twitch_token'] = new_token
    if new_refresh_token and new_refresh_token != refresh_token:
        session['twitch_refresh_token'] = new_refresh_token
    if twitch_user:
        session['twitch_user_id'] = (validation_json['user_id'])
        # Attempt to find a user associated with the returned twitch user id
        user = User.get_user_by_twitch_id(session['twitch_user_id'])
        if user:
            login_user(user)
            return True
        # Create User in database since we couldn't find an existing account associated with this twitch user id
        user = User(
            session['twitch_user_id'],
            twitch_login,
            twitch_user['data'][0]['display_name']
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return True
    return False
