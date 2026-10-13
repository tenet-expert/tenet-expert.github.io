#!/usr/bin/env python3
"""Keep TUNE_RUBBER tire texts in sync with Drive «Резина Чери.xlsx» (лист Chery)."""
from pathlib import Path

A = "&"  # entity prefix built at runtime so transport layers cannot decode it
ESC_GOOD = ('({"&":"' + A + 'amp;","<":"' + A + 'lt;",">":"' + A + 'gt;","\\"":"'
            + A + 'quot;","\'":"' + A + '#39;"}[m])')
ESC_BAD = '({"&":"&","<":"<",">":">","\\"":""","\'":"' + A + '#39;"}[m])'

# (old, new) pairs; each applied once, idempotent.
PAIRS = [
    (ESC_BAD, ESC_GOOD),
    ('["235/55 R19",15750,63000,"0 · под заказ"]',
     '["235/55 R19",15750,63000,"0 · под заказ 3 раб дня"]'),
    ('["Royal Black Royalstud II 235/50 R19 103T шип",15500,62000,"1"]',
     '["Royal Black Royalstud II 235/50 R19 103T, шип.",15500,62000,"1"]'),
    ('["Hankook 235/55R18 100T Winter I*cept X RW10 TL",15500,62000,"1"]',
     '["Автошина 235/55 R18 Tracmax 104T XL X-Privilo S500 TL (шип.)",12500,50000,"3"]'),
    # Drive 12.10.2026: T9 R20 Fortune в наличии 2
    ('["T9 R20",[["Fortune 245/50R20 105T Polaro Ice TL, 230 шип.",15500,62000,"1"]]]',
     '["T9 R20",[["Fortune 245/50R20 105T Polaro Ice TL, 230 шип.",15500,62000,"2"]]]'),
    # Drive 12.10.2026: Arrizo R17 + Hankook 225/45R18
    ('["Arrizo R17",[["Pirelli Formula 215/50R17 95T XL Ice TL, шип.",11100,44400,"1"]]]',
     '["Arrizo R17",[["Автошина Hankook 225/45R18 95T XL Winter i*Pike RS2 W429 TL (шип.)",18500,74000,"1"],["Pirelli Formula 215/50R17 95T XL Ice TL, шип.",11100,44400,"1"]]]'),
]

def patch(path: Path) -> bool:
    if not path.exists():
        return False
    t = path.read_text(encoding="utf-8")
    orig = t
    for old, new in PAIRS:
        if new in t:
            print(path, "already:", new[:50])
        elif old in t:
            t = t.replace(old, new, 1)
            print(path, "patched:", new[:50])
        else:
            print(path, "not found:", old[:50])
    if t != orig:
        path.write_text(t, encoding="utf-8")
        return True
    return False

def main():
    changed = False
    for p in (Path("index.html"), Path("_site/index.html")):
        changed = patch(p) or changed
    if not changed:
        print("no file changed")

if __name__ == "__main__":
    main()
