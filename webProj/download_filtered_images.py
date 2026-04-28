
import requests
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.amazon.com/'
}

# Filtered product images for B0DDDWWJBC from the list
b0ddd_images = [
    'https://m.media-amazon.com/images/I/71bJfqYBiFL._AC_SY450_.jpg',
    'https://m.media-amazon.com/images/I/51x5hG0vunL._AC_.jpg',
    'https://m.media-amazon.com/images/I/4100og2cJOL._AC_US40_.jpg',
    'https://m.media-amazon.com/images/I/518djRtzJdL._AC_US40_.jpg',
    'https://m.media-amazon.com/images/I/51+uKQS+wbL._AC_US40_.jpg',
    'https://m.media-amazon.com/images/I/51mZ9OzNNpL._AC_US40_.jpg',
]

os.makedirs('images/B0DDDWWJBC', exist_ok=True)

print("=== Downloading B0DDDWWJBC product images ===\n")
for i, url in enumerate(b0ddd_images):
    filename = f'images/B0DDDWWJBC/{i+1}.jpg'
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(r.content)
        print(f"✅ {filename} - {len(r.content)} bytes")
    except Exception as e:
        print(f"❌ {filename} - {e}")

print("\nDone!")
