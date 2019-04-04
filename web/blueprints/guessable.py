from flask import (
    Blueprint, flash, render_template, request, redirect, url_for
)
from flask_login import current_user, login_required

from web.models import Guessable

guessable = Blueprint('guessable', __name__)


@guessable.route('/')
def index():
    guessables = current_user.get_user_guessables()
    return render_template('guessable/index.html', guessables=guessables)


@guessable.route('/create', methods=['GET', 'POST'])
def create():
    if current_user.count_user_guessables() >= 30:
        flash('You already have the maximum number of guessables', 'info')
        return redirect(url_for('guessable.index'))
    if request.form:
        name, variations, errors = validate_input(
            request.form['guessable_name'], request.form['guessable_variations'], None
        )
        if errors:
            return render_template(
                'guessable/create.html',
                name=request.form['guessable_name'],
                variations=request.form['guessable_variations'],
                errors=errors)
        new_guessable = Guessable()
        new_guessable.create_guessable(name, variations, current_user.id)
        return redirect(url_for('guessable.index'))
    return render_template('guessable/create.html')


@guessable.route('/edit/<uuid:uuid>', methods=['GET', 'POST'])
def update(uuid):
    current_guessable = Guessable.get_guessable_by_uuid(uuid, current_user.id)
    ','.join(current_guessable.variations)
    if request.form:
        name, variations, errors = validate_input(
            request.form['guessable_name'], request.form['guessable_variations'], uuid
        )
        if errors:
            return render_template(
                'guessable/update.html',
                name=request.form['guessable_name'],
                variations=request.form['guessable_variations'],
                errors=errors
            )
        current_guessable = current_user.get_user_guessable(uuid)
        current_guessable.update_guessable(name, variations)
        return redirect(url_for('guessable.index'))
    return render_template('guessable/update.html', name=current_guessable.name, variations=variations)


@guessable.route('/delete/<uuid:uuid>', methods=['POST'])
def delete(uuid):
    current_guessable = current_user.get_user_guessable(uuid)
    current_guessable.delete_guessable()
    return redirect(url_for('guessable.index'))


def validate_input(name, variations, uuid):
    errors = []
    if not name or not variations:
        errors += ['All fields are required']
    if not all(x.isalnum() or x.isspace() for x in name):
        errors += ['Guessable Name must be alphanumeric']
    result = ensure_variations_unique_per_user(variations, uuid)
    if not result:
        errors += ['Guessable Variations cannot be empty. Duplicates and non-unique values are automatically removed.']
    for variation in result:
        if variation and not variation.isalnum():
            errors += ['Guessable Variations must be alphanumeric']
            break
    return name, result, errors


def ensure_variations_unique_per_user(variations, uuid=None):
    guessables = current_user.get_all_user_guessables()
    existing_variations = [item for sublist in guessables for item in sublist.variations if sublist.uuid != uuid]
    result = []
    [result.append(x.strip().lower()) for x in variations.split(',') if x not in result and x not in existing_variations]
    return result


@guessable.before_request
@login_required
def login_check():
    pass

