import requests
import re

url = "https://www.pexels.com/video/female-doctor-on-an-online-consultation-7579342/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
try:
    r = requests.get(url, headers=headers, timeout=10)
    print("Status:", r.status_code)
    mp4s = set(re.findall(r'https://[^\s"\'<>]+\.mp4[^\s"\'<>]*', r.text))
    print("Found MP4s:", len(mp4s))
    for m in list(mp4s)[:5]:
        print("MP4:", m)
except Exception as e:
    print("Error:", e)
