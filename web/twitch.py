import requests

import web.config as config


class Twitch:
    def __init__(self):
        self.twitch_base = "https://id.twitch.tv/oauth2"
        self.client_id = f"client_id={config.TWITCH_CLIENT_ID}"
        self.client_secret = f"client_secret={config.TWITCH_SECRET}"
        self.response_type = "response_type=code"
        self.scope = "scope=user_read"
        self.grant_type = "grant_type=authorization_code"

    def validate_token(self, token):
        response = requests.get(self.twitch_base + '/validate', headers={'Authorization': f'OAuth {token}'})
        if response.status_code != 200:
            return False
        return True
