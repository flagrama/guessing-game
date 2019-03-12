import json
import requests

import web.config as config


twitch_base = "https://id.twitch.tv/oauth2"
scope = "user_read"


def authorize(redirect_uri, state):
    return (twitch_base + '/authorize'
            + f"?client_id={config.TWITCH_CLIENT_ID}"
            + f"&redirect_uri={redirect_uri}"
            + f"&response_type=code"
            + f"&scope={scope}"
            + f"&state={state}")


def create_token(authorization_code, redirect_uri):
    response = requests.post(twitch_base + '/token'
                             + f"?client_id={config.TWITCH_CLIENT_ID}"
                             + f"&client_secret={config.TWITCH_SECRET}"
                             + f"&code={authorization_code}"
                             + f"&grant_type=authorization_code"
                             + f"&redirect_uri={redirect_uri}")
    if response is None:
        return None
    return json.loads(response.text)


def validate_token(token):
    response = requests.get(twitch_base + '/validate', headers={'Authorization': f'OAuth {token}'})
    if response.status_code != 200:
        return False
    return True


def revoke_token(token):
    requests.post(twitch_base + '/revoke'
                  + f"?client_id={config.TWITCH_CLIENT_ID}"
                  + f"&token={token}")
