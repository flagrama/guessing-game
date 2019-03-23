from flask import (
    Blueprint, render_template, request, redirect, url_for
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
            if variation and not variation.isalnum():
                errors += ['Guessable Variations must be alphanumeric']
                break
        if errors:
            return render_template('guessable/create.html', errors=errors)

        new_guessable = Guessable()
        new_guessable.create_guessable(request.form['guessable_name'], result, current_user.id)
        return redirect(url_for('guessable.index'))
    return render_template('guessable/create.html')


@guessable.route('/edit/<uuid:uuid>', methods=['GET', 'POST'])
def update(uuid):
    if request.form:
        errors = []
        if not request.form['guessable_name'] or not request.form['guessable_variations']:
            errors += ['All fields are required']
        if not request.form['guessable_name'].isalnum():
            errors += ['Guessable Name must be alphanumeric']
        result = [x.strip() for x in request.form['guessable_variations'].split(',')]
        for variation in result:
            if variation and not variation.isalnum():
                errors += ['Guessable Variations must be alphanumeric']
                break
        if errors:
            return render_template('guessable/update.html', errors=errors)

        Guessable.update_guessable(current_user.id, uuid, request.form['guessable_name'], result)
        return redirect(url_for('guessable.index'))
    return render_template('guessable/update.html')


@guessable.route('/delete/<uuid:uuid>', methods=['POST'])
def delete(uuid):
    print(uuid, flush=True)
    Guessable.delete_guessable(current_user.id, uuid)
    return redirect(url_for('guessable.index'))


@guessable.before_request
@login_required
def login_check():
    pass

