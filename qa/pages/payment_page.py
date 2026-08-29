from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class PaymentPage(BasePage):
    BUTTON = (By.CSS_SELECTOR, '[data-testid="payment-button"]')
    STATUS = (By.CSS_SELECTOR, '[data-testid="payment-status"]')

    def payment_status(self):
        return self.text(self.STATUS)

    def pay(self):
        self.click(self.BUTTON)
