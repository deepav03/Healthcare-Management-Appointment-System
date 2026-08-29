from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class MedicalRecordPage(BasePage):
    RECORD = (By.CSS_SELECTOR, '[data-testid="medical-record"]')

    def record_count(self):
        return len(self.driver.find_elements(*self.RECORD))
