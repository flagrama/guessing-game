import web.config as config


class Twitch:
    twitch_base = "https://id.twitch.tv/oauth2"
    client_id = f"client_id={config.TWITCH_CLIENT_ID}"
    client_secret = f"client_secret={config.TWITCH_SECRET}"
    response_type = "response_type=code"
    scope = "scope=user_read"
    grant_type = "grant_type=authorization_code"
