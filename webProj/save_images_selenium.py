
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import os

# Setup chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Create directories
os.makedirs('images/B0DDDWWJBC', exist_ok=True)
os.makedirs('images/B0CWZ2Z5TS', exist_ok=True)

# Get B0DDDWWJBC page
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.amazon.com/dp/B0DDDWWJBC')

# Find all image elements in product description
print("Finding images for B0DDDWWJBC...")
images = driver.find_elements("css selector", "#productDescription img")

for i, img in enumerate(images):
    src = img.get_attribute('src')
    if src:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.amazon.com/'
            }
            r = requests.get(src, headers=headers)
            filename = f'images/B0DDDWWJBC/{i+1}.jpg'
            with open(filename, 'wb') as f:
                f.write(r.content)
            print(f"Saved {filename} - {len(r.content)} bytes")
        except Exception as e:
            print(f"Failed {src}: {e}")

# Now B0CWZ2Z5TS
driver.get('https://www.amazon.com/dp/B0CWZ2Z5TS')
print("\nFinding images for B0CWZ2Z5TS...")
images = driver.find_elements("css selector", "#productDescription img")

for i, img in enumerate(images):
    src = img.get_attribute('src')
    if src:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.amazon.com/'
            }
            r = requests.get(src, headers=headers)
            filename = f'images/B0CWZ2Z5TS/{i+1}.jpg'
            with open(filename, 'wb') as f:
                f.write(r.content)
            print(f"Saved {filename} - {len(r.content)} bytes")
        except Exception as e:
            print(f"Failed {src}: {e}")

driver.quit()
print("\nDone!")
