import os

import redis
import irc.bot

from common import ListListener
from web import create_app, twitch
from web.models import User, Guessable, Participant

create_app('web.config.DatabaseOnlyConfig').app_context().push()


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, token):
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
        connection.cap('REQ', 'twitch.tv/membership', 'twitch.tv/tags', 'twitch.tv/commands')

        if os.environ.get('DYNO') == 'standard_bot.1':
            users = User.get_all_users_with_bot_enabled()
            for user in users:
                self.redis_server.rpush('rejoin', user.twitch_login_name)
            in_progress_games = self.redis_server.smembers('active_games')
            for game in in_progress_games:
                self.redis_server.rpush('pending_games', f"RESUME {game.decode('utf-8')}")

    def on_pubmsg(self, connection, event):
        # If a chat message starts with an exclamation point, try to run it as a command
        if event.arguments[0][:1] == '!':
            command = event.arguments[0].split(' ')[0][1:].lower()
            self.do_command(event, command)
        return

    def do_command(self, event, command):
        user_id = self.get_tag(event.tags, 'user-id')
        room_id = self.get_tag(event.tags, 'room-id')
        is_whitelist = self.redis_server.sismember('WHITELIST_' + room_id, user_id)
        is_mod = bool(int(self.get_tag(event.tags, 'mod')))
        active_games = self.redis_server.smembers('active_games')
        pending_games = self.redis_server.lrange('pending_games', 0, -1)
        is_active = bool([x for x in active_games if event.target.encode() == x])
        is_pending = bool([x for x in pending_games if event.target.encode() == x])
        args_list = event.arguments[0].lower().split(' ')

        if user_id == room_id or is_mod:
            if command == "whitelist":
                if len(args_list) > 1:
                    new_user = twitch.client_get_users_by_login(args_list[1])
                    if len(new_user['data']) == 0:
                        self.connection.privmsg(event.target, f'User {args_list[1]} not found on Twitch.')
                        return
                    new_user_id = new_user['data'][0]['id']
                    if self.redis_server.sismember('WHITELIST_' + room_id, new_user_id):
                        self.connection.privmsg(event.target, f'User {args_list[1]} is already in whitelist.')
                        return
                    self.redis_server.sadd('WHITELIST_' + room_id, new_user_id)
                    user = User.get_user_by_twitch_id(room_id)
                    user.add_to_whitelist(new_user_id)
                    self.connection.privmsg(event.target, f'User {args_list[1]} has been added to whitelist.')
            if command == "remwhitelist":
                if len(args_list) > 1:
                    new_user = twitch.client_get_users_by_login(args_list[1])
                    if len(new_user['data']) == 0:
                        self.connection.privmsg(event.target, f'User {args_list[1]} not found on Twitch.')
                        return
                    new_user_id = new_user['data'][0]['id']
                    if not self.redis_server.sismember('WHITELIST_' + room_id, new_user_id):
                        self.connection.privmsg(event.target, f'User {args_list[1]} is not in the whitelist.')
                        return
                    self.redis_server.srem('WHITELIST_' + room_id, new_user_id)
                    user = User.get_user_by_twitch_id(room_id)
                    user.remove_from_whitelist(new_user_id)
                    self.connection.privmsg(event.target, f'User {args_list[1]} has been removed from whitelist.')
        if user_id == room_id or is_mod or is_whitelist:
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
        variations = Guessable.get_all_users_variations(room_id)
        result = self.check_variations(variations, variation)
        if result:
            self.redis_server.publish(channel_name, f'ANSWER {variation}')

    def guess_command(self, user_id, room_id, channel_name, username, variation):
        participant = Participant.get_participant_by_twitch_ids(room_id, user_id)
        if not participant:
            participant = Participant()
            channel_user_id = User.get_user_by_twitch_id(room_id).id
            participant.create_participant(username, user_id, channel_user_id)
        variations = Guessable.get_all_users_variations(room_id)
        result = self.check_variations(variations, variation)
        if result:
            self.redis_server.publish(channel_name, f'GUESS {user_id} {variation}')

    def points_command(self, user_id, room_id, channel_name, username, point_type):
        if point_type == "current_points":
            user_points = self.redis_server.hget(f'{channel_name}_points', user_id)
            if not user_points:
                user_points = '0'.encode()
            user_points = user_points.decode('utf-8')
            self.connection.privmsg(channel_name, f"{username} has {user_points} points in the active game.")
        else:
            data = Participant.get_participant_points_by_twitch_ids(room_id, user_id)
            if data:
                self.connection.privmsg(channel_name, f"{username} has {data} points.")

    def handle_messages(self, message):
        message = message.decode('utf-8')

        if 'JOIN' in message[:4]:
            self.connection.join(f'#{message[5:]}')
            self.connection.privmsg(f'#{message[5:]}', f'Welcome, {message[5:]}! Thanks for using the Guessing Game.')
        if 'PART' in message[:4]:
            self.connection.privmsg(f'#{message[5:]}', f'See you soon {message[5:]}.')
            self.connection.part(f'#{message[5:]}')

    def handle_rejoins(self, message):
        create_app('web.config.DatabaseOnlyConfig').app_context().push()
        message = message.decode('utf-8')

        self.connection.join(f'#{message}')
        user = User.get_user_by_twitch_login_name(message)
        for whitelist_user in user.whitelist:
            self.redis_server.sadd('WHITELIST_' + str(user.twitch_id), str(whitelist_user))

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
