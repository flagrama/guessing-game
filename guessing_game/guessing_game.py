import os

import redis

from common import ListListener, SubscriptionListener


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
            self.redis_server.delete(command[1])


class GuessingGame(object):
    def __init__(self, channel):
        self.redis_server = redis.Redis.from_url(os.environ.get('REDIS_URL'))
        commands_handler = SubscriptionListener(self.handle_commands, self.redis_server, [channel])
        commands_handler.start()

    def handle_commands(self, message):
        command = message.decode('utf-8')
