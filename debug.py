import requests
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def laad_nd_cookies(pad="nd_cookies.txt"):
    cookies = {}
    with open(pad, "r") as f:
        for regel in f:
            if "=" in regel:
                naam, waarde = regel.strip().split("=", 1)
                cookies[naam.strip()] = waarde.strip()
    return cookies

cookies = laad_nd_cookies()
r = requests.get("https://www.nd.nl/reader", headers=HEADERS, cookies=cookies, timeout=10)

print("Status:", r.status_code)
print("b8fb8a46 in response:", "b8fb8a46" in r.text)
print("storage.pubble.cloud in response:", "storage.pubble.cloud" in r.text)
print("9ed0159c in response:", "9ed0159c" in r.text)
