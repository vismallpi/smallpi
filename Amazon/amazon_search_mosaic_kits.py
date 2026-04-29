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
MAX_RETRIES = 3
# 接收log的飞书用户open_id
FEISHU_RECEIVER_ID = "ou_a331505193726d421fb0108a11bc6197"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Send log to Feishu dialog
def send_log_to_feishu(log_text):
    """Send log message to specified Feishu user via OpenClaw message API"""
    import os
    import sys
    # We can call OpenClaw's message tool by executing command
    try:
        cmd = f'''openclaw message send --channel feishu --target {FEISHU_RECEIVER_ID} --message "{log_text.replace('"', '\\"')}"'''
        os.system(cmd)
        print(f"[LOG SENT] {log_text}")
    except Exception as e:
        print(f"[LOG FAILED] {log_text}\nError: {e}")

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
    
    log_text = "=== [Phase 1] Searching with requests (lightweight) ===\n"
    print(log_text)
    send_log_to_feishu(log_text)
    
    while len(found_hrefs) < len(TARGET_ASINS):
        log_text = f"Searching page {page}..."
        print(log_text)
        send_log_to_feishu(log_text)
        
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
                log_text = f"  Attempt {retry + 1}/{MAX_RETRIES} failed: {type(e).__name__}: {e}"
                print(log_text)
                send_log_to_feishu(log_text)
                if retry < MAX_RETRIES - 1:
                    log_text = f"  Waiting 10s before retry...\n"
                    print(log_text)
                    send_log_to_feishu(log_text)
                    time.sleep(10)
        
        if not success:
            log_text = f"❌ Failed to load page {page} after {MAX_RETRIES} retries\n"
            print(log_text)
            send_log_to_feishu(log_text)
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
                            log_text = f"  ✅ Found ASIN: {asin} on page {page}"
                            print(log_text)
                            send_log_to_feishu(log_text)
                            log_text = f"      Link: {full_href}\n"
                            print(log_text)
                            send_log_to_feishu(log_text)
                            found_hrefs.append((asin, full_href))
        
        if len(found_hrefs) == len(TARGET_ASINS):
            break
        
        # Check if there's next page by looking for "Next" button
        next_button = soup.select_one('a.s-pagination-next')
        if not next_button or 's-pagination-disabled' in next_button.get('class', []):
            log_text = "❌ No more pages available\n"
            print(log_text)
            send_log_to_feishu(log_text)
            break
        
        page += 1
        time.sleep(10)
    
    log_text = f"[Phase 1 completed] Found {len(found_hrefs)}/{len(TARGET_ASINS)} target ASINs\n"
    print(log_text)
    send_log_to_feishu(log_text)
    return found_hrefs

def get_category_ranking(driver, asin):
    """Extract category ranking from Amazon product page, specifically look for Best Sellers Rank in Product Specifications"""
    rankings = []
    from selenium.webdriver.common.by import By
    try:
        # Method 1: Look specifically for Product Specifications section
        product_spec_headers = driver.find_elements(By.XPATH, "//*[contains(text(), 'Product Specifications')]")
        if product_spec_headers:
            # Get the table after Product Specifications
            for header in product_spec_headers:
                try:
                    # Find the next table after this header
                    table = header.find_element(By.XPATH, "./following::table[1]")
                    text = table.text
                    lines = text.split("\n")
                    # Look for Best Sellers Rank and then the mosaic tile line
                    for i, line in enumerate(lines):
                        if "Best Sellers" in line or "best seller" in line.lower():
                            # Check next lines for mosaic tile ranking
                            for check_line in lines[i+1:]:
                                check_line = check_line.strip()
                                if "#" in check_line and "mosaic" in check_line.lower() and "tile" in check_line.lower():
                                    rankings.append(check_line)
                                    break
                            break
                    # If not found in this table, search entire table text
                    if not rankings:
                        for line in lines:
                            line = line.strip()
                            if "#" in line and "mosaic" in line.lower() and "tile" in line.lower():
                                rankings.append(line)
                                break
                    if rankings:
                        break
                except Exception:
                    continue
        
        # Method 2: If not found in table, search entire page text
        if not rankings:
            body = driver.find_element(By.TAG_NAME, "body")
            text = body.text
            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if "#" in line and "mosaic" in line.lower() and "tile" in line.lower():
                    rankings.append(line)
                    break
        
        # Method 3: Look for any Best Sellers Rank that contains mosaic
        if not rankings:
            body = driver.find_element(By.TAG_NAME, "body")
            text = body.text
            lines = text.split("\n")
            found_best_sellers = False
            for line in lines:
                line = line.strip()
                if "Best Sellers Rank" in line:
                    found_best_sellers = True
                if found_best_sellers and "#" in line and "mosaic" in line.lower() and "tile" in line.lower():
                    rankings.append(line)
                    break
        
        # Send all found rankings to Feishu
        if rankings:
            for rank in rankings:
                send_log_to_feishu(f"  📊 {asin} Category Ranking: {rank}")
        else:
            send_log_to_feishu(f"  ⚠️ {asin}: No category ranking found")
        
        return rankings
    except Exception as e:
        send_log_to_feishu(f"  ⚠️ Failed to extract ranking for {asin}: {type(e).__name__}: {e}")
        return []

def send_screenshot_to_feishu(screenshot_path, asin):
    """Send screenshot file to Feishu dialog"""
    try:
        # Use full path to openclaw
        cmd = f"/usr/bin/openclaw message send --channel feishu --target {FEISHU_RECEIVER_ID} --media '{screenshot_path}'"
        # os.system returns exit_code * 256, so 0 means success
        return_code = os.system(cmd)
        if return_code == 0:
            send_log_to_feishu(f"  ✅ Screenshot {asin} sent to Feishu")
            return True
        else:
            exit_code = return_code >> 8
            send_log_to_feishu(f"  ❌ Failed to send screenshot {asin}, exit code: {exit_code}")
            return False
    except Exception as e:
        send_log_to_feishu(f"  ❌ Failed to send screenshot {asin}: {type(e).__name__}: {e}")
        return False

def take_screenshots(found_hrefs):
    """Use selenium only for taking screenshots - only open product pages we already found"""
    if not found_hrefs:
        log_text = "No ASINs found, skipping screenshot phase"
        print(log_text)
        send_log_to_feishu(log_text)
        return 0
    
    log_text = "=== [Phase 2] Taking screenshots with selenium ===\n"
    print(log_text)
    send_log_to_feishu(log_text)
    
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
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(300)  # 5 minutes
    
    success_count = 0
    from selenium.webdriver.common.by import By
    for (asin, href) in found_hrefs:
        log_text = f"Processing {asin}..."
        print(log_text)
        send_log_to_feishu(log_text)
        for retry in range(MAX_RETRIES):
            try:
                log_text = f"  Attempt {retry + 1}/{MAX_RETRIES}: Opening {asin}"
                print(log_text)
                send_log_to_feishu(log_text)
                driver.get(href)
                time.sleep(30)  # Wait for page load
                
                # Check for Amazon bot check page buttons
                bot_check_handled = False
                # 1. Try "Continue shopping" button
                try:
                    buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Continue shopping')]")
                    if buttons:
                        log_text = f"  🔘 Found 'Continue shopping' button, clicking..."
                        print(log_text)
                        send_log_to_feishu(log_text)
                        buttons[0].click()
                        time.sleep(15)  # Wait for page reload after click
                        bot_check_handled = True
                except Exception as e:
                    pass
                
                # 2. Try "Try again" button (robot check page)
                if not bot_check_handled:
                    try:
                        buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Try again')]")
                        if buttons:
                            log_text = f"  🔘 Found 'Try again' button (robot check), clicking..."
                            print(log_text)
                            send_log_to_feishu(log_text)
                            buttons[0].click()
                            time.sleep(15)  # Wait for page reload after click
                            bot_check_handled = True
                    except Exception as e:
                        pass
                
                # 3. Try any "Continue" button
                if not bot_check_handled:
                    try:
                        buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Continue')]")
                        if buttons:
                            log_text = f"  🔘 Found 'Continue' button, clicking..."
                            print(log_text)
                            send_log_to_feishu(log_text)
                            buttons[0].click()
                            time.sleep(15)  # Wait for page reload after click
                    except Exception as e:
                        pass
                
                # Scroll to bottom of page to load all content including Product Specifications
                try:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(10)  # Wait for content to load after scrolling
                except Exception as e:
                    pass
                
                # 1. Get category ranking
                log_text = f"  Extracting category ranking..."
                print(log_text)
                send_log_to_feishu(log_text)
                rankings = get_category_ranking(driver, asin)
                
                # 2. Take screenshot
                screenshot_path = os.path.join(SCREENSHOT_DIR, f"{asin}_screenshot.png")
                driver.save_screenshot(screenshot_path)
                log_text = f"  ✅ Screenshot saved: {screenshot_path}"
                print(log_text)
                send_log_to_feishu(log_text)
                
                # 3. Send screenshot to Feishu
                send_screenshot_to_feishu(screenshot_path, asin)
                
                success_count += 1
                break
            except Exception as e:
                log_text = f"  ❌ Attempt {retry + 1} failed: {type(e).__name__}: {e}\n"
                print(log_text)
                send_log_to_feishu(log_text)
                if retry < MAX_RETRIES - 1:
                    log_text = "  Waiting 15s before retry...\n"
                    print(log_text)
                    send_log_to_feishu(log_text)
                    time.sleep(15)
    
    log_text = "\n=== [All completed] ==="
    print(log_text)
    send_log_to_feishu(log_text)
    log_text = f"Total ASINs found: {len(found_hrefs)}/{len(TARGET_ASINS)}"
    print(log_text)
    send_log_to_feishu(log_text)
    log_text = f"Screenshots successful: {success_count}/{len(found_hrefs)}"
    print(log_text)
    send_log_to_feishu(log_text)
    log_text = f"Screenshots saved to: {SCREENSHOT_DIR}"
    print(log_text)
    send_log_to_feishu(log_text)
    
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
