#!/usr/bin/env python3
"""Карточка «График сотрудников» в кабинет tenet-expert.github.io."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MARKER = "/* График сотрудников · октябрь 2026"

CARD_ANCHOR = '["calc","%","Калькулятор","Платёж и калькулятор КМ от 10.09"]'
CARD_LINE = '["sched","Гр","График сотрудников","Октябрь: смены, дежурства, собрание"],\n        '

EXTRA_OLD = 'boardrep:"Отчёт"}'
EXTRA_NEW = 'boardrep:"Отчёт",sched:"График"}'

MAP_OLD = "offer,tune,senior}"
MAP_NEW = "offer,tune,senior,sched}"


def patch(html: str, css: str, js: str) -> str:
    if "График сотрудников" not in html and CARD_ANCHOR in html:
        html = html.replace(CARD_ANCHOR, CARD_LINE + CARD_ANCHOR, 1)
    if 'sched:"График"' not in html and EXTRA_OLD in html:
        html = html.replace(EXTRA_OLD, EXTRA_NEW, 1)
    if "senior,sched}" not in html and MAP_OLD in html:
        html = html.replace(MAP_OLD, MAP_NEW, 1)
    if "hub/sched.jpg" not in html and "</style>" in html:
        html = html.replace("</style>", "\n" + css.strip() + "\n</style>", 1)
    if MARKER not in html:
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
    css = (ROOT / "sched.css").read_text(encoding="utf-8")
    js = (ROOT / "sched.js").read_text(encoding="utf-8")
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
        print("schedule patch: nothing to write")


if __name__ == "__main__":
    main()
