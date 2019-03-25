import os

import redis

from common import ListListener, SubscriptionListener, Database


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
            update_participant_sql = f"UPDATE participants SET current_points=0 FROM users WHERE participants.user_id=users.id AND users.twitch_login_name='{command[1].split('#')[1]}'"
            Database.execute_insert_update_sql(update_participant_sql)


class GuessingGame(object):
    def __init__(self, channel):
        self.redis_server = redis.Redis.from_url(os.environ.get('REDIS_URL'))
        commands_handler = SubscriptionListener(self.handle_commands, self.redis_server, [channel])
        commands_handler.start()

    def handle_commands(self, channel, data):
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
                if guess.decode('utf-8') == guessable:
                    user_id = user_id.decode('utf-8')
                    get_participant_sql = f"SELECT points, current_points FROM participants JOIN users ON participants.user_id=users.id WHERE users.twitch_login_name='{channel.split('#')[1]}' AND participants.twitch_id={user_id}"
                    points, current_points = Database.execute_select_sql(get_participant_sql)[0]
                    update_participant_sql = f"UPDATE participants SET points={points + 1} FROM users WHERE participants.user_id=users.id AND users.twitch_login_name='{channel.split('#')[1]}' AND participants.twitch_id={user_id}"
                    Database.execute_insert_update_sql(update_participant_sql)
                    update_participant_sql = f"UPDATE participants SET current_points={current_points + 1} FROM users WHERE participants.user_id=users.id AND users.twitch_login_name='{channel.split('#')[1]}' AND participants.twitch_id={user_id}"
                    Database.execute_insert_update_sql(update_participant_sql)
                    self.redis_server.hdel(f'{channel}_guesses', user_id)
