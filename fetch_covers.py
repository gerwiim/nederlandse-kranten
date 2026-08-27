import requests
import json
import re
from datetime import datetime

now = datetime.now()
yyyy = now.strftime("%Y")
mm   = now.strftime("%m")
dd   = now.strftime("%d")
datum_compact = f"{yyyy}{mm}{dd}"  # bv. 20260827

# ─── De Telegraaf ────────────────────────────────────────────────────────────

def get_telegraaf_url():
    api = "https://mhu-tlg-production-backend-api.twipecloud.net/api/data/KiosquePublications/TWPMHUTLG?format=json"
    try:
        r = requests.get(api, timeout=10)
        data = r.json()
        pub = data["KiosquePublications"][0]
        package_id   = pub["ContentPackageId"]
        thumbnail_id = pub["Publications"][0]["ThumbnailPublicationPageId"]
        return f"https://mhu-tlg-webreader-production.twipemobile.com/data/{package_id}/covers/Preview-MEDIUM-{thumbnail_id}.jpg"
    except Exception as e:
        print(f"Telegraaf fout: {e}")
        return None

# ─── NRC ─────────────────────────────────────────────────────────────────────

def get_nrc_url():
    api = f"https://www.nrc.nl/de/data/NH/{datum_compact}/"
    try:
        r = requests.get(api, timeout=10)
        data = r.json()
        # Pagina 0 = voorpagina (pagina 101)
        page = data["pages"][0]
        return page["fullscreen_url_orig"]
    except Exception as e:
        print(f"NRC fout: {e}")
        return None

# ─── app.js bijwerken ─────────────────────────────────────────────────────────

def update_appjs(telegraaf_url, nrc_url):
    with open("app.js", "r", encoding="utf-8") as f:
        content = f.read()

    if telegraaf_url:
        content = re.sub(
            r'(naam: "De Telegraaf",[^}]*voorpagina: ")[^"]*(")',
            rf'\g<1>{telegraaf_url}\2',
            content
        )
        print(f"Telegraaf URL bijgewerkt: {telegraaf_url}")

    if nrc_url:
        content = re.sub(
            r'(naam: "NRC",[^}]*voorpagina: ")[^"]*(")',
            rf'\g<1>{nrc_url}\2',
            content
        )
        print(f"NRC URL bijgewerkt: {nrc_url}")

    with open("app.js", "w", encoding="utf-8") as f:
        f.write(content)

# ─── Uitvoeren ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Datum: {yyyy}-{mm}-{dd}")
    telegraaf_url = get_telegraaf_url()
    nrc_url       = get_nrc_url()
    update_appjs(telegraaf_url, nrc_url)
    print("Klaar!")
