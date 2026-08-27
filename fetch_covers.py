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

def update_appjs(updates):
    with open("app.js", "r", encoding="utf-8") as f:
        content = f.read()

    for label, zoek, vervang in updates:
        if vervang:
            new_content = re.sub(zoek, vervang, content, flags=re.DOTALL)
            if new_content != content:
                content = new_content
                print(f"  ✓ Bijgewerkt: {label}")
            else:
                print(f"  ✗ Geen match gevonden voor: {label}")

    with open("app.js", "w", encoding="utf-8") as f:
        f.write(content)

    print("app.js bijgewerkt.")


# ─── Uitvoeren ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Datum: {yyyy}-{mm}-{dd}")

    telegraaf_url = get_telegraaf_url()
    nrc_url       = get_nrc_url()
    rd_url        = get_rd_url()
    vk_url        = get_dpg_url("vk", "Volkskrant")
    ad_url        = get_dpg_url("ad/ad", "Algemeen Dagblad")
    parool_url    = get_dpg_url("hp", "Het Parool")
    trouw_url     = get_dpg_url("tr", "Trouw")
    nd_url        = get_nd_url()

    # Regex matcht zowel "..." als `...` als voorpagina waarde
    def vervang_url(naam, nieuwe_url):
        if not nieuwe_url:
            return None
        return rf'\g<1>{nieuwe_url}\g<2>'

    updates = [
        (
            "Telegraaf",
            r'(naam: "De Telegraaf".*?voorpagina: ["`])[^"`]*(["`])',
            vervang_url("Telegraaf", telegraaf_url),
        ),
        (
            "NRC",
            r'(naam: "NRC".*?voorpagina: ["`])[^"`]*(["`])',
            vervang_url("NRC", nrc_url),
        ),
        (
            "Reformatorisch Dagblad",
            r'(naam: "Reformatorisch Dagblad".*?voorpagina: ["`])[^"`]*(["`])',
            vervang_url("Reformatorisch Dagblad", rd_url),
        ),
        (
            "Volkskrant",
            r'(naam: "de Volkskrant".*?voorpagina: ["`])[^"`]*(["`])',
            vervang_url("Volkskrant", vk_url),
        ),
        (
            "Algemeen Dagblad",
            r'(naam: "Algemeen Dagblad".*?voorpagina: ["`])[^"`]*(["`])',
            vervang_url("Algemeen Dagblad", ad_url),
        ),
        (
            "Het Parool",
            r'(naam: "Het Parool".*?voorpagina: ["`])[^"`]*(["`])',
            vervang_url("Het Parool", parool_url),
        ),
        (
            "Trouw",
            r'(naam: "Trouw".*?voorpagina: ["`])[^"`]*(["`])',
            vervang_url("Trouw", trouw_url),
        ),
        (
            "Nederlands Dagblad",
            r'(naam: "Nederlands Dagblad".*?voorpagina: ["`])[^"`]*(["`])',
            vervang_url("Nederlands Dagblad", nd_url),
        ),
    ]

    update_appjs(updates)
    print("Klaar!")
