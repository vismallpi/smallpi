#!/usr/bin/env python3
"""
Debug script for category ranking extraction
Only test ranking extraction, no bundling with other steps
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Configuration
ASIN = "B0DDDWWJBC"
PRODUCT_URL = f"https://www.amazon.com/dp/{ASIN}"

def get_category_ranking(driver):
    """Extract category ranking from Amazon product page, specifically look for Best Sellers Rank in Product Specifications"""
    rankings = []
    try:
        print("=== Starting ranking extraction ===")
        
        # Method 1: Look specifically for Product Specifications section
        product_spec_headers = driver.find_elements(By.XPATH, "//*[contains(text(), 'Product Specifications')]")
        print(f"Found {len(product_spec_headers)} Product Specifications headers")
        if product_spec_headers:
            # Get the table after Product Specifications
            for i, header in enumerate(product_spec_headers):
                try:
                    print(f"  Checking header {i+1}...")
                    # Find the next table after this header
                    table = header.find_element(By.XPATH, "./following::table[1]")
                    text = table.text
                    print(f"  Table text length: {len(text)}")
                    lines = text.split("\n")
                    # Look for Best Sellers Rank and then the mosaic tile ranking
                    for line_i, line in enumerate(lines):
                        if "Best Sellers" in line or "best seller" in line.lower():
                            print(f"    Found Best Sellers Rank at line {line_i+1}")
                            # Check next lines for mosaic tile ranking
                            for check_line in lines[line_i+1:]:
                                check_line = check_line.strip()
                                if "#" in check_line and "mosaic" in check_line.lower() and "tile" in check_line.lower():
                                    rankings.append(check_line)
                                    print(f"    ✅ Found ranking: {check_line}")
                                    break
                            break
                    # If not found in this table, search entire table text
                    if not rankings:
                        for line in lines:
                            line = line.strip()
                            if "#" in line and "mosaic" in line.lower() and "tile" in line.lower():
                                rankings.append(line)
                                print(f"  ✅ Found ranking in table: {line}")
                                break
                    if rankings:
                        break
                except Exception as e:
                    print(f"  ❌ Error checking header {i+1}: {type(e).__name__}: {e}")
                    continue
        
        # Method 2: If not found in table, search entire page text
        if not rankings:
            print("\n=== Method 2: Search entire page text ===")
            body = driver.find_element(By.TAG_NAME, "body")
            text = body.text
            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if "#" in line and "mosaic" in line.lower() and "tile" in line.lower():
                    rankings.append(line)
                    print(f"  ✅ Found ranking on page: {line}")
                    break
        
        # Method 3: Look for any Best Sellers Rank that contains mosaic
        if not rankings:
            print("\n=== Method 3: Search after Best Sellers Rank ===")
            body = driver.find_element(By.TAG_NAME, "body")
            text = body.text
            lines = text.split("\n")
            found_best_sellers = False
            for line in lines:
                line = line.strip()
                if "Best Sellers Rank" in line:
                    found_best_sellers = True
                    print(f"  Found Best Sellers Rank: {line}")
                if found_best_sellers and "#" in line and "mosaic" in line.lower() and "tile" in line.lower():
                    rankings.append(line)
                    print(f"  ✅ Found ranking after Best Sellers: {line}")
                    break
        
        print(f"\n=== Final result ===")
        print(f"Found {len(rankings)} rankings:")
        for rank in rankings:
            print(f"  - {rank}")
        
        return rankings
    except Exception as e:
        print(f"❌ Overall error: {type(e).__name__}: {e}")
        return []

def main():
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    prefs = {
        "profile.default_content_setting_values.notifications": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(300)
    
    print(f"Opening product page: {PRODUCT_URL}")
    driver.get(PRODUCT_URL)
    time.sleep(30)  # Wait for page load
    
    # Check for bot check and click continue
    print("Checking for bot check buttons...")
    bot_check_handled = False
    try:
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Continue shopping')]")
        if buttons:
            print(f"  🔘 Found 'Continue shopping' button, clicking...")
            buttons[0].click()
            time.sleep(15)
            bot_check_handled = True
    except Exception as e:
        pass
    
    if not bot_check_handled:
        try:
            buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Try again')]")
            if buttons:
                print(f"  🔘 Found 'Try again' button, clicking...")
                buttons[0].click()
                time.sleep(15)
                bot_check_handled = True
        except Exception as e:
            pass
    
    # Scroll to bottom to load all content
    print("Scrolling to bottom of page...")
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)
    except Exception as e:
        print(f"  Scroll failed: {e}")
    
    # Extract ranking
    rankings = get_category_ranking(driver)
    
    # Save page source for debugging
    with open("/tmp/product_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"\nPage source saved to /tmp/product_page.html for debugging")
    
    driver.quit()
    return 0

if __name__ == "__main__":
    exit(main())
