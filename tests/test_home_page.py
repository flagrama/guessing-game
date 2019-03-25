import unittest

from flask_testing import TestCase

from web import create_app, db


class HomePageTest(TestCase):

    def create_app(self):
        application = create_app('web.config.TestingConfig')
        self.client = application.test_client()
        return application

    def test_uses_home_template(self):
        self.client.get('/')
        self.assert_template_used('home.html')


if __name__ == '__main__':
    unittest.main()
