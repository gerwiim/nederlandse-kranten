import requests
import re
import os
from datetime import datetime

now = datetime.now()
yyyy = now.strftime("%Y")
mm   = now.strftime("%m")
dd   = now.strftime("%d")

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
        print(f"Telegraaf gevonden: {pub_date} (package {package_id})")
        return url
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
        return url
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
    return url


# ─── DPG Media kranten (Volkskrant, AD, Parool, Trouw) ───────────────────────

def get_dpg_url(code, naam):
    url = f"https://cdn-03.tapp.dpgmedia.cloud/packshot/{code}/latest.png"
    print(f"{naam} URL: {url}")
    return url


# ─── Nederlands Dagblad ───────────────────────────────────────────────────────

def get_nd_url():
    url = "https://storage.pubble.cloud/9ed0159c/paper/559d18b2/files/large/1.jpg"
    print(f"ND URL: {url}")
    return url


# ─── app.js bijwerken ─────────────────────────────────────────────────────────

def vervang_voorpagina(content, oude_url, nieuwe_url, label):
    escaped = re.escape(oude_url)
    new_content = re.sub(escaped, nieuwe_url, content)
    if new_content != content:
        print(f"  ✓ Bijgewerkt: {label}")
    else:
        print(f"  ✗ Geen match gevonden voor: {label}")
    return new_content

def lees_huidige_url(content, naam):
    patroon = rf'naam:\s*"{re.escape(naam)}".*?voorpagina:\s*["`]([^"`]+)["`]'
    match = re.search(patroon, content, re.DOTALL)
    if match:
        return match.group(1)
    return None

def update_appjs(url_map):
    with open("app.js", "r", encoding="utf-8") as f:
        content = f.read()

    for label, oude_url, nieuwe_url in url_map:
        if nieuwe_url and oude_url:
            content = vervang_voorpagina(content, oude_url, nieuwe_url, label)

    with open("app.js", "w", encoding="utf-8") as f:
        f.write(content)

    print("app.js bijgewerkt.")


# ─── Uitvoeren ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Datum: {yyyy}-{mm}-{dd}")

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

    telegraaf_url = get_telegraaf_url()
    nrc_url       = get_nrc_url()
    rd_url        = get_rd_url()
    vk_url        = get_dpg_url("vk", "Volkskrant")
    ad_url        = get_dpg_url("ad/ad", "Algemeen Dagblad")
    parool_url    = get_dpg_url("hp", "Het Parool")
    trouw_url     = get_dpg_url("tr", "Trouw")
    nd_url        = get_nd_url()

    url_map = [
        ("Telegraaf",              huidige_telegraaf, telegraaf_url),
        ("NRC",                    huidige_nrc,       nrc_url),
        ("Reformatorisch Dagblad", huidige_rd,        rd_url),
        ("Volkskrant",             huidige_vk,        vk_url),
        ("Algemeen Dagblad",       huidige_ad,        ad_url),
        ("Het Parool",             huidige_parool,    parool_url),
        ("Trouw",                  huidige_trouw,     trouw_url),
        ("Nederlands Dagblad",     huidige_nd,        nd_url),
    ]

    update_appjs(url_map)
    print("Klaar!")
