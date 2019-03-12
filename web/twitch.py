import json
import requests
from urllib.parse import quote

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
        return None
    return json.loads(response.text)


def revoke_token(token):
    requests.post(twitch_base + '/revoke'
                  + f"?client_id={config.TWITCH_CLIENT_ID}"
                  + f"&token={token}")


def refresh_token(token_refresh_token):
    response = requests.post(twitch_base + '/token'
                             + f"?grant_type=refresh_token"
                             + f"&refresh_token={quote(token_refresh_token)}"
                             + f"&client_id={config.TWITCH_CLIENT_ID}"
                             + f"&client_secret={config.TWITCH_SECRET}")
    if response is None:
        return None, None
    refresh_json = json.loads(response.text)
    return refresh_json['access_token'], refresh_json['refresh_token']


def get_users(token, refresh, user_names, allow_refresh=True):
    if isinstance(user_names, str):
        user_names = [user_names]
    parameters = f'?login={user_names[0]}'
    # for user in user_names[1:]:           # If querying multiple users
    #     parameters += f'&login={user}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(twitch_base + '/users' + parameters, headers=headers)
    if response is None:
        return None, None, None
    if response.status_code == 401 and 'www-authenticate' in response.headers and allow_refresh:
        token, refresh = refresh_token(refresh)
        if token is None or refresh is None:
            return None, None, None
        return get_users(token, refresh, user_names, allow_refresh=False)
    return token, refresh, json.loads(response.text)

