#!/usr/bin/env python3
"""Keep TUNE_RUBBER tire texts in sync with Drive «Резина Чери.xlsx» (лист Chery)."""
from pathlib import Path

# (old, new) pairs; each applied once, idempotent.
PAIRS = [
    ('["235/55 R19",15750,63000,"0 · под заказ"]',
     '["235/55 R19",15750,63000,"0 · под заказ 3 раб дня"]'),
    ('["Royal Black Royalstud II 235/50 R19 103T шип",15500,62000,"1"]',
     '["Royal Black Royalstud II 235/50 R19 103T, шип.",15500,62000,"1"]'),
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
