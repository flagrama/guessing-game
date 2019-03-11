from flask import (
    Blueprint, render_template, redirect, session
)

authentication = Blueprint('authentication', __name__)


@authentication.route('/login')
def login():
    session['twitch_token'] = True
    return redirect('/')
