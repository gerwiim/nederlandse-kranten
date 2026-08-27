import requests
import re
import os
import time
from datetime import datetime

now = datetime.now()
yyyy = now.strftime("%Y")
mm   = now.strftime("%m")
dd   = now.strftime("%d")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN")

# ─── AI Upscaling via Replicate (Real-ESRGAN) ────────────────────────────────

def upscale(image_url, label=""):
    if not REPLICATE_TOKEN:
        print(f"  Geen Replicate token gevonden, upscaling overgeslagen voor {label}")
        return image_url
    try:
        print(f"  Upscaling {label}...")
        r = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={
                "Authorization": f"Token {REPLICATE_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "version": "f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa",
                "input": {
                    "image": image_url,
                    "scale": 2,
                    "face_enhance": False,
                }
            },
            timeout=30,
        )
        response_data = r.json()
        print(f"  Replicate response: {response_data}")

        if "id" not in response_data:
            print(f"  Geen 'id' in response, upscaling overgeslagen voor {label}")
            return image_url

        prediction_id = response_data["id"]
        print(f"  Job gestart: {prediction_id}")

        # Wacht op resultaat (max 120 seconden)
        for _ in range(40):
            time.sleep(3)
            poll = requests.get(
                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                headers={"Authorization": f"Token {REPLICATE_TOKEN}"},
                timeout=15,
            )
            result = poll.json()
            status = result.get("status")
            if status == "succeeded":
                upscaled_url = result["output"]
                print(f"  ✓ Upscaling klaar: {upscaled_url}")
                return upscaled_url
            elif status == "failed":
                print(f"  ✗ Upscaling mislukt: {result.get('error')}")
                return image_url
            else:
                print(f"  ... status: {status}")

        print(f"  ✗ Timeout bij upscaling van {label}")
        return image_url

    except Exception as e:
        print(f"  Upscaling fout ({label}): {e}")
        return image_url


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
        print(f"Telegraaf gevonden: {pub_date} (package {package_id})")
        return upscale(url, "Telegraaf")
    except Exception as e:
        print(f"Telegraaf fout: {e}")
        return None


# ─── NRC ─────────────────────────────────────────────────────────────────────

def get_nrc_url():
    api = f"https://www.nrc.nl/de/data/NH/{yyyy}/{mm}/{dd}/"
    try:
        r = requests.get(api, headers=HEADERS, timeout=10)
        print(f"NRC status: {r.status_code}")
        data = r.json()
        page = data["pages"][0]
        url = page["fullscreen_url_orig"]
        print(f"NRC URL gevonden: {url}")
        return upscale(url, "NRC")
    except Exception as e:
        print(f"NRC fout: {e}")
        return None


# ─── Reformatorisch Dagblad ───────────────────────────────────────────────────

def get_rd_url():
    from datetime import date
    d = date.today()
    if d.weekday() == 6:  # zondag
        d = date.fromordinal(d.toordinal() - 1)
    datum = d.strftime("%Y%m%d")
    url = f"https://cdn.erdee.nl/epaper/_fpage/RDB/{yyyy}/RDB_RDB_{datum}.jpg"
    print(f"RD URL: {url}")
    return upscale(url, "Reformatorisch Dagblad")


# ─── DPG Media kranten (Volkskrant, AD, Parool, Trouw) ───────────────────────

def get_dpg_url(code, naam):
    url = f"https://cdn-03.tapp.dpgmedia.cloud/packshot/{code}/latest.png"
    print(f"{naam} URL: {url}")
    return upscale(url, naam)


# ─── Nederlands Dagblad ───────────────────────────────────────────────────────

def get_nd_url():
    url = "https://storage.pubble.cloud/9ed0159c/paper/559d18b2/files/large/1.jpg"
    print(f"ND URL: {url}")
    return upscale(url, "Nederlands Dagblad")


# ─── app.js bijwerken ─────────────────────────────────────────────────────────

def vervang_voorpagina(content, oude_url, nieuwe_url, label):
    """Vervangt een specifieke URL in app.js, ongeacht aanhalingstekens of backticks."""
    escaped = re.escape(oude_url)
    new_content = re.sub(escaped, nieuwe_url, content)
    if new_content != content:
        print(f"  ✓ Bijgewerkt: {label}")
    else:
        print(f"  ✗ Geen match gevonden voor: {label} ({oude_url[:60]}...)")
    return new_content

def get_huidige_urls(content):
    """Leest de huidige voorpagina URLs uit app.js."""
    patroon = r'voorpagina:\s*["`]([^"`]+)["`]'
    return re.findall(patroon, content)

def update_appjs(url_map):
    with open("app.js", "r", encoding="utf-8") as f:
        content = f.read()

    print("Huidige URLs in app.js:")
    for url in get_huidige_urls(content):
        print(f"  {url}")

    for label, oude_url, nieuwe_url in url_map:
        if nieuwe_url and oude_url:
            content = vervang_voorpagina(content, oude_url, nieuwe_url, label)

    with open("app.js", "w", encoding="utf-8") as f:
        f.write(content)

    print("app.js bijgewerkt.")


# ─── Huidige URLs uitlezen uit app.js ────────────────────────────────────────

def lees_huidige_url(content, naam):
    """Zoekt de voorpagina URL voor een specifieke krant op naam."""
    patroon = rf'naam:\s*"{re.escape(naam)}".*?voorpagina:\s*["`]([^"`]+)["`]'
    match = re.search(patroon, content, re.DOTALL)
    if match:
        return match.group(1)
    return None


# ─── Uitvoeren ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Datum: {yyyy}-{mm}-{dd}")

    # Lees huidige URLs uit app.js
    with open("app.js", "r", encoding="utf-8") as f:
        appjs = f.read()

    huidige_telegraaf = lees_huidige_url(appjs, "De Telegraaf")
    huidige_nrc       = lees_huidige_url(appjs, "NRC")
    huidige_rd        = lees_huidige_url(appjs, "Reformatorisch Dagblad")
    huidige_vk        = lees_huidige_url(appjs, "de Volkskrant")
    huidige_ad        = lees_huidige_url(appjs, "Algemeen Dagblad")
    huidige_parool    = lees_huidige_url(appjs, "Het Parool")
    huidige_trouw     = lees_huidige_url(appjs, "Trouw")
    huidige_nd        = lees_huidige_url(appjs, "Nederlands Dagblad")

    print(f"Huidige Telegraaf URL: {huidige_telegraaf}")
    print(f"Huidige NRC URL: {huidige_nrc}")
    print(f"Huidige RD URL: {huidige_rd}")

    # Haal nieuwe URLs op en upscale
    telegraaf_url = get_telegraaf_url()
    nrc_url       = get_nrc_url()
    rd_url        = get_rd_url()
    vk_url        = get_dpg_url("vk", "Volkskrant")
    ad_url        = get_dpg_url("ad/ad", "Algemeen Dagblad")
    parool_url    = get_dpg_url("hp", "Het Parool")
    trouw_url     = get_dpg_url("tr", "Trouw")
    nd_url        = get_nd_url()

    url_map = [
        ("Telegraaf",            huidige_telegraaf, telegraaf_url),
        ("NRC",                  huidige_nrc,       nrc_url),
        ("Reformatorisch Dagblad", huidige_rd,      rd_url),
        ("Volkskrant",           huidige_vk,        vk_url),
        ("Algemeen Dagblad",     huidige_ad,        ad_url),
        ("Het Parool",           huidige_parool,    parool_url),
        ("Trouw",                huidige_trouw,     trouw_url),
        ("Nederlands Dagblad",   huidige_nd,        nd_url),
    ]

    update_appjs(url_map)
    print("Klaar!")
