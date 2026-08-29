from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class DashboardPage(BasePage):
    DASHBOARD_CARD = (By.CSS_SELECTOR, '[data-testid="dashboard-card"]')
    APPOINTMENT_ITEM = (By.CSS_SELECTOR, '[data-testid="appointment-item"]')
    NOTIFICATION_ITEM = (By.CSS_SELECTOR, '[data-testid="notification-item"]')
    SIGN_OUT = (By.XPATH, "//button[.//span[normalize-space()='Sign out']]")

    def metric_count(self):
        return len(self.driver.find_elements(*self.DASHBOARD_CARD))

    def appointment_count(self):
        return len(self.driver.find_elements(*self.APPOINTMENT_ITEM))

    def notification_count(self):
        return len(self.driver.find_elements(*self.NOTIFICATION_ITEM))

    def sign_out(self):
        self.click(self.SIGN_OUT)
