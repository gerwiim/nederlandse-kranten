import requests
import re
from datetime import datetime

now = datetime.now()
yyyy = now.strftime("%Y")
mm   = now.strftime("%m")
dd   = now.strftime("%d")
datum_compact = f"{yyyy}{mm}{dd}"  # bv. 20260827

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# ─── De Telegraaf ────────────────────────────────────────────────────────────

def get_telegraaf_url():
    api = "https://mhu-tlg-production-backend-api.twipecloud.net/Data/DataService.svc/getcontentpackagelist/TWPMHUTLG/0/30"
    try:
        r = requests.get(api, headers=HEADERS, timeout=10)
        data = r.json()
        editie       = data[0]
        package_id   = editie["ContentPackageId"]
        thumbnail_id = editie["ThumbnailId"]
        pub_date     = editie["PublicationDate"][:10]
        url = f"https://mhu-tlg-webreader-production.twipemobile.com/data/{package_id}/covers/Preview-MEDIUM-{thumbnail_id}.jpg"
        print(f"Telegraaf gevonden: {pub_date} (package {package_id}) → {url}")
        return url
    except Exception as e:
        print(f"Telegraaf fout: {e}")
        return None

# ─── NRC ─────────────────────────────────────────────────────────────────────

def get_nrc_hash():
    api = f"https://www.nrc.nl/de/data/NH/{datum_compact}/"
    try:
        r = requests.get(api, headers=HEADERS, timeout=10)
        print(f"NRC status: {r.status_code}")
        print(f"NRC response (eerste 200 tekens): {r.text[:200]}")
        data = r.json()
        page = data["pages"][0]
        url = page["fullscreen_url_orig"]
        match = re.search(r'101-full-([a-f0-9]+)\.jpg', url)
        if match:
            hash_waarde = match.group(1)
            print(f"NRC hash gevonden: {hash_waarde}")
            return hash_waarde
        print(f"NRC: hash niet gevonden in URL: {url}")
        return None
    except Exception as e:
        print(f"NRC fout: {e}")
        return None

# ─── app.js bijwerken ─────────────────────────────────────────────────────────

def update_appjs(telegraaf_url, nrc_hash):
    with open("app.js", "r", encoding="utf-8") as f:
        content = f.read()

    if telegraaf_url:
        content = re.sub(
            r'"https://mhu-tlg-webreader-production\.twipemobile\.com/data/[^"]*"',
            f'"{telegraaf_url}"',
            content
        )
        print("Telegraaf URL bijgewerkt.")

    if nrc_hash:
        content = re.sub(
            r'(101-full-)[a-f0-9]+(\.jpg)',
            rf'\g<1>{nrc_hash}\2',
            content
        )
        print(f"NRC hash bijgewerkt naar: {nrc_hash}")

    with open("app.js", "w", encoding="utf-8") as f:
        f.write(content)

    print("app.js bijgewerkt.")

# ─── Uitvoeren ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Datum: {yyyy}-{mm}-{dd}")
    telegraaf_url = get_telegraaf_url()
    nrc_hash      = get_nrc_hash()
    update_appjs(telegraaf_url, nrc_hash)
    print("Klaar!")
