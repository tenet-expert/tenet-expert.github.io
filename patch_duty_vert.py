#!/usr/bin/env python3
"""Force vertical stacked duty PDF + in-app preview with Назад (PWA-safe)."""
from pathlib import Path
import re

MARKER = "<!-- duty-vert-d3 -->"
OVERLAY_TAG = '<script src="duty-overlay.js?v=d3"></script>'

CSS_REPL = [
    (
        ".cl-cars{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}",
        ".cl-cars{display:grid;grid-template-columns:1fr;gap:8px}",
    ),
    (
        "@media (max-width:1100px){.cl-cars{grid-template-columns:repeat(3,minmax(0,1fr))}}",
        "@media (min-width:900px){.cl-cars{grid-template-columns:1fr 1fr}}",
    ),
    (
        "@media (max-width:720px){.cl-cars{grid-template-columns:1fr 1fr}}",
        "@media (min-width:1280px){.cl-cars{grid-template-columns:repeat(3,minmax(0,1fr))}}",
    ),
    (
        ".cl-foot{display:grid;grid-template-columns:1fr 1fr;gap:8px}",
        ".cl-foot{display:grid;grid-template-columns:1fr;gap:8px}",
    ),
    (
        ".cl-cars{grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:4px}",
        ".cl-cars{grid-template-columns:1fr!important;gap:6px}",
    ),
]


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


def fix_css(html: str) -> str:
    for old, new in CSS_REPL:
        html = html.replace(old, new)
    html = re.sub(
        r"\.cl-cars\{display:grid;grid-template-columns:repeat\(5,[^}]+\}",
        ".cl-cars{display:grid;grid-template-columns:1fr;gap:8px}",
        html,
        count=1,
    )
    return html


def inject_overlay(html: str) -> str:
    if "duty-overlay.js" not in html:
        if "</body>" in html:
            html = html.replace("</body>", OVERLAY_TAG + "\n</body>", 1)
        else:
            html += "\n" + OVERLAY_TAG + "\n"
    if MARKER not in html:
        html = html.replace("<head>", "<head>\n" + MARKER, 1)
    return html


def fix_pdf(html: str, pdf: str) -> str:
    if not pdf:
        print("no pdf snippet")
        return html
    if "function dutyPdfClose(){" in html:
        html, n = re.subn(
            r"    function dutyPdfClose\(\)\{[\s\S]*?\n    function dutyRead\(",
            lambda _m: pdf + "    function dutyRead(",
            html,
            count=1,
        )
        print("replaced close+pdf", n)
    elif "function dutyPdf(src){" in html:
        html, n = re.subn(
            r"    function dutyPdf\(src\)\{[\s\S]*?\n    function dutyRead\(",
            lambda _m: pdf + "    function dutyRead(",
            html,
            count=1,
        )
        print("replaced pdf", n)
    else:
        print("dutyPdf not in html")
    return html


def main():
    pdf = load_pdf()
    print("pdf snippet", len(pdf), "open", "dutyPdfOpen" in pdf)
    targets = [
        Path("index.html"),
        Path("_site/index.html"),
        Path("TENET_T4L_netlify/index.html"),
    ]
    for p in targets:
        if not p.exists() or p.stat().st_size < 10000:
            print("skip", p)
            continue
        html = p.read_text(encoding="utf-8")
        html = fix_pdf(html, pdf)
        html = fix_css(html)
        html = inject_overlay(html)
        p.write_text(html, encoding="utf-8")
        print(
            "patched",
            p,
            p.stat().st_size,
            "vertical",
            "const carH=198" in html,
            "overlay",
            "dutyPdfOpen" in html,
            "no5col",
            ".cl-cars{display:grid;grid-template-columns:repeat(5" not in html,
        )
    site = Path("_site")
    site.mkdir(exist_ok=True)
    root = Path("index.html")
    dest = site / "index.html"
    if root.exists() and "dutyPdfOpen" in root.read_text(encoding="utf-8"):
        dest.write_text(root.read_text(encoding="utf-8"), encoding="utf-8")
        print("copied root index -> _site", dest.stat().st_size)
    overlay = Path("duty-overlay.js")
    if overlay.exists():
        (site / "duty-overlay.js").write_text(overlay.read_text(encoding="utf-8"), encoding="utf-8")
        print("copied overlay js")


if __name__ == "__main__":
    main()
