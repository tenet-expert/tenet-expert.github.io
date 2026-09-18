#!/usr/bin/env python3
from pathlib import Path

def heal(text):
    n = 0
    pairs = [
        ("${vin?\"" + chr(10) + "VIN: \"+vin:\"\"}", '${vin?"\\nVIN: "+vin:""}'),
        ("${inn?\"" + chr(10) + "ИНН: \"+inn:\"\"}", '${inn?"\\nИНН: "+inn:""}'),
        ("${vin?'" + chr(10) + "VIN: '+vin:''}", "${vin?'\\nVIN: '+vin:''}"),
    ]
    # built at runtime so JSON transport cannot eat the newline
    broken_vin = '${vin?"' + chr(10) + 'VIN: "+vin:""}'
    good_vin = '${vin?"' + '\\n' + 'VIN: "+vin:""}'
    broken_inn = '${inn?"' + chr(10) + 'ИНН: "+inn:""}'
    good_inn = '${inn?"' + '\\n' + 'ИНН: "+inn:""}'
    for old, new in ((broken_vin, good_vin), (broken_inn, good_inn)):
        if old in text:
            text = text.replace(old, new)
            n += 1
    return text, n

def main():
    changed = 0
    for path in (Path("index.html"), Path("_site/index.html"), Path("TENET_T4L_netlify/index.html")):
        if not path.exists() or path.stat().st_size < 1000:
            continue
        src = path.read_text(encoding="utf-8")
        out, n = heal(src)
        if out != src:
            path.write_text(out, encoding="utf-8")
            print("healed", path, "fixes", n)
            changed += 1
        else:
            print(path, "clean")
    print("changed", changed)

if __name__ == "__main__":
    main()
