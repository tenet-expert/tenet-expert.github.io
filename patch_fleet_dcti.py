#!/usr/bin/env python3
"""Fleet trade-in: deduct FLEET_TI (100 000) only when «Скидка от ДЦ за трейд-ин»
(kmUseDcTi / ofDcTi) is checked, not on the manufacturer trade-in (kmUseTi).
The DC checkbox is shown and effective on its own. Direct column logic for
kmUseTi (table trade-in / возмещение) is unchanged. Corporate-VIN BFS mode
(calcFleet) is not touched. Also trims the blank lines that patch_board.py
adds before BOARD_OCT on every build. Idempotent; all-or-nothing per file;
node --check guard.
"""
import os, re, shutil, subprocess, tempfile
from pathlib import Path

DONE = "/*fleet-dcti*/"
SUBS = [
    # calcKm: DC trade-in discount independent of manufacturer trade-in
    ('const useDcTi=useTi && kmVal("kmUseDcTi", false);',
     'const useDcTi=kmVal("kmUseDcTi", false);' + DONE),
    # fleet column + T7 «от 2 333» (uses tiMpt)
    ('const tiMpt=useTi?(typeof FLEET_TI==="number"?FLEET_TI:100000):0;',
     'const tiMpt=useDcTi?(typeof FLEET_TI==="number"?FLEET_TI:100000):0;'),
    ('rrc:mptRrc, trade:!!useTi}', 'rrc:mptRrc, trade:!!useDcTi}'),
    ('Старт 2 333 000${useTi?" − трейд-ин "+rub(tiMpt):""}',
     'Старт 2 333 000${useDcTi?" − трейд-ин "+rub(tiMpt):""}'),
    # TENET / TENET PLUS comparison (fleet part)
    ('const altTi=useTi?(typeof FLEET_TI==="number"?FLEET_TI:100000):0;',
     'const altTi=useDcTi?(typeof FLEET_TI==="number"?FLEET_TI:100000):0;'),
    ('<span>${useTi?"Флит + трейд-ин":"Флит"}${altSub?',
     '<span>${useDcTi?"Флит + трейд-ин":"Флит"}${altSub?'),
    # sidebar recommended cars (kmPrioRecRows)
    ('const tiFleet=useTi?(typeof FLEET_TI==="number"?FLEET_TI:50000):0;',
     'const tiFleet=d.useDcTi?(typeof FLEET_TI==="number"?FLEET_TI:50000):0;'),
    # calcKm UI: DC checkbox always visible
    ('${useTi?`<label class="check-row"><input id="kmUseDcTi"',
     '${true?`<label class="check-row"><input id="kmUseDcTi"'),
    ('${useTi&&useDcTi?`<label class="field" style="max-width:none"><span>Сумма скидки ДЦ за трейд-ин',
     '${useDcTi?`<label class="field" style="max-width:none"><span>Сумма скидки ДЦ за трейд-ин'),
    # КП (offer)
    ('const useDcTi=useTi && (S?!!S.useDcTi:offerOn("ofDcTi"));',
     'const useDcTi=(S?!!S.useDcTi:offerOn("ofDcTi"));'),
    ('useDcTi:useTi && on("kmUseDcTi"),', 'useDcTi:on("kmUseDcTi"),'),
    ('${d.useTi?`<label class="check-row"><input id="ofDcTi"',
     '${true?`<label class="check-row"><input id="ofDcTi"'),
    ('${d.useTi&&d.useDcTi?offerField("Скидка ДЦ за трейд-ин',
     '${d.useDcTi?offerField("Скидка ДЦ за трейд-ин'),
    ('      const ti=typeof FLEET_TI==="number"?FLEET_TI:100000;\n'
     '      const months=Math.max(1, Math.round(Number(d.months)||60));\n'
     '      const down=Math.max(0, Math.round(Number(d.down)||0));\n'
     '      const have=',
     '      const ti=d.useDcTi?(typeof FLEET_TI==="number"?FLEET_TI:100000):0;\n'
     '      const months=Math.max(1, Math.round(Number(d.months)||60));\n'
     '      const down=Math.max(0, Math.round(Number(d.down)||0));\n'
     '      const have='),
    ('"Цена по госпрограмме с учётом субсидии и трейд-ин "+rub(gov)+" ₽",',
     '"Цена по госпрограмме с учётом субсидии"+(ti?" и трейд-ин ":" ")+rub(gov)+" ₽",'),
]
BLANKS = re.compile(r"\n(?:[ \t]*\n){2,}(    const BOARD_OCT = )")


def js_ok(html):
    node = shutil.which("node")
    if not node:
        return True
    for k, m in enumerate(re.finditer(r"<script>(.*?)</script>", html, re.S)):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(m.group(1))
        r = subprocess.run([node, "--check", f.name], capture_output=True, text=True)
        os.unlink(f.name)
        if r.returncode:
            print("node --check failed for inline script", k, r.stderr[:500])
            return False
    return True


def patch(text):
    out = text
    if DONE not in out:
        for old, new in SUBS:
            if out.count(old) != 1:
                print("fleet-dcti: anchor count", out.count(old), "->", old[:70].replace("\n", " "))
                out = text
                break
            out = out.replace(old, new, 1)
    out = BLANKS.sub(r"\n\n\1", out)
    return out


def main():
    for p in (Path("index.html"), Path("_site/index.html")):
        if not p.exists() or p.stat().st_size < 100000:
            continue
        src = p.read_text(encoding="utf-8")
        out = patch(src)
        if out == src:
            print(p, "fleet-dcti: nothing to do")
            continue
        if not js_ok(out):
            print(p, "fleet-dcti: JS check failed -> not written")
            continue
        p.write_text(out, encoding="utf-8")
        print(p, "fleet-dcti: patched", "(dcti)" if DONE in out and DONE not in src else "(blank lines only)")


if __name__ == "__main__":
    main()
