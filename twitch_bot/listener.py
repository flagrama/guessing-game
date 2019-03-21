import threading


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
