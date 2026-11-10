#!/usr/bin/env python3
"""Final force: put color name on every empty st-swatch."""
from pathlib import Path

p = Path("_site/index.html")
if not p.exists():
    p = Path("index.html")
html = p.read_text(encoding="utf-8")
old = '<div class="st-swatch" aria-hidden="true"></div>'
new = '<div class="st-swatch">${escape(r.color||"")}</div>'
if old in html:
    html = html.replace(old, new)
    p.write_text(html, encoding="utf-8")
    print("color name forced")
else:
    print("swatch string not found")
