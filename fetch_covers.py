import requests
import re
from datetime import datetime, date

now = datetime.now()
yyyy = now.strftime("%Y")
mm   = now.strftime("%m")
dd   = now.strftime("%d")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# ─── URL-functies ─────────────────────────────────────────────────────────────

def get_ad_url():
    return "https://cdn-03.tapp.dpgmedia.cloud/packshot/ad/ad/latest.png"

def get_nd_url():
    try:
        r = requests.get("https://www.nd.nl/reader", headers=HEADERS, timeout=10)
        match = re.search(r'https://storage\.pubble\.cloud/[^"?]+/files/large/1\.jpg', r.text)
        if match:
            return match.group(0)
        print("ND: geen URL gevonden")
        return None
    except Exception as e:
        print(f"ND fout: {e}")
        return None

def get_rd_url():
    d = date.today()
    if d.weekday() == 6:  # zondag
        d = date.fromordinal(d.toordinal() - 1)
    datum = d.strftime("%Y%m%d")
    return f"https://cdn.erdee.nl/epaper/_fpage/RDB/{d.year}/RDB_RDB_{datum}.jpg"

def get_parool_url():
    return "https://cdn-03.tapp.dpgmedia.cloud/packshot/hp/latest.png"

def get_nrc_url():
    api = f"https://www.nrc.nl/de/data/NH/{yyyy}/{mm}/{dd}/"
    try:
        r = requests.get(api, headers=HEADERS, timeout=10)
        data = r.json()
        return data["pages"][0]["fullscreen_url_orig"]
    except Exception as e:
        print(f"NRC fout: {e}")
        return None

def get_telegraaf_url():
    api = "https://mhu-tlg-production-backend-api.twipecloud.net/Data/DataService.svc/getcontentpackagelist/TWPMHUTLG/0/30"
    try:
        r = requests.get(api, headers=HEADERS, timeout=10)
        data = r.json()
        editie = data[0]
        package_id   = editie["ContentPackageId"]
        thumbnail_id = editie["ThumbnailId"]
        return f"https://mhu-tlg-webreader-production.twipemobile.com/data/{package_id}/covers/Preview-MEDIUM-{thumbnail_id}.jpg"
    except Exception as e:
        print(f"Telegraaf fout: {e}")
        return None

def get_trouw_url():
    return "https://cdn-03.tapp.dpgmedia.cloud/packshot/tr/latest.png"

def get_vk_url():
    return "https://cdn-03.tapp.dpgmedia.cloud/packshot/vk/latest.png"


# ─── app.js bijwerken ─────────────────────────────────────────────────────────

def vervang_url_in_appjs(content, naam, nieuwe_url):
    """Vervang de voorpagina-URL voor een krant op basis van de naam in app.js."""
    for quote in ['`', '"']:
        q = re.escape(quote)
        patroon = rf'(naam:\s*"{re.escape(naam)}"[^{{}}]*?voorpagina:\s*{q})([^{q}]+)({q})'
        nieuwe_content = re.sub(patroon, lambda m: m.group(1) + nieuwe_url + m.group(3), content, flags=re.DOTALL)
        if nieuwe_content != content:
            print(f"  ✓ Bijgewerkt: {naam}")
            return nieuwe_content
    print(f"  ✗ Geen match gevonden voor: {naam}")
    return content


# ─── Uitvoeren ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Datum: {yyyy}-{mm}-{dd}")

    with open("app.js", "r", encoding="utf-8") as f:
        appjs = f.read()

    # Naam moet exact overeenkomen met naam in app.js
    updates = [
        ("Algemeen Dagblad",       get_ad_url()),
        ("Nederlands Dagblad",     get_nd_url()),
        ("NRC",                    get_nrc_url()),
        ("Het Parool",             get_parool_url()),
        ("Reformatorisch Dagblad", get_rd_url()),
        ("De Telegraaf",           get_telegraaf_url()),
        ("Trouw",                  get_trouw_url()),
        ("de Volkskrant",          get_vk_url()),
    ]

    for naam, url in updates:
        if url:
            appjs = vervang_url_in_appjs(appjs, naam, url)

    with open("app.js", "w", encoding="utf-8") as f:
        f.write(appjs)

    print("app.js bijgewerkt.")
    print("Klaar!")
