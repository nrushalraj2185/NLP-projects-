import requests
import os

os.makedirs('static/images', exist_ok=True)

urls = {
    "raju_bg.jpg": "https://i0.wp.com/businessmanagementblog.com/wp-content/uploads/2023/01/Raju-3-idiots-fear-is-not-good-for-grades.jpg?fit=907%2C558&ssl=1",
    "raju_interview.jpg": "https://i.ytimg.com/vi/JicAH6JuRq0/maxresdefault.jpg",
    "raju_avatar.jpg": "https://c.ndtvimg.com/2021-06/lnlt2bu8_3-idiots_625x300_02_June_21.jpg"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

for name, url in urls.items():
    try:
        print(f"Downloading {name}...")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(f'static/images/{name}', 'wb') as f:
                f.write(response.content)
            print(f"✅ Saved {name}")
        else:
            print(f"❌ Failed to download {name}: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error downloading {name}: {e}")
