from flask import (
    Blueprint, redirect, url_for
)
from flask import current_app as app
from flask_login import current_user


bot = Blueprint('bot', __name__)


@bot.route('/bot/change_status', methods=['POST'])
def change_status():
    message = f'PART {current_user.twitch_login_name}'
    result = current_user.change_bot_enabled()
    if result:
        message = f'JOIN {current_user.twitch_login_name}'
    app.config['REDIS'].publish('standard_bot', message)
    return redirect(url_for('main.dashboard'))
