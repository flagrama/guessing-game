from flask import (
    Blueprint, render_template, request, redirect, url_for
)
from flask_login import current_user, login_required

from web.models import User


guessable = Blueprint('guessable', __name__)


@guessable.route('/')
def index():
    guessables = User.get_guessables(current_user.id)
    print(guessables, flush=True)
    return render_template('guessable/index.html')


@guessable.route('/create', methods=['GET', 'POST'])
def create():
    if request.form:
        return redirect(url_for('guessable.index'))
    return render_template('guessable/create.html')


@guessable.before_request
@login_required
def login_check():
    pass

