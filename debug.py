import re

with open("app.js", "r", encoding="utf-8") as f:
    appjs = f.read()

naam = "Algemeen Dagblad"
nieuwe_url = "https://TEST.png"

patroon = r'(naam:\s*"' + re.escape(naam) + r'"[^}]*?voorpagina:\s*")([^"]+)(")'
print("Patroon:", patroon)

match = re.search(patroon, appjs, flags=re.DOTALL)
if match:
    print("Match gevonden:", repr(match.group(0)))
else:
    print("Geen match")
