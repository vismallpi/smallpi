#!/usr/bin/env python3
"""
Amazon Mosaic Kits Search Automation
Steps:
1. Open Amazon homepage
2. Search for "mosaic kits for adults"
3. Find specific ASINs (B0DDDWWJBC, B0CWZ2Z5TS), keep flipping pages if not found on first page
4. Click into product page and take screenshot
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
TARGET_ASINS = ["B0DDDWWJBC", "B0CWZ2Z5TS"]
SEARCH_KEYWORD = "mosaic kits for adults"
AMAZON_URL = "https://www.amazon.com/"
SCREENSHOT_DIR = "/root/.openclaw/workspace/Amazon/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

def main():
    print("=== Starting Amazon Automation ===\n")
    
    # Step 1: Open Amazon homepage
    print("[Step 1] Opening Amazon homepage...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(AMAZON_URL)
    time.sleep(3)
    print("✅ Amazon homepage opened\n")
    
    # Step 2: Search for the keyword
    print(f"[Step 2] Searching for '{SEARCH_KEYWORD}'...")
    try:
        # Wait for search box to be available
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
        )
        search_box.clear()
        search_box.send_keys(SEARCH_KEYWORD)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)
        print("✅ Search completed\n")
    except Exception as e:
        print(f"❌ Search failed: {e}")
        driver.quit()
        return
    
    found_asins = []
    page_number = 1
    
    # Step 3: Find target ASINs, keep flipping pages if needed
    print("[Step 3] Looking for target ASINs...")
    while len(found_asins) < len(TARGET_ASINS):
        print(f"  Checking page {page_number}...")
        
        # Get all product links on current page
        product_links = driver.find_elements(By.CSS_SELECTOR, "a.a-link-normal.s-no-outline")
        
        for link in product_links:
            href = link.get_attribute("href")
            if href:
                # Check if href contains any of our target ASINs
                for asin in TARGET_ASINS:
                    if asin in href and asin not in found_asins:
                        print(f"  ✅ Found ASIN: {asin} on page {page_number}")
                        found_asins.append(asin)
        
        if len(found_asins) == len(TARGET_ASINS):
            break
        
        # Check if there's a next page
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.s-pagination-next")
            if "s-pagination-disabled" in next_button.get_attribute("class"):
                print("  ❌ No more pages available")
                break
            next_button.click()
            page_number += 1
            time.sleep(5)
        except Exception as e:
            print(f"  ❌ Cannot find next page button: {e}")
            break
    
    print(f"\n  Found {len(found_asins)}/{len(TARGET_ASINS)} target ASINs")
    
    # Step 4: Click into product page and take screenshot
    print("\n[Step 4] Taking screenshots for found ASINs...")
    for asin in found_asins:
        product_url = f"https://www.amazon.com/dp/{asin}"
        print(f"  Opening {asin}...")
        driver.get(product_url)
        time.sleep(5)
        
        # Take full page screenshot
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{asin}_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"  ✅ Screenshot saved: {screenshot_path}")
    
    print("\n=== Automation completed ===")
    print(f"Total found: {len(found_asins)}/{len(TARGET_ASINS)}")
    print(f"Screenshots saved to: {SCREENSHOT_DIR}")
    
    driver.quit()

if __name__ == "__main__":
    main()
