import unittest
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

    def test_redirects_to_home(self):
        response = self.client.get('/login')
        expected_location = 'https://id.twitch.tv/oauth2/authorize'
        actual_location = parse.urljoin(response.location, parse.urlparse(response.location).path)
        self.assertEqual(expected_location, actual_location)

    def test_twitch_token_failed(self):
        app.config['TEST_FAIL'] = True
        self.client.get('/login/authorized')
        with self.client.session_transaction() as session:
            self.assertFalse('twitch_token' in session)

    def test_twitch_token_set(self):
        app.config['TEST_AUTH'] = True
        self.client.get('/login/authorized')
        with self.client.session_transaction() as session:
            self.assertTrue('twitch_token' in session)


if __name__ == '__main__':
    unittest.main()
