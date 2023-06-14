from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller

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

driver = webdriver.Chrome(options = chrome_options)

url = "http://tripadvisor.com"
driver.get(f"{url}")
print(driver.title)
with open("./scrape.txt", "w") as f:
    f.write(f"String")