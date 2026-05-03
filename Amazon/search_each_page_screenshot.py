#!/usr/bin/env python3
"""
Search keyword on Amazon, get screenshot for each page from 1 to max page
Used when you need to screenshot every page even if ASIN not found
All logs sent real-time to Feishu
"""

import time
import os
import sys
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Configuration
FEISHU_RECEIVER_ID = "ou_a331505193726d421fb0108a11bc6197"
BASE_URL = "https://www.amazon.com"
SEARCH_URL = "https://www.amazon.com/s"
SCREENSHOT_DIR = "/root/.openclaw/workspace/Amazon/screenshots"
REQUEST_TIMEOUT = 180
MAX_RETRIES = 1
MAX_PAGE = 5
# Headers to mimic real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Override print to send to Feishu real-time
original_print = print
def new_print(*args, **kwargs):
    # Always print to console
    original_print(*args, **kwargs)
    # Convert args to string
    msg = " ".join(str(arg) for arg in args)
    if msg.strip():
        # Use original_print for internal logging, avoid recursion
        original_print(f"[LOG SENT] {msg[:50]}...")
        try:
            cmd = f'''openclaw message send --channel feishu --target {FEISHU_RECEIVER_ID} --message "{msg.replace('"', '\\"')}"'''
            os.system(cmd)
        except Exception as e:
            original_print(f"[LOG FAILED] {msg}\nError: {e}")
print = new_print

def take_page_screenshot(page_num, keyword):
    """Take full page screenshot of search result page with selenium"""
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
    
    service = Service(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(300)
    
    params = {
        'k': keyword,
        'page': page_num
    }
    url = SEARCH_URL + '?' + '&'.join([f"{k}={v}" for k,v in params.items()])
    
    success = False
    screenshot_path = os.path.join(SCREENSHOT_DIR, f"{keyword.replace(' ', '_')}_page_{page_num}.png")
    
    try:
        driver.get(url)
        time.sleep(30)  # Wait for page load
        
        # Handle robot check if needed
        try:
            from selenium.webdriver.common.by import By
            buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Continue shopping')]")
            if buttons:
                print(f"  🔘 Found 'Continue shopping' button, clicking...")
                buttons[0].click()
                time.sleep(15)
        except Exception:
            pass
        
        try:
            from selenium.webdriver.common.by import By
            buttons = driver.find_elements(By.Xpath, "//*[contains(text(), 'Try again')]")
            if buttons:
                print(f"  🔘 Found 'Try again' button, clicking...")
                buttons[0].click()
                time.sleep(15)
        except Exception:
            pass
        
        # Scroll to top and take screenshot
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(5)
        
        driver.save_screenshot(screenshot_path)
        print(f"  ✅ Page {page_num} screenshot saved: {screenshot_path}")
        success = True
    except Exception as e:
        print(f"  ❌ Failed to take screenshot for page {page_num}: {type(e).__name__}: {e}")
    
    driver.quit()
    return success, screenshot_path

def search_with_page_screenshots(keyword, target_asin):
    """Search each page from 1 to MAX_PAGE, take screenshot for each page"""
    print(f"\n{'='*60}")
    print(f"Starting search with full page screenshots:")
    print(f"Keyword: '{keyword}', target ASIN: {target_asin}")
    print(f"Max pages: {MAX_PAGE}")
    print(f"{'='*60}\n")
    
    found = False
    found_page = 0
    found_position = 0
    found_url = None
    
    for page in range(1, MAX_PAGE + 1):
        print(f"=== Page {page}/{MAX_PAGE} ===")
        
        params = {
            'k': keyword,
            'page': page
        }
        
        success = False
        response = None
        for retry in range(MAX_RETRIES):
            try:
                response = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                success = True
                break
            except Exception as e:
                print(f"  Attempt {retry + 1}/{MAX_RETRIES} failed: {type(e).__name__}: {e}")
                if retry < MAX_RETRIES - 1:
                    print("  Waiting 10s before retry...\n")
                    time.sleep(10)
        
        # Take screenshot of this page regardless of result
        print(f"  Taking screenshot for page {page}...")
        take_page_screenshot(page, keyword)
        
        if not success:
            print(f"❌ Failed to load page {page} after {MAX_RETRIES} retries\n")
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        product_links = soup.select('a.a-link-normal.s-no-outline')
        
        current_position = 1
        for link in product_links:
            href = link.get('href')
            if href:
                full_href = BASE_URL + href if href.startswith('/') else href
                if target_asin in full_href:
                    found = True
                    found_page = page
                    found_position = current_position
                    found_url = full_href
                    print(f"✅ Found ASIN {target_asin} on page {page}, position #{current_position}")
                    print(f"   Product URL: {found_url}\n")
                    break
                current_position += 1
        
        if found:
            break
        
        # Check if there's next page - but we still continue to max page for screenshot
        next_button = soup.select_one('a.s-pagination-next')
        if not next_button or 's-pagination-disabled' in next_button.get('class', []):
            print("  No more pages available, stopping\n")
            break
        
        time.sleep(15)
    
    print("\n=== Final Result ===")
    print(f"Keyword: '{keyword}', target ASIN: {target_asin}")
    if found:
        print(f"✅ Found at page {found_page}, position #{found_position}")
        print(f"URL: {found_url}")
    else:
        print(f"❌ Not found in {MAX_PAGE} pages")
    print(f"All pages 1-{min(MAX_PAGE, page)} have been screenshot saved to {SCREENSHOT_DIR}")
    print()
    
    return found, found_page, found_position

if __name__ == "__main__":
    print("\n🚀 [ENTRY] Script search_each_page_screenshot.py started, entered main function...\n")
    import sys
    print(f"📋 Received command line arguments: {sys.argv}")
    if len(sys.argv) == 3:
        keyword = sys.argv[1]
        asin = sys.argv[2]
        print(f"🔍 Parameters:")
        print(f"   Search Keyword: '{keyword}'")
        print(f"   Target ASIN: {asin}\n")
        search_with_page_screenshots(keyword, asin)
    else:
        print(f"❌ Wrong number of arguments: expected 2, got {len(sys.argv) - 1}")
        print("Usage: python search_each_page_screenshot.py <search_keyword> <target_asin>")
