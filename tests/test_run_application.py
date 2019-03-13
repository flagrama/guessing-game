import unittest

from flask_testing import TestCase

from web import create_app
import web.wsgi


class RunApplicationTest(TestCase):

    def create_app(self):
        return create_app()

    def test_wsgi(self):
        app = web.wsgi.application
        client = app.test_client()
        response = client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
