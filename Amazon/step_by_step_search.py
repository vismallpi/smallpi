#!/usr/bin/env python3
"""Step by step search with screenshot for each step"""

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

SCREENSHOT_DIR = '/root/.openclaw/workspace/Amazon/screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Initialize driver
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-gpu')
service = Service(executable_path='/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.set_page_load_timeout(300)

# Step 1: Open first page and screenshot
print("=== Step 1: Open first page ===")
url = 'https://www.amazon.com/s?k=mosaic+beginner'
driver.get(url)
time.sleep(30)

# Handle robot check
try:
    buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Continue shopping')]")
    if buttons:
        print("🔘 Found 'Continue shopping' button, clicking...")
        buttons[0].click()
        time.sleep(15)
except Exception as e:
    pass

driver.execute_script("window.scrollTo(0, 0);")
time.sleep(5)
screenshot_path1 = f'{SCREENSHOT_DIR}/mosaic_beginner_page1.png'
driver.save_screenshot(screenshot_path1)
print(f'✅ First page screenshot saved: {screenshot_path1}')

# Step 2: Find next page button and screenshot that position
print("\n=== Step 2: Screenshot next page button position ===")
try:
    next_button = driver.find_element(By.CSS_SELECTOR, 'a.s-pagination-next')
    # Scroll to next button
    driver.execute_script("arguments[0].scrollIntoView();", next_button)
    time.sleep(3)
    screenshot_path2 = f'{SCREENSHOT_DIR}/mosaic_beginner_nextpage_button.png'
    driver.save_screenshot(screenshot_path2)
    print(f'✅ Next page button position screenshot saved: {screenshot_path2}')
    
    # Step 3: Click next page and screenshot second page
    print("\n=== Step 3: Click next page and screenshot second page ===")
    next_button.click()
    time.sleep(30)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(5)
    screenshot_path3 = f'{SCREENSHOT_DIR}/mosaic_beginner_page2.png'
    driver.save_screenshot(screenshot_path3)
    print(f'✅ Second page screenshot saved: {screenshot_path3}')
    
except Exception as e:
    print(f"❌ Error finding/clicking next page: {type(e).__name__}: {e}")

driver.quit()
print("\n=== All done! ===")
