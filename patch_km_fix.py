#!/usr/bin/env python3
"""КМ — фиксы, не коридор. Кредит T7 (Александр, 18.11.2026): 50/30 у всех T7, кроме Актив 2WD.

1. KM из Sheet вида «A / B» = две фиксированные суммы: A — с трейд-ином, B — без трейд-ина
   (T7 «0 / 50» = 0 тыс. с ТИ, 50 тыс. без ТИ; с 18.11.2026). Строго по позиции, без min/max.
   Данные: KM_MODELS.kmMin = A (с ТИ), kmMax = B (без ТИ); prioMin/prioMax так же.
   Значения KM_CORRIDOR (сырьё Sheet) раскладываются по позиции и перекрывают kmMin/kmMax
   соответствующих моделей TENET — даже если синк записал их в другом порядке.
   Код: kmBand() отдаёт одно число (lo = hi), тексты «коридор/до/от» -> «КМ … с трейд-ином / … без трейд-ина».
   VIN-фиксы KM_FORK (07.11: из KM_CORRIDOR и TERMS_PRIO), приоритет по VIN и TENET+ 0/0 не меняются (они уже фиксы).
2. Кредит T7 (18.11.2026, отменяет правило «t7p cr 0»): t7p / t7a4 / t7p4 =
   cr 50 000 / crBack 30 000; t7a (Актив 2WD) всегда cr 0 / crBack 0.
   NO_CREDIT = {t7a}, чтобы синк из Sheet не повесил 50/30 на Актив 2WD.

3. Нал (27.10 21:43): скидка ДЦ под тот же фикс КМ, что и в кредите; потолок T9 30% РРЦ; КП переносит скидку.

Вызывается из patch_terms_sync.py (после синка) и в конце patch_issue.py (последний шаг сборки).
Идемпотентен. Любое сомнение -> файл не пишется.
"""
import re, shutil, subprocess, tempfile, os
from pathlib import Path

TARGETS = [Path("index.html"), Path("_site/index.html")]
NO_CREDIT = {"t7a"}  # 18.11.2026: кредит 50/30 у всех T7, кроме Актив 2WD (t7a всегда cr 0 / crBack 0)
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
        trim = m.group(2).strip()
        if re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", trim):
            continue  # VIN-фикс живёт в KM_FORK
        kind = "prio" if "приоритет" in trim.lower() else "km"
        out.append((m.group(1).strip(), kind, _num(p.group(1)), _num(p.group(2)), trim))
    # общие строки сначала, строки по комплектации (Prime) поверх
    out.sort(key=lambda f: 0 if _generic(f[4]) else 1)
    return out


def _generic(trim):
    return trim.lower() in ("", "все", "любые", "приоритет", "остальные")


def _trim_match(trim, row):
    if _generic(trim):
        return True
    name = re.search(r'name:"([^"]*)"', row)
    nm = (name.group(1) if name else "").lower()
    words = [w for w in re.split(r"[\s/]+", trim.lower()) if w and w not in ("2wd", "4wd")]
    alias = {"prime": "прайм", "active": "актив", "ultra": "ультра"}
    return all(w in nm or alias.get(w, "#") in nm for w in words)


def _model_match(sheet_model, row):
    name = re.search(r'name:"([^"]*)"', row)
    brand = re.search(r'brand:"([^"]*)"', row)
    if not name or not brand or brand.group(1) != "TENET":
        return False
    return name.group(1).split(" ")[0].upper() == sheet_model.upper()


def _set(row, key, val):
    return re.sub(r"(\b" + key + r":)(-?\d+(?:\.\d+)?)", lambda m: m.group(1) + str(val), row, count=1)


T9_PIN = re.compile(r'(\{model:"T9",trim:"[^"]*",km:")[^"]*(")')


def pin_t9(text):
    """03.11.2026: T9 КМ = 0 / 30 (с ТИ / без ТИ). Старое правило −30/50 отменено.
    Любое значение в коридоре T9 приводится к 0 / 30. A8 не трогается."""
    sp = _span(text, "KM_CORRIDOR")
    if not sp:
        return text
    blk = T9_PIN.sub(lambda m: m.group(1) + "0 / 30" + m.group(2), text[sp[0]:sp[1]])
    return text[:sp[0]] + blk + text[sp[1]:]


# 18.11.2026, указание Александра: модельный КМ T7 0/50, пять приоритетных VIN −50/0.
# Chery Tiggo 7L (t7l) и кредитные поля (t7p/t7a4/t7p4 cr/crBack) не трогаются.
# VIN-фиксы коридора (100/200, 50/100) не трогаются.
T7_PRIO_VINS = (
    "EDEFB32B8TE105355",
    "EDXFD32B2TE042710",
    "EDEFB32BXTE100707",
    "EDEFB32B8TE099203",
    "EDEFD32B5TE102522",
)
T7_PRIO_ROWS = {
    "EDEFB32B8TE105355": '{model:"T7",vin:"EDEFB32B8TE105355",trim:"Актив",year:"2026",color:"Белый",extra:"",pay:1000,kmTi:-50,kmCash:0}',
    "EDXFD32B2TE042710": '{model:"T7",vin:"EDXFD32B2TE042710",trim:"Актив 4WD",year:"2026",color:"Белый",extra:"",pay:1000,kmTi:-50,kmCash:0}',
    "EDEFB32BXTE100707": '{model:"T7",vin:"EDEFB32BXTE100707",trim:"Актив",year:"2026",color:"Белый",extra:"",pay:1000,kmTi:-50,kmCash:0}',
    "EDEFB32B8TE099203": '{model:"T7",vin:"EDEFB32B8TE099203",trim:"Прайм",year:"2026",color:"Белый",extra:"",pay:1000,kmTi:-50,kmCash:0}',
    "EDEFD32B5TE102522": '{model:"T7",vin:"EDEFD32B5TE102522",trim:"Прайм 4WD",year:"2026",color:"Белый",extra:"",pay:1000,kmTi:-50,kmCash:0}',
}
T7_PRIO_NOTE = "5 VIN: EDEFB32B8TE105355, EDXFD32B2TE042710, EDEFB32BXTE100707, EDEFB32B8TE099203, EDEFD32B5TE102522; остальные приоритеты T7 — стандарт 0/50"
T7_PRIO_CORRIDOR = '{model:"T7",trim:"Приоритет",km:"−50 / 0",note:"' + T7_PRIO_NOTE + '"}'
T7_ROW_RE = re.compile(r'\{model:"T7",trim:"([^"]*)",km:"([^"]*)",note:"([^"]*)"\}')
T7_PRIO_ITEM_RE = re.compile(r'\{model:"T7",vin:"([A-Z0-9]{17})"[^}]*\}')


def pin_t7(text):
    """18.11.2026: TENET T7 КМ = 0 / 50; 5 приоритетных VIN = −50 / 0.

    Защищает живой сайт от отката следующим синкам (ту-google / patch_terms_sync),
    если в Sheet снова окажется старое 30/80. Не меняет Chery Tiggo 7L и cr/crBack.
    """
    sp = _span(text, "KM_CORRIDOR")
    if not sp:
        return text
    blk = text[sp[0]:sp[1]]
    rows = list(T7_ROW_RE.finditer(blk))
    has_prio = False
    for m in rows:
        trim = m.group(1)
        if re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", trim):
            continue  # VIN-фикс коридора не трогаем
        if "приоритет" in trim.lower():
            has_prio = True
            blk = blk[:m.start()] + T7_PRIO_CORRIDOR + blk[m.end():]
            rows = list(T7_ROW_RE.finditer(blk))  # refresh after replacement (same length not guaranteed)
            break
    if not has_prio:
        # вставить строку приоритета перед первой общей строкой T7
        m0 = T7_ROW_RE.search(blk)
        if m0:
            blk = blk[:m0.start()] + T7_PRIO_CORRIDOR + ",\n      " + blk[m0.start():]
        else:
            # коридор без T7 — вставим после T4L / в конец массива
            ins = "      " + T7_PRIO_CORRIDOR + ",\n      {model:\"T7\",trim:\"Все\",km:\"0 / 50\",note:\"\"},\n"
            end = blk.rfind("]")
            blk = blk[:end] + ins + blk[end:]
    # общие строки T7 (Все / Остальные / Любые) -> 0 / 50
    def _gen(m):
        trim = m.group(1)
        if re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", trim):
            return m.group(0)
        if "приоритет" in trim.lower():
            return m.group(0)
        return '{model:"T7",trim:"%s",km:"0 / 50",note:"%s"}' % (trim, m.group(3))
    blk = T7_ROW_RE.sub(_gen, blk)
    text = text[:sp[0]] + blk + text[sp[1]:]

    # TERMS_PRIO: 5 VIN −50/0; старый модельный 30/80 у прочих T7 -> 0/50
    sp = _span(text, "TERMS_PRIO")
    if sp:
        blk = text[sp[0]:sp[1]]
        seen = set()
        def _prio(m):
            vin = m.group(1)
            row = m.group(0)
            if vin in T7_PRIO_VINS:
                seen.add(vin)
                row = re.sub(r"kmTi:-?\d+", "kmTi:-50", row, count=1)
                row = re.sub(r"kmCash:-?\d+", "kmCash:0", row, count=1)
                if "kmTi:" not in row:
                    row = row[:-1] + ",kmTi:-50,kmCash:0}"
                return row
            if re.search(r"kmTi:30\b", row) and re.search(r"kmCash:80\b", row):
                row = re.sub(r"kmTi:30\b", "kmTi:0", row, count=1)
                row = re.sub(r"kmCash:80\b", "kmCash:50", row, count=1)
                return row
            return row
        blk = T7_PRIO_ITEM_RE.sub(_prio, blk)
        missing = [v for v in T7_PRIO_VINS if v not in seen]
        if missing:
            # вставить недостающие приоритеты перед закрытием массива
            ins = ",\n      ".join(T7_PRIO_ROWS[v] for v in missing)
            end = blk.rfind("]")
            # запятая перед вставкой, если последний элемент её не имеет
            head = blk[:end].rstrip()
            if not head.endswith(",") and not head.endswith("["):
                head += ","
            blk = head + "\n      " + ins + "\n    ];"
        text = text[:sp[0]] + blk + text[sp[1]:]

    # PRIO_VINS должен содержать эти 5 VIN
    sp = _span(text, "PRIO_VINS")
    if sp:
        blk = text[sp[0]:sp[1]]
        for v in T7_PRIO_VINS:
            if '"%s"' % v not in blk and "'%s'" % v not in blk:
                blk = blk.replace("])", ", \"%s\"])" % v, 1)
        text = text[:sp[0]] + blk + text[sp[1]:]
    return text


def sync_vin_forks(text):
    """07.11: VIN > model. Rebuild at runtime from synchronized data, never a trim-wide override."""
    sp = _span(text, "KM_FORK")
    if not sp:
        return text
    return text[:sp[0]] + "\n    const KM_FORK = " + 'Object.fromEntries([\n      ...KM_CORRIDOR.filter(r=>/^[A-HJ-NPR-Z0-9]{17}$/.test(r.trim)).map(r=>{\n        const pair=r.km.replace(/[−–]/g,"-").split("/").map(Number);\n        return [r.trim,{ti:pair[0],cash:pair[1]}];\n      }),\n      ...TERMS_PRIO.filter(r=>Number.isFinite(r.kmTi)&&Number.isFinite(r.kmCash)).map(r=>[r.vin,{ti:r.kmTi,cash:r.kmCash}])\n    ])' + ";" + text[sp[1]:]


L6_KM_TI = 100
L6_KM_CASH = 200
L6_KM_IDS = ("l6e", "l6u")  # Ultra 4WD (l6u4) без фикса КМ
L6_CORRIDOR_ROW = '{model:"L6",trim:"Кроме Ultra 4WD",km:"100 / 200",note:"фикс: с ТИ 100, без ТИ 200"}'
L6_CORRIDOR_RE = re.compile(r'\{model:"L6",trim:"[^"]*",km:"[^"]*",note:"[^"]*"\}')


def pin_l6(text):
    """22.11.2026: L6 Elegant/Ultra КМ 100 с ТИ / 200 без ТИ.
    L6 Ultra 4WD (l6u4) в коридор и в этот фикс не входит.
    Один источник чисел — константы выше. Вызывается после синка Sheet."""
    sp = _span(text, "KM_CORRIDOR")
    if sp:
        blk = text[sp[0]:sp[1]]
        if L6_CORRIDOR_RE.search(blk):
            blk = L6_CORRIDOR_RE.sub(L6_CORRIDOR_ROW, blk, count=1)
        elif '{model:"L4"' in blk:
            blk = blk.replace('{model:"L4"', L6_CORRIDOR_ROW + ",\n      " + '{model:"L4"', 1)
        text = text[:sp[0]] + blk + text[sp[1]:]
    sp = _span(text, "KM_MODELS")
    if not sp:
        return text
    blk = text[sp[0]:sp[1]]

    def _row(m):
        row = m.group(0)
        for key, val in (("kmMin", L6_KM_TI), ("kmMax", L6_KM_CASH), ("prioMin", L6_KM_TI), ("prioMax", L6_KM_CASH)):
            if re.search(r"\b" + key + r":-?\d+(?:\.\d+)?", row):
                row = re.sub(r"\b" + key + r":-?\d+(?:\.\d+)?", "%s:%s" % (key, val), row, count=1)
            else:
                row = row[:-1] + ",%s:%s}" % (key, val)
        return row

    blk = re.sub(r'\{id:"(?:l6e|l6u)"(?!4)[^}]*\}', _row, blk)
    return text[:sp[0]] + blk + text[sp[1]:]


def fix_data(text):
    text = pin_l6(sync_vin_forks(pin_t7(pin_t9(text))))
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
        for model, kind, ti, cash, trim in fixes:
            if _model_match(model, row) and _trim_match(trim, row):
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
     '<p class="calc-note">КМ ${(kmBand(kmVin, useTi, true, m).lo)} тыс.${'),
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


BG_START = "    /* TENET_BG_START 19.11.2026: аналог спеца до 30.11.2026 включительно, Europe/Samara. С 01.12.2026 termsBgActive()=false. */"
BG_END = "    /* TENET_BG_END */"

BG_BLOCK = r'''    /* TENET_BG_START 19.11.2026: аналог спеца до 30.11.2026 включительно, Europe/Samara. С 01.12.2026 termsBgActive()=false. */
    const TERMS_BG_UNTIL = "2026-11-30";
    const TERMS_BG = [
      {model:"T7",trim:"Актив 2WD",price:"2 400 нал, 2 300 ТИ"},
      {model:"T7",trim:"Прайм 2WD",price:"2 550 нал, 2 450 ТИ"},
      {model:"T7",trim:"Актив 4WD",price:"2 600 нал, 2 500 ТИ"},
      {model:"T7",trim:"Прайм 4WD",price:"2 800 нал, 2 700 ТИ"},
      {model:"T8",trim:"Актив 2WD 5 мест",price:"2 800 нал, 2 700 ТИ"},
      {model:"T8",trim:"Прайм 2WD 5 мест",price:"2 900 нал, 2 800 ТИ"},
      {model:"T8",trim:"Прайм 4WD 7 мест",price:"3 200 нал, 3 100 ТИ"},
      {model:"T8",trim:"Ультра 4WD 7 мест",price:"3 300 нал, 3 200 ТИ"},
      {model:"A8",trim:"Ультра 2.0",price:"3 100 нал, 3 000 ТИ"},
      {model:"T9",trim:"Прайм 5 мест",price:"3 500 нал, 3 400 ТИ"},
      {model:"T9",trim:"Ультра 5 мест",price:"3 800 нал, 3 600 ТИ"},
      {model:"T9",trim:"Ультра 7 мест",price:"3 900 нал, 3 700 ТИ"}
    ];
    const PANGO_BG = {
      t7a:{cash:2400000,ti:2300000},
      t7p:{cash:2550000,ti:2450000},
      t7a4:{cash:2600000,ti:2500000},
      t7p4:{cash:2800000,ti:2700000},
      t8a:{cash:2800000,ti:2700000},
      t8p:{cash:2900000,ti:2800000},
      t8p4:{cash:3200000,ti:3100000},
      t8u4:{cash:3300000,ti:3200000},
      ta8u:{cash:3100000,ti:3000000},
      tt9p:{cash:3500000,ti:3400000},
      tt9u:{cash:3800000,ti:3600000},
      tt9u7:{cash:3900000,ti:3700000}
    };
    function termsBgActive(){
      /* Until 2026-11-30 inclusive, Europe/Samara (UTC+4, no DST). */
      try{
        const ymd=new Intl.DateTimeFormat("en-CA",{timeZone:"Europe/Samara",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
        return ymd<=TERMS_BG_UNTIL;
      }catch(e){
        return new Date(Date.now()+4*3600*1000).toISOString().slice(0,10)<=TERMS_BG_UNTIL;
      }
    }
    function pangoBetter(a,b){
      if(!a) return b||null;
      if(!b) return a;
      return {cash:Math.min(a.cash,b.cash),ti:Math.min(a.ti,b.ti)};
    }
    function isPangoBg(car){
      if(!car || typeof termsBgActive!=="function" || !termsBgActive() || typeof PANGO_BG==="undefined") return false;
      const t=String(car.trim||"").toLowerCase();
      if(t.includes("престиж")||t.includes("prestige")) return false;
      const id=typeof kmIdFromCar==="function"?kmIdFromCar(car):"";
      return !!(id && PANGO_BG[id]);
    }
    function isPangoPlus(car){
      if(!car || typeof tplusChoiceOn!=="function" || !tplusChoiceOn()) return false;
      const id=typeof kmIdFromCar==="function"?kmIdFromCar(car):"";
      return !!(id && TPLUS_CHOICE.prices[id]);
    }
    function isPangoDeal(car,id){
      if(!car) return false;
      if(car.invoice) return true;
      if(typeof isPangoBg==="function" && isPangoBg(car)) return true;
      return typeof isPangoPlus==="function" && isPangoPlus(car);
    }
    /* TENET_BG_END */
'''

PANGO_OF = '''    function pangoOf(id){
      const vin=typeof kmVin==="string"?String(kmVin).toUpperCase():"";
      const vinPrice=(vin && typeof EXCL_FIX!=="undefined" && EXCL_FIX[vin]) || (vin && typeof PANGO_VIN!=="undefined" && PANGO_VIN[vin]) || null;
      const trimPrice=(typeof PANGO_FIX!=="undefined" && PANGO_FIX[id]) || null;
      const bg=(typeof termsBgActive==="function" && termsBgActive() && typeof PANGO_BG!=="undefined" && PANGO_BG[id]) || null;
      const plus=(typeof tplusChoiceOn==="function" && tplusChoiceOn() && TPLUS_CHOICE.prices[id]) || null;
      const camp=pangoBetter(bg, plus);
      if(vinPrice) return pangoBetter(vinPrice, camp);
      return pangoBetter(trimPrice, camp);
    }
'''

PANGO_OF_RE = re.compile(r"    function pangoOf\(id\)\{.*?\n    \}\n", re.S)

BG_SECTION = (
    '`${typeof termsBgActive==="function"&&termsBgActive()&&typeof TERMS_BG!=="undefined"?`'
    '<section class="terms-acc spec-bg"><h2 class="terms-acc-h">'
    '<button type="button" class="terms-acc-btn" aria-expanded="false" aria-controls="spec-bg-panel">'
    '<span class="terms-chevron" aria-hidden="true"></span>'
    '<span class="terms-acc-title">Без границ · до 30.11</span></button></h2>'
    '<div class="terms-acc-panel" id="spec-bg-panel" hidden><div class="terms-cards">`+termGroup(TERMS_BG,"price")+`</div></div></section>`:""}`+'
)

CSS_RULES = """
.terms-spec .spec-bg{grid-column:1/-1;background:#eef6ee}
.terms-spec .spec-bg h2,.terms-spec .spec-bg .terms-acc-title{color:#1e5c24}
.terms-spec .spec-bg .terms-cards{grid-template-columns:repeat(4,1fr)}
.terms-spec .spec-bg .term-card{background:#fff;border-color:#b7d4b9}
.terms-spec .spec-bg .term-group{border:1.5px solid #7da87f;box-shadow:none}
.terms-spec .spec-bg .term-group>b{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#1e5c24;border-bottom:1px solid #cde5ce;padding-bottom:6px}
@media(max-width:800px){
  .terms-spec .spec-bg .terms-cards{grid-template-columns:1fr}
}
"""

TERMS_SPEC_OPEN = '`<div class="terms-spec">`+'


def _insert_block(text):
    if "TENET_BG_START" in text:
        text = re.sub(
            r"[ 	]*/\* TENET_BG_START .*?" + re.escape(BG_END),
            BG_BLOCK.rstrip(),
            text,
            count=1,
            flags=re.S,
        )
    else:
        m = PANGO_OF_RE.search(text)
        if m:
            text = text[: m.end()] + "\n" + BG_BLOCK + text[m.end():]
        else:
            anchor = "    const TERMS_PRIO = ["
            if anchor not in text:
                print("borderless: no pangoOf/TERMS_PRIO anchor")
                return text
            text = text.replace(anchor, BG_BLOCK + "\n" + anchor, 1)
    if PANGO_OF_RE.search(text):
        text = PANGO_OF_RE.sub(PANGO_OF, text, count=1)
    else:
        print("borderless: pangoOf not replaced")
    return text


def _insert_terms_section(text):
    if "spec-bg-panel" in text and "Без границ · до 30.11" in text:
        return text
    needle = '`<div class="terms-spec">`+\n        `<section class="terms-acc spec-tenet">'
    if needle not in text:
        needle2 = '`<div class="terms-spec">`+'
        if needle2 not in text:
            print("borderless: terms-spec accordion not found")
            return text
        text = text.replace(needle2, '`<div class="terms-spec">`+\n        ' + BG_SECTION + "\n        ", 1)
        return text
    text = text.replace(
        needle,
        '`<div class="terms-spec">`+\n        ' + BG_SECTION + "\n        " + '`<section class="terms-acc spec-tenet">',
        1,
    )
    return text


def _insert_css(text):
    if ".terms-spec .spec-bg{" in text:
        return text
    anchor = ".terms-spec .spec-plus{background:#f4efe4}"
    if anchor in text:
        return text.replace(anchor, anchor + CSS_RULES, 1)
    # fallback: before first @media for terms-spec
    alt = "@media(max-width:800px){\n  .terms-spec{grid-template-columns:1fr}"
    if alt in text:
        return text.replace(alt, CSS_RULES + alt, 1)
    print("borderless: CSS anchor not found")
    return text


def _rewire_invoice(text):
    # Source index.html (kmPango variant, spaces around &&)
    src_pair = (
        "      const pShow=pangoOnly || !!(_pg && (showMpt || showSub || canSub));\n"
        "      const kmPango=!!(pangoOnly || (selected && selected.invoice && _pg));"
    )
    src_pair_new = (
        "      const kmPango=!!(pangoOnly || (selected && isPangoDeal(selected,m.id) && _pg));\n"
        "      const pShow=pangoOnly || kmPango || !!(_pg && (showMpt || showSub || canSub));"
    )
    if src_pair in text:
        text = text.replace(src_pair, src_pair_new)
        print("borderless: kmPango/pShow rewired (source variant)")
    elif "isPangoDeal(selected,m.id) && _pg" in text and "const kmPango=" in text:
        pass
    elif "const kmPango=" in text and "selected && selected.invoice" in text:
        text = text.replace("selected && selected.invoice", "selected && isPangoDeal(selected,m.id)")
        print("borderless: spaced selected.invoice rewired")

    # Built page (compact &&, no kmPango): show PANGO when this VIN is on the deal
    live_pshow = "const pShow=!!(_pg && (showMpt || showSub || canSub));"
    live_pshow_new = "const pShow=!!(_pg && (showMpt || showSub || canSub || (selected&&isPangoDeal(selected,m.id))));"
    if live_pshow in text:
        text = text.replace(live_pshow, live_pshow_new)
        print("borderless: pShow rewired (built variant)")

    compact_old = "selected&&selected.invoice"
    compact_new = "selected&&isPangoDeal(selected,m.id)"
    n = text.count(compact_old)
    if n:
        text = text.replace(compact_old, compact_new)
        print("borderless: rewired selected.invoice -> isPangoDeal", n)
    return text


def _badges(text):
    old_calc = (
        '${(typeof EXCL_FIX!=="undefined"&&EXCL_FIX[c.vin])?`<span class="mpt-tag super-tag">СУПЕРСПЕЦ</span>`:(c.invoice?`<span class="mpt-tag inv-tag">Спец инвойс</span>`:"")}'
    )
    new_calc = (
        '${(typeof EXCL_FIX!=="undefined"&&EXCL_FIX[c.vin])?`<span class="mpt-tag super-tag">СУПЕРСПЕЦ</span>`:(c.invoice?`<span class="mpt-tag inv-tag">Спец инвойс</span>`:(typeof isPangoBg==="function"&&isPangoBg(c)?`<span class="mpt-tag inv-tag">Без границ</span>`:(typeof isPangoPlus==="function"&&isPangoPlus(c)?`<span class="mpt-tag inv-tag">Выбор</span>`:"")))}'
    )
    if old_calc in text:
        text = text.replace(old_calc, new_calc)
        print("borderless: calc VIN badge updated")
    elif "isPangoBg(c)?`<span class=\"mpt-tag inv-tag\">Без границ</span>`" in text or "isPangoBg(c)?`<span class='mpt-tag inv-tag'>Без границ</span>`" in text:
        pass
    else:
        if "СУПЕРСПЕЦ</span>`:(c.invoice?" in text and "Без границ</span>`:\"\")}" not in text:
            print("borderless: calc VIN badge anchor drifted")

    old_meta = '${st}${(typeof EXCL_FIX!=="undefined"&&EXCL_FIX[c.vin])?" · СУПЕРСПЕЦ":(c.invoice?" · спец инвойс":"")}'
    new_meta = '${st}${(typeof EXCL_FIX!=="undefined"&&EXCL_FIX[c.vin])?" · СУПЕРСПЕЦ":(c.invoice?" · спец инвойс":(typeof isPangoBg==="function"&&isPangoBg(c)?" · без границ":(typeof isPangoPlus==="function"&&isPangoPlus(c)?" · выбор":"")))}'
    if old_meta in text:
        text = text.replace(old_meta, new_meta)
        print("borderless: calc meta updated")

    old_bits = 'else if(r.invoice) bits.push(`<span class="st inv">Спец инвойс</span>`);'
    new_bits = (
        'else if(r.invoice) bits.push(`<span class="st inv">Спец инвойс</span>`);\n'
        '      else if(typeof isPangoBg==="function"&&isPangoBg(r)) bits.push(`<span class="st inv">Без границ</span>`);\n'
        '      else if(typeof isPangoPlus==="function"&&isPangoPlus(r)) bits.push(`<span class="st inv">Выбор</span>`);'
    )
    if old_bits in text and "Без границ</span>`);" not in text.split(old_bits, 1)[1][:280]:
        text = text.replace(old_bits, new_bits)
        print("borderless: stock table badge updated")
    bg_tag = 'isPangoBg(c)?`<span class="mpt-tag inv-tag">Без границ</span>`:""'
    plus_tag = 'isPangoBg(c)?`<span class="mpt-tag inv-tag">Без границ</span>`:(typeof isPangoPlus==="function"&&isPangoPlus(c)?`<span class="mpt-tag inv-tag">Выбор</span>`:"")'
    if bg_tag in text:
        text = text.replace(bg_tag, plus_tag)
        print("borderless: calc badge gained Выбор")
    bg_meta = 'isPangoBg(c)?" · без границ":""'
    plus_meta = 'isPangoBg(c)?" · без границ":(typeof isPangoPlus==="function"&&isPangoPlus(c)?" · выбор":"")'
    if bg_meta in text:
        text = text.replace(bg_meta, plus_meta)
        print("borderless: calc meta gained выбор")
    bg_bits = 'else if(typeof isPangoBg==="function"&&isPangoBg(r)) bits.push(`<span class="st inv">Без границ</span>`);'
    plus_bits = bg_bits + '\n      else if(typeof isPangoPlus==="function"&&isPangoPlus(r)) bits.push(`<span class="st inv">Выбор</span>`);'
    if bg_bits in text and "Выбор</span>`);" not in text:
        text = text.replace(bg_bits, plus_bits)
        print("borderless: stock badge gained Выбор")
    return text


def _insert_plus_section(text):
    """TENET Plus Выбор sits in the same спеццены block as «Без границ»."""
    if "TENET Plus Выбор" in text and "spec-vybor-panel" in text:
        return text
    needle = 'id="spec-bg-panel"><h3>Без границ · до 30.11</h3><div class="terms-cards">`+termGroup(TERMS_BG,"price")+`</div></section>`:""}`+'
    section = (
        needle + "\n        "
        '`${typeof tplusChoiceOn==="function"&&tplusChoiceOn()?'
        '`<section class="spec-part spec-vybor" id="spec-vybor-panel"><h3>${escape(tplusChoiceTitle())}</h3>'
        '<div class="terms-cards">`+termGroup(tplusChoiceRows(),"price")+`</div></section>`:""}`+'
    )
    if needle in text:
        text = text.replace(needle, section, 1)
        print("borderless: TENET Plus Выбор section inserted")
        return text
    print("borderless: Выбор section anchor not found")
    return text


def _insert_plus_css(text):
    if ".terms-spec .spec-vybor{" in text:
        return text
    css = """
.terms-spec .spec-vybor{background:#f4f7ee}
.terms-spec .spec-vybor h3{color:#1e5c24}
.terms-spec .spec-vybor .terms-cards{grid-template-columns:1fr 1fr}
.terms-spec .spec-vybor .term-card{background:#fff;border-color:#c5d4b0}
.terms-spec .spec-vybor .term-group{border:1.5px solid #8aa87d;box-shadow:none}
.terms-spec .spec-vybor .term-group>b{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#1e5c24;border-bottom:1px solid #d5e5cd;padding-bottom:6px}
@media(max-width:800px){
  .terms-spec .spec-vybor .terms-cards{grid-template-columns:1fr}
}
"""
    anchor = ".terms-spec .spec-bg .term-group>b{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#1e5c24;border-bottom:1px solid #cde5ce;padding-bottom:6px}"
    if anchor in text:
        return text.replace(anchor, anchor + css, 1)
    print("borderless: Выбор CSS anchor not found")
    return text


def ensure_borderless(text):
    """Pin «Без границ» data, pangoOf, TУ block, PANGO deal path and badges."""
    src = text
    text = _insert_block(text)
    text = _insert_terms_section(text)
    text = _insert_plus_section(text)
    text = _insert_css(text)
    text = _insert_plus_css(text)
    text = _rewire_invoice(text)
    text = _badges(text)
    if text != src:
        print("borderless: applied")
    else:
        print("borderless: already in place")
    return text


def ensure_data_js(text):
    """For terms-calc-data.js: data + helpers + pangoOf (EXCL_FIX-safe)."""
    return _insert_block(text)


def _sub(text, old, new, label):
    if old not in text:
        return text
    print("l6u4 ui:", label)
    return text.replace(old, new, 1)


def pin_l6u4_ui(text):
    """22.11.2026: L6 Ultra 4WD — без КМ, скидка ДЦ = 0 и скрыта, КАСКО+GAP не ниже 200 000.
    Сборка подменяет calcKm/КП шаблоном, поэтому пин ставится после неё."""
    text = _sub(
        text,
        '      const useDcTi=kmVal("kmUseDcTi", false);/*fleet-dcti*/\n'
        '      const useDcCr=useLoan?kmVal("kmUseDcCr", false):kmVal("kmUseDcCash", false);/*km-cash-fix*/',
        '      const l6u4=m.id==="l6u4";/*l6u4-lock*/\n'
        '      const useDcTi=l6u4?false:kmVal("kmUseDcTi", false);/*fleet-dcti*/\n'
        '      const useDcCr=l6u4?false:(useLoan?kmVal("kmUseDcCr", false):kmVal("kmUseDcCash", false));/*km-cash-fix*/',
        "calc dc",
    )
    text = _sub(
        text,
        '        pack=kmVal("kmPack", 150000);\n        casco=Math.min(pack, 80000);',
        '        pack=kmVal("kmPack", l6u4?200000:150000);\n'
        '        if(l6u4 && pack<200000) pack=200000;/*l6u4-casco*/\n'
        '        casco=Math.min(pack, 80000);',
        "calc pack",
    )
    text = _sub(
        text,
        '        casco=kmVal("kmCasco", 80000);',
        '        casco=kmVal("kmCasco", l6u4?200000:80000);\n'
        '        if(l6u4 && casco<200000) casco=200000;/*l6u4-casco*/',
        "calc casco",
    )
    text = _sub(
        text,
        '      if(_pgTrim && !useLoan) pack=150000;',
        '      if(_pgTrim && !useLoan && !l6u4) pack=150000;\n'
        '      if(l6u4 && pack<200000) pack=200000;',
        "calc pango pack",
    )
    text = _sub(
        text,
        '${true?`<label class="check-row"><input id="kmUseDcTi" type="checkbox" ${useDcTi?"checked":""} /> <span>Скидка от ДЦ за трейд-ин ${rub(KM_DC_DEF)}</span></label>`:""}',
        '${l6u4?`<p class="calc-note">Скидка ДЦ на L6 Ultra 4WD не применяется.</p>`:`<label class="check-row"><input id="kmUseDcTi" type="checkbox" ${useDcTi?"checked":""} /> <span>Скидка от ДЦ за трейд-ин ${rub(KM_DC_DEF)}</span></label>`}',
        "calc dc ti",
    )
    text = _sub(
        text,
        '${useLoan?`<label class="check-row"><input id="kmUseDcCr"',
        '${!l6u4&&useLoan?`<label class="check-row"><input id="kmUseDcCr"',
        "calc dc credit",
    )
    text = _sub(
        text,
        '${!useLoan?`<label class="check-row"><input id="kmUseDcCash"',
        '${!l6u4&&!useLoan?`<label class="check-row"><input id="kmUseDcCash"',
        "calc dc cash",
    )
    text = _sub(
        text,
        '${useLoan\n'
        '              ?`<label class="field" style="max-width:none"><span>Каско расширенное, ₽</span><input id="kmPack" inputmode="numeric" value="${pack}" /></label>`\n'
        '              :`<label class="field" style="max-width:none"><span>КАСКО, ₽</span><input id="kmCasco" inputmode="numeric" value="${casco}" /></label>`}',
        '${useLoan\n'
        '              ?`<label class="field" style="max-width:none"><span>Каско расширенное, ₽${l6u4?" · минимум 200 000":""}</span><input id="kmPack" inputmode="numeric" value="${pack}" /></label>`\n'
        '              :`<label class="field" style="max-width:none"><span>КАСКО, ₽${l6u4?" · минимум 200 000":""}</span><input id="kmCasco" inputmode="numeric" value="${casco}" /></label>`}',
        "calc casco label",
    )
    text = _sub(
        text,
        '${prio?`<div class="note-box">Приоритетный VIN ${escape(kmVin)}. Коридор ${lo} … ${hi} тыс.</div>`:""}',
        '${!l6u4&&prio?`<div class="note-box">Приоритетный VIN ${escape(kmVin)}. Коридор ${lo} … ${hi} тыс.</div>`:""}',
        "calc prio km",
    )
    text = _sub(
        text,
        '<p class="eyebrow">КМ без НДС${selected&&isPangoDeal(selected,m.id)&&_pg?" · спеццена":""}</p>\n'
        '            <div class="calc-out">${rub(Math.round((selected&&isPangoDeal(selected,m.id)&&_pg?pKm:km)/1000)*1000)} ₽</div>\n'
        '            <p class="calc-note">${lo===hi?"Фикс "+lo:"Коридор "+lo+" … "+hi} тыс. · сейчас ${Math.round(selected&&isPangoDeal(selected,m.id)&&_pg?pKmK:kmK)} тыс. · ${(selected&&isPangoDeal(selected,m.id)&&_pg?pOk:ok)?(lo===hi?"на фиксе":"в коридоре"):"вне коридора"}</p>',
        '${l6u4?"":`<p class="eyebrow">КМ без НДС${selected&&isPangoDeal(selected,m.id)&&_pg?" · спеццена":""}</p>\n'
        '            <div class="calc-out">${rub(Math.round((selected&&isPangoDeal(selected,m.id)&&_pg?pKm:km)/1000)*1000)} ₽</div>\n'
        '            <p class="calc-note">${(m.id==="l6e"||m.id==="l6u")&&typeof kmFixPair==="function"?("КМ "+kmFixPair(kmVin, prio, m)+" · "):""}${lo===hi?"Фикс "+lo:"Коридор "+lo+" … "+hi} тыс. · сейчас ${Math.round(selected&&isPangoDeal(selected,m.id)&&_pg?pKmK:kmK)} тыс. · ${(selected&&isPangoDeal(selected,m.id)&&_pg?pOk:ok)?(lo===hi?"на фиксе":"в коридоре"):"вне коридора"}</p>`}',
        "calc km block",
    )
    text = _sub(
        text,
        '      const useDcTi=(S?!!S.useDcTi:offerOn("ofDcTi"));\n'
        '      const useDcCr=(S?!!S.useDcCr:offerOn("ofDcCr"));/*km-cash-fix*/',
        '      const l6u4=m.id==="l6u4";/*l6u4-lock*/\n'
        '      const useDcTi=l6u4?false:(S?!!S.useDcTi:offerOn("ofDcTi"));\n'
        '      const useDcCr=l6u4?false:(S?!!S.useDcCr:offerOn("ofDcCr"));/*km-cash-fix*/',
        "offer dc",
    )
    text = _sub(
        text,
        '        pack=S?(Number(S.pack)||0):(offerNum("ofPack", 150000)||0);\n'
        '        casco=Math.min(pack, 80000);\n'
        '      }else casco=S?(Number(S.casco)||0):(offerNum("ofCasco", 0)||0);',
        '        pack=S?(Number(S.pack)||0):(offerNum("ofPack", l6u4?200000:150000)||0);\n'
        '        if(l6u4 && pack<200000) pack=200000;/*l6u4-casco*/\n'
        '        casco=Math.min(pack, 80000);\n'
        '      }else{\n'
        '        casco=S?(Number(S.casco)||0):(offerNum("ofCasco", l6u4?200000:0)||0);\n'
        '        if(l6u4 && casco<200000) casco=200000;/*l6u4-casco*/\n'
        '      }',
        "offer casco",
    )
    text = _sub(
        text,
        '${true?`<label class="check-row"><input id="ofDcTi" type="checkbox" ${d.useDcTi?"checked":""} /> <span>Скидка ДЦ за трейд-ин</span></label>`:""}\n'
        '        ${d.useDcTi?offerField("Скидка ДЦ за трейд-ин, ₽", `<input id="ofDcTiAmt" inputmode="numeric" value="${d.dcTi||d.dcDef}" />`):""}\n'
        '        <label class="check-row"><input id="ofDcCr" type="checkbox" ${d.useDcCr?"checked":""} /> <span>${d.useLoan?"Скидка ДЦ за кредит":"Скидка ДЦ"}</span></label>\n'
        '        ${d.useDcCr?offerField(d.useLoan?"Скидка ДЦ за кредит, ₽":"Скидка ДЦ, ₽", `<input id="ofDcCrAmt" inputmode="numeric" value="${d.dcCr||d.dcDef}" />`):""}',
        '${d.m.id==="l6u4"?`<p class="calc-note">Скидка ДЦ на L6 Ultra 4WD не применяется.</p>`:""}\n'
        '        ${d.m.id==="l6u4"?"":`<label class="check-row"><input id="ofDcTi" type="checkbox" ${d.useDcTi?"checked":""} /> <span>Скидка ДЦ за трейд-ин</span></label>`}\n'
        '        ${(d.m.id!=="l6u4" && d.useDcTi)?offerField("Скидка ДЦ за трейд-ин, ₽", `<input id="ofDcTiAmt" inputmode="numeric" value="${d.dcTi||d.dcDef}" />`):""}\n'
        '        ${d.m.id==="l6u4"?"":`<label class="check-row"><input id="ofDcCr" type="checkbox" ${d.useDcCr?"checked":""} /> <span>${d.useLoan?"Скидка ДЦ за кредит":"Скидка ДЦ"}</span></label>`}\n'
        '        ${(d.m.id!=="l6u4" && d.useDcCr)?offerField(d.useLoan?"Скидка ДЦ за кредит, ₽":"Скидка ДЦ, ₽", `<input id="ofDcCrAmt" inputmode="numeric" value="${d.dcCr||d.dcDef}" />`):""}',
        "offer form",
    )
    text = _sub(
        text,
        '${d.useLoan?offerField("Каско расширенное, ₽", `<input id="ofPack" inputmode="numeric" value="${d.pack}" />`):offerField("КАСКО, ₽", `<input id="ofCasco" inputmode="numeric" value="${d.casco}" />`)}',
        '${d.useLoan?offerField("Каско расширенное, ₽"+(d.m.id==="l6u4"?" · минимум 200 000":""), `<input id="ofPack" inputmode="numeric" value="${d.pack}" />`):offerField("КАСКО, ₽"+(d.m.id==="l6u4"?" · минимум 200 000":""), `<input id="ofCasco" inputmode="numeric" value="${d.casco}" />`)}',
        "offer casco label",
    )
    return text


def apply(text):
    return pin_l6u4_ui(ensure_borderless(rename_trims(fix_code(fix_data(text)))))


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
