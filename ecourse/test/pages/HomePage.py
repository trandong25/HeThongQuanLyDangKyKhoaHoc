# from selenium.webdriver.common.by import By
# from ecourse.test.pages.BasePage import BasePage
#
#
# class HomePage(BasePage):
#     URL = "http://127.0.0.1:5000/"
#
#     SEARCH_INPUT = (By.NAME, "kw")
#     SEARCH_BUTTON = (By.CSS_SELECTOR, "form button")
#
#     CLASS_ROWS = (By.CSS_SELECTOR, "table tbody tr")
#     BTN_REGISTER = (By.CSS_SELECTOR, "table tbody tr td:last-child button:not(.disabled)")
#
#     PAGINATION = (By.CSS_SELECTOR, ".pagination li")
#
#     def open_page(self):
#         self.open(self.URL)
#
#     def search(self, kw):
#         self.typing(*self.SEARCH_INPUT, kw)
#         self.click(*self.SEARCH_BUTTON)
#
#     def get_classes(self):
#         return self.finds(*self.CLASS_ROWS)
#
#     def add_first_course(self):
#         # self.click(*self.BTN_REGISTER)
#         btns = self.finds(*self.BTN_REGISTER)
#
#         if len(btns) == 0:
#             return False
#
#         btn = btns[0]
#
#         self.driver.execute_script("window.scrollTo(0, 500)")
#
#         self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
#
#         self.driver.execute_script("arguments[0].click();", btn)
#
#         return True
#
#     def count_classes(self):
#         return len(self.finds(*self.CLASS_ROWS))
#
#     def count_pagination(self):
#         return len(self.finds(*self.PAGINATION))


from selenium.webdriver.common.by import By
from ecourse.test.pages.BasePage import BasePage


class HomePage(BasePage):
    URL = "http://127.0.0.1:5000/"

    SEARCH_INPUT = (By.NAME, "kw")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "#mynavbar > form > button")

    CLASS_ROWS = (By.CSS_SELECTOR, "table tbody tr")
    BTN_REGISTER = (By.CSS_SELECTOR, "table tbody tr td:last-child button:not(.disabled)")

    PAGINATION = (By.CSS_SELECTOR, ".pagination li")

    def open_page(self):
        self.open(self.URL)

    def search(self, kw):
        self.typing(*self.SEARCH_INPUT, kw)
        self.click(*self.SEARCH_BUTTON)

    def get_classes(self):
        return self.finds(*self.CLASS_ROWS)

    def add_first_course(self):
        btns = self.finds(*self.BTN_REGISTER)

        if len(btns) == 0:
            return False

        btn = btns[0]

        self.driver.execute_script("window.scrollTo(0, 600)")

        self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)

        self.driver.execute_script("arguments[0].click();", btn)

        return True

    def count_classes(self):
        return len(self.finds(*self.CLASS_ROWS))

    def count_pagination(self):
        return len(self.finds(*self.PAGINATION))
