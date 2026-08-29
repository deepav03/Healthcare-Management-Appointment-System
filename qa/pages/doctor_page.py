from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class DoctorPage(BasePage):
    SEARCH = (By.CSS_SELECTOR, '[data-testid="doctor-search"]')
    CARDS = (By.CSS_SELECTOR, '[data-testid="doctor-card"]')

    def search_doctor(self, value):
        self.type(self.SEARCH, value)

    def doctor_count(self):
        return len(self.driver.find_elements(*self.CARDS))
