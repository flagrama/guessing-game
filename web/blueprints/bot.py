from flask import (
    Blueprint, redirect, url_for
)
from flask import current_app as app
from flask_login import current_user, login_required


bot = Blueprint('bot', __name__)


@bot.route('/bot/change_status', methods=['POST'])
def change_status():
    message = f'PART {current_user.twitch_login_name}'
    result = current_user.change_bot_enabled()
    if result:
        for whitelist_user in current_user.whitelist:
            app.config['REDIS'].sadd('WHITELIST_' + str(current_user.twitch_id), str(whitelist_user))
        message = f'JOIN {current_user.twitch_login_name}'
    else:
        app.config['REDIS'].delete('WHITELIST_' + str(current_user.twitch_id))
    app.config['REDIS'].rpush('standard_bot', message)
    return redirect(url_for('main.dashboard'))


@bot.before_request
@login_required
def login_check():
    pass
