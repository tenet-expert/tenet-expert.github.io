#!/usr/bin/env python3
"""Третья вкладка «Должники» в разделе «Тюнинг» из Drive «Долг по доп. об.»
(папка «Тюнинг и резина», id 1L9gmJDIAeiYMBhr2iD0U-qv-KOnZOy70dP8neEraQF4, Лист1).
Вызывается из patch_tune_rubber.py. Идемпотентно."""
import json
from pathlib import Path

# Drive 28.10.2026 18:24 Samara: все непустые строки Лист1 как в файле
DEBT_COLS = ["ФИО", "Сумма", "% за неделю", "% за месяц"]
DEBT_ROWS = [
    ["Спицын А", 30000, None, None],
]
MARK = "const TUNE_DEBT ="

def block():
    return ("    " + MARK + " {cols:" + json.dumps(DEBT_COLS, ensure_ascii=False)
            + ",rows:" + json.dumps(DEBT_ROWS, ensure_ascii=False) + "};\n"
            "    function tuneDebtHtml(){\n"
            "      const c=TUNE_DEBT.cols;\n"
            "      const head=\"<tr>\"+c.map(x=>\"<th>\"+escape(x)+\"</th>\").join(\"\")+\"</tr>\";\n"
            "      const body=TUNE_DEBT.rows.map(r=>\"<tr>\"+r.map((v,i)=>\"<td>\"+(i===0?escape(String(v==null?\"\":v)):(typeof v===\"number\"?(i===1?tuneMoney(v):escape(String(v))):\"—\"))+\"</td>\").join(\"\")+\"</tr>\").join(\"\");\n"
            "      return `<div class=\"card\"><p class=\"eyebrow\">Должники</p><h3 style=\"margin:4px 0 8px\">Долг по доп. оборудованию</h3><p class=\"tune-note\">Данные как в файле «Долг по доп. об.». Прочерк — в файле пусто.</p><div class=\"tune-scroll\"><table class=\"tune-table\">${head}${body}</table></div></div>`;\n"
            "    }\n")

PAIRS = [
    ('if(tuneTab!=="do" && tuneTab!=="chery") tuneTab="chery";',
     'if(tuneTab!=="do" && tuneTab!=="chery" && tuneTab!=="debt") tuneTab="chery";'),
    ('const tabs=[["do","Тюнинг"],["chery","Резина"]];',
     'const tabs=[["do","Тюнинг"],["chery","Резина"],["debt","Должники"]];'),
    ('const body=tuneTab==="do"?tuneDoHtml():tuneRubberHtml(tuneTab);',
     'const body=tuneTab==="do"?tuneDoHtml():tuneTab==="debt"?tuneDebtHtml():tuneRubberHtml(tuneTab);'),
]

def patch(path: Path) -> bool:
    if not path.exists():
        return False
    t = orig = path.read_text(encoding="utf-8")
    i = t.find(MARK)
    if i >= 0:  # replace existing block with current data
        s = t.rfind("\n", 0, i) + 1
        e = t.find("    function tune(){", i)
        t = t[:s] + block() + t[e:]
    else:
        anchor = "    function tune(){"
        if anchor in t:
            t = t.replace(anchor, block() + anchor, 1)
        else:
            print(path, "anchor not found")
    for old, new in PAIRS:
        if new in t: pass
        elif old in t: t = t.replace(old, new, 1)
        else: print(path, "not found:", old[:50])
    if t != orig:
        path.write_text(t, encoding="utf-8"); print(path, "debt tab patched"); return True
    return False

def main():
    for p in (Path("index.html"), Path("_site/index.html")):
        patch(p)

if __name__ == "__main__":
    main()
