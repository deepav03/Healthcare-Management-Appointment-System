from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class RegistrationPage(BasePage):
    EMAIL = (By.CSS_SELECTOR, '[data-testid="registration-email"]')
    PASSWORD = (By.CSS_SELECTOR, '[data-testid="registration-password"]')
    SUBMIT = (By.CSS_SELECTOR, '[data-testid="registration-submit"]')

    def register(self, first_name, last_name, phone, email, password):
        self.type((By.CSS_SELECTOR, '[data-testid="registration-first-name"]'), first_name)
        self.type((By.CSS_SELECTOR, '[data-testid="registration-last-name"]'), last_name)
        self.type((By.CSS_SELECTOR, '[data-testid="registration-phone"]'), phone)
        self.type(self.EMAIL, email)
        self.type(self.PASSWORD, password)
        self.type((By.CSS_SELECTOR, '[data-testid="registration-password-confirmation"]'), password)
        self.click(self.SUBMIT)
