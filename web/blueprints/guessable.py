import json

from flask import (
    Blueprint, flash, render_template, request, redirect, url_for
)
from flask_login import current_user, login_required

from web.models import Guessable


guessable = Blueprint('guessable', __name__)


@guessable.route('/')
def index():
    guessables = Guessable.get_users_guessables(current_user.id)
    return render_template('guessable/index.html', guessables=guessables)


@guessable.route('/create', methods=['GET', 'POST'])
def create():
    if request.form:
        errors = []
        if not request.form['guessable_name'] or not request.form['guessable_variations']:
            errors += ['All fields are required']
        if not request.form['guessable_name'].isalnum():
            errors += ['Guessable Name must be alphanumeric']
        result = [x.strip() for x in request.form['guessable_variations'].split(',')]
        for variation in result:
            if not variation.isalnum():
                errors += ['Guessable Variations must be alphanumeric']
                break
        if errors:
            return render_template('guessable/create.html', errors=errors)

        new_guessable = Guessable()
        new_guessable.create_guessable(request.form['guessable_name'], result, current_user.id)
        return redirect(url_for('guessable.index'))
    return render_template('guessable/create.html')


@guessable.route('/edit/<uuid:uuid>')
def update(uuid):
    pass


@guessable.route('/delete/<uuid:uuid>')
def delete(uuid):
    pass


@guessable.before_request
@login_required
def login_check():
    pass

