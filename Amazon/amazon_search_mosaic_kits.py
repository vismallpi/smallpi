#!/usr/bin/env python3
"""
Amazon Mosaic Kits Search Automation
Hybrid approach: use requests for searching (lightweight), use selenium only for final screenshot
Steps:
1. Use requests to search for "mosaic kits for adults"
2. Find specific ASINs (B0DDDWWJBC, B0CWZ2Z5TS), keep flipping pages if not found on first page
3. After getting product URLs, use selenium to open each and take screenshot
"""

import time
import os
import pytz
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Configuration
TARGET_ASINS = ["B0DDDWWJBC", "B0CWZ2Z5TS"]
SEARCH_KEYWORD = "mosaic kits for adults"
BASE_URL = "https://www.amazon.com"
SEARCH_URL = "https://www.amazon.com/s"
SCREENSHOT_DIR = "/root/.openclaw/workspace/Amazon/screenshots"
REQUEST_TIMEOUT = 180  # 3 minutes for requests
MAX_RETRIES = 1
# 接收log的飞书用户open_id
FEISHU_RECEIVER_ID = "ou_a331505193726d421fb0108a11bc6197"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Save original print before overriding
original_print = print

# Create log file with timestamp - Daily Auto Search
RUN_ID = int(time.time())
LOG_FILE = f"/root/.openclaw/workspace/Amazon/logs/{RUN_ID}_daily_search.log"
SCREENSHOT_DIR = f"/root/.openclaw/workspace/Amazon/logs/{RUN_ID}_daily_screenshots"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Send log to Feishu real-time + write to file with timestamp
def send_log(log_text):
    """Send log message to Feishu in real-time + write to log file"""
    from datetime import datetime
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{now}] {log_text}"
    
    try:
        # Write to log file
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
        # Send to Feishu
        cmd = f'''openclaw message send --channel feishu --target {FEISHU_RECEIVER_ID} --message "{log_text.replace('"', '\\"')}"'''
        os.system(cmd)
        original_print(f"[LOG SENT + FILE] {log_text[:50]}...")
    except Exception as e:
        original_print(f"[LOG FAILED] {log_text}\nError: {e}")

# Override print to send to Feishu real-time + write to file
def new_print(*args, **kwargs):
    # Always print to console (original)
    original_print(*args, **kwargs)
    # Convert args to string
    msg = " ".join(str(arg) for arg in args)
    if msg.strip():
        # Send to Feishu and write to file
        send_log(msg)

print = new_print

# Headers to mimic real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

def search_and_find_asins():
    """Use requests to search and find target ASINs - lightweight, less data"""
    found_hrefs = []
    page = 1
    
    print("=== [Phase 1] Searching with requests (lightweight) ===\n")
    
    while len(found_hrefs) < len(TARGET_ASINS):
        print(f"Searching page {page}...")
        
        params = {
            'k': SEARCH_KEYWORD,
            'page': page
        }
        
        success = False
        for retry in range(MAX_RETRIES):
            try:
                response = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                success = True
                break
            except Exception as e:
                print(f"  Attempt {retry + 1}/{MAX_RETRIES} failed: {type(e).__name__}: {e}")
                if retry < MAX_RETRIES - 1:
                    print(f"  Waiting 10s before retry...\n")
                    time.sleep(10)
        
        if not success:
            print(f"❌ Failed to load page {page} after {MAX_RETRIES} retries\n")
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        product_links = soup.select('a.a-link-normal.s-no-outline')
        
        for link in product_links:
            href = link.get('href')
            if href:
                full_href = BASE_URL + href if href.startswith('/') else href
                for asin in TARGET_ASINS:
                    if asin in full_href:
                        already_found = any(f[0] == asin for f in found_hrefs)
                        if not already_found:
                            print(f"  ✅ Found ASIN: {asin} on page {page}")
                            print(f"      Link: {full_href}\n")
                            found_hrefs.append((asin, full_href))
        
        if len(found_hrefs) == len(TARGET_ASINS):
            break
        
        # Check if there's next page by looking for "Next" button
        next_button = soup.select_one('a.s-pagination-next')
        if not next_button or 's-pagination-disabled' in next_button.get('class', []):
            print("❌ No more pages available\n")
            break
        
        page += 1
        time.sleep(10)
    
    print(f"[Phase 1 completed] Found {len(found_hrefs)}/{len(TARGET_ASINS)} target ASINs\n")
    return found_hrefs

def send_screenshot_to_feishu(screenshot_path, asin):
    """Send screenshot file to Feishu dialog"""
    try:
        # Use full path to openclaw
        cmd = f"/usr/bin/openclaw message send --channel feishu --target {FEISHU_RECEIVER_ID} --media '{screenshot_path}'"
        # os.system returns exit_code * 256, so 0 means success
        return_code = os.system(cmd)
        if return_code == 0:
            print(f"  ✅ Screenshot {asin} sent to Feishu")
            return True
        else:
            exit_code = return_code >> 8
            print(f"  ❌ Failed to send screenshot {asin}, exit code: {exit_code}")
            return False
    except Exception as e:
        print(f"  ❌ Failed to send screenshot {asin}: {type(e).__name__}: {e}")
        return False

def take_screenshots(found_hrefs):
    """Use selenium only for taking screenshots - only open product pages we already found"""
    if not found_hrefs:
        print("No ASINs found, skipping screenshot phase")
        return 0
    
    print("=== [Phase 2] Taking screenshots with selenium ===\n")
    
    # Chrome options - enable images for correct page rendering
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
    
    # Use system installed chromedriver instead of downloading
    service = Service(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(300)  # 5 minutes
    
    success_count = 0
    from selenium.webdriver.common.by import By
    for (asin, href) in found_hrefs:
        print(f"Processing {asin}...")
        for retry in range(MAX_RETRIES):
            try:
                print(f"  Opening {asin}")
                driver.get(href)
                time.sleep(30)  # Wait for page load
                
                # Check for Amazon bot check page buttons
                # 1. Try "Continue shopping" button
                try:
                    buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Continue shopping')]")
                    if buttons:
                        print(f"  🔘 Found 'Continue shopping' button, clicking...")
                        buttons[0].click()
                        time.sleep(15)  # Wait for page reload after click
                except Exception as e:
                    pass
                
                # 2. Try "Try again" button (robot check page)
                try:
                    buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Try again')]")
                    if buttons:
                        print(f"  🔘 Found 'Try again' button (robot check), clicking...")
                        buttons[0].click()
                        time.sleep(15)  # Wait for page reload after click
                except Exception as e:
                    pass
                
                # 3. Try any "Continue" button
                try:
                    buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Continue')]")
                    if buttons:
                        print(f"  🔘 Found 'Continue' button, clicking...")
                        buttons[0].click()
                        time.sleep(15)  # Wait for page reload after click
                except Exception as e:
                    pass
                
                # Scroll to top of page to show search result position in screenshot
                try:
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(5)  # Wait for content to stabilize
                except Exception as e:
                    pass
                
                # Take screenshot
                screenshot_path = os.path.join(SCREENSHOT_DIR, f"{asin}_screenshot.png")
                driver.save_screenshot(screenshot_path)
                print(f"  ✅ Screenshot saved: {screenshot_path}")
                
                # Send screenshot to Feishu
                send_screenshot_to_feishu(screenshot_path, asin)
                
                success_count += 1
                break
            except Exception as e:
                print(f"  ❌ Attempt failed: {type(e).__name__}: {e}\n")
                if retry < MAX_RETRIES - 1:
                    print("  Waiting 15s before retry...\n")
                    time.sleep(15)
    
    print("\n=== [All completed] ===")
    print(f"Total ASINs found: {len(found_hrefs)}/{len(TARGET_ASINS)}")
    print(f"Screenshots successful: {success_count}/{len(found_hrefs)}")
    print(f"Screenshots saved to: {SCREENSHOT_DIR}")
    
    driver.quit()
    return success_count

def main():
    # Phase 1: Find ASINs with lightweight requests
    found_hrefs = search_and_find_asins()
    
    # Phase 2: Take screenshots with selenium
    success_count = take_screenshots(found_hrefs)
    
    return 0 if success_count == len(found_hrefs) else 1

if __name__ == "__main__":
    exit(main())
