import unittest
from unittest import mock

from flask import current_app as app
from flask_testing import TestCase

from web import create_app, db
from web.models import User
from tests.mocks import mocked_requests

user = User(1000, "test_user", "test_user")


class TwitchApiTest(TestCase):

    def create_app(self):
        application = create_app('web.config.TestingConfig')
        application.config["DATABASE_URL"] = "sqlite://"
        db.init_app(application)
        db.create_all(app=application)
        application.app_context().push()
        self.client = application.test_client()
        return application

    @mock.patch('requests.get', side_effect=mocked_requests)
    def test_get_users(self, mock_get):
        db.session.add(user)
        db.session.commit()
        with self.client.session_transaction() as session:
            session['twitch_user_id'] = "1000"
            session['twitch_token'] = "abc123"
            session['twitch_refresh_token'] = "def456"
        response = self.client.get('/')
        with self.client.session_transaction() as session:
            self.assertTrue('test_user' in str(response.data))

    @mock.patch('requests.get', side_effect=mocked_requests)
    @mock.patch('requests.post', side_effect=mocked_requests)
    def test_refresh_server_unavailable(self, mock_get, mock_post):
        db.session.add(user)
        db.session.commit()
        response = self.client.get(f'/login/authorized?state={app.secret_key}&code=refreshserverisdown', follow_redirects=True)
        self.assertTrue('Log In' in str(response.data))

    @mock.patch('requests.get', side_effect=mocked_requests)
    @mock.patch('requests.post', side_effect=mocked_requests)
    def test_refresh_token(self, mock_get, mock_post):
        self.client.get(f'/login/authorized?state={app.secret_key}&code=badapicall')
        with self.client.session_transaction() as session:
            self.assertFalse(session['twitch_refresh_token'] == "def456")

    @mock.patch('requests.get', side_effect=mocked_requests)
    @mock.patch('requests.post', side_effect=mocked_requests)
    def test_api_down(self, mock_get, mock_post):
        new_user = user
        new_user.twitch_login_name = "empty_users"
        db.session.add(user)
        db.session.commit()
        response = self.client.get(f'/login/authorized?state={app.secret_key}&code=empty_users', follow_redirects=True)
        self.assertTrue('Log In' in str(response.data))


if __name__ == '__main__':
    unittest.main()
