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
                result = self.callback(message['channel'], message['data'])
                if result == "EXIT":
                    return


class ListListener(threading.Thread):
    def __init__(self, callback, redis, keys):
        threading.Thread.__init__(self, daemon=True)
        self.callback = callback
        self.redis = redis
        self.keys = keys

    def run(self):
        while True:
            for key in self.keys:
                command = self.redis.lpop(key)
                if command:
                    result = self.callback(command)
                    if result == "EXIT":
                        return
