import requests
import re
from datetime import datetime

now = datetime.now()
yyyy = now.strftime("%Y")
mm   = now.strftime("%m")
dd   = now.strftime("%d")
datum_compact = f"{yyyy}{mm}{dd}"  # bv. 20260827

# ─── De Telegraaf ────────────────────────────────────────────────────────────

def get_telegraaf_url():
    api = "https://mhu-tlg-production-backend-api.twipecloud.net/Data/DataService.svc/getcontentpackagelist/TWPMHUTLG/0/30"
    try:
        r = requests.get(api, timeout=10)
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
        r = requests.get(api, timeout=10)
        data = r.json()
        page = data["pages"][0]
        # Haal de hash op uit de URL, bv. "101-full-b4ba3b.jpg" → "b4ba3b"
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

    # Telegraaf: vervang de volledige URL tussen aanhalingstekens
    if telegraaf_url:
        content = re.sub(
            r'(voorpagina:\s*"https://mhu-tlg-webreader-production\.twipemobile\.com/data/)[^"]*(")',
            rf'\g<1>{telegraaf_url.split("/data/")[1]}\2',
            content
        )
        # Eenvoudiger: vervang gewoon de hele URL direct
        content = re.sub(
            r'"https://mhu-tlg-webreader-production\.twipemobile\.com/data/[^"]*"',
            f'"{telegraaf_url}"',
            content
        )
        print(f"Telegraaf URL bijgewerkt.")

    # NRC: alleen de hash vervangen in de template literal
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
