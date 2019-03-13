import unittest

from flask_testing import TestCase

from web import create_app


class HomePageTest(TestCase):

    def create_app(self):
        app = create_app()
        self.client = app.test_client()
        return app

    def test_uses_home_template(self):
        self.client.get('/')
        self.assert_template_used('home.html')


if __name__ == '__main__':
    unittest.main()
