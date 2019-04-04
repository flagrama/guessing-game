import json
import os
import requests
from urllib.parse import quote

from flask import current_app as app

twitch_auth_base = "https://id.twitch.tv/oauth2"
twitch_api_base = "https://api.twitch.tv/helix"
scope = "user_read"


def authorize(redirect_uri, state):
    return (twitch_auth_base + '/authorize'
            + f"?client_id={app.config['TWITCH_CLIENT_ID']}"
            + f"&redirect_uri={redirect_uri}"
            + f"&response_type=code"
            + f"&scope={scope}"
            + f"&state={state}")


def create_token(authorization_code, redirect_uri):
    response = requests.post(twitch_auth_base + '/token'
                             + f"?client_id={app.config['TWITCH_CLIENT_ID']}"
                             + f"&client_secret={app.config['TWITCH_SECRET']}"
                             + f"&code={authorization_code}"
                             + f"&grant_type=authorization_code"
                             + f"&redirect_uri={redirect_uri}")
    if response is None:
        return None
    return json.loads(response.text)


def validate_token(token):
    response = requests.get(twitch_auth_base + '/validate', headers={'Authorization': f'OAuth {token}'})
    if response.status_code != 200:
        return None
    return json.loads(response.text)


def revoke_token(token):
    requests.post(twitch_auth_base + '/revoke'
                  + f"?client_id={app.config['TWITCH_CLIENT_ID']}"
                  + f"&token={token}")


def refresh_token(token_refresh_token):
    response = requests.post(twitch_auth_base + '/token'
                             + f"?grant_type=refresh_token"
                             + f"&refresh_token={quote(token_refresh_token)}"
                             + f"&client_id={app.config['TWITCH_CLIENT_ID']}"
                             + f"&client_secret={app.config['TWITCH_SECRET']}")
    if response is None:
        return None, None
    refresh_json = json.loads(response.text)
    return refresh_json['access_token'], refresh_json['refresh_token']


def get_users_by_login(token, refresh, user_names, allow_refresh=True):
    if not isinstance(user_names, list):
        user_names = [user_names]
    param_list = []
    data = {'data': []}
    parameters = {'login': []}
    for user in user_names:
        user = user.lower()
        cached_user = app.config['REDIS'].get('TWITCH_API_' + user)
        if cached_user:
            data['data'].append(json.loads(cached_user.decode('utf-8')))
            continue
        param_list.append(user)
    if param_list:
        headers = {'Authorization': f'Bearer {token}'}
        for i in range(0, len(param_list), 100):
            parameters['login'].append(param_list[i:i + 100])
            response = requests.get(twitch_api_base + '/users', params=parameters, headers=headers)
            if response is None:
                return None, None, None
            if response.status_code == 401 and 'www-authenticate' in response.headers and allow_refresh:
                token, refresh = refresh_token(refresh)
                if token is None or refresh is None:
                    return None, None, None
                return get_users_by_login(token, refresh, user_names, allow_refresh=False)
            response_json = json.loads(response.text)
            [app.config['REDIS'].setex('TWITCH_API_' + x['login'], 86400, json.dumps(x)) for x in response_json['data']]
            [data['data'].append(x) for x in response_json['data']]
    return token, refresh, data


def client_get_users_by_login(user_names):
    if not isinstance(user_names, list):
        user_names = [user_names]
    param_list = []
    data = {'data': []}
    parameters = {'login': []}
    for user in user_names:
        user = user.lower()
        cached_user = app.config['REDIS'].get('TWITCH_API_' + user)
        if cached_user:
            data['data'].append(json.loads(cached_user.decode('utf-8')))
            continue
        param_list.append(user)
    if param_list:
        headers = {'Client-ID': os.environ.get('TWITCH_CLIENT_ID')}
        for i in range(0, len(param_list), 100):
            parameters['login'].append(param_list[i:i + 100])
            response = requests.get(twitch_api_base + '/users', params=parameters, headers=headers)
            if response is None:
                return None
            response_json = json.loads(response.text)
            [app.config['REDIS'].setex('TWITCH_API_' + x['login'], 86400, json.dumps(x)) for x in response_json['data']]
            [data['data'].append(x) for x in response_json['data']]
    return data


def get_users_by_id(token, refresh, ids, allow_refresh=True):
    if not isinstance(ids, list):
        ids = [ids]
    param_list = []
    data = {'data': []}
    parameters = {'id': []}
    for user in ids:
        user = user.lower()
        cached_id = app.config['REDIS'].get('TWITCH_API_' + user)
        if cached_id:
            data['data'].append(json.loads(cached_id.decode('utf-8')))
            continue
        param_list.append(user)
    if param_list:
        headers = {'Authorization': f'Bearer {token}'}
        for i in range(0, len(param_list), 100):
            parameters['id'].append(param_list[i:i + 100])
            response = requests.get(twitch_api_base + '/users', params=parameters, headers=headers)
            if response is None:
                return None, None, None
            if response.status_code == 401 and 'www-authenticate' in response.headers and allow_refresh:
                token, refresh = refresh_token(refresh)
                if token is None or refresh is None:
                    return None, None, None
                return get_users_by_id(token, refresh, ids, allow_refresh=False)
            response_json = json.loads(response.text)
            [app.config['REDIS'].setex('TWITCH_API_' + x['id'], 86400, json.dumps(x)) for x in response_json['data']]
            [data['data'].append(x) for x in response_json['data']]
    return token, refresh, data
