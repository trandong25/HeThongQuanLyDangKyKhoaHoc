from selenium.webdriver.common.by import By
from ecourse.test.pages.BasePage import BasePage


class RegisterPage(BasePage):
    URL = "http://127.0.0.1:5000/register"

    NAME = (By.NAME, "name")
    USERNAME = (By.NAME, "username")
    PASSWORD = (By.NAME, "password")
    CONFIRM = (By.NAME, "confirm")

    BTN_REGISTER = (By.CSS_SELECTOR, "form button")

    def open_page(self):
        self.open(self.URL)

    def register(self, name, username, password):
        self.typing(*self.NAME, name)
        self.typing(*self.USERNAME, username)
        self.typing(*self.PASSWORD, password)
        self.typing(*self.CONFIRM, password)
        self.click(*self.BTN_REGISTER)