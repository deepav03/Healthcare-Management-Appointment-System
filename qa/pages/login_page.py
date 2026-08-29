from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    EMAIL = (By.CSS_SELECTOR, '[data-testid="login-email"]')
    PASSWORD = (By.CSS_SELECTOR, '[data-testid="login-password"]')
    SUBMIT = (By.CSS_SELECTOR, '[data-testid="login-button"]')
    ERROR = (By.CSS_SELECTOR, '[role="alert"]')

    def login(self, email, password):
        self.type(self.EMAIL, email)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)

    def error_message(self):
        return self.text(self.ERROR)
