from selenium.webdriver.common.by import By
from ecourse.test.pages.BasePage import BasePage


class ClassRegisterPage(BasePage):
    URL = "http://127.0.0.1:5000/class_register"

    BTN_DELETE = (By.CSS_SELECTOR, "button.btn-danger")
    BTN_CHECKOUT = (By.CSS_SELECTOR, "button.btn-success")

    CART_ROWS = (By.CSS_SELECTOR, "table tbody tr")

    def open_page(self):
        self.open(self.URL)

    def delete_course(self):
        self.click(*self.BTN_DELETE)

    def checkout(self):
        self.click(*self.BTN_CHECKOUT)

    def has_courses(self):
        return len(self.finds(*self.CART_ROWS)) > 0
