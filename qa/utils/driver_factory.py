from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils.config_reader import config


def create_driver():
    if config.browser.lower() != "chrome":
        raise ValueError(f"Unsupported browser: {config.browser}")
    options = Options()
    if config.headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)
