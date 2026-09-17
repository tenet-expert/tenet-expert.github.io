#!/usr/bin/env python3
from pathlib import Path

PAIR_OLD = "return {key, name:(a&&a.name)||(b&&b.name)||name, was:a?a.percent:null, now:b?b.percent:null};"
PAIR_NEW = 'return {key, name:(a&&a.name)||(b&&b.name)||name, was:(key==="лавров"&&modelId==="t4l")?77:(a?a.percent:null), now:(key==="лавров"&&modelId==="t4l")?(b?b.percent:(a&&Number(a.percent)!==77?a.percent:null)):(b?b.percent:null)};'

AVG_OLD = "        return `<div class=\"rate-col\">"
AVG_NEW = """        const firsts=staffRows.filter(p=>p.was!=null).map(p=>Number(p.was));
        const avg=firsts.length?Math.round(firsts.reduce((s,v)=>s+v,0)/firsts.length):null;
        const avgCls=avg==null?"":(avg>=(typeof EXPERT==="number"?EXPERT:90)?" ok":avg<(typeof PASS==="number"?PASS:70)?" low":"");
        const avgRow=avg==null?"":`<div class=\"rate-avg\"><div><b>Средний по отделу</b></div><span class=\"pct${avgCls}\">${avg}%</span><span class=\"pct\">—</span></div>`;
        return `<div class=\"rate-col\">"""

GUEST_OLD = '${guests.length?`<div class="rate-split">гости</div>${guests.map(p=>personRow(p,false)).join("")}`:""}'
GUEST_NEW = '${avgRow}${guests.length?`<div class="rate-split">гости</div>${guests.map(p=>personRow(p,false)).join("")}`:""}'

CSS_OLD = ".rate-split{margin:10px 0 4px;border:0;border-top:1px solid var(--fg);padding-top:8px;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:700;}"
CSS_NEW = CSS_OLD + ".rate-avg{display:grid;grid-template-columns:minmax(0,1fr) 44px 44px;gap:4px;align-items:center;margin:8px 0 2px;padding:8px 0;border-top:1px dashed var(--border);border-bottom:1px dashed var(--border);}.rate-avg b{font-size:12px;font-weight:700;color:var(--muted);}.rate-avg .pct{text-align:right;font-size:14px;font-weight:800;letter-spacing:-.03em;font-variant-numeric:tabular-nums;}"


def patch(text: str) -> str:
    if PAIR_OLD in text:
        text = text.replace(PAIR_OLD, PAIR_NEW, 1)
        print("pair lavrov t4l 77")
    if AVG_OLD in text and "Средний по отделу" not in text:
        text = text.replace(AVG_OLD, AVG_NEW, 1)
        print("avg calc")
    if GUEST_OLD in text and "${avgRow}${guests.length" not in text:
        text = text.replace(GUEST_OLD, GUEST_NEW, 1)
        print("avg row before guests")
    if CSS_OLD in text and ".rate-avg{" not in text:
        text = text.replace(CSS_OLD, CSS_NEW, 1)
        print("avg css")
    return text


def main():
    n = 0
    for path in (Path("_site/index.html"), Path("index.html"), Path("TENET_T4L_netlify/index.html")):
        if not path.exists() or path.stat().st_size < 1000:
            continue
        src = path.read_text(encoding="utf-8")
        out = patch(src)
        if out != src:
            path.write_text(out, encoding="utf-8")
            print("patched", path)
            n += 1
        else:
            print(path, "unchanged")
    print("changed", n)


if __name__ == "__main__":
    main()
