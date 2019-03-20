from flask import (
    Blueprint, redirect, session, url_for
)
from flask import current_app as app
from flask_login import login_required, logout_user, current_user

import web.twitch as twitch

bot = Blueprint('bot', __name__)


@bot.route('/bot/change_status')
def change_status():
    message = f'PART {current_user.twitch_login_name}'
    result = current_user.change_bot_enabled()
    if result:
        message = f'JOIN {current_user.twitch_login_name}'
    app.config['REDIS'].publish('standard_bot', message)
    return redirect(url_for('main.index'))


@bot.before_request
@login_required
def validate_token():
    if 'twitch_token' in session:
        validation_json = twitch.validate_token(session['twitch_token'])
        if not validation_json:
            logout_user()
            session.clear()
