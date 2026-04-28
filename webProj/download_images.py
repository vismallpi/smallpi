
import requests
import os

os.makedirs('images', exist_ok=True)

# Download images
images = [
    {
        'asin': 'B0DDDWWJBC',
        'url': 'https://m.media-amazon.com/images/I/81mhvY8xWHL._AC_SY679_.jpg',
        'filename': 'B0DDDWWJBC-main.jpg'
    },
    {
        'asin': 'B0CWZ2Z5TS',
        'url': 'https://m.media-amazon.com/images/I/81QKkhYqiL._AC_SY679_.jpg',
        'filename': 'B0CWZ2Z5TS-main.jpg'
    }
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.amazon.com/'
}

for img in images:
    try:
        r = requests.get(img['url'], headers=headers)
        with open(f'images/{img["filename"]}', 'wb') as f:
            f.write(r.content)
        print(f"✅ Downloaded {img['filename']}, size: {len(r.content)} bytes")
    except Exception as e:
        print(f"❌ Failed {img['filename']}: {e}")
