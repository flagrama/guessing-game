import unittest

from flask_testing import LiveServerTestCase
from selenium import webdriver

from web.app import create_app


class TestBase(LiveServerTestCase):

    def create_app(self):
        config_name = 'testing'
        app = create_app(config_name)
        self.client = app.test_client()
        return app

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get(self.get_server_url())

    def tearDown(self):
        self.driver.quit()

    def test_server_is_up_and_running(self):
        response = self.client.get('/')
        self.assertEqual(response._status_code, 200)


if __name__ == '__main__':
    unittest.main()
