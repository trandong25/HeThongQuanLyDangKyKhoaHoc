from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def open(self, url):
        self.driver.get(url)

    def find(self, by, value):
        return self.driver.find_element(by, value)

    def finds(self, by, value):
        return self.driver.find_elements(by, value)

    def typing(self, by, value, text):
        e = self.find(by, value)
        e.clear()
        e.send_keys(text)

    def click(self, by, value):
        e = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((by, value))
        )
        e.click()

    def accept_alert(self):
        try:
            alert = self.driver.switch_to.alert
            text = alert.text
            alert.accept()
            return text.lower()
        except:
            return None