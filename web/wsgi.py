import os
from web import create_app

application = create_app(os.environ['APP_SETTINGS'])
