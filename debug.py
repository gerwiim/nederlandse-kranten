import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# Probeer de Pubble API direct
urls = [
    "https://api.pubble.cloud/v1/papers/nd/issues/latest",
    "https://nd.nl/api/epaper",
    "https://www.nd.nl/epaper",
]

for url in urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"\n{url}")
        print(f"Status: {r.status_code}")
        print(r.text[:300])
    except Exception as e:
        print(f"{url} → fout: {e}")
