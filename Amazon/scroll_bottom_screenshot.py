#!/usr/bin/env python3
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

SCREENSHOT_DIR = '/root/.openclaw/workspace/Amazon/screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-gpu')
service = Service(executable_path='/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.set_page_load_timeout(300)

url = 'https://www.amazon.com/s?k=mosaic+beginner'
driver.get(url)
time.sleep(30)

# Handle robot check
try:
    from selenium.webdriver.common.by import By
    buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Continue shopping')]")
    if buttons:
        buttons[0].click()
        time.sleep(15)
except Exception as e:
    pass

# Scroll to bottom
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)
screenshot_path = f'{SCREENSHOT_DIR}/mosaic_beginner_page1_bottom.png'
driver.save_screenshot(screenshot_path)
print(f'✅ Bottom of page screenshot saved: {screenshot_path}')

driver.quit()
