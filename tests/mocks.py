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
    if 'badapicall' in args[0]:
        return MockResponse('{"error": "Unauthorized",'
                            + ' "message": "Token invalid or missing required scope",'
                            + '"status": 401}',
                            401,
                            """{"www-authenticate": "OAuth realm='TwitchTV', error='invalid_token'"}""")
    if '/token' in args[0] and 'grant_type=authorization_code' in args[0]:
        return MockResponse("""{"access_token": "abc123", "refresh_token": "def456"}""", 200)
    if '/token' in args[0] and 'grant_type=refresh_token' in args[0]:
        return MockResponse("""{"access_token": "ghi789", "refresh_token": "jkl000"}""", 200)
    if '/validate' in args[0]:
        return MockResponse('{"client_id":"a1b2c3d4ef","login":"test_user",'
                            + '"scopes":["user_read"],"user_id":"1000"}', 200)
    if '/revoke' in args[0]:
        return MockResponse(None, 200)

    return MockResponse(None, 404)
