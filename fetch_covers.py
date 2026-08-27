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
        # Start de upscale job
        r = requests.post(
            "https://api.replicate.com/v1/models/nightmareai/real-esrgan/predictions",
            headers={
                "Authorization": f"Token {REPLICATE_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "input": {
                    "image": image_url,
                    "scale": 2,
                    "face_enhance": False,
                }
            },
            timeout=30,
        )
        prediction = r.json()
        prediction_id = prediction["id"]
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

def get_nrc_hash():
    api = f"https://www.nrc.nl/de/data/NH/{yyyy}/{mm}/{dd}/"
    try:
        r = requests.get(api, headers=HEADERS, timeout=10)
        print(f"NRC status: {r.status_code}")
        data = r.json()
        page = data["pages"][0]
        url = page["fullscreen_url_orig"]
        match = re.search(r'101-full-([a-f0-9]+)\.jpg', url)
        if match:
            hash_waarde = match.group(1)
            print(f"NRC hash gevonden: {hash_waarde}")
            upscaled = upscale(url, "NRC")
            return hash_waarde, upscaled
        print(f"NRC: hash niet gevonden in URL: {url}")
        return None, None
    except Exception as e:
        print(f"NRC fout: {e}")
        return None, None


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

def update_appjs(updates):
    with open("app.js", "r", encoding="utf-8") as f:
        content = f.read()

    for zoek, vervang in updates:
        if vervang:
            new_content = re.sub(zoek, vervang, content)
            if new_content != content:
                content = new_content
                print(f"  Bijgewerkt: {zoek[:60]}...")
            else:
                print(f"  Geen match gevonden voor: {zoek[:60]}...")

    with open("app.js", "w", encoding="utf-8") as f:
        f.write(content)

    print("app.js bijgewerkt.")


# ─── Uitvoeren ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Datum: {yyyy}-{mm}-{dd}")

    telegraaf_url = get_telegraaf_url()
    nrc_hash, nrc_url = get_nrc_hash()
    rd_url        = get_rd_url()
    vk_url        = get_dpg_url("vk", "Volkskrant")
    ad_url        = get_dpg_url("ad/ad", "Algemeen Dagblad")
    parool_url    = get_dpg_url("hp", "Het Parool")
    trouw_url     = get_dpg_url("tr", "Trouw")
    nd_url        = get_nd_url()

    updates = [
        # Telegraaf
        (
            r'(naam: "De Telegraaf"[^}]*voorpagina: ")[^"]*(")',
            rf'\g<1>{telegraaf_url}\2' if telegraaf_url else None,
        ),
        # NRC (volledige URL vervangen)
        (
            r'(naam: "NRC"[^}]*voorpagina: ")[^"]*(")',
            rf'\g<1>{nrc_url}\2' if nrc_url else None,
        ),
        # RD
        (
            r'(naam: "Reformatorisch Dagblad"[^}]*voorpagina: ")[^"]*(")',
            rf'\g<1>{rd_url}\2' if rd_url else None,
        ),
        # Volkskrant
        (
            r'(naam: "de Volkskrant"[^}]*voorpagina: ")[^"]*(")',
            rf'\g<1>{vk_url}\2' if vk_url else None,
        ),
        # AD
        (
            r'(naam: "Algemeen Dagblad"[^}]*voorpagina: ")[^"]*(")',
            rf'\g<1>{ad_url}\2' if ad_url else None,
        ),
        # Parool
        (
            r'(naam: "Het Parool"[^}]*voorpagina: ")[^"]*(")',
            rf'\g<1>{parool_url}\2' if parool_url else None,
        ),
        # Trouw
        (
            r'(naam: "Trouw"[^}]*voorpagina: ")[^"]*(")',
            rf'\g<1>{trouw_url}\2' if trouw_url else None,
        ),
        # Nederlands Dagblad
        (
            r'(naam: "Nederlands Dagblad"[^}]*voorpagina: ")[^"]*(")',
            rf'\g<1>{nd_url}\2' if nd_url else None,
        ),
    ]

    update_appjs(updates)
    print("Klaar!")
