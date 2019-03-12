from flask import (
    Blueprint, url_for, session, redirect, flash, request
)
from flask import current_app as app

import web.twitch as twitch

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
        json = twitch.create_token(authorization_code, redirect_uri)
        if json is None:
            flash('Access denied')
        else:
            session['twitch_token'] = (json['access_token'])
            session['twitch_refresh_token'] = (json['refresh_token'])
    return redirect('/')


@authentication.route('/logout')
def logout():
    twitch.revoke_token(session.pop('twitch_token', None))
    session.pop('twitch_refresh_token', None)
    return redirect('/')
