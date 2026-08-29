from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class PrescriptionPage(BasePage):
    ITEM = (By.CSS_SELECTOR, '[data-testid="prescription-item"]')

    def item_count(self):
        return len(self.driver.find_elements(*self.ITEM))
