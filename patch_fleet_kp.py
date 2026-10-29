#!/usr/bin/env python3
"""Флит-КП: вкладка «КП Флит», флит-рисовальщик PDF, группа «Технологии и мультимедиа» для T4L.
Встраивает fleet-kp.js инлайном перед </body> (идемпотентно, между маркерами)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
START, END = "<!--FLEET-KP-->", "<!--/FLEET-KP-->"

def main():
    js = (ROOT / "fleet-kp.js").read_text(encoding="utf-8").replace("</script", "<\\/script")
    block = f"{START}<script>\n{js}\n</script>{END}"
    for rel in ("_site/index.html", "index.html"):
        p = ROOT / rel
        if not p.exists():
            continue
        html = p.read_text(encoding="utf-8")
        html = re.sub(re.escape(START) + r".*?" + re.escape(END), "", html, flags=re.S)
        i = html.rfind("</body>")
        if i < 0:
            print("patch_fleet_kp: no </body> in", rel); continue
        html = html[:i] + block + "\n" + html[i:]
        p.write_text(html, encoding="utf-8")
        print("patch_fleet_kp: patched", rel)

if __name__ == "__main__":
    main()
