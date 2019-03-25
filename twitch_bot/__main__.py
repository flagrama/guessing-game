import os

from . import TwitchBot

standard_bot = TwitchBot(os.environ.get('TWITCH_BOT_USERNAME'),
                         os.environ.get('TWITCH_BOT_TOKEN'))
standard_bot.start()
