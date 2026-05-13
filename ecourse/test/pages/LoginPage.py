from selenium.webdriver.common.by import By
from ecourse.test.pages.BasePage import BasePage


class LoginPage(BasePage):
    URL = "http://127.0.0.1:5000/login"

    USERNAME = (By.NAME, "username")
    PASSWORD = (By.NAME, "password")

    BTN_LOGIN = (By.CSS_SELECTOR, "div.card-body > form > button")

    ERROR_MSG = (By.CLASS_NAME, "alert-danger")

    def open_page(self):
        self.open(self.URL)

    def login(self, username, password):
        self.typing(*self.USERNAME, username)
        self.typing(*self.PASSWORD, password)
        self.click(*self.BTN_LOGIN)

    def has_error(self):
        return len(self.finds(*self.ERROR_MSG)) > 0

