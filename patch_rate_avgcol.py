#!/usr/bin/env python3
from pathlib import Path

BOARD_OLD = '<div class="rate-board">${Object.values(MODELS).filter(x=>x.id!=="t7l"&&x.id!=="t4").map(modelCol).join("")}</div>'
BOARD_NEW = '<div class="rate-board">${Object.values(MODELS).filter(x=>x.id!=="t7l"&&x.id!=="t4").map(modelCol).join("")}${avgCol()}</div>'
PIN_MARK = "      const pinNeeded=hasExam1()"

RET_OLD = '        return `<div class="rate-col rate-col-avg"><div class="eyebrow">отдел</div><h3>Среднее</h3><div class="rate-head"><span>состав</span><span>ср.</span></div>${taken.map(row).join("")}${wait.map(row).join("")}</div>`;'
RET_NEW = (
    "        const poolN=rows.reduce((s,p)=>s+(p.n||0),0);\n"
    "        const poolS=rows.reduce((s,p)=>s+(p.sum!=null?p.sum:((p.avg||0)*(p.n||0))),0);\n"
    "        const dept=poolN?Math.round(poolS/poolN):null;\n"
    "        const deptCls=dept==null?\"\":(dept>=(typeof EXPERT===\"number\"?EXPERT:90)?\" ok\":dept<(typeof PASS===\"number\"?PASS:70)?\" low\":\"\");\n"
    "        const deptRow=dept==null?\"\":`<div class=\"rate-avg\"><div><b>Средний по отделу</b></div><span class=\"pct${deptCls}\">${dept}%</span></div>`;\n"
    "        return `<div class=\"rate-col rate-col-avg\"><div class=\"eyebrow\">отдел</div><h3>Среднее</h3><div class=\"rate-head\"><span>состав</span><span>ср.</span></div>${taken.map(row).join(\"\")}${wait.map(row).join(\"\")}${deptRow}</div>`;"
)

ROW_OLD = "          const avg=vals.length?Math.round(vals.reduce((s,v)=>s+v,0)/vals.length):null;\n          return {key,name,avg,n:vals.length};"
ROW_NEW = "          const sum=vals.reduce((s,v)=>s+v,0);\n          const avg=vals.length?Math.round(sum/vals.length):null;\n          return {key,name,avg,n:vals.length,sum};"

CSS_BOARD_OLD = ".rate-board{display:flex;gap:10px;overflow-x:auto;margin-top:16px;padding-bottom:8px;-webkit-overflow-scrolling:touch;}"
CSS_BOARD_NEW = ".rate-board{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;margin-top:12px;padding-bottom:0;}"
CSS_COL_OLD = ".rate-col{flex:1 0 196px;min-width:196px;border:1px solid var(--border);background:var(--surface);border-radius:var(--radius);padding:12px 12px 10px;box-shadow:var(--shadow);}"
CSS_COL_NEW = ".rate-col{min-width:0;border:1px solid var(--border);background:var(--surface);border-radius:var(--radius);padding:10px 8px 8px;box-shadow:var(--shadow);}.rate-col h3{font-size:15px;margin:0 0 8px;}.rate-col-avg .rate-head,.rate-col-avg .rate-person,.rate-col-avg .rate-avg{grid-template-columns:minmax(0,1fr) 40px;}.rate-person b{font-size:13px;}"

def patch(text):
    if BOARD_OLD in text and "${avgCol()}" not in text:
        text = text.replace(BOARD_OLD, BOARD_NEW, 1)
        print("board + avgCol")
    if ROW_OLD in text:
        text = text.replace(ROW_OLD, ROW_NEW, 1)
        print("row keep sum")
    if RET_OLD in text:
        text = text.replace(RET_OLD, RET_NEW, 1)
        print("dept avg in 6th col")
    if CSS_BOARD_OLD in text:
        text = text.replace(CSS_BOARD_OLD, CSS_BOARD_NEW, 1)
        print("board css 6col")
    if CSS_COL_OLD in text:
        text = text.replace(CSS_COL_OLD, CSS_COL_NEW, 1)
        print("col css compact")
    elif "rate-col-avg .rate-avg" not in text and ".rate-col-avg .rate-head,.rate-col-avg .rate-person{grid-template-columns:minmax(0,1fr) 40px;}" in text:
        text = text.replace(
            ".rate-col-avg .rate-head,.rate-col-avg .rate-person{grid-template-columns:minmax(0,1fr) 40px;}",
            ".rate-col-avg .rate-head,.rate-col-avg .rate-person,.rate-col-avg .rate-avg{grid-template-columns:minmax(0,1fr) 40px;}",
            1,
        )
        print("avg row 2col in 6th")
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
