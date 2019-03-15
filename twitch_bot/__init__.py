import os
import threading
import urllib.parse as urlparse

import redis
import irc.bot
import psycopg2


class Listener(threading.Thread):
    def __init__(self, callback, redis, channels):
        threading.Thread.__init__(self)
        if isinstance(channels, str):
            channels = [channels]
        self.callback = callback
        self.redis = redis
        self.pubsub = self.redis.pubsub()
        for channel in channels:
            self.pubsub.subscribe(channel)

    def run(self):
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                self.callback(message['channel'], message['data'])


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        self.client_id = os.environ.get('TWITCH_BOT_CLIENT_ID')
        self.token = os.environ.get('TWITCH_BOT_TOKEN')
        self.username = os.environ.get('TWITCH_BOT_USERNAME')

        redis_server = redis.Redis.from_url(os.environ.get('REDIS_URL'))
        message_handler = Listener(self.handle_messages, redis_server, ['standard_bot'])

        server = 'irc.chat.twitch.tv'
        port = 6667

        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port, self.token)], self.username, self.username
        )

        message_handler.start()

    def on_welcome(self, connection, event):
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port

        con = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cursor = con.cursor()
        cursor.execute("SELECT twitch_login_name FROM users")
        users = cursor.fetchall()

        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')

        for user in users:
            connection.join(f'#{user}')

    def handle_messages(self, channel, data):
        data = data.decode('utf-8')

        if 'JOIN' in data[:4]:
            self.connection.join(f'#{data[5:]}')
        if 'PART' in data[:4]:
            self.connection.part(f'#{data[5:]}')


if __name__ == "__main__":
    bot = TwitchBot()
    bot.start()
