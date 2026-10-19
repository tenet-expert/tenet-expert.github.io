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
    # Drive 14.10.2026: шиномонтаж комплексный R16 6800, R17-R19 8000, R20 10600
    ('mount:[["R16",5300],["R17, R18, R19",6300],["R20",8600]]',
     'mount:[["R16",6800],["R17, R18, R19",8000],["R20",10600]]'),
    # Drive 16.10.2026: новые Ikon Tyres в T8 R19, T8 R18, T7 R18, T4L (группа «T4L / L6»)
    ('["T8 R19",[["Royal Black Royalstud II 235/50 R19 103T, шип.",15500,62000,"1"],["Fortune 235/50R19 103T Polaro Ice TL, шип.",15500,62000,"2"]]]',
     '["T8 R19",[["Royal Black Royalstud II 235/50 R19 103T, шип.",15500,62000,"1"],["Автошина Ikon Tyres 235/50 R19 103T XL Autograph Snow 3 SUV TL",21000,84000,"2"],["Fortune 235/50R19 103T Polaro Ice TL, шип.",15500,62000,"2"]]]'),
    ('["T8 R18",[["Pirelli Formula 235/55 R18 104T XL Ice TL, шип.",15500,62000,"1"],["Автошина 235/55 R18 Tracmax 104T XL X-Privilo S500 TL (шип.)",12500,50000,"3"]]]',
     '["T8 R18",[["Pirelli Formula 235/55 R18 104T XL Ice TL, шип.",15500,62000,"1"],["Автошина Ikon Tyres 235/55R18 104T XL Character Ice 7 SUV TL (шип.)",17500,70000,"2"],["Автошина 235/55 R18 Tracmax 104T XL X-Privilo S500 TL (шип.)",12500,50000,"3"]]]'),
    ('["T7 R18",[["Pirelli Formula 225/55 R18 102T XL Ice TL, шип.",14500,58000,"2"]',
     '["T7 R18",[["Автошина Ikon Tyres 225/55 R18 Ikon Character Ice 7 SUV 102T XL (шип.)",16000,64000,"3"],["Pirelli Formula 225/55 R18 102T XL Ice TL, шип.",14500,58000,"2"]'),
    ('["T4L",[["Fortune 225/60 R18 104T Polaro Ice TL, шип.",12000,48000,"2"],["Pirelli Formula 225/60 R18 104T XL Ice TL, шип.",15500,62000,"1"]]]',
     '["T4L / L6",[["Fortune 225/60 R18 104T Polaro Ice TL, шип.",12000,48000,"2"],["Pirelli Formula 225/60 R18 104T XL Ice TL, шип.",15500,62000,"1"],["Автошина 225/60 R18 Ikon 104T XL Character Ice 7 SUV TL /шипованная/",16000,64000,"3"]]]'),
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
