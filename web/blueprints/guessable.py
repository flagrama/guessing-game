from flask import (
    Blueprint
)


guessable = Blueprint('guessable', __name__)


@guessable.route('/')
def index():
    return "Guessable"
