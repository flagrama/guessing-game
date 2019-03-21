import threading


class TwitchBotThread(threading.Thread):
    def __init__(self, username, token):
        threading.Thread.__init__(self, daemon=True)
        self.username = username
        self.token = token

    def run(self):
        from . import TwitchBot
        bot = TwitchBot(self.username, self.token)
        bot.start()
