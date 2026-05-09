# from selenium.webdriver.common.by import By
# from ecourse.test.pages.BasePage import BasePage
#
#
# class ClassRegisterPage(BasePage):
#     URL = "http://127.0.0.1:5000/class_register"
#
#     # BTN_DELETE = (By.CSS_SELECTOR, "button.btn-danger")
#     BTN_DELETE = (By.CSS_SELECTOR, "table tbody tr:first-child .btn-danger")
#     BTN_CHECKOUT = (By.CSS_SELECTOR, "button.btn-success:not([disabled])")
#     # BTN_CHECKOUT = (By.CSS_SELECTOR, "button.btn-success")
#
#     CART_ROWS = (By.CSS_SELECTOR, "table tbody tr")
#
#     def open_page(self):
#         self.open(self.URL)
#
#     def delete_course(self):
#         self.click(*self.BTN_DELETE)
#
#     def checkout(self):
#         self.click(*self.BTN_CHECKOUT)
#
#     def has_courses(self):
#         return len(self.finds(*self.CART_ROWS)) > 0
#
#     def count_courses(self):
#         return len(self.finds(*self.CART_ROWS))

from selenium.webdriver.common.by import By
from ecourse.test.pages.BasePage import BasePage


class ClassRegisterPage(BasePage):
    URL = "http://127.0.0.1:5000/class_register"

    # Chỉ lấy nút delete KHÔNG bị disabled
    BTN_DELETE = (By.CSS_SELECTOR, "button.btn-danger:not(.disabled)")

    # BTN_CHECKOUT = (By.CSS_SELECTOR, "button.btn-success")
    BTN_CHECKOUT = (By.CSS_SELECTOR, ".card-footer button.btn-success")

    CART_ROWS = (By.CSS_SELECTOR, "table tbody tr")

    def open_page(self):
        self.open(self.URL)

    def delete_course(self):
        btns = self.finds(*self.BTN_DELETE)

        if len(btns) == 0:
            return False

        btn = btns[0]

        self.driver.execute_script("window.scrollTo(0, 1500)")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)

        self.driver.execute_script("arguments[0].click();", btn)

        return True

    def checkout(self):
        try:
            btn = self.find(*self.BTN_CHECKOUT)

            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)

            self.driver.execute_script("window.scrollBy(0, -200);")

            btn.click()
            return True
        except:
            return False
    def has_courses(self):
        return len(self.finds(*self.CART_ROWS)) > 0

    def count_courses(self):
        return len(self.finds(*self.CART_ROWS))
