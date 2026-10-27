#!/usr/bin/env python3
"""Раздел «График выдач» — только для сессии РОП."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MARKER = "/* График выдач"

LOGIN_OLD = """        const baked=await bakedPin(sn);
        if(pinEq(pinRaw, baked)){
          state.surname=sn; state.display=v.replace(/\\s+/g," "); state.authed=true; save();"""

LOGIN_NEW = """        if(pinEq(pinRaw, PIN)){
          state.surname=sn||"роп"; state.display=v.replace(/\\s+/g," "); state.authed=true; state.rop=true; save();
          view="hub"; state.section="hub"; render();
          return;
        }
        const baked=await bakedPin(sn);
        if(pinEq(pinRaw, baked)){
          state.surname=sn; state.display=v.replace(/\\s+/g," "); state.authed=true; state.rop=false; save();"""

CLOUD_OLD = """        state.surname=sn; state.display=v.replace(/\\s+/g," "); state.authed=true; save();
        if(userRun()){ resumeExam(userRun()); return; }
        view="hub"; state.section="hub"; render();
      };"""

CLOUD_NEW = """        state.surname=sn; state.display=v.replace(/\\s+/g," "); state.authed=true; state.rop=false; save();
        if(userRun()){ resumeExam(userRun()); return; }
        view="hub"; state.section="hub"; render();
      };"""

LOGOUT_OLD = 'state.surname=""; state.display=""; state.authed=false; save();'
LOGOUT_NEW = 'state.surname=""; state.display=""; state.authed=false; state.rop=false; save();'

SCHED_CARD = '        ["sched","Гр","График сотрудников","Октябрь: смены, дежурства, собрание"],'
SCHED_CARD_NEW = """        ...(typeof isRop==="function"&&isRop()?[["issue","В","График выдач","Слоты оформителей — в общий график"]]:[]),
        ["sched","Гр","График сотрудников","Октябрь: смены, дежурства, собрание"],"""


def patch(html: str, css: str, js: str) -> str:
    if "state.rop=true" not in html and LOGIN_OLD in html:
        html = html.replace(LOGIN_OLD, LOGIN_NEW, 1)
    if "state.rop=false; save();\n        if(userRun())" not in html and CLOUD_OLD in html:
        html = html.replace(CLOUD_OLD, CLOUD_NEW, 1)
    if "state.rop=false; save(); view=\"login\"" not in html and LOGOUT_OLD in html:
        html = html.replace(LOGOUT_OLD, LOGOUT_NEW, 1)
    if "sched,issue}" not in html and "senior,sched}" in html:
        html = html.replace("senior,sched}", "senior,sched,issue}", 1)
    elif "offer,sched,issue}" not in html and "offer,sched}" in html:
        html = html.replace("offer,sched}", "offer,sched,issue}", 1)
    elif ",issue}" not in html and "offer,tune,senior}" in html:
        html = html.replace("offer,tune,senior}", "offer,tune,senior,issue}", 1)
    if 'issue:"Выдачи"' not in html:
        if 'sched:"График"' in html:
            html = html.replace('sched:"График"', 'sched:"График",issue:"Выдачи"', 1)
        elif 'boardrep:"Отчёт"};' in html:
            html = html.replace('boardrep:"Отчёт"};', 'boardrep:"Отчёт",issue:"Выдачи"};', 1)
        html = html.replace(
            "if(extra[active]) items.push([active, extra[active]]);",
            'if(extra[active] && (active!=="issue" || (typeof isRop==="function" && isRop()))) items.push([active, extra[active]]);',
            1,
        )
    if 'data-go="issue"' not in html and SCHED_CARD in html:
        html = html.replace(SCHED_CARD, SCHED_CARD_NEW, 1)
    if ".issue-page" not in html and "</style>" in html:
        html = html.replace("</style>", "\n" + css + "\n</style>", 1)
    if "function isRop()" not in html:
        anchor = '<nav class="bot" id="navBot"></nav>\n  <script>'
        block = (
            '<nav class="bot" id="navBot"></nav>\n  <script>\n'
            + js.strip()
            + "\n  </script>\n  <script>"
        )
        if anchor in html:
            html = html.replace(anchor, block, 1)
        elif "</body>" in html:
            html = html.replace("</body>", "<script>\n" + js.strip() + "\n</script>\n</body>", 1)
    return html


def main():
    css = (ROOT / "issue.css").read_text(encoding="utf-8")
    js = (ROOT / "issue.js").read_text(encoding="utf-8")
    done = 0
    for p in (Path("_site/index.html"), Path("index.html")):
        if not p.exists() or p.stat().st_size < 50000:
            continue
        raw = p.read_text(encoding="utf-8")
        nxt = patch(raw, css, js)
        if nxt != raw:
            p.write_text(nxt, encoding="utf-8")
            print("patched", p, p.stat().st_size)
            done += 1
        else:
            print("unchanged", p)
    if not done:
        print("issue patch: nothing to write")


if __name__ == "__main__":
    main()
    # «Спец инвойс» по цене закупки LS: patch_issue.py — последний шаг сборки (после
    # patch_stock_src / patch_fleet_dcti), токен без scope workflow не может править pages.yml.
    try:
        import runpy
        from pathlib import Path as _P
        if _P("patch_spec_invoice.py").exists():
            runpy.run_path("patch_spec_invoice.py", run_name="__main__")
    except BaseException as e:  # never fail the Pages build because of the label
        print("spec-invoice: skipped:", e)
    # КМ — фиксы (A с ТИ / B без ТИ) и T7 Prime 2WD без кредитной скидки 50/30 (27.10.2026).
    try:
        import runpy
        from pathlib import Path as _P
        if _P("patch_km_fix.py").exists():
            runpy.run_path("patch_km_fix.py", run_name="__main__")
    except BaseException as e:  # never fail the Pages build because of this step
        print("km-fix: skipped:", e)
