from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class PatientPage(BasePage):
    PROFILE = (By.CSS_SELECTOR, '[data-testid="patient-profile"]')

    def profile_visible(self):
        return bool(self.driver.find_elements(*self.PROFILE))
