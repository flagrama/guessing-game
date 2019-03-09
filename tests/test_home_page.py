import unittest

from flask_testing import TestCase

from web.app import create_app


class HomePageTest(TestCase):

    def create_app(self):
        config_name = 'testing'
        app = create_app(config_name)
        self.client = app.test_client()
        return app

    def test_root_url_resolves_to_home_page_view(self):
        response = self.client.get('/', content_type='html/text')
        self.assertIn(
            'Log In with Twitch',
            str(response.data)
        )


if __name__ == '__main__':
    unittest.main()
