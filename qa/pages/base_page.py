from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config_reader import config


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.explicit_wait_seconds)

    def open(self, path="/"):
        self.driver.get(f"{config.ui_base_url.rstrip('/')}/{path.lstrip('/')}")

    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, value):
        element = self.find(locator)
        element.clear()
        element.send_keys(value)

    def text(self, locator):
        return self.find(locator).text
