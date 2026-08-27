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
    api = "https://mhu-tlg-production-backend-api.twipecloud.net/api/data/KiosquePublications/TWPMHUTLG?format=json"
    try:
        r = requests.get(api, timeout=10)
        data = r.json()

        # Zoek door alle KiosquePublications en hun Publications
        # De echte krant heeft een PublicationName in het formaat "DD-MM-YYYY"
        datum_patroon = re.compile(r"^\d{2}-\d{2}-\d{4}$")

        for kiosque in data["KiosquePublications"]:
            for pub in kiosque.get("Publications", []):
                naam = pub.get("PublicationName", "")
                if datum_patroon.match(naam):
                    package_id   = kiosque["ContentPackageId"]
                    thumbnail_id = pub["ThumbnailPublicationPageId"]
                    url = f"https://mhu-tlg-webreader-production.twipemobile.com/data/{package_id}/covers/Preview-MEDIUM-{thumbnail_id}.jpg"
                    print(f"Telegraaf gevonden: {naam} → {url}")
                    return url

        print("Telegraaf: geen editie met datumnaam gevonden")
        return None

    except Exception as e:
        print(f"Telegraaf fout: {e}")
        return None

# ─── NRC ─────────────────────────────────────────────────────────────────────

def get_nrc_url():
    api = f"https://www.nrc.nl/de/data/NH/{datum_compact}/"
    try:
        r = requests.get(api, timeout=10)
        data = r.json()
        page = data["pages"][0]
        url = page["fullscreen_url_orig"]
        print(f"NRC gevonden: {url}")
        return url
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

    if nrc_url:
        content = re.sub(
            r'(naam: "NRC",[^}]*voorpagina: ")[^"]*(")',
            rf'\g<1>{nrc_url}\2',
            content
        )

    with open("app.js", "w", encoding="utf-8") as f:
        f.write(content)

    print("app.js bijgewerkt.")

# ─── Uitvoeren ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Datum: {yyyy}-{mm}-{dd}")
    telegraaf_url = get_telegraaf_url()
    nrc_url       = get_nrc_url()
    update_appjs(telegraaf_url, nrc_url)
    print("Klaar!")
