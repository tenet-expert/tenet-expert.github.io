#!/usr/bin/env python3
"""Флит-КП: вкладка «КП Флит», флит-рисовальщик PDF, группа «Технологии и мультимедиа» для T4L.
Встраивает fleet-kp.js инлайном перед </body> (идемпотентно, между маркерами)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
START, END = "<!--FLEET-KP-->", "<!--/FLEET-KP-->"

LEASE_SUBS = [
    # «КП Лизинг» убрана: её полностью заменил «КП Флит» (вкладка, карточка раздела, стили карточки, диспетчер).
    ('["lease","КП Лизинг"]', '["fleet","КП Флит"]'),
    ('["lease","Л","КП Лизинг","Компания, флит, аванс и PDF"]', '["fleet","Ф","КП Флит","С1/С2, безнал, субсидия, трейд-ин и PDF"]'),
    ('data-offer-tab="lease"', 'data-offer-tab="fleet"'),
    ('if(offerTab==="lease") return offerLease();', 'if(offerTab==="lease") offerTab="fleet";'),
]

def drop_lease(html):
    for a, b in LEASE_SUBS:
        if a not in html and b not in html:
            print("patch_fleet_kp: lease pattern not found:", a[:40])
        html = html.replace(a, b)
    return html

def main():
    off = ROOT / "offer-official.js"  # оснащение/ТТХ КП по официальным прайсам — до fleet-kp.js
    js = ((off.read_text(encoding="utf-8") + "\n") if off.exists() else "") + (ROOT / "fleet-kp.js").read_text(encoding="utf-8")
    js = js.replace("</script", "<\\/script")
    block = f"{START}<script>\n{js}\n</script>{END}"
    for rel in ("_site/index.html", "index.html"):
        p = ROOT / rel
        if not p.exists():
            continue
        html = p.read_text(encoding="utf-8")
        html = drop_lease(html)
        html = re.sub(re.escape(START) + r".*?" + re.escape(END), "", html, flags=re.S)
        i = html.rfind("</body>")
        if i < 0:
            print("patch_fleet_kp: no </body> in", rel); continue
        html = html[:i] + block + "\n" + html[i:]
        p.write_text(html, encoding="utf-8")
        print("patch_fleet_kp: patched", rel)

if __name__ == "__main__":
    main()
