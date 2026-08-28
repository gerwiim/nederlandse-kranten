with open("app.js", "r", encoding="utf-8") as f:
    appjs = f.read()

oud = 'voorpagina: "https://cdn-03.tapp.dpgmedia.cloud/packshot/ad/ad/latest.png"'
nieuw = 'voorpagina: "https://TEST.png"'

if oud in appjs:
    print("Gevonden!")
    appjs = appjs.replace(oud, nieuw)
    print("Vervangen.")
else:
    print("Niet gevonden.")
