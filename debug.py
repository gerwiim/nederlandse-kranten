import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

r = requests.get("https://www.nd.nl/reader", headers=HEADERS, timeout=10)
print("Status:", r.status_code)
print("URL na redirect:", r.url)
print(r.text[:2000])
