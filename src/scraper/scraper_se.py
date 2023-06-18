from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller


class SeleniumDriver:
    def __init__(self):    
        chromedriver_autoinstaller.install()
        chrome_options = webdriver.ChromeOptions()

        options = [
            "--window-size=1200,1200",
            "--ignore-certificate-errors",
            "--headless",
            "--disable-gpu"
        ]

        for option in options:
            chrome_options.add_argument(option)

        self._driver = webdriver.Chrome(options = chrome_options)
    
    def get(self, url: str, wait: str = "") -> str:
        self._driver.get(url)
        if not wait == "":
            WebDriverWait(self._driver, 30).until(EC.presence_of_element_located((By.XPATH, wait)))
        return self._driver.page_source
    
    def close(self):
        self._driver.quit()