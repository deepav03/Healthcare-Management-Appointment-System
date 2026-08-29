from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class SchedulePage(BasePage):
    DATE = (By.CSS_SELECTOR, '[data-testid="availability-date"]')
    SLOTS = (By.CSS_SELECTOR, '[data-testid="availability-slot"]')

    def slot_count(self):
        return len(self.driver.find_elements(*self.SLOTS))
