release: ./release-tasks.sh
web: gunicorn --config=config/gunicorn.py web.wsgi --reload
standard_bot: python -m twitch_bot
worker: python guessing_game/__init__.py
