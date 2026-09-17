#!/usr/bin/env python3
"""Vertical duty PDF + in-app preview with Back button."""
from pathlib import Path
import re

def load_pdf():
    js = Path("duty-fn.js")
    if js.exists():
        t = js.read_text(encoding="utf-8")
        a = t.find("    function dutyPdfClose(){")
        if a < 0:
            a = t.find("    function dutyPdf(src){")
        b = t.find("    function dutyRead(){")
        if a >= 0 and b > a:
            return t[a:b]
    return ""

def fix(html: str, pdf: str) -> str:
    if not pdf:
        print("no pdf snippet")
        return html
    if "function dutyPdfClose(){" in html:
        html, n = re.subn(
            r"    function dutyPdfClose\(\)\{[\s\S]*?\n    function dutyRead\(",
            lambda _m: pdf + "    function dutyRead(",
            html, count=1)
        print("replaced close+pdf", n)
    elif "function dutyPdf(src){" in html:
        html, n = re.subn(
            r"    function dutyPdf\(src\)\{[\s\S]*?\n    function dutyRead\(",
            lambda _m: pdf + "    function dutyRead(",
            html, count=1)
        print("replaced pdf", n)
    else:
        print("dutyPdf not in html")
    html = html.replace(
        ".cl-cars{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}",
        ".cl-cars{display:grid;grid-template-columns:1fr;gap:8px}",
    )
    html = html.replace(
        "@media (max-width:1100px){.cl-cars{grid-template-columns:repeat(3,minmax(0,1fr))}}",
        "@media (min-width:900px){.cl-cars{grid-template-columns:1fr 1fr}}",
    )
    html = html.replace(
        "@media (max-width:720px){.cl-cars{grid-template-columns:1fr 1fr}}",
        "@media (min-width:1280px){.cl-cars{grid-template-columns:repeat(3,minmax(0,1fr))}}",
    )
    html = html.replace(
        ".cl-foot{display:grid;grid-template-columns:1fr 1fr;gap:8px}",
        ".cl-foot{display:grid;grid-template-columns:1fr;gap:8px}",
    )
    html = html.replace(
        ".cl-cars{grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:4px}",
        ".cl-cars{grid-template-columns:1fr!important;gap:6px}",
    )
    return html

def main():
    pdf = load_pdf()
    print("pdf snippet", len(pdf), "open" , "dutyPdfOpen" in pdf)
    for p in (Path("index.html"), Path("_site/index.html"), Path("TENET_T4L_netlify/index.html")):
        if not p.exists() or p.stat().st_size < 10000:
            continue
        html = p.read_text(encoding="utf-8")
        out = fix(html, pdf)
        p.write_text(out, encoding="utf-8")
        print("patched", p, p.stat().st_size, "vertical", "const carH=198" in out, "overlay", "dutyPdfOpen" in out)

if __name__ == "__main__":
    main()
