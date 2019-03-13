import unittest

from flask_testing import TestCase

from web import create_app, db


class HomePageTest(TestCase):

    def create_app(self):
        application = create_app('web.config.TestingConfig')
        application.config["DATABASE_URL"] = "sqlite://"
        db.init_app(application)
        db.create_all(app=application)
        application.app_context().push()
        self.client = application.test_client()
        return application

    def test_uses_home_template(self):
        self.client.get('/')
        self.assert_template_used('home.html')


if __name__ == '__main__':
    unittest.main()
