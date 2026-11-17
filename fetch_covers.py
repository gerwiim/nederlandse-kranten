import requests
import re
import json
import os
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# GitHub Actions draait in UTC; gebruik Nederlandse tijd zodat de datum klopt.
now = datetime.now(ZoneInfo("Europe/Amsterdam"))
vandaag_datum = now.date()
yyyy = now.strftime("%Y")
mm = now.strftime("%m")
dd = now.strftime("%d")
vandaag = vandaag_datum.isoformat()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "nl-NL,nl;q=0.9,en;q=0.8",
}

ARCHIEF_BESTAND = "archive.json"
COVERS_MAP = "covers"
MAX_DAGEN = 7

# Kranten waarvan we de afbeelding zelf opslaan (externe URL is niet datumspecifiek
# of blokkeert direct linken vanaf een andere website).
DOWNLOAD_KRANTEN = {"Algemeen Dagblad", "Het Parool", "Trouw", "de Volkskrant", "Reformatorisch Dagblad"}

os.makedirs(COVERS_MAP, exist_ok=True)

# ─── URL-functies ────────────────────────────────────────────────────────────

def get_ad_url():
    return "https://cdn-03.tapp.dpgmedia.cloud/packshot/ad/ad/latest.png"

ND_PATROON = re.compile(
    r'https:(?://|\\/\\/)storage\.pubble\.cloud(?:/|\\/)9ed0159c(?:/|\\/)paper(?:/|\\/)([0-9a-zA-Z]+)(?:/|\\/)files'
)

def get_nd_url():
    # Probeer meerdere pagina's: de archiefpagina is eerder van opbouw veranderd.
    kandidaten = [
        f"https://www.nd.nl/archive/{yyyy}/{now.month}",
        f"https://www.nd.nl/archive/{yyyy}/{mm}",
        "https://www.nd.nl/krant",
        "https://www.nd.nl/digitale-krant",
        "https://www.nd.nl/",
    ]
    for pagina in kandidaten:
        try:
            r = requests.get(pagina, headers=HEADERS, timeout=10)
        except Exception as e:
            print(f"ND: fout bij {pagina}: {e}")
            continue
        match = ND_PATROON.search(r.text)
        print(f"ND: {pagina} -> HTTP {r.status_code}, {len(r.text)} tekens, "
              f"{'gevonden' if match else 'geen pubble-link'}")
        if match:
            return f"https://storage.pubble.cloud/9ed0159c/paper/{match.group(1)}/files/large/1.jpg"
    print("ND: geen URL gevonden — controleer de opbouw van nd.nl")
    return None

def get_nrc_url():
    api = f"https://www.nrc.nl/de/data/NH/{yyyy}/{mm}/{dd}/"
    try:
        r = requests.get(api, headers=HEADERS, timeout=10)
        data = r.json()
        return data["pages"][0]["fullscreen_url_orig"]
    except Exception as e:
        print(f"NRC fout (op zondag verschijnt geen NRC): {e}")
        return None

def get_parool_url():
    return "https://cdn-03.tapp.dpgmedia.cloud/packshot/hp/latest.png"

def get_rd_url():
    d = vandaag_datum
    if d.weekday() == 6:  # zondag: geen RD
        return None
    return f"https://www.digibron.nl/images/generated/reformatorisch-dagblad/katern-nieuws/{d.year}/{d.month:02d}/{d.day:02d}/1-large.jpg"

def get_rd_reserve_url():
    # Lagere resolutie, maar zonder de beveiligingscontrole van digibron.
    d = vandaag_datum
    return f"https://cdn.erdee.nl/epaper/_fpage/RDB/{d.year}/RDB_RDB_{d:%Y%m%d}.jpg"

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

# ─── Afbeelding downloaden ───────────────────────────────────────────────────

def bestandsnaam(naam):
    return naam.lower().replace(" ", "-").replace("'", "")

def is_afbeelding(inhoud):
    return (inhoud.startswith(b"\xff\xd8\xff")        # JPEG
            or inhoud.startswith(b"\x89PNG")          # PNG
            or inhoud[:4] == b"RIFF" and inhoud[8:12] == b"WEBP"
            or inhoud[4:8] == b"ftyp")                # AVIF/HEIF

def download_afbeelding(naam, url):
    pad = os.path.join(COVERS_MAP, f"{bestandsnaam(naam)}-{vandaag}.jpg")
    pogingen = [{}]
    if "digibron.nl" in url:
        pogingen = [{"Referer": "https://www.digibron.nl/"}]
    elif "erdee.nl" in url:
        pogingen = [{"Referer": "https://www.rd.nl/"}, {}]
    for extra in pogingen:
        try:
            r = requests.get(url, headers={**HEADERS, "Accept": "image/jpeg,image/png,image/*;q=0.8,*/*;q=0.5", **extra}, timeout=15)
        except Exception as e:
            print(f" ✗ Download fout {naam}: {e}")
            continue
        type_ = r.headers.get("Content-Type", "")
        # Kijk naar de bytes zelf: sommige servers geven een verkeerd Content-Type mee.
        if r.status_code == 200 and is_afbeelding(r.content):
            with open(pad, "wb") as f:
                f.write(r.content)
            print(f" ✓ Gedownload: {pad} ({len(r.content)} bytes, {type_})")
            return pad
        print(f" ✗ Download mislukt {naam}: HTTP {r.status_code}, Content-Type '{type_}', "
              f"Referer {extra.get('Referer', '-')}, begin: {r.content[:60]!r}")
    return None

# ─── Oude bestanden opruimen ─────────────────────────────────────────────────

def ruim_oude_covers_op(bewaarde_datums):
    verwijderd = 0
    for bestand in os.listdir(COVERS_MAP):
        if not bestand.endswith(".jpg"):
            continue
        datum_str = bestand[-14:-4]  # laatste 10 tekens voor .jpg
        if datum_str not in bewaarde_datums:
            os.remove(os.path.join(COVERS_MAP, bestand))
            print(f" 🗑 Cover verwijderd: {bestand}")
            verwijderd += 1
    if verwijderd == 0:
        print(" ✓ Geen oude covers om op te ruimen")

# ─── Uitvoeren ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Datum: {vandaag} ({now:%H:%M} Nederlandse tijd)")

    nieuwe_urls = {}

    for krant in KRANTEN:
        naam = krant["naam"]
        url = krant["nieuw"]()
        if not url:
            print(f" – Overgeslagen: {naam} (geen URL opgehaald)")
            continue

        if naam in DOWNLOAD_KRANTEN:
            lokaal_pad = download_afbeelding(naam, url)
            if not lokaal_pad and naam == "Reformatorisch Dagblad":
                print(" ↪ Reformatorisch Dagblad: probeer reservebron (erdee.nl)")
                lokaal_pad = download_afbeelding(naam, get_rd_reserve_url())
            if lokaal_pad:
                nieuwe_urls[naam] = lokaal_pad
            else:
                print(f" ⚠ Fallback naar live URL: {naam}")
                nieuwe_urls[naam] = url
        else:
            nieuwe_urls[naam] = url
            print(f" ✓ Opgehaald: {naam}")

    try:
        with open(ARCHIEF_BESTAND, "r", encoding="utf-8") as f:
            archief = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        archief = {}

    # Samenvoegen: als een krant bij de tweede run van de dag mislukt,
    # blijft het resultaat van de eerste run staan. Een lokaal bestand wordt
    # niet overschreven door een (mogelijk niet werkende) externe fallback-URL.
    dag = archief.get(vandaag, {})
    for naam, url in nieuwe_urls.items():
        oud = dag.get(naam, "")
        if oud.startswith(COVERS_MAP + "/") and not url.startswith(COVERS_MAP + "/"):
            continue
        dag[naam] = url
    if dag:
        archief[vandaag] = dag

    gesorteerde_datums = sorted(archief.keys(), reverse=True)
    for oude_datum in gesorteerde_datums[MAX_DAGEN:]:
        del archief[oude_datum]
        print(f" 🗑 Verwijderd uit archief: {oude_datum}")

    with open(ARCHIEF_BESTAND, "w", encoding="utf-8") as f:
        json.dump(archief, f, ensure_ascii=False, indent=2)
    print(f"archive.json bijgewerkt ({len(archief)} dagen opgeslagen).")

    ruim_oude_covers_op(set(archief.keys()))

    print("Klaar!")
