import unittest
from unittest import mock
from urllib import parse

from flask import current_app as app
from flask_testing import TestCase

from web import create_app
from tests.mocks import mocked_requests


class LoginRedirectTest(TestCase):

    def create_app(self):
        app = create_app()
        self.client = app.test_client()
        return app

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
            session['twitch_refresh_token'] = "def456"
        self.client.get('/logout', follow_redirects=True)
        with self.client.session_transaction() as session:
            self.assertFalse('twitch_token' in session)

    @mock.patch('requests.get', side_effect=mocked_requests)
    def test_validate_token(self, mock_get):
        with self.client.session_transaction() as session:
            session['twitch_token'] = 'abc123'
            session['twitch_refresh_token'] = "def456"
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


if __name__ == '__main__':
    unittest.main()
