
import requests
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.amazon.com/'
}

# B0DDDWWJBC images (A+ content)
b0ddd_images = [
    'https://m.media-amazon.com/images/I/81mhvY81xGL._AC_SY879_.jpg',
    'https://m.media-amazon.com/images/I/71yGVyXrWfL._AC_SY879_.jpg',
    'https://m.media-amazon.com/images/I/81tYtWvF+sL._AC_SY879_.jpg',
    'https://m.media-amazon.com/images/I/71hVnOKNLbL._AC_SY879_.jpg',
    'https://m.media-amazon.com/images/I/81w+GpQrGbL._AC_SY879_.jpg',
    'https://m.media-amazon.com/images/I/71gZdpzTjqL._AC_SY879_.jpg'
]

# B0CWZ2Z5TS images
b0cwz_images = [
    'https://m.media-amazon.com/images/I/81QKkhYqiOL._AC_SY879_.jpg',
    'https://m.media-amazon.com/images/I/71g5w-LLzGL._AC_SY879_.jpg',
    'https://m.media-amazon.com/images/I/81hN0oNvCfL._AC_SY879_.jpg',
    'https://m.media-amazon.com/images/I/71gKdpzTjqL._AC_SY879_.jpg',
    'https://m.media-amazon.com/images/I/81w+GpQrGbL._AC_SY879_.jpg',
    'https://m.media-amazon.com/images/I/71yVnOKNLbL._AC_SY879_.jpg'
]

os.makedirs('images/B0DDDWWJBC', exist_ok=True)
os.makedirs('images/B0CWZ2Z5TS', exist_ok=True)

print("=== Downloading B0DDDWWJBC images ===\n")
for i, url in enumerate(b0ddd_images):
    filename = f'images/B0DDDWWJBC/{i+1}.jpg'
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ {filename} - {len(response.content)} bytes")
    except Exception as e:
        print(f"❌ {filename} - {e}")

print("\n=== Downloading B0CWZ2Z5TS images ===\n")
for i, url in enumerate(b0cwz_images):
    filename = f'images/B0CWZ2Z5TS/{i+1}.jpg'
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ {filename} - {len(response.content)} bytes")
    except Exception as e:
        print(f"❌ {filename} - {e}")

print("\n=== All downloads completed ===")
