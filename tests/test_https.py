import unittest

from web.app import create_app


class BasicTestCase(unittest.TestCase):

    def setUp(self):
        config_name = 'https'
        app = create_app(config_name)
        self.client = app.test_client()

    def test_redirect_to_https(self):
        response = self.client.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 302)
        self.assertIn('https', response.location)

    def test_index_exists(self):
        response = self.client.get('/', content_type='html/text', base_url='https://localhost')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
