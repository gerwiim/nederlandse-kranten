import requests
import re
import json
import os
from datetime import datetime, date, timedelta

now = datetime.now()
yyyy = now.strftime("%Y")
mm = now.strftime("%m")
dd = now.strftime("%d")
vandaag = f"{yyyy}-{mm}-{dd}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

ARCHIEF_BESTAND = "archive.json"
COVERS_MAP = "covers"
MAX_DAGEN = 7

# Kranten waarvoor we de afbeelding downloaden (geen datumspecifieke externe URL)
DOWNLOAD_KRANTEN = {"Algemeen Dagblad", "Het Parool", "Trouw", "de Volkskrant", "Reformatorisch Dagblad"}

os.makedirs(COVERS_MAP, exist_ok=True)

# ─── URL-functies ────────────────────────────────────────────────────────────

def get_ad_url():
    return "https://cdn-03.tapp.dpgmedia.cloud/packshot/ad/ad/latest.png"

def get_nd_url():
    maand = str(now.month)
    try:
        r = requests.get(f"https://www.nd.nl/archive/{yyyy}/{maand}", headers=HEADERS, timeout=10)
        match = re.search(r'https://storage\.pubble\.cloud/9ed0159c/paper/[^/]+/files/thumb/1\.jpg', r.text)
        if match:
            return match.group(0).replace("/thumb/", "/large/").split("?")[0]
        print("ND: geen URL gevonden in archief")
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
    return f"https://www.digibron.nl/images/generated/reformatorisch-dagblad/katern-nieuws/{d.year}/{d.month:02d}/{d.day:02d}/1-large.jpg"

def get_telegraaf_url():
    api = "https://mhu-tlg-production-backend-api.twipecloud.net/Data/DataService.svc/getcontentpackagelist/TWPMHUTLG/0/30"
    try:
        r = requests.get(api, headers=HEADERS, timeout=10)
        data = r.json()
        editie = data[0]
        package_id = editie["ContentPackageId"]
        thumbnail_id = editie["ThumbnailId"]
        return f"https://mhu-tlg-webreader-production.twipemobile.com/data/{package_id}/covers/Preview-MEDIUM-{thumbnail_id}.jpg"
    except Exception as e:
        print(f"Telegraaf fout: {e}")
        return None

def get_trouw_url():
    return "https://cdn-03.tapp.dpgmedia.cloud/packshot/tr/latest.png"

def get_vk_url():
    return "https://cdn-03.tapp.dpgmedia.cloud/packshot/vk/latest.png"

# ─── Krantenlijst ────────────────────────────────────────────────────────────

KRANTEN = [
    {"naam": "Algemeen Dagblad",       "nieuw": get_ad_url},
    {"naam": "Nederlands Dagblad",     "nieuw": get_nd_url},
    {"naam": "NRC",                    "nieuw": get_nrc_url},
    {"naam": "Het Parool",             "nieuw": get_parool_url},
    {"naam": "Reformatorisch Dagblad", "nieuw": get_rd_url},
    {"naam": "De Telegraaf",           "nieuw": get_telegraaf_url},
    {"naam": "Trouw",                  "nieuw": get_trouw_url},
    {"naam": "de Volkskrant",          "nieuw": get_vk_url},
]

# ─── Hulpfuncties app.js ─────────────────────────────────────────────────────

def maak_regel(quote, url):
    return f"voorpagina: {quote}{url}{quote}"

def vind_huidige_url(content, naam, quote):
    q = re.escape(quote)
    patroon = r'naam:\s*"' + re.sub(r'([\\.+*?\^$\{\}\[\]\|\(\)])', r'\\\1', naam) + r'".*?voorpagina:\s*' + q + r'([^' + q + r']+)' + q
    match = re.search(patroon, content, flags=re.DOTALL)
    if match:
        return match.group(1)
    return None

def vervang_url(content, naam, quote, huidig, nieuwe_url):
    oude_regel = maak_regel(quote, huidig)
    nieuwe_regel = maak_regel(quote, nieuwe_url)
    if oude_regel in content:
        content = content.replace(oude_regel, nieuwe_regel)
        print(f" ✓ Bijgewerkt in app.js: {naam}")
    else:
        print(f" ✗ Niet gevonden in app.js: {naam}")
    return content

APPJS_KRANTEN = [
    {"naam": "Algemeen Dagblad",       "quote": '"'},
    {"naam": "Nederlands Dagblad",     "quote": '"'},
    {"naam": "NRC",                    "quote": '"'},
    {"naam": "Het Parool",             "quote": '"'},
    {"naam": "Reformatorisch Dagblad", "quote": '"'},
    {"naam": "De Telegraaf",           "quote": '"'},
    {"naam": "Trouw",                  "quote": '"'},
    {"naam": "de Volkskrant",          "quote": '"'},
]

# ─── Afbeelding downloaden ───────────────────────────────────────────────────

def bestandsnaam(naam):
    return naam.lower().replace(" ", "-").replace("'", "")

def download_afbeelding(naam, url):
    pad = os.path.join(COVERS_MAP, f"{bestandsnaam(naam)}-{vandaag}.jpg")
    extra_headers = {}
    if "digibron.nl" in url:
        extra_headers["Referer"] = "https://www.digibron.nl/"
    try:
        r = requests.get(url, headers={**HEADERS, **extra_headers}, timeout=15)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            with open(pad, "wb") as f:
                f.write(r.content)
            print(f" ✓ Gedownload: {pad}")
            return pad
        else:
            print(f" ✗ Download mislukt ({r.status_code}): {naam}")
            return None
    except Exception as e:
        print(f" ✗ Download fout {naam}: {e}")
        return None

# ─── Oude bestanden opruimen ─────────────────────────────────────────────────

def ruim_oude_covers_op():
    grens = date.today() - timedelta(days=MAX_DAGEN)
    verwijderd = 0
    for bestand in os.listdir(COVERS_MAP):
        if not bestand.endswith(".jpg"):
            continue
        try:
            datum_str = bestand[-14:-4]  # laatste 10 tekens voor .jpg
            bestand_datum = date.fromisoformat(datum_str)
            if bestand_datum < grens:
                os.remove(os.path.join(COVERS_MAP, bestand))
                print(f" 🗑 Cover verwijderd: {bestand}")
                verwijderd += 1
        except Exception:
            continue
    if verwijderd == 0:
        print(" ✓ Geen oude covers om op te ruimen")

# ─── Uitvoeren ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Datum: {vandaag}")

    # Haal alle URLs op en download waar nodig
    live_urls = {}   # originele externe URLs
    nieuwe_urls = {} # uiteindelijke URLs voor archief en app.js

    for krant in KRANTEN:
        url = krant["nieuw"]()
        naam = krant["naam"]
        if not url:
            print(f" – Overgeslagen: {naam} (geen URL opgehaald)")
            continue

        live_urls[naam] = url

        if naam in DOWNLOAD_KRANTEN:
            lokaal_pad = download_afbeelding(naam, url)
            if lokaal_pad:
                nieuwe_urls[naam] = lokaal_pad
            else:
                print(f" ⚠ Fallback naar live URL: {naam}")
                nieuwe_urls[naam] = url
        else:
            nieuwe_urls[naam] = url
            print(f" ✓ Opgehaald: {naam}")

    # Sla op in archive.json (max 7 dagen bewaren)
    try:
        with open(ARCHIEF_BESTAND, "r", encoding="utf-8") as f:
            archief = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        archief = {}

    archief[vandaag] = nieuwe_urls

    gesorteerde_datums = sorted(archief.keys(), reverse=True)
    for oude_datum in gesorteerde_datums[MAX_DAGEN:]:
        del archief[oude_datum]
        print(f" 🗑 Verwijderd uit archief: {oude_datum}")

    with open(ARCHIEF_BESTAND, "w", encoding="utf-8") as f:
        json.dump(archief, f, ensure_ascii=False, indent=2)
    print(f"archive.json bijgewerkt ({len(archief)} dagen opgeslagen).")

    # Ruim oude cover-bestanden op
    ruim_oude_covers_op()

    # Bijwerken app.js
    with open("app.js", "r", encoding="utf-8") as f:
        appjs = f.read()

    for krant in APPJS_KRANTEN:
        naam = krant["naam"]
        if naam not in nieuwe_urls:
            continue
        quote = krant["quote"]

        huidig = vind_huidige_url(appjs, naam, quote)
        if huidig is None:
            print(f" ✗ Huidige URL niet gevonden in app.js: {naam}")
            continue

        # Gedownloade kranten krijgen het lokale pad in app.js
        appjs = vervang_url(appjs, naam, quote, huidig, nieuwe_urls[naam])

    with open("app.js", "w", encoding="utf-8") as f:
        f.write(appjs)

    print("app.js bijgewerkt.")
    print("Klaar!")
