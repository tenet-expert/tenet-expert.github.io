#!/usr/bin/env python3
"""Force vertical stacked duty PDF + in-app preview with Назад (PWA-safe)."""
from pathlib import Path
import re

MARKER = "<!-- duty-vert-d4 -->"
OVERLAY_TAG = '<script src="duty-overlay.js?v=d4"></script>'

EXTRA_CSS = """
.cl-sec{margin:2px 0 8px}
.cl-sec-title{display:flex;align-items:center;gap:10px;margin:4px 2px 10px;font:800 12px/1 Inter,Arial,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#8a7d6e}
.cl-sec-title:before,.cl-sec-title:after{content:"";flex:1;height:1px;background:#eadfcf}
.cl-salon{background:#f3eee4;border:1px dashed #d9cbb6;border-radius:16px;padding:10px 10px 12px}
.cl-salon .cl-sec-title{margin-top:2px}
.cl-note-lab{display:block;margin-top:8px;font-size:10px;color:#7a7166}
.cl-note{width:100%;margin-top:4px;min-height:44px;border:1px solid #eadfcf;border-radius:10px;padding:8px 10px;font:500 12px/1.35 Inter,Arial,sans-serif;resize:vertical;background:#fff;box-sizing:border-box}
.cl-salon .cl-note{margin-top:8px;background:#fbf7f0}
"""

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


def load_js():
    js = Path("duty-fn.js")
    return js.read_text(encoding="utf-8") if js.exists() else ""


def load_pdf():
    t = load_js()
    a = t.find("    function dutyPdfClose(){")
    if a < 0:
        a = t.find("    function dutyPdf(src){")
    b = t.find("    function dutyRead(){")
    if a >= 0 and b > a:
        return t[a:b]
    return ""


def load_duty_ui():
    t = load_js()
    a = t.find("    function duty(){")
    b = t.find("    function gibddSplitFio(")
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
    if ".cl-sec-title{" not in html:
        needle = ".cl-chips label{display:inline-flex;"
        idx = html.find(needle)
        if idx >= 0:
            html = html[:idx] + EXTRA_CSS + html[idx:]
        elif "</style>" in html:
            html = html.replace("</style>", EXTRA_CSS + "\n</style>", 1)
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


def fix_duty_ui(html: str, ui: str) -> str:
    if not ui:
        print("no duty ui snippet")
        return html
    if "function duty(){" in html:
        html, n = re.subn(
            r"    function duty\(\)\{[\s\S]*?\n    function gibddSplitFio\(",
            lambda _m: ui + "    function gibddSplitFio(",
            html,
            count=1,
        )
        print("replaced duty ui", n)
    else:
        print("duty() not in html")
    return html


def main():
    pdf = load_pdf()
    ui = load_duty_ui()
    print("pdf snippet", len(pdf), "open", "dutyPdfOpen" in pdf, "notes", "carH=214" in pdf)
    print("ui snippet", len(ui), "sec", "cl-sec-title" in ui)
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
        html = fix_duty_ui(html, ui)
        html = fix_css(html)
        html = inject_overlay(html)
        p.write_text(html, encoding="utf-8")
        print(
            "patched",
            p,
            p.stat().st_size,
            "notes",
            "_note" in html and "cl-sec-title" in html,
            "overlay",
            "dutyPdfOpen" in html,
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
