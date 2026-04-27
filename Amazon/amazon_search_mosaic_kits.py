#!/usr/bin/env python3
"""
Amazon Mosaic Kits Search Automation
Steps:
1. Open Amazon homepage
2. Search for "mosaic kits for adults"
3. Find specific ASINs (B0DDDWWJBC, B0CWZ2Z5TS), keep flipping pages if not found on first page
4. Click into product page directly from search results and take screenshot
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
        search_box.send_keys(SEARCH_KEY)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)
        print("✅ Search completed\n")
    except Exception as e:
        print(f"❌ Search failed: {e}")
        driver.quit()
        return
    
    found_links = []  # Store (asin, link_element)
    page_number = 1
    
    # Step 3: Find target ASINs, keep flipping pages if needed
    print("[Step 3] Looking for target ASINs...")
    while len(found_links) < len(TARGET_ASINS):
        print(f"  Checking page {page_number}...")
        
        # Get all product links on current page
        product_links = driver.find_elements(By.CSS_SELECTOR, "a.a-link-normal.s-no-outline")
        
        for link in product_links:
            href = link.get_attribute("href")
            if href:
                # Check if href contains any of our target ASINs
                for asin in TARGET_ASINS:
                    if asin in href:
                        # Check if already found
                        already_found = any(f[0] == asin for f in found_links)
                        if not already_found:
                            print(f"  ✅ Found ASIN: {asin} on page {page_number}")
                            print(f"      Link: {href}")
                            found_links.append((asin, link))
        
        if len(found_links) == len(TARGET_ASINS):
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
    
    print(f"\n  Found {len(found_links)}/{len(TARGET_ASINS)} target ASINs")
    
    # Step 4: Click into product page directly from search results and take screenshot
    print("\n[Step 4] Taking screenshots for found ASINs...")
    for (asin, link) in found_links:
        print(f"  Clicking into {asin} from search results...")
        # Scroll the link into view
        driver.execute_script("arguments[0].scrollIntoView(true);", link)
        time.sleep(1)
        # Click the link directly
        link.click()
        time.sleep(5)  # Wait for page to load
        
        # Take full page screenshot
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{asin}_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"  ✅ Screenshot saved: {screenshot_path}")
        
        # Go back to search results page for next product
        driver.back()
        time.sleep(3)
    
    print("\n=== Automation completed ===")
    print(f"Total found: {len(found_links)}/{len(TARGET_ASINS)}")
    print(f"Screenshots saved to: {SCREENSHOT_DIR}")
    
    driver.quit()

if __name__ == "__main__":
    main()
