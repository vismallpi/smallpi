
import requests
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.amazon.com/'
}

# Filtered product images for B0CWZ2Z5TS
b0cwz_images = [
    'https://m.media-amazon.com/images/I/51plNLXayGL._AC_SY450_.jpg',
    'https://m.media-amazon.com/images/I/51cAqFkckrL._AC_US40_.jpg',
    'https://m.media-amazon.com/images/I/51OK82ywmTL._AC_US40_.jpg',
    'https://m.media-amazon.com/images/I/51zYk9APd7L._AC_US40_.jpg',
    'https://m.media-amazon.com/images/I/51plNLXayGL._AC_.jpg',
]

os.makedirs('images/B0CWZ2Z5TS', exist_ok=True)

print("=== Downloading B0CWZ2Z5TS product images ===\n")
for i, url in enumerate(b0cwz_images):
    filename = f'images/B0CWZ2Z5TS/{i+1}.jpg'
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(r.content)
        print(f"✅ {filename} - {len(r.content)} bytes")
    except Exception as e:
        print(f"❌ {filename} - {e}")

print("\nDone!")
