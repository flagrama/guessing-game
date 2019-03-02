from web.app import app

import unittest


class BasicTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_redirect_to_https(self):
        response = self.app.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 302)
        self.assertIn('https', response.location)

    def test_index_exists(self):
        response = self.app.get('/', content_type='html/text', base_url='https://localhost')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
