import unittest

from flask_testing import TestCase

from web import create_app, db
import web.wsgi


class RunApplicationTest(TestCase):

    def create_app(self):
        application = create_app('web.config.TestingConfig')
        application.config["DATABASE_URL"] = "sqlite://"
        db.init_app(application)
        db.create_all(app=application)
        application.app_context().push()
        self.client = application.test_client()
        return application

    def test_wsgi(self):
        app = web.wsgi.application
        client = app.test_client()
        response = client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
