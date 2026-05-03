#!/usr/bin/env python3
"""
Amazon ASIN Search and Screenshot Automation
Function: Search for a keyword on Amazon, find target ASIN, record page/position, take screenshot
All logs are sent real-time to Feishu dialog
"""

import time
import os
import sys
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Configuration
FEISHU_RECEIVER_ID = "ou_a331505193726d421fb0108a11bc6197"
BASE_URL = "https://www.amazon.com"
SEARCH_URL = "https://www.amazon.com/s"
SCREENSHOT_DIR = "/root/.openclaw/workspace/Amazon/screenshots"
REQUEST_TIMEOUT = 180
MAX_RETRIES = 1
# Headers to mimic real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Send log to Feishu real-time
def send_log(log_text):
    """Send log message to Feishu in real-time"""
    try:
        cmd = f'''openclaw message send --channel feishu --target {FEISHU_RECEIVER_ID} --message "{log_text.replace('"', '\\"')}"'''
        os.system(cmd)
        print(f"[LOG SENT] {log_text[:50]}...")
    except Exception as e:
        print(f"[LOG FAILED] {log_text}\nError: {e}")

# Override print to send to Feishu real-time
original_print = print
def new_print(*args, **kwargs):
    # Always print to console
    original_print(*args, **kwargs)
    # Convert args to string
    msg = " ".join(str(arg) for arg in args)
    if msg.strip():
        # Use original_print for send_log internal, avoid recursion
        original_print(f"[LOG SENT] {msg[:50]}...")
        try:
            cmd = f'''openclaw message send --channel feishu --target {FEISHU_RECEIVER_ID} --message "{msg.replace('"', '\\"')}"'''
            os.system(cmd)
        except Exception as e:
            original_print(f"[LOG FAILED] {msg}\nError: {e}")
print = new_print

def search_asin_position(keyword, target_asin):
    """
    Search for keyword on Amazon, find target ASIN position
    Returns: (found, page_number, position_in_page, product_url)
    """
    found = False
    page = 1
    position = 0
    product_url = None
    MAX_PAGE = 5  # Search up to 5 pages
    
    print(f"=== Starting search for keyword: '{keyword}', target ASIN: {target_asin} ===")
    
    while not found and page <= MAX_PAGE:
        print(f"Searching page {page}...")
        
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
        
        if not success:
            print(f"❌ Failed to load page {page} after {MAX_RETRIES} retries (503 Service Unavailable)\n")
            # If page load fails due to 503, return with 503 error status
            return False, page, 0, None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        product_links = soup.select('a.a-link-normal.s-no-outline')
        
        current_position = 1
        for link in product_links:
            href = link.get('href')
            if href:
                full_href = BASE_URL + href if href.startswith('/') else href
                if target_asin in full_href:
                    found = True
                    position = current_position
                    product_url = full_href
                    print(f"✅ Found ASIN {target_asin} on page {page}, position #{current_position}")
                    print(f"   Product URL: {product_url}\n")
                    break
                current_position += 1
        
        if found:
            break
        
        # Check if there's next page
        next_button = soup.select_one('a.s-pagination-next')
        if not next_button or 's-pagination-disabled' in next_button.get('class', []):
            print("❌ No more pages available, ASIN not found\n")
            break
        
        page += 1
        time.sleep(10)
    
    if not found and page > MAX_PAGE:
        print(f"❌ Reached max page {MAX_PAGE}, ASIN not found\n")
    
    return found, page, position, product_url

def take_product_screenshot(product_url, keyword, asin):
    """
    Open product page with selenium and take screenshot
    """
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
    
    success = False
    screenshot_path = os.path.join(SCREENSHOT_DIR, f"{asin}_{keyword.replace(' ', '_')}_screenshot.png")
    
    for retry in range(MAX_RETRIES):
        try:
            print(f"  Opening product page: {asin}")
            driver.get(product_url)
            time.sleep(30)  # Wait for page load
            
            # Handle robot check if needed
            try:
                buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Continue shopping')]")
                if buttons:
                    print("  🔘 Found 'Continue shopping' button, clicking...")
                    buttons[0].click()
                    time.sleep(15)
            except Exception:
                pass
            
            try:
                buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Try again')]")
                if buttons:
                    print("  🔘 Found 'Try again' button, clicking...")
                    buttons[0].click()
                    time.sleep(15)
            except Exception:
                pass
            
            # Scroll to top
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(5)
            
            # Take screenshot
            driver.save_screenshot(screenshot_path)
            print(f"  ✅ Screenshot saved: {screenshot_path}")
            success = True
            break
        except Exception as e:
            print(f"  ❌ Attempt failed: {type(e).__name__}: {e}\n")
            if retry < MAX_RETRIES - 1:
                print("  Waiting 15s before retry...\n")
                time.sleep(15)
    
    driver.quit()
    return success, screenshot_path

def search_and_screenshot(keyword, asin):
    """
    Main function: search for ASIN, record position, take screenshot
    """
    print(f"\n{'='*60}")
    print(f"Processing: Keyword='{keyword}', ASIN={asin}")
    print(f"{'='*60}\n")
    
    # Step 1: Search and find position
    found, page_num, pos_num, product_url = search_asin_position(keyword, asin)
    
    result = {
        "keyword": keyword,
        "asin": asin,
        "found": found,
        "page": page_num,
        "position": pos_num,
        "product_url": product_url,
        "screenshot_path": None,
        "screenshot_success": False
    }
    
    if not found:
        print(f"❌ ASIN {asin} not found in search results for keyword '{keyword}'")
        return result
    
    # Step 2: Take screenshot
    if found and product_url:
        success, screenshot_path = take_product_screenshot(product_url, keyword, asin)
        result["screenshot_path"] = screenshot_path
        result["screenshot_success"] = success
    
    print(f"\n=== Final Result for {keyword} + {asin} ===")
    print(f"Found: {found}")
    if found:
        print(f"Page: {page_num}, Position: {pos_num}")
        print(f"Screenshot: {'Success' if success else 'Failed'}")
        if success:
            print(f"Screenshot saved to: {screenshot_path}")
    print()
    
    return result

def batch_search(keyword_asins):
    """
    Batch process multiple (keyword, asin) pairs
    keyword_asins: list of tuples [(keyword, asin), ...]
    """
    results = []
    for keyword, asin in keyword_asins:
        result = search_and_screenshot(keyword, asin)
        results.append(result)
        time.sleep(15)  # Wait between searches
    
    print("\n" + "="*60)
    print("BATCH SEARCH COMPLETE")
    print("="*60)
    print("\nSummary:")
    for res in results:
        status = "✅ FOUND" if res['found'] else "❌ NOT FOUND"
        print(f"  {status} | {res['asin']} | '{res['keyword']}'")
        if res['found']:
            print(f"          Page {res['page']}, Position {res['position']}")
            if res['screenshot_success']:
                print(f"          Screenshot: {res['screenshot_path']}")
        print()
    
    return results

if __name__ == "__main__":
    # Example usage:
    # python amazon_search_asin_screenshot.py "mosaic kits for adults" B0DDDWWJBC
    print("\n🚀 [ENTRY] Script amazon_search_asin_screenshot.py started, entered main function...\n")
    import sys
    print(f"📋 Received command line arguments: {sys.argv}")
    if len(sys.argv) == 3:
        keyword = sys.argv[1]
        asin = sys.argv[2]
        print(f"🔍 Parameters:")
        print(f"   Search Keyword: '{keyword}'")
        print(f"   Target ASIN: {asin}\n")
        search_and_screenshot(keyword, asin)
    else:
        print(f"❌ Wrong number of arguments: expected 2, got {len(sys.argv) - 1}")
        print("Usage: python amazon_search_asin_screenshot.py <search_keyword> <target_asin>")
        print("\nExample:")
        print("  python amazon_search_asin_screenshot.py \"mosaic kits for adults\" B0DDDWWJBC")
