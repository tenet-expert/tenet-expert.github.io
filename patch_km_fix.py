#!/usr/bin/env python3
"""КМ — фиксы, не коридор; без кредитной скидки 50/30 на T7 Prime 2WD (Александр, 27.10.2026 16:32).

1. KM из Sheet вида «A / B» = две фиксированные суммы: A — с трейд-ином, B — без трейд-ина
   (T7 «30 / 80» = 30 тыс. с ТИ, 80 тыс. без ТИ). Строго по позиции, без min/max.
   Данные: KM_MODELS.kmMin = A (с ТИ), kmMax = B (без ТИ); prioMin/prioMax так же.
   Значения KM_CORRIDOR (сырьё Sheet) раскладываются по позиции и перекрывают kmMin/kmMax
   соответствующих моделей TENET — даже если синк записал их в другом порядке.
   Код: kmBand() отдаёт одно число (lo = hi), тексты «коридор/до/от» -> «КМ … с трейд-ином / … без трейд-ина».
   VIN-фиксы KM_FORK, приоритет −100/0 и TENET+ 0/0 не меняются (они уже фиксы).
2. T7 Prime 2WD (id t7p): cr/crBack («Выгодный кредит» 50 000 / возмещение 30 000) = 0.
   Строка приходит из «Цены и поддержки» через terms-calc-data.js (ту-google-08/14), поэтому
   обнуляется на каждой сборке. Другие T7 не трогаются.

3. Нал (27.10 21:43): скидка ДЦ под тот же фикс КМ, что и в кредите; потолок T9 30% РРЦ; КП переносит скидку.

Вызывается из patch_terms_sync.py (после синка) и в конце patch_issue.py (последний шаг сборки).
Идемпотентен. Любое сомнение -> файл не пишется.
"""
import re, shutil, subprocess, tempfile, os
from pathlib import Path

TARGETS = [Path("index.html"), Path("_site/index.html")]
NO_CREDIT = {"t7p"}
NUM = r"((?:[−\-–]\s*)?\d+(?:[.,]\d+)?)"
PAIR = re.compile(NUM + r"\s*/\s*" + NUM)


def _num(s):
    s = s.replace("−", "-").replace("–", "-").replace(" ", "").replace(",", ".")
    v = float(s)
    return int(v) if v == int(v) else v


def _span(text, name):
    m = re.search(r"^\s*const " + name + r" = ", text, re.M)
    if not m:
        return None
    i, depth, q = m.end(), 0, None
    while i < len(text):
        ch = text[i]
        if q:
            if ch == "\\":
                i += 2
                continue
            if ch == q:
                q = None
        elif ch in "\"'`":
            q = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == ";" and depth == 0:
            return m.start(), i + 1
        i += 1
    return None


def corridor_fixes(text):
    """[(model, kind, ti, cash)] from KM_CORRIDOR, positional: first = с ТИ, second = без ТИ."""
    sp = _span(text, "KM_CORRIDOR")
    out = []
    if not sp:
        return out
    for m in re.finditer(r'\{model:"([^"]+)",trim:"([^"]*)",km:"([^"]*)"', text[sp[0]:sp[1]]):
        p = PAIR.search(m.group(3))
        if not p:
            continue
        kind = "prio" if "приоритет" in m.group(2).lower() else "km"
        out.append((m.group(1).strip(), kind, _num(p.group(1)), _num(p.group(2))))
    return out


def _model_match(sheet_model, row):
    name = re.search(r'name:"([^"]*)"', row)
    brand = re.search(r'brand:"([^"]*)"', row)
    if not name or not brand or brand.group(1) != "TENET":
        return False
    return name.group(1).split(" ")[0].upper() == sheet_model.upper()


def _set(row, key, val):
    return re.sub(r"(\b" + key + r":)(-?\d+(?:\.\d+)?)", lambda m: m.group(1) + str(val), row, count=1)


T9_PIN = re.compile(r'(\{model:"T9",trim:"[^"]*",km:")[−\-–]\s*30\s*/\s*0(")')


def pin_t9(text):
    """27.10.2026 22:18: T9 КМ без ТИ 0 -> 50 (фикс −30 / 50). Sheet C12 и канон уже −30 / 50;
    если синк принесёт старое «−30 / 0» — поправить. A8 не трогается."""
    sp = _span(text, "KM_CORRIDOR")
    if not sp:
        return text
    blk = T9_PIN.sub(lambda m: m.group(1) + "−30 / 50" + m.group(2), text[sp[0]:sp[1]])
    return text[:sp[0]] + blk + text[sp[1]:]


def fix_data(text):
    text = pin_t9(text)
    sp = _span(text, "KM_MODELS")
    if not sp:
        return text
    blk = text[sp[0]:sp[1]]
    fixes = corridor_fixes(text)
    lines = blk.split("\n")
    for k, line in enumerate(lines):
        m = re.search(r'\{id:"([^"]+)"', line)
        if not m:
            continue
        row = line
        if m.group(1) in NO_CREDIT:
            row = _set(_set(row, "cr", 0), "crBack", 0)
        for model, kind, ti, cash in fixes:
            if _model_match(model, row):
                a, b = ("prioMin", "prioMax") if kind == "prio" else ("kmMin", "kmMax")
                row = _set(_set(row, a, ti), b, cash)
                if kind == "km" and not any(f[0] == model and f[1] == "prio" for f in fixes):
                    row = _set(_set(row, "prioMin", ti), "prioMax", cash)
        lines[k] = row
    nb = "\n".join(lines)
    return text[:sp[0]] + nb + text[sp[1]:]


CODE = [
    # kmBand: одно число вместо коридора
    ('      return {lo:m.kmMin, hi:m.kmMax, lock:false};\n    }\n    function kmBandTxt(',
     '      { const t=useTi?m.kmMin:m.kmMax; return {lo:t, hi:t, lock:false, fix:true}; }\n    }\n'
     '    function kmFixRaw(s){ return String(s||"").replace(/((?:[−\\-–]\\s*)?\\d+(?:[.,]\\d+)?)\\s*\\/\\s*((?:[−\\-–]\\s*)?\\d+(?:[.,]\\d+)?)/g, (x,a,b)=>a.replace(/\\s/g,"")+" с ТИ / "+b.replace(/\\s/g,"")+" без ТИ"); }\n'
     '    function kmFixPair(vin, prio, m){ const a=kmBand(vin, true, prio, m), b=kmBand(vin, false, prio, m); return a.lo===b.lo?(a.lo+" тыс. с трейд-ином и без"):(a.lo+" тыс. с трейд-ином / "+b.lo+" тыс. без трейд-ина"); }\n'
     '    function kmBandTxt('),
    ('word:k+0.05<lo?"ниже коридора":(k-0.05>hi?"выше коридора":"в коридоре")',
     'word:k+0.05<lo?"ниже фикса":(k-1>hi?"выше фикса":"по фиксу")'),
    ('Скидка от ДЦ за кредит${dcFit?` · до ${rub(dcFit)} в коридоре`:""}',
     'Скидка от ДЦ за кредит${dcFit?` · ${rub(dcFit)} под КМ ${lo} тыс.`:""}'),
    ('Сумма скидки ДЦ за кредит, ₽ · коридор от ${lo} тыс.',
     'Сумма скидки ДЦ за кредит, ₽ · КМ ${lo} тыс. ${useTi?"с трейд-ином":"без трейд-ина"}'),
    ('Приоритетный VIN ${escape(kmVin)}. Коридор ${kmBandTxt(lo,hi)}${useTi?" · с трейд-ин":" · без трейд-ин"}.',
     'Приоритетный VIN ${escape(kmVin)}. КМ ${kmBandTxt(lo,hi)}${useTi?" с трейд-ином":" без трейд-ина"}.'),
    ('Для VIN ${escape(kmVin)} коридор ${kmBandTxt(lo,hi)}${useTi?" · с трейд-ин":" · без трейд-ин"}.',
     'Для VIN ${escape(kmVin)} КМ ${kmBandTxt(lo,hi)}${useTi?" с трейд-ином":" без трейд-ина"}.'),
    ('<p class="calc-note">Коридор ${prioKmTxt}.', '<p class="calc-note">КМ ${prioKmTxt}.'),
    ('КМ ${Math.round(ordDeal.km/1000)} тыс. · коридор ${typeof kmBandTxt==="function"?kmBandTxt(ob.lo,ob.hi):ob.lo+" … "+ob.hi}',
     'КМ ${Math.round(ordDeal.km/1000)} тыс. · фикс ${typeof kmBandTxt==="function"?kmBandTxt(ob.lo,ob.hi):ob.lo+" тыс."}${useTi?" с трейд-ином":" без трейд-ина"}'),
    ('<p class="calc-note">Коридор ${kmBandTxt(lo,hi)} · сейчас',
     '<p class="calc-note">КМ ${typeof kmFixPair==="function"?kmFixPair(kmVin, prio, m):kmBandTxt(lo,hi)} · сейчас'),
    ('termGroup(KM_CORRIDOR,"km")',
     'termGroup((typeof kmFixRaw==="function"?KM_CORRIDOR.map(r=>Object.assign({},r,{km:kmFixRaw(r.km),note:kmFixRaw(r.note)})):KM_CORRIDOR),"km")'),
]


# 27.10.2026 21:43 (Александр): «За нал фикс км такой же, как с кредитом».
# Нал: скидка ДЦ подбирается под фикс КМ той же формулой (kmDcCrFit/kmDcCrMin), что и кредитная,
# по умолчанию ВЫКЛЮЧЕНА (22:18: «можем не давать её, сделай через галочку»). Потолок: T9 — вся скидка не больше 30% РРЦ; если фикс недостижим — пометка.
CASH = [
    ('const useDcCr=useLoan && kmVal("kmUseDcCr", false);',
     'const useDcCr=useLoan?kmVal("kmUseDcCr", false):kmVal("kmUseDcCash", false);/*km-cash-fix*/'),
    ('        dcCr=Math.max(0, Math.round(dcCr));\n        kmDcKeep=dcCr;\n      }\n      const discount=tiAmt+spec+dcTi+dcCr+crAmt;',
     '        dcCr=Math.max(0, Math.round(dcCr));\n        kmDcKeep=dcCr;\n      }\n'
     '      const dcCap=(m.stock==="tt9"||/^T9 /.test(m.name||""))?Math.max(0, Math.floor((rrc*0.3-(tiAmt+spec+dcTi+crAmt))/1000)*1000):Infinity;\n'
     '      const dcCapped=useDcCr && dcCr>dcCap;\n'
     '      if(dcCapped) dcCr=dcCap;\n'
     '      const discount=tiAmt+spec+dcTi+dcCr+crAmt;'),
    ('ordDc=Math.max(0, Math.round(ordDc));',
     'ordDc=Math.max(0, Math.round(ordDc)); if(typeof dcCap==="number" && ordDc>dcCap) ordDc=dcCap;'),
    ('<input id="kmDcCr" inputmode="numeric" value="${dcCr}" /></label>`:""}',
     '<input id="kmDcCr" inputmode="numeric" value="${dcCr}" /></label>`:""}'
     '\n            ${!useLoan?`<label class="check-row"><input id="kmUseDcCash" type="checkbox" ${useDcCr?"checked":""} /> <span>Скидка от ДЦ под фикс КМ ${lo} тыс. ${useTi?"с трейд-ином":"без трейд-ина"}</span></label>`:""}'
     '\n            ${!useLoan&&useDcCr?`<label class="field" style="max-width:none"><span>Скидка ДЦ (нал), ₽ · подобрана под КМ ${lo} тыс.</span><input id="kmDcCr" inputmode="numeric" value="${dcCr}" /></label>`:""}'
     '\n            ${dcCapped?`<div class="note-box">Фикс КМ ${lo} тыс. недостижим: потолок скидки T9 — 30% от РРЦ (${rub(Math.round(rrc*0.3))}). Скидка ДЦ ограничена ${rub(dcCap)}.</div>`:""}'
     '\n            ${useDcCr&&!dcCapped&&dcCr===0&&kmK+0.05<lo?`<div class="note-box">КМ ниже фикса ${lo} тыс. уже без скидки ДЦ — скидку ДЦ не даём.</div>`:""}'),
    ('useDcCr:useLoan && on("kmUseDcCr"),',
     'useDcCr:useLoan?on("kmUseDcCr"):on("kmUseDcCash"),'),
    ('const useDcCr=useLoan && (S?!!S.useDcCr:offerOn("ofDcCr"));',
     'const useDcCr=(S?!!S.useDcCr:offerOn("ofDcCr"));/*km-cash-fix*/'),
    ('if(dcCr) discs.push(["Скидка ДЦ за кредит", dcCr]);',
     'if(dcCr) discs.push([useLoan?"Скидка ДЦ за кредит":"Скидка ДЦ", dcCr]);'),
    ('${d.useLoan?`<label class="check-row"><input id="ofDcCr" type="checkbox" ${d.useDcCr?"checked":""} /> <span>Скидка ДЦ за кредит</span></label>`:""}',
     '<label class="check-row"><input id="ofDcCr" type="checkbox" ${d.useDcCr?"checked":""} /> <span>${d.useLoan?"Скидка ДЦ за кредит":"Скидка ДЦ"}</span></label>'),
    ('${d.useLoan&&d.useDcCr?offerField("Скидка ДЦ за кредит, ₽", `<input id="ofDcCrAmt"',
     '${d.useDcCr?offerField(d.useLoan?"Скидка ДЦ за кредит, ₽":"Скидка ДЦ, ₽", `<input id="ofDcCrAmt"'),
]
CODE.extend(CASH)


# 29.10.2026 (Александр): «КМ ровный». Расчётный КМ (формула доход/НДС − цена×fee, скидка ДЦ
# округляется до 1000 ₽) даёт дроби 30,8 / 80,3 / −29,8. Отображаемый КМ = ровно фикс A (с ТИ) или
# B (без ТИ) из Sheet / KM_FORK / приоритета. Цвет и слово «по фиксу / ниже фикса» считаются по
# расчётному значению (честный контроль), скидки, потолок T9 30% и галочки не меняются.
ROUND = [
    ('      const kmK=km/1000;\n',
     '      const kmK=km/1000;\n'
     '      const kmFixK=raw=>Math.round(raw);/*km-round real*/\n'),
    ('<div class="calc-out">${rub(Math.round(kmPango?pKm:km))} ₽</div>',
     '<div class="calc-out">${rub(kmFixK((kmPango?pKm:km)/1000)*1000)} ₽</div>'),
    ('· сейчас ${(kmPango?pKmK:kmK).toFixed(1)} тыс. ·',
     '· сейчас ${kmFixK(kmPango?pKmK:kmK)} тыс. ·'),
    ('<p class="calc-note">КМ ${Math.round(ordDeal.km/1000)} тыс. · фикс',
     '<p class="calc-note">КМ ${kmFixK(ordDeal.km/1000)} тыс. · фикс'),
    ('<p class="calc-note">КМ ${Math.round(prioDeal.km/1000)} тыс.${',
     '<p class="calc-note">КМ ${(KM_FORK[kmVin]?(useTi?KM_FORK[kmVin].ti:KM_FORK[kmVin].cash):(useTi?-100:0))} тыс.${'),
]
CODE.extend(ROUND)


# 29.10.2026 (Склад): в «Приоритете» строки, проданные без менеджера в Sheet (зелёная заливка,
# колонка «Менеджер» пустая), были зелёными без подписи -> показываем «Продано».
# «Рекомендуем» не показывает проданные (TERMS_PRIO.sold) и брони (STOCK.reserved).
PRIO = [
    ('const mark=sold&&r.seller?`<span class="sold-mark">Продано · ${escape(r.seller)} <i>${n}</i></span>`:',
     'const mark=sold?(r.seller?`<span class="sold-mark">Продано · ${escape(r.seller)} <i>${n}</i></span>`:`<span class="sold-mark">Продано</span>`):'),
    ('return list.filter(c=>PRIO_VINS.has(c.vin) && c.vin!==kmVin && !(typeof stockIsDemo==="function"?stockIsDemo(c):c.demo)).map(c=>{',
     'const prioOff=new Set((typeof TERMS_PRIO!=="undefined"?TERMS_PRIO:[]).filter(r=>r.sold||r.reserved).map(r=>r.vin));\n      return list.filter(c=>PRIO_VINS.has(c.vin) && c.vin!==kmVin && !c.reserved && !c.sold && !prioOff.has(c.vin) && !(typeof stockIsDemo==="function"?stockIsDemo(c):c.demo)).map(c=>{'),
]
CODE.extend(PRIO)


# 29.10.2026 (Александр): отображаемые названия комплектаций — по справочнику CM.Expert
# (trim-dictionary.csv, тот же, что у Склада): модель латиницей, комплектация по-русски.
# Только отображение: KM_MODELS.name, TERMS_INV / TERMS_INV_PLUS / TERMS_PRIO {model,trim}.
# Ключи id, суммы, КМ, скидки не меняются. Старое имя модели КМ сохраняется в nm0
# (по нему offer-логика ищет «4WD»). Применяется в apply() — после синка ТУ, в т.ч. 08/14.
OFFER_4WD = [
    ('if(/4wd/i.test((m&&m.name)||"") && r.price4)',
     'if(/4wd/i.test((m&&(m.nm0||m.name))||"") && r.price4)'),
]
CODE.extend(OFFER_4WD)
TRIM_MISS = []


def _trim_dict():
    import csv
    out = {}
    p = Path("trim-dictionary.csv")
    if not p.exists():
        return out
    with p.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            o, n = (r.get("old") or "").strip(), (r.get("new") or "").strip()
            if o and n:
                out[o] = n
    return out


def rename_trims(text):
    d = _trim_dict()
    if not d:
        return text
    n_done = 0
    sp = _span(text, "KM_MODELS")
    if sp:
        blk = text[sp[0]:sp[1]]

        def km(m):
            nonlocal n_done
            row = m.group(0)
            name = re.search(r'name:"([^"]*)"', row)
            if not name or "nm0:" in row:
                return row
            new = d.get(name.group(1))
            if not new:
                TRIM_MISS.append("KM_MODELS " + name.group(1))
                return row
            if new == name.group(1):
                return row
            n_done += 1
            return row.replace('name:"%s"' % name.group(1), 'name:"%s",nm0:"%s"' % (new, name.group(1)), 1)
        blk = re.sub(r'\{id:"[^"]+"[^\n]*', km, blk)
        text = text[:sp[0]] + blk + text[sp[1]:]
    for blkname in ("TERMS_INV", "TERMS_INV_PLUS", "TERMS_PRIO"):
        sp = _span(text, blkname)
        if not sp:
            continue
        blk = text[sp[0]:sp[1]]

        def mt(m):
            nonlocal n_done
            model, mid, trim = m.group(1), m.group(2), m.group(3)
            new = d.get(model + " " + trim)
            if not new:
                TRIM_MISS.append(blkname + " " + model + " " + trim)
                return m.group(0)
            nm = d.get(model, model)
            if new.startswith(nm + " "):
                nmod, ntrim = nm, new[len(nm) + 1:]
            elif new.startswith(model + " "):
                nmod, ntrim = model, new[len(model) + 1:]
            else:
                nmod, ntrim = new.rsplit(" ", 1)
            if (nmod, ntrim) == (model, trim):
                return m.group(0)
            n_done += 1
            return 'model:"%s"%strim:"%s"' % (nmod, mid, ntrim)
        blk = re.sub(r'model:"([^"]+)"(,(?:vin:"[^"]*",)?)trim:"([^"]*)"', mt, blk)
        text = text[:sp[0]] + blk + text[sp[1]:]
    print("km-fix: trims renamed", n_done, "| not in dictionary:", "; ".join(TRIM_MISS) or "—")
    return text


def fix_code(text):
    for old, new in CODE:
        if new in text:
            continue
        n = text.count(old)
        if n == 0:
            print("km-fix: anchor not found:", old[:70])
            continue
        text = text.replace(old, new)
    return text


def js_ok(html):
    node = shutil.which("node")
    if not node:
        return True
    for m in re.finditer(r"<script>(.*?)</script>", html, re.S):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(m.group(1))
        r = subprocess.run([node, "--check", f.name], capture_output=True, text=True)
        os.unlink(f.name)
        if r.returncode:
            print("km-fix: node --check failed:", r.stderr[:400])
            return False
    return True


def apply(text):
    return rename_trims(fix_code(fix_data(text)))


def main():
    for p in TARGETS:
        if not p.exists() or p.stat().st_size < 100000:
            continue
        src = p.read_text(encoding="utf-8")
        out = apply(src)
        if out == src:
            print("km-fix:", p, "already fixed")
            continue
        if not js_ok(out):
            print("km-fix:", p, "JS check failed -> not written")
            continue
        p.write_text(out, encoding="utf-8")
        print("km-fix:", p, "patched")


if __name__ == "__main__":
    main()
