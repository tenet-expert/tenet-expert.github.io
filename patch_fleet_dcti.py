#!/usr/bin/env python3
"""Fleet trade-in: deduct FLEET_TI (100 000) only when «Скидка от ДЦ за трейд-ин»
(kmUseDcTi / ofDcTi) is checked, not on the manufacturer trade-in (kmUseTi).
The DC checkbox is shown and effective on its own. Direct column logic for
kmUseTi (table trade-in / возмещение) is unchanged. Corporate-VIN BFS mode
(calcFleet) is not touched. Also trims the blank lines that patch_board.py
adds before BOARD_OCT on every build. Idempotent; every substitution is
re-applied independently on each build (earlier steps may revert pieces);
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
DONE2 = "/*fleet-2389*/"
# Stage 2: special T7 Active 2WD fleet base 2 333 000 -> 2 389 000 (ФЛИТ 08.10),
# and КП fleet payment computed from the same price as «Цена по госпрограмме».
SUBS2 = [
    ('const FLEET_PIN = {"EDXFB32B7TE062327":2333000};',
     'const FLEET_PIN = {"EDXFB32B7TE062327":2389000};' + DONE2),
    ('fleetSubQuote(Math.max(0, 2333000-tiMpt),', 'fleetSubQuote(Math.max(0, 2389000-tiMpt),'),
    ('<p class="eyebrow">Флит · от 2 333</p>', '<p class="eyebrow">Флит · от 2 389</p>'),
    ('Старт 2 333 000${useDcTi?', 'Старт 2 389 000${useDcTi?'),
    ('const q=typeof fleetSubQuote==="function"?fleetSubQuote(base, sub, have, f.do||70000',
     'const q=typeof fleetSubQuote==="function"?fleetSubQuote(Math.max(0, base-ti), sub, have, f.do||70000'),
]
DONE3 = "/*fleet-pin2*/"
# Stage 3: both special T7 Active 2WD cars pinned at 2 389 000; column names both VINs.
SUBS3 = [
    ('const FLEET_PIN = {"EDXFB32B7TE062327":2389000};' + DONE2,
     'const FLEET_PIN = {"EDXFB32B7TE062327":2389000,"EDXFB32B2TE041658":2389000};' + DONE2 + DONE3),
    ('<p class="calc-note">EDXFB32B7TE062327${fleetPin?" · этот VIN":""}. Старт 2 389 000',
     '<p class="calc-note">EDXFB32B2TE041658 · EDXFB32B7TE062327${fleetPin?" · этот VIN":""}. Старт 2 389 000'),
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


PIN_RE = re.compile(r'const FLEET_PIN = \{[^}]*\};(?:/\*fleet-[a-z0-9]+\*/)*')
PIN_NEW = ('const FLEET_PIN = {"EDXFB32B7TE062327":2389000,"EDXFB32B2TE041658":2389000};'
           + DONE2 + DONE3)
NOTE_RE = re.compile(r'<p class="calc-note">(?:EDXFB32B2TE041658 · )?EDXFB32B7TE062327\$\{fleetPin')
NOTE_NEW = '<p class="calc-note">EDXFB32B2TE041658 · EDXFB32B7TE062327${fleetPin'


def apply_each(text, subs):
    # Each substitution is applied on its own whenever its old text is present
    # exactly once, so pieces reverted by earlier build steps (patch_km.py
    # re-splices the KM block) are re-patched on every build. Markers are
    # informational only.
    out = text
    for old, new in subs:
        n = out.count(old)
        if n == 1:
            out = out.replace(old, new, 1)
        elif n > 1:
            print("fleet: ambiguous anchor", n, "->", old[:70].replace("\n", " "))
    return out


def patch(text):
    out = apply_each(text, SUBS)
    out = apply_each(out, [s for s in SUBS2 if not s[0].startswith("const FLEET_PIN")])
    if len(PIN_RE.findall(out)) == 1:
        out = PIN_RE.sub(lambda m: PIN_NEW, out)
    if len(NOTE_RE.findall(out)) == 1:
        out = NOTE_RE.sub(lambda m: NOTE_NEW, out)
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
        print(p, "fleet-dcti: patched")


if __name__ == "__main__":
    main()
