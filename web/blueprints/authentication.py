import json

from flask import (
    Blueprint, url_for, session, redirect, flash, request
)
from flask import current_app as app
import requests

from web.twitch import Twitch

authentication = Blueprint('authentication', __name__)


@authentication.route('/login')
def login():
    redirect_uri = f"redirect_uri={url_for('authentication.authorized', _external=True)}"
    state = f"state={app.secret_key}"
    authorization_uri = (
            Twitch.twitch_base + '/authorize?' + Twitch.client_id
            + '&' + redirect_uri
            + '&' + Twitch.response_type
            + '&' + Twitch.scope
            + '&' + state
    )
    return redirect(authorization_uri)


@authentication.route('/login/authorized')
def authorized():
    redirect_uri = f"redirect_uri={url_for('authentication.authorized', _external=True)}"
    authorization_code = request.args.get('code')
    csrf_state = request.args.get('state')
    if csrf_state != app.secret_key:
        flash('Access denied')
        return redirect('/')
    if authorization_code:
        token_uri = (
            Twitch.twitch_base + '/token?' + Twitch.client_id
            + '&' + Twitch.client_secret
            + '&' + f"code={authorization_code}"
            + '&' + Twitch.grant_type
            + '&' + redirect_uri
        )
        resp = requests.post(token_uri)
        if resp is None:
            flash('Access denied')
        else:
            resp = json.loads(resp.text)
            session['twitch_token'] = (resp['access_token'])
    return redirect('/')


@authentication.route('/logout')
def logout():
    session.pop('twitch_token', None)
    return redirect('/')
