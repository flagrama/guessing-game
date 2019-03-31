import os

import redis

from common import ListListener, SubscriptionListener
from web import create_app
from web.models import User, Guessable, Participant, Result


class GuessingGameManager(object):
    def __init__(self):
        self.redis_server = redis.Redis.from_url(os.environ.get('REDIS_URL'))
        guessing_game_manager = ListListener(
            self.handle_guessing_games, self.redis_server, ['pending_games', 'ending_games']
        )
        guessing_game_manager.start()

    def handle_guessing_games(self, message):
        message = message.decode('utf-8')
        command = message.split(' ')
        if command[0] == "START":
            GuessingGame(command[1])
            self.redis_server.sadd('active_games', command[1])
        if command[0] == "FINISH":
            self.redis_server.publish(command[1], 'FINISH')
            self.redis_server.srem('active_games', command[1])
            self.redis_server.delete(f'{command[1]}_guesses')
            self.redis_server.delete(command[1])
        if command[0] == "RESUME":
            GuessingGame(command[1])


class GuessingGame(object):
    def __init__(self, channel):
        self.redis_server = redis.Redis.from_url(os.environ.get('REDIS_URL'))
        commands_handler = SubscriptionListener(self.handle_commands, self.redis_server, [channel])
        commands_handler.start()

    def handle_commands(self, channel, data):
        create_app('web.config.DatabaseOnlyConfig').app_context().push()
        data = data.decode('utf-8').split(' ')
        channel = channel.decode('utf-8')
        command = data[0]
        if command == "GUESS":
            if len(data) < 3:
                return
            user_id = data[1]
            guessable = data[2]
            self.redis_server.hset(f'{channel}_guesses', user_id, guessable)
        if command == "ANSWER":
            if len(data) < 2:
                return
            guessable = data[1]
            guesses = self.redis_server.hgetall(f'{channel}_guesses')
            for user_id, guess in guesses.items():
                channel_user_id = User.get_user_by_twitch_login_name(channel.split('#')[1]).twitch_id
                variations = Guessable.get_all_users_variations(channel_user_id)
                current_variations = [item for sublist in variations for item in sublist if guessable in item]
                if [item[0] for item in current_variations if guess.decode('utf-8') in item]:
                    user_id = user_id.decode('utf-8')
                    user_points = self.redis_server.hget(f'{channel}_points', user_id)
                    if not user_points:
                        user_points = '0'.encode()
                    self.redis_server.hset(f'{channel}_points', user_id, int(user_points.decode('utf-8')) + 1)
                    self.redis_server.hdel(f'{channel}_guesses', user_id)
        if command == "FINISH":
            all_user_points = self.redis_server.hgetall(f'{channel}_points')
            all_user_points = {key.decode(): val.decode() for key, val in all_user_points.items()}
            channel_user = User.get_user_by_twitch_login_name(channel.split('#')[1])
            if all_user_points:
                result = Result()
                result.create_result(all_user_points, channel_user.id)
            for user in all_user_points:
                user_points = self.redis_server.hget(f'{channel}_points', user)
                user_points = int(user_points.decode('utf-8'))
                participant = Participant.get_participant_by_twitch_ids(channel_user.twitch_id, user)
                participant.add_points(user_points)
                self.redis_server.hdel(f'{channel}_points', user)
            return "EXIT"
