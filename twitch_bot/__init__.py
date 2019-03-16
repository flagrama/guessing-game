import os
import threading
import urllib.parse as urlparse

import redis
import irc.bot
import psycopg2


class TwitchBotThread(threading.Thread):
    def __init__(self, username, token):
        threading.Thread.__init__(self, daemon=True)
        self.username = username
        self.token = token

    def run(self):
        bot = TwitchBot(self.username, self.token)
        bot.start()


class Listener(threading.Thread):
    def __init__(self, callback, redis, channels):
        threading.Thread.__init__(self, daemon=True)
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
    def __init__(self, username, token):
        self.client_id = os.environ.get('TWITCH_BOT_CLIENT_ID')

        redis_server = redis.Redis.from_url(os.environ.get('REDIS_URL'))
        message_handler = Listener(self.handle_messages, redis_server, ['standard_bot'])

        server = 'irc.chat.twitch.tv'
        port = 6667

        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port, token)], username, username
        )

        message_handler.start()

    def on_welcome(self, connection, event):
        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')

        users = [x[0] for x in self.__execute_sql("SELECT twitch_login_name FROM users")]
        for user in users:
            connection.join(f'#{user}')
            connection.privmsg(f'#{user}', 'Hello, World!')

    def handle_messages(self, channel, data):
        data = data.decode('utf-8')

        if 'JOIN' in data[:4]:
            self.connection.join(f'#{data[5:]}')
            self.connection.privmsg(f'#{data[5:]}', f'Welcome, {data[5:]}! Thanks for using the Guessing Game.')
        if 'PART' in data[:4]:
            self.connection.privmsg(f'#{data[5:]}', f'See you soon {data[5:]}.')
            self.connection.part(f'#{data[5:]}')

    @staticmethod
    def __execute_sql(sql):
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
        cursor.execute(sql)
        data = cursor.fetchall()
        con.close()
        return data

if __name__ == "__main__":
    standard_bot = TwitchBot(os.environ.get('TWITCH_BOT_USERNAME'),
                                   os.environ.get('TWITCH_BOT_TOKEN'))
    standard_bot.start()
