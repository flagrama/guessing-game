import unittest
import subprocess
from os import environ

from flask_testing import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from web.app import create_app


class LoginTest(TestCase):

    def create_app(self):
        config_name = 'selenium'
        app = create_app(config_name)
        self.client = app.test_client()
        return app

    def setUp(self):
        self.webserver = subprocess.Popen([
            'gunicorn',
            'web.wsgi:app',
            '--bind=0.0.0.0:5000',
            '--certfile=util/server.crt',
            '--keyfile=util/server.key'
        ])
        options = webdriver.ChromeOptions()
        if 'GOOGLE_CHROME_BIN' in environ:
            options.binary_location = environ['GOOGLE_CHROME_BIN']
        options.add_argument('no-sandbox')
        options.add_argument('disable-dev-shm-usage')
        options.add_argument('headless')
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        self.driver.quit()
        self.webserver.terminate()

    def test_can_login(self):
        # The user goes to check out the Guessing Game Twitch bot
        self.driver.get('https://localhost:5000')

        # He notices a button asking him to login using Twitch
        login_button = self.driver.find_element_by_id('login_with_twitch')
        self.assertEqual(
            login_button.text,
            'Log In with Twitch'
        )

        # He deals with the Twitch Authorization workflow
        login_button.click()
        self.driver.find_element_by_name('username').send_keys(environ['TWITCH_ACCOUNT_USERNAME'], Keys.TAB)
        self.driver.find_element_by_name('password').send_keys(environ['TWITCH_ACCOUNT_PASSWORD'])
        twitch_login_button = self.driver.find_element_by_css_selector('button.js-login-button')
        twitch_login_button.click()
        self.driver.implicitly_wait(5)
        twitch_authorize_button = self.driver.find_elements_by_css_selector('button.js-authorize')
        if twitch_authorize_button:
            twitch_authorize_button.click()

        # He clicks the button and is directed to the Guessing Game home page
        logout_button = self.driver.find_element_by_id('logout')
        self.assertIn(
            'Log Out',
            logout_button.text
        )


if __name__ == '__main__':
    unittest.main()
