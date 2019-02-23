from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app)


@app.route('/')
def hello():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run()
