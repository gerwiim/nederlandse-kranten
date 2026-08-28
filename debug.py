import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# Probeer de Pubble API met de bekende klant-ID
urls = [
    "https://api.pubble.cloud/v2/customers/9ed0159c/papers/latest",
    "https://api.pubble.cloud/v2/papers/9ed0159c/latest",
    "https://storage.pubble.cloud/9ed0159c/paper/latest/files/large/1.jpg",
    "https://pubble.cloud/api/customers/9ed0159c/issues/latest",
]

for url in urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"\n{url}")
        print(f"Status: {r.status_code}")
        print(r.text[:200])
    except Exception as e:
        print(f"{url} → fout: {e}")
