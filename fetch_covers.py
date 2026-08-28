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

def get_nrc_url():
    api = f"https://www.nrc.nl/de/data/NH/{yyyy}/{mm}/{dd}/"
    try:
        r = requests.get(api, headers=HEADERS, timeout=10)
        data = r.json()
        return data["pages"][0]["fullscreen_url_orig"]
    except Exception as e:
        print(f"NRC fout: {e}")
        return None

def get_parool_url():
    return "https://cdn-03.tapp.dpgmedia.cloud/packshot/hp/latest.png"

def get_rd_url():
    d = date.today()
    if d.weekday() == 6:  # zondag
        d = date.fromordinal(d.toordinal() - 1)
    datum = d.strftime("%Y%m%d")
    return f"https://cdn.erdee.nl/epaper/_fpage/RDB/{d.year}/RDB_RDB_{datum}.jpg"

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


# ─── Hulpfuncties ─────────────────────────────────────────────────────────────

def maak_regel(quote, url):
    return f"voorpagina: {quote}{url}{quote}"

def vind_huidige_url(content, naam, quote):
    """Zoek de huidige voorpagina-URL voor een specifieke krant."""
    q = re.escape(quote)
    # Zoek de naam, dan de eerstvolgende voorpagina-regel met het juiste quote-teken
    patroon = r'naam:\s*"' + re.sub(r'([\.\+\*\?\^\$\{\}\[\]\|\(\)])', r'\\\1', naam) + r'".*?voorpagina:\s*' + q + r'([^' + q + r']+)' + q
    match = re.search(patroon, content, flags=re.DOTALL)
    if match:
        return match.group(1)
    return None

def vervang_url(content, naam, quote, huidig, nieuwe_url):
    """Vervang de voorpagina-URL via str.replace."""
    oude_regel = maak_regel(quote, huidig)
    nieuwe_regel = maak_regel(quote, nieuwe_url)
    if oude_regel in content:
        content = content.replace(oude_regel, nieuwe_regel)
        print(f"  ✓ Bijgewerkt: {naam}")
    else:
        print(f"  ✗ Niet gevonden: {naam}")
    return content


# ─── Krantenlijst ─────────────────────────────────────────────────────────────

KRANTEN = [
    {"naam": "Algemeen Dagblad",       "quote": '"',  "huidig": "https://cdn-03.tapp.dpgmedia.cloud/packshot/ad/ad/latest.png", "nieuw": get_ad_url},
    {"naam": "Nederlands Dagblad",     "quote": '"',  "huidig": None, "nieuw": get_nd_url},
    {"naam": "NRC",                    "quote": "`",  "huidig": None, "nieuw": get_nrc_url},
    {"naam": "Het Parool",             "quote": '"',  "huidig": "https://cdn-03.tapp.dpgmedia.cloud/packshot/hp/latest.png", "nieuw": get_parool_url},
    {"naam": "Reformatorisch Dagblad", "quote": "`",  "huidig": None, "nieuw": get_rd_url},
    {"naam": "De Telegraaf",           "quote": '"',  "huidig": None, "nieuw": get_telegraaf_url},
    {"naam": "Trouw",                  "quote": '"',  "huidig": "https://cdn-03.tapp.dpgmedia.cloud/packshot/tr/latest.png", "nieuw": get_trouw_url},
    {"naam": "de Volkskrant",          "quote": '"',  "huidig": "https://cdn-03.tapp.dpgmedia.cloud/packshot/vk/latest.png", "nieuw": get_vk_url},
]


# ─── Uitvoeren ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Datum: {yyyy}-{mm}-{dd}")

    with open("app.js", "r", encoding="utf-8") as f:
        appjs = f.read()

    for krant in KRANTEN:
        nieuwe_url = krant["nieuw"]()
        if not nieuwe_url:
            print(f"  – Overgeslagen: {krant['naam']} (geen URL opgehaald)")
            continue

        huidig = krant["huidig"]
        if huidig is None:
            huidig = vind_huidige_url(appjs, krant["naam"], krant["quote"])

        if huidig is None:
            print(f"  ✗ Huidige URL niet gevonden in app.js: {krant['naam']}")
            continue

        appjs = vervang_url(appjs, krant["naam"], krant["quote"], huidig, nieuwe_url)

    with open("app.js", "w", encoding="utf-8") as f:
        f.write(appjs)

    print("app.js bijgewerkt.")
    print("Klaar!")
