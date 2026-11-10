#!/usr/bin/env python3
"""Force orange tone on stock cards."""
from pathlib import Path

p = Path("_site/index.html")
if not p.exists():
    p = Path("index.html")
html = p.read_text(encoding="utf-8")

# Inject orange into stockTone
old = 'if(c.includes("крас")) return "tone-red";'
new = '''if(c.includes("оранж")||c.includes("апельсин")) return "tone-orange";
      if(c.includes("крас")) return "tone-red";'''
if old in html and "tone-orange" not in html:
    html = html.replace(old, new, 1)
    print("stockTone patched")

# Inject CSS
css = '''.st-row.tone-orange:not(.is-reserved):not(.is-invoice){background:#fff6ef}
.st-row.tone-orange .st-swatch{background:#e07a2f;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.25)}'''
if "tone-orange .st-swatch" not in html:
    if ".st-row.tone-red .st-swatch" in html:
        html = html.replace(
            ".st-row.tone-red .st-swatch{background:#c23b3b}",
            ".st-row.tone-red .st-swatch{background:#c23b3b}" + css,
            1
        )
        print("css injected")
    else:
        html = html.replace("</style>", css + "</style>", 1)
        print("css appended")

p.write_text(html, encoding="utf-8")
