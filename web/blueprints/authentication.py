from flask import (
    Blueprint, url_for, session, redirect, flash, request
)
from flask import current_app as app

from web import db
import web.twitch as twitch
from web.models import User

authentication = Blueprint('authentication', __name__)


@authentication.route('/login')
def login():
    redirect_uri = url_for('authentication.authorized', _external=True)
    return redirect(twitch.authorize(redirect_uri, app.secret_key))


@authentication.route('/login/authorized')
def authorized():
    redirect_uri = url_for('authentication.authorized', _external=True)
    authorization_code = request.args.get('code')
    csrf_state = request.args.get('state')
    if csrf_state != app.secret_key:
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
    return redirect('/')


@authentication.route('/logout')
def logout():
    twitch.revoke_token(session.pop('twitch_token', None))
    session.clear()
    return redirect('/')


def __login_user(token, refresh_token):
    validation_json = twitch.validate_token(token)
    twitch_login = validation_json['login']
    new_token, new_refresh_token, user = (
        twitch.get_users(token, refresh_token, twitch_login))
    if new_token and new_token != token:
        session['twitch_token'] = new_token
    if new_refresh_token and new_refresh_token != refresh_token:
        session['twitch_refresh_token'] = new_refresh_token
    if user:
        session['twitch_user_id'] = (validation_json['user_id'])
        if User.get_user_by_twitch_id(session['twitch_user_id']):
            return True
        user = User(
            session['twitch_user_id'],
            twitch_login,
            user['data'][0]['display_name']
        )
        db.session.add(user)
        db.session.commit()
        message = f'JOIN {twitch_login}'
        app.config['REDIS'].publish('standard_bot', message)
        return True
    return False
