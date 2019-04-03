from flask import (
    Blueprint, render_template, session
)
from flask_login import current_user, login_required

from web.models import Result
from web.twitch import get_users_by_id

results = Blueprint('results', __name__)


@results.route('/')
def index():
    results = current_user.get_user_results()
    return render_template('results/index.html', results=results)


@results.route('/<uuid:uuid>')
def read(uuid):
    results = {}
    users = []
    result = current_user.get_user_result(uuid)
    for key, value in result.results.items():
        users.append(key)
        results[key] = {'points': value}
    response = get_users_by_id(session['twitch_token'], session['twitch_refresh_token'], users)
    for user in response[2]['data']:
        results[user['id']]['name'] = user['display_name']
    return render_template('results/read.html', result=result, results=results)


@results.before_request
@login_required
def login_check():
    pass
