import unittest

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
        self.assert_redirects(response, '/')

    def test_twitch_token_set(self):
        self.client.get('/login')
        with self.client.session_transaction() as session:
            self.assertTrue(session['twitch_token'])


if __name__ == '__main__':
    unittest.main()
