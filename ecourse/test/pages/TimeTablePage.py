from selenium.webdriver.common.by import By
from ecourse.test.pages.BasePage import BasePage


class TimetablePage(BasePage):
    URL = "http://127.0.0.1:5000/timetable"

    TABLE = (By.TAG_NAME, "table")
    EMPTY_MSG = (By.CLASS_NAME, "alert-warning")

    def open_page(self):
        self.open(self.URL)

    def has_timetable(self):
        return len(self.finds(*self.TABLE)) > 0

    def is_empty(self):
        return len(self.finds(*self.EMPTY_MSG)) > 0