import re

with open("app.js", "r") as f:
    appjs = f.read()

match = re.search(r'naam:\s*"NRC".{0,200}', appjs, flags=re.DOTALL)
print(repr(match.group(0)) if match else "NRC niet gevonden")
