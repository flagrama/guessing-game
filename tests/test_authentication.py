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
    def mocked_requests_post(*args, **kwargs):
        class MockResponse:
            def __init__(self, text, status_code):
                self.text = text
                self.status_code = status_code

            def text(self):
                return self.text

        if 'noauth' in args[0]:
            return None
        if '/token' in args[0]:
            return MockResponse("""{"access_token": "abc123"}""", 200)

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

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_twitch_not_authorized(self, mock_post):
        response = self.client.get(f'/login/authorized?code=noauth&state={app.secret_key}', follow_redirects=True)
        self.assertTrue('Access denied' in str(response.data))

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_twitch_token_set(self, mock_post):
        self.client.get(f'/login/authorized?state={app.secret_key}&code=abc123')
        with self.client.session_transaction() as session:
            self.assertTrue('twitch_token' in session)

    def test_logout(self):
        with self.client.session_transaction() as session:
            session['twitch_token'] = 'abc123'
        self.client.get('/')
        with self.client.session_transaction() as session:
            self.assertTrue('twitch_token' in session)
        self.client.get('/logout', follow_redirects=True)
        with self.client.session_transaction() as session:
            self.assertFalse('twitch_token' in session)


if __name__ == '__main__':
    unittest.main()
