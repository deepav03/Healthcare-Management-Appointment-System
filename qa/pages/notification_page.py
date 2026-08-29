from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class NotificationPage(BasePage):
    ITEM = (By.CSS_SELECTOR, '[data-testid="notification-item"]')

    def notification_count(self):
        return len(self.driver.find_elements(*self.ITEM))
