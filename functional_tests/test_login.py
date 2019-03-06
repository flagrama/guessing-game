import unittest
from os import environ

from flask_testing import LiveServerTestCase
from selenium import webdriver

from web.app import create_app


class LoginTest(LiveServerTestCase):

    def create_app(self):
        config_name = 'testing'
        app = create_app(config_name)
        self.client = app.test_client()
        return app

    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.quit()

    def test_can_login(self):
        # The user goes to check out the Twitch guessing game
        self.driver.get(self.get_server_url())

        # He notices a button asking him to login using Twitch
        login_button = self.driver.find_element_by_id('login_with_twitch')
        self.assertEqual(
            login_button.text,
            'Log In with Twitch'
        )

        # He clicks the button and is directed to a Twitch login page
        login_button.click()
        twitch_login_button = self.driver.find_element_by_class_name('js-login-text')
        self.assertEqual(
            twitch_login_button.text,
            'Log In'
        )

        # He fills in his username and password clicks on the Log In button and
        # is directed to the Twitch authorization page
        self.driver.execute_script(f"document.getElementById('username').value='{environ['test_twitch_username']}';")
        self.driver.execute_script(f"document.getElementById('password').value='{environ['test_twitch_password']}';")
        twitch_login_button.click()
        twitch_authorize_button = self.driver.find_element_by_class_name('js-authorize-text')
        self.assertEqual(
            twitch_authorize_button.text,
            'Authorize'
        )

        # He clicks the Authorize button and is redirected to the guessing-game application
        twitch_authorize_button.click()
        header_text = self.driver.find_element_by_tag_name('h1').text
        self.assertIn(
            'Guessing Game',
            header_text
        )



if __name__ == '__main__':
    unittest.main()
