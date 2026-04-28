
import requests
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.amazon.com/'
}

# Image URLs from Amazon product page
images = [
    {
        'name': 'B0DDDWWJBC_1.jpg',
        'url': 'https://m.media-amazon.com/images/I/81mhvY81xGL._AC_SY879_.jpg'
    },
    {
        'name': 'B0DDDWWJBC_2.jpg', 
        'url': 'https://m.media-amazon.com/images/I/71yGVyXrWfL._AC_SY879_.jpg'
    },
    {
        'name': 'B0DDDWWJBC_3.jpg',
        'url': 'https://m.media-amazon.com/images/I/81tYtWvF+sL._AC_SY879_.jpg'
    },
    {
        'name': 'B0CWZ2Z5TS_1.jpg',
        'url': 'https://m.media-amazon.com/images/I/81QKkhYqiOL._AC_SY879_.jpg'
    },
    {
        'name': 'B0CWZ2Z5TS_2.jpg',
        'url': 'https://m.media-amazon.com/images/I/71g5w-LLzGL._AC_SY879_.jpg'
    },
    {
        'name': 'B0CWZ2Z5TS_3.jpg',
        'url': 'https://m.media-amazon.com/images/I/81hN0oNvCfL._AC_SY879_.jpg'
    }
]

os.makedirs('images', exist_ok=True)

for img in images:
    try:
        print(f"Downloading {img['name']}...")
        response = requests.get(img['url'], headers=headers, timeout=30)
        response.raise_for_status()
        with open(f"images/{img['name']}", 'wb') as f:
            f.write(response.content)
        print(f"✅ Done: {img['name']} ({len(response.content)} bytes)")
    except Exception as e:
        print(f"❌ Failed: {img['name']} - {e}")

print("\nAll downloads completed!")
