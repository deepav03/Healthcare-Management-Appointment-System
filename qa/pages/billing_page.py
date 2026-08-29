from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class BillingPage(BasePage):
    BILL = (By.CSS_SELECTOR, '[data-testid="bill-item"]')

    def bill_count(self):
        return len(self.driver.find_elements(*self.BILL))
