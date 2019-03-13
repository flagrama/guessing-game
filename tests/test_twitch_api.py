import unittest
from unittest import mock

from flask_testing import TestCase

from web import create_app
from tests.mocks import mocked_requests


class TwitchApiTest(TestCase):

    def create_app(self):
        app = create_app()
        self.client = app.test_client()
        return app

    @mock.patch('requests.get', side_effect=mocked_requests)
    def test_get_users(self, mock_get):
        with self.client.session_transaction() as session:
            session['twitch_token'] = "abc123"
            session['twitch_refresh_token'] = "def456"
        self.client.get('/')
        with self.client.session_transaction() as session:
            self.assertTrue('twitch_display_name' in session)

    @mock.patch('requests.get', side_effect=mocked_requests)
    @mock.patch('requests.post', side_effect=mocked_requests)
    def test_bad_api_call_and_token_refresh(self, mock_get, mock_post):
        with self.client.session_transaction() as session:
            session['twitch_token'] = "badapicall"
            session['twitch_refresh_token'] = "def456"
        self.client.get('/')
        with self.client.session_transaction() as session:
            self.assertFalse(session['twitch_refresh_token'] == "def456")

    @mock.patch('requests.get', side_effect=mocked_requests)
    def test_api_call_server_unavailable(self, mock_get):
        with self.client.session_transaction() as session:
            session['twitch_token'] = "apiserverisdown"
            session['twitch_refresh_token'] = "def456"
        response = self.client.get('/')
        self.assertTrue('test_user' in str(response.data))

    @mock.patch('requests.get', side_effect=mocked_requests)
    @mock.patch('requests.post', side_effect=mocked_requests)
    def test_refresh_server_unavailable(self, mock_get, mock_post):
        with self.client.session_transaction() as session:
            session['twitch_token'] = "badapicall"
            session['twitch_refresh_token'] = "refreshserverisdown"
        response = self.client.get('/')
        self.assertTrue('test_user' in str(response.data))


if __name__ == '__main__':
    unittest.main()
