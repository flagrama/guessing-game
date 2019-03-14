release: ./release-tasks.sh
web: gunicorn --config=config/gunicorn.py web.wsgi
worker: python twitch_bot/__init__.py
