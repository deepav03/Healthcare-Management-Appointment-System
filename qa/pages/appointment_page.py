from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class AppointmentPage(BasePage):
    ITEMS = (By.CSS_SELECTOR, '[data-testid="appointment-item"]')
    DATE = (By.CSS_SELECTOR, '[data-testid="appointment-date"]')
    SLOT = (By.CSS_SELECTOR, '[data-testid="appointment-slot"]')
    BOOK = (By.CSS_SELECTOR, '[data-testid="book-appointment"]')
    CANCEL = (By.CSS_SELECTOR, '[data-testid="cancel-appointment"]')
    RESCHEDULE = (By.CSS_SELECTOR, '[data-testid="reschedule-appointment"]')

    def appointment_count(self):
        return len(self.driver.find_elements(*self.ITEMS))

    def select_date(self, value):
        self.type(self.DATE, value)

    def select_slot(self, value):
        self.click(self.SLOT)
        self.find(self.SLOT).send_keys(value)

    def book_appointment(self):
        self.click(self.BOOK)
