import threading


class SubscriptionListener(threading.Thread):
    def __init__(self, callback, redis, keys):
        threading.Thread.__init__(self, daemon=True)
        if isinstance(keys, str):
            keys = [keys]
        self.callback = callback
        self.redis = redis
        self.pubsub = self.redis.pubsub()
        for channel in keys:
            self.pubsub.subscribe(channel)

    def run(self):
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                self.callback(message['channel'], message['data'])


class ListListener(threading.Thread):
    def __init__(self, callback, redis, key):
        threading.Thread.__init__(self, daemon=True)
        self.callback = callback
        self.redis = redis
        self.key = key

    def run(self):
        while True:
            command = self.redis.lpop(self.key)
            if command:
                self.callback(command)
