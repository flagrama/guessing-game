from flask import (
    Blueprint, redirect, session, url_for
)
from flask import current_app as app

import web.twitch as twitch
from web.models import User

bot = Blueprint('bot', __name__)


@bot.route('/bot/change_status')
def change_status():
    if 'current_user' in session:
        user = User.get_user_by_id(session['current_user'])
        message = f'PART {user.twitch_login_name}'
        result = user.change_bot_enabled()
        if result:
            message = f'JOIN {user.twitch_login_name}'
        app.config['REDIS'].publish('standard_bot', message)
    return redirect(url_for('main.index'))


@bot.before_request
def validate_token():
    if 'twitch_token' in session:
        validation_json = twitch.validate_token(session['twitch_token'])
        if not validation_json:
            session.clear()
