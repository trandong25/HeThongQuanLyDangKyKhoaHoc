from selenium.webdriver.common.by import By
from ecourse.test.pages.BasePage import BasePage


class HomePage(BasePage):
    URL = "http://127.0.0.1:5000/"

    SEARCH_INPUT = (By.NAME, "kw")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "form button")

    CLASS_ROWS = (By.CSS_SELECTOR, "table tbody tr")
    BTN_REGISTER = (By.CSS_SELECTOR, "table tbody tr button")

    PAGINATION = (By.CSS_SELECTOR, ".pagination li")

    def open_page(self):
        self.open(self.URL)

    def search(self, kw):
        self.typing(*self.SEARCH_INPUT, kw)
        self.click(*self.SEARCH_BUTTON)

    def get_classes(self):
        return self.finds(*self.CLASS_ROWS)

    def add_first_course(self):
        self.click(*self.BTN_REGISTER)

    def count_classes(self):
        return len(self.finds(*self.CLASS_ROWS))

    def count_pagination(self):
        return len(self.finds(*self.PAGINATION))
