import unittest
from unittest import mock
from urllib import parse

from flask import current_app as app
from flask_testing import TestCase

from web.app import create_app


class LoginRedirectTest(TestCase):

    def create_app(self):
        config_name = 'testing'
        app = create_app(config_name)
        self.client = app.test_client()
        return app

    # This method will be used by the mock to replace requests.get
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
            return MockResponse("""{"error": "Unauthorized","""
                                + """ "message": "Token invalid or missing required scope","""
                                  + """"status": 401}""",
                                401,
                                """{"www-authenticate": "OAuth realm='TwitchTV', error='invalid_token'"}""")
        if '/token' in args[0] and 'grant_type=authorization_code' in args[0]:
            return MockResponse("""{"access_token": "abc123", "refresh_token": "def456"}""", 200)
        if '/token' in args[0] and 'grant_type=refresh_token' in args[0]:
            return MockResponse("""{"access_token": "ghi789", "refresh_token": "jkl000"}""", 200)
        if '/validate' in args[0]:
            return MockResponse(None, 200)
        if '/revoke' in args[0]:
            return MockResponse(None, 200)

        return MockResponse(None, 404)

    def test_login_button_navigates_to_twitch(self):
        response = self.client.get('/login')
        expected_location = 'https://id.twitch.tv/oauth2/authorize'
        actual_location = parse.urljoin(response.location, parse.urlparse(response.location).path)
        self.assertEqual(expected_location, actual_location)

    def test_redirects_to_home(self):
        response = self.client.get('/login/authorized')
        self.assert_redirects(response, '/')

    def test_twitch_csrf(self):
        response = self.client.get('/login/authorized', follow_redirects=True)
        self.assertTrue('Access denied' in str(response.data))

    @mock.patch('requests.post', side_effect=mocked_requests)
    def test_twitch_not_authorized(self, mock_post):
        response = self.client.get(f'/login/authorized?code=noauth&state={app.secret_key}', follow_redirects=True)
        self.assertTrue('Access denied' in str(response.data))

    @mock.patch('requests.post', side_effect=mocked_requests)
    def test_twitch_token_set(self, mock_post):
        self.client.get(f'/login/authorized?state={app.secret_key}&code=abc123')
        with self.client.session_transaction() as session:
            self.assertTrue('twitch_token' in session)

    @mock.patch('requests.get', side_effect=mocked_requests)
    @mock.patch('requests.post', side_effect=mocked_requests)
    def test_logout(self, mock_get, mock_post):
        with self.client.session_transaction() as session:
            session['twitch_token'] = 'abc123'
        self.client.get('/logout', follow_redirects=True)
        with self.client.session_transaction() as session:
            self.assertFalse('twitch_token' in session)

    @mock.patch('requests.get', side_effect=mocked_requests)
    def test_validate_token(self, mock_get):
        with self.client.session_transaction() as session:
            session['twitch_token'] = 'abc123'
        self.client.get('/')
        with self.client.session_transaction() as session:
            self.assertTrue('twitch_token' in session)

    def test_invalid_token(self):
        with self.client.session_transaction() as session:
            session['twitch_token'] = 'bad_token'
            session['twitch_refresh_token'] = 'bad_token'
        self.client.get('/')
        with self.client.session_transaction() as session:
            self.assertFalse('twitch_token' in session)

    # @mock.patch('requests.get', side_effect=mocked_requests)
    # @mock.patch('requests.post', side_effect=mocked_requests)
    # def test_refresh_token(self, mock_get, mock_post):
    #     with self.client.session_transaction() as session:
    #         session['twitch_token'] = 'abc123'
    #         session['twitch_refresh_token'] = 'def456'
    #     self.client.get('/')
    #     with self.client.session_transaction() as session:
    #         self.assertFalse(session['twitch_token'] == 'abc123')
    #         self.assertFalse(session['twitch_refresh_token'] == 'def456')


if __name__ == '__main__':
    unittest.main()
