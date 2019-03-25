import os
from uuid import uuid4

import redis
import irc.bot

from common import ListListener, Database


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, token):
        self.client_id = os.environ.get('TWITCH_BOT_CLIENT_ID')

        self.redis_server = redis.Redis.from_url(os.environ.get('REDIS_URL'))
        command_handler = ListListener(self.handle_messages, self.redis_server, ['standard_bot'])
        rejoin_handler = ListListener(self.handle_rejoins, self.redis_server, ['rejoin'])

        server = 'irc.chat.twitch.tv'
        port = 6667

        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port, token)], username, username
        )

        command_handler.start()
        rejoin_handler.start()

    def on_welcome(self, connection, event):
        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')

        if os.environ.get('DYNO') == 'standard_bot.1':
            users = [x[0] for x in Database.execute_select_sql(Database.SQL_GET_BOT_ENABLED_ROOMS)]
            for user in users:
                self.redis_server.rpush('rejoin', user)

    def on_pubmsg(self, connection, event):
        # If a chat message starts with an exclamation point, try to run it as a command
        if event.arguments[0][:1] == '!':
            command = event.arguments[0].split(' ')[0][1:].lower()
            self.do_command(event, command)
        return

    def do_command(self, event, command):
        user_id = self.get_tag(event.tags, 'user-id')
        room_id = self.get_tag(event.tags, 'room-id')
        is_mod = bool(int(self.get_tag(event.tags, 'mod')))
        active_games = self.redis_server.smembers('active_games')
        pending_games = self.redis_server.lrange('pending_games', 0, -1)
        is_active = bool([x for x in active_games if event.target.encode() == x])
        is_pending = bool([x for x in pending_games if event.target.encode() == x])
        args_list = event.arguments[0].lower().split(' ')

        if user_id == room_id or is_mod:
            if command == "start":
                if not is_active and not is_pending:
                    self.redis_server.rpush('pending_games', f'START {event.target}')
                    self.connection.privmsg(event.target, 'Guessing Game started.')
                    return
                self.connection.privmsg(event.target, 'Guessing Game already active.')
            if command == "finish":
                if is_active:
                    self.redis_server.rpush('ending_games', f'FINISH {event.target}')
                    self.connection.privmsg(event.target, 'Guessing Game finished.')
                    return
                self.connection.privmsg(event.target, 'Guessing Game not yet active')
            if command == "answer":
                if is_active and len(args_list) > 1:
                    self.answer_command(room_id, args_list[1], event.target)
        if command == "points":
            username = self.get_tag(event.tags, 'display-name').lower()
            if is_active:
                self.points_command(user_id, room_id, event.target, username, 'current_points')
            else:
                self.points_command(user_id, room_id, event.target, username, 'points')
        if command == "guess":
            if is_active and len(args_list) > 1:
                username = self.get_tag(event.tags, 'display-name').lower()
                self.guess_command(user_id, room_id, event.target, username, args_list[1])

    def answer_command(self, room_id, variation, channel_name):
        variations = [x for x in Database.execute_select_sql(Database.SQL_CURRENT_USER_VARIATIONS.format(room_id))]
        result = self.check_variations(variations, variation)
        if result:
            self.redis_server.publish(channel_name, f'ANSWER {variation}')

    def guess_command(self, user_id, room_id, channel_name, username, variation):
        participant = Database.execute_select_sql(Database.SQL_GET_PARTICIPANT.format(room_id, user_id))
        if not participant:
            channel_user_id = Database.execute_select_sql(Database.SQL_CHANNEL_USER_ID.format(room_id))[0][0]
            create_participant_sql = Database.SQL_PARTICIPANT_INSERT.format(
                uuid4(), username, user_id, channel_user_id
            )
            Database.execute_insert_update_sql(create_participant_sql)
        variations = [x for x in Database.execute_select_sql(
            Database.SQL_CURRENT_USER_VARIATIONS.format(room_id))]
        result = self.check_variations(variations, variation)
        if result:
            self.redis_server.publish(channel_name, f'GUESS {user_id} {variation}')

    def points_command(self, user_id, room_id, channel_name, username, type):
        data = Database.execute_select_sql(Database.SQL_GET_POINTS.format(f"{type}", room_id, user_id))
        if data:
            points = data[0][0]
            self.connection.privmsg(channel_name, f"{username} has {points} points in the active game.")

    def handle_messages(self, message):
        message = message.decode('utf-8')

        if 'JOIN' in message[:4]:
            self.connection.join(f'#{message[5:]}')
            self.connection.privmsg(f'#{message[5:]}', f'Welcome, {message[5:]}! Thanks for using the Guessing Game.')
        if 'PART' in message[:4]:
            self.connection.privmsg(f'#{message[5:]}', f'See you soon {message[5:]}.')
            self.connection.part(f'#{message[5:]}')

    def handle_rejoins(self, message):
        message = message.decode('utf-8')

        self.connection.join(f'#{message}')

    @staticmethod
    def check_variations(variations, user_variation):
        return [
            item for sublist in variations
            for subsublist in sublist
            for item in subsublist if item == user_variation
        ]

    @staticmethod
    def get_tag(tags, target_tag):
        for tag in tags:
            if tag['key'] == target_tag:
                return tag['value']
        return None
