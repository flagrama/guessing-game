from flask import (
    Blueprint, render_template
)
from flask_login import login_required

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('home.html')


@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@main.route('/help')
def help():
    return render_template('help.html')
