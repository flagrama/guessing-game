def mocked_requests(*args, **kwargs):
    class MockResponse:
        def __init__(self, text, status_code, headers=None):
            self.text = text
            self.status_code = status_code
            self.headers = headers

        def text(self):
            return self.text

        def status_code(self):
            return self.status_code

        def headers(self):
            return self.headers

    if 'noauth' in args[0]:
        return None
    if ('/validate' not in args[0]
            and 'headers' in kwargs
            and 'Authorization' in kwargs['headers']
            and 'apiserverisdown' in kwargs['headers']['Authorization']):
        return None
        return None
    if ('/users' in args[0]
            and 'headers' in kwargs
            and 'Authorization' in kwargs['headers']
            and 'badapicall' in kwargs['headers']['Authorization']):
        return MockResponse('{"error": "Unauthorized",'
                            + ' "message": "Token invalid or missing required scope",'
                            + '"status": 401}',
                            401,
                            """{"www-authenticate": "OAuth realm='TwitchTV', error='invalid_token'"}""")
    if '/token' in args[0] and 'grant_type=refresh_token' in args[0] and 'refreshserverisdown' in args[0]:
        return None
    if '/token' in args[0] and 'grant_type=authorization_code' in args[0]:
        return MockResponse("""{"access_token": "abc123", "refresh_token": "def456"}""", 200)
    if '/token' in args[0] and 'grant_type=refresh_token' in args[0]:
        return MockResponse("""{"access_token": "abc123", "refresh_token": "ghi789"}""", 200)
    if '/validate' in args[0]:
        return MockResponse('{"client_id":"a1b2c3d4ef","login":"test_user",'
                            + '"scopes":["user_read"],"user_id":"1000"}', 200)
    if '/revoke' in args[0]:
        return MockResponse(None, 200)
    if '/users' in args[0]:
        return MockResponse('{"data": [{"id": "44322889","login": "dallas","display_name": "dallas","type": "staff",'
                            '"broadcaster_type": "","description": "Just a gamer playing games and chatting. :)",'
                            '"profile_image_url": '
                            '"https://static-cdn.jtvnw.net/jtv_user_pictures/dallas-profile_image-1a2c906ee2c35f12'
                            '-300x300.png","offline_image_url": '
                            '"https://static-cdn.jtvnw.net/jtv_user_pictures/dallas-channel_offline_image'
                            '-1a2c906ee2c35f12-1920x1080.png","view_count": 191836881,"email": '
                            '"login@provider.com"}]}', 200)

    return MockResponse(None, 404)
