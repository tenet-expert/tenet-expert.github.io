#!/usr/bin/env python3
"""Put MPT payment next to regular credit; PV for MPT is minus 200k."""
from pathlib import Path
import re

CSS = """
.pay-split{display:grid;grid-template-columns:1fr;gap:10px;margin-top:12px}
@media (min-width:720px){.pay-split{grid-template-columns:1fr 1fr;align-items:start}}
.pay-col{border:1px solid #eadfcf;border-radius:14px;padding:10px 12px;background:#fff}
.pay-col.mpt{background:#f3eee4;border-style:dashed;border-color:#d9cbb6}
.pay-col .eyebrow{margin:0 0 6px}
.pay-col .bank-row{margin-top:8px}
.mpt-break{margin-top:12px;padding-top:10px;border-top:1px dashed #d9cbb6}
.mpt-break div{display:flex;justify-content:space-between;gap:10px;align-items:baseline;padding:3px 0;font-size:13px}
.mpt-break span{color:var(--muted,#6d5a3e)}
.mpt-break b{font-variant-numeric:tabular-nums;font-weight:700;text-align:right}
.mpt-break small{display:block;color:var(--muted,#6d5a3e);margin-top:6px}
"""


def load_calc():
    p = Path("terms-calc-ui-b.js")
    if not p.exists():
        return ""
    t = p.read_text(encoding="utf-8")
    a = t.find("    function calcKm(){")
    b = t.find("    function calc(){")
    if a >= 0 and b > a:
        return t[a:b]
    return ""


def inject_css(html: str) -> str:
    extra = ""
    if ".pay-split{" not in html:
        extra += CSS
    elif ".mpt-break{" not in html:
        extra += """
.mpt-break{margin-top:12px;padding-top:10px;border-top:1px dashed #d9cbb6}
.mpt-break div{display:flex;justify-content:space-between;gap:10px;align-items:baseline;padding:3px 0;font-size:13px}
.mpt-break span{color:var(--muted,#6d5a3e)}
.mpt-break b{font-variant-numeric:tabular-nums;font-weight:700;text-align:right}
.mpt-break small{display:block;color:var(--muted,#6d5a3e);margin-top:6px}
"""
    if extra and "</style>" in html:
        return html.replace("</style>", extra + "\n</style>", 1)
    return html


def fix_calc(html: str, calc: str) -> str:
    if not calc or "function calcKm(){" not in html:
        print("calcKm missing")
        return html
    html, n = re.subn(
        r"    function calcKm\(\)\{[\s\S]*?\n    function calc\(",
        lambda _m: calc + "    function calc(",
        html,
        count=1,
    )
    print("replaced calcKm", n)
    return html


def main():
    calc = load_calc()
    print("calc snippet", len(calc), "split", "pay-split" in calc, "MPT_CUT", "MPT_CUT" in calc)
    for p in (Path("index.html"), Path("_site/index.html"), Path("TENET_T4L_netlify/index.html")):
        if not p.exists() or p.stat().st_size < 10000:
            print("skip", p)
            continue
        html = p.read_text(encoding="utf-8")
        html = fix_calc(html, calc)
        html = inject_css(html)
        p.write_text(html, encoding="utf-8")
        print("patched", p, p.stat().st_size, "split", "pay-split" in html)


if __name__ == "__main__":
    main()
