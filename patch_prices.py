# -*- coding: utf-8 -*-
"""Прайсы: только официальные сайты (tenet.ru, haval.ru, chery.ru). Сверено 29.10.2026.
Идемпотентно: правит DOCS в index.html и блоки <!--OFFICIAL-PRICES--> в docs/*.html.
Цены калькулятора (ТУ/КМ/РРЦ/скидки) НЕ трогает."""
import re
from pathlib import Path

CDN = "https://cdn.perxis.ru/originals/%s/original"
TCDN = "https://1.cdn.perxis.ru/originals/%s/original"
HAVAL = {
 "jolion": ("Haval Jolion", "14.08.2026", CDN % "da1hsmobeucc73999j40", [
   ("Комфорт", "1.5T 2WD MT", 2099000), ("Оптимум", "1.5T 2WD DCT", 2499000), ("Премиум", "1.5T 2WD DCT", 2699000),
   ("Оптимум", "1.5T 4WD DCT", 2649000), ("Премиум", "1.5T 4WD DCT", 2849000), ("Техно+", "1.5T 4WD DCT", 2949000)]),
 "m6": ("Haval M6", "14.08.2026", CDN % "da1hsh8beucc73999j3g", [
   ("Оптимум", "MT 143 л.с.", 2099000), ("Оптимум", "AT 143 л.с.", 2349000)]),
 "h3": ("Haval H3", "17.08.2026", CDN % "da1hstgbeucc73999j4g", [
   ("Оптимум", "1.5T 2WD", 2749000), ("Премиум", "1.5T 2WD", 2949000), ("Оптимум", "1.5T 4WD", 3099000),
   ("Премиум", "1.5T 4WD", 3249000), ("Техно+", "1.5T 4WD", 3549000)]),
 "f7": ("Haval F7", "11.08.2026", CDN % "d9tibrgbeucc73998fmg", [
   ("Оптимум", "1.5T 2WD", 2999000), ("Премиум", "1.5T 2WD", 3199000), ("Оптимум", "2.0T 4WD", 3399000),
   ("Премиум", "2.0T 4WD", 3599000), ("Техно+", "2.0T 4WD", 3799000)]),
 "f7x": ("Haval F7x", "11.08.2026", CDN % "d9tic0gbeucc73998fn0", [
   ("Премиум", "", 3799000), ("Техно+", "", 3999000)]),
 "h7": ("Haval H7", "27.10.2026", CDN % "dbg8ignvbdlg00bp57a0", [
   ("Премиум", "", 3999000), ("Техно+", "", 4199000), ("Космо", "", 4249000)]),
 "dargo": ("Haval Dargo", "20.07.2026 (цены на 10.04.2026)", CDN % "d9f0urobeucc73e9vlo0", [
   ("Оптимум", "", 3499000), ("Премиум", "", 3699000), ("Техно+", "", 3899000)]),
}
RIVAL_PAGES = {"t4l": ["jolion", "m6"], "t7": ["h3", "jolion"], "t8": ["f7", "f7x", "h7"], "t9": ["dargo"]}

def rub(n): return f"{n:,}".replace(",", " ") + " ₽"

def block(keys):
    h = ['<!--OFFICIAL-PRICES--><h2>Официальные прайсы производителя · сверено 29.10.2026</h2>',
         '<p class="lead">МЦП — максимальная цена перепродажи из PDF на haval.ru. Ниже — старые дилерские листы, это архив.</p>']
    for k in keys:
        name, date, url, rows = HAVAL[k]
        h.append(f'<h2>{name} · прайс {date}</h2><table><thead><tr><th>Комплектация</th><th>Версия</th><th>МЦП</th></tr></thead><tbody>')
        h += [f'<tr><td>{t}</td><td>{v}</td><td class="num">{rub(p)}</td></tr>' for t, v, p in rows]
        h.append(f'</tbody></table><div class="acts"><a class="btn ghost" href="{url}" target="_blank" rel="noopener">PDF с haval.ru</a></div>')
    h.append('<h2>Архив: дилерские листы</h2><!--/OFFICIAL-PRICES-->')
    return "".join(h)

def put(path, html):
    p = Path(path); s = p.read_text(encoding="utf-8")
    s2 = re.sub(r'<!--OFFICIAL-PRICES-->.*?<!--/OFFICIAL-PRICES-->', lambda m: html, s, flags=re.S)
    if s2 == s and "<!--OFFICIAL-PRICES-->" not in s:
        s2 = re.sub(r'(<div class="note">.*?</div>)', lambda m: m.group(1) + html, s, count=1, flags=re.S)
    if s2 != s: p.write_text(s2, encoding="utf-8")

T8 = ('<!--OFFICIAL-PRICES--><p class="eyebrow">TENET · прайс на 10.09.2026 · tenet.ru</p><h1>T8 — рекомендованные цены</h1>'
 '<p class="lead">Официальный прайс-лист tenet.ru (tenet_list_25.09.pdf, цены на 10.09.2026). 5 мест 1.6 186 и 2.0 197.</p>'
 '<div class="note">РЦП — рекомендованная цена перепродажи, МЦП — максимальная с учётом всех выгод. Не оферта. Скидки импортёра не обещать сверх прайса.</div>'
 '<table><thead><tr><th>Комплектация</th><th>Мотор</th><th>РЦП</th><th>МЦП с выгодами</th></tr></thead><tbody>'
 '<tr><td>Актив</td><td>1.6 DCT 186</td><td class="num">3 099 000 ₽</td><td class="num">2 899 000 ₽</td></tr>'
 '<tr><td>Прайм</td><td>1.6 DCT 186</td><td class="num">3 299 000 ₽</td><td class="num">3 099 000 ₽</td></tr>'
 '<tr><td>Прайм</td><td>2.0 197</td><td class="num">3 630 000 ₽</td><td class="num">3 480 000 ₽</td></tr>'
 '<tr><td>Ультра</td><td>2.0 197</td><td class="num">3 885 000 ₽</td><td class="num">3 735 000 ₽</td></tr></tbody></table>'
 '<div class="acts"><a class="btn ivory" href="t8-pricelist.pdf" target="_blank">PDF прайса 10.09.2026</a></div>'
 '<h2>Архив: прайс 01.09.2026 (устарел)</h2><!--/OFFICIAL-PRICES-->')

DOCS = {
 'docs/t4l-price.html': '{file:"docs/t4l-pricelist.pdf", title:"Прайс T4L · 09.10.2026", kind:"Прайс", pages:"PDF tenet.ru", note:"Официальный: РЦП 2 344 000 / 2 494 000, с выгодами 2 199 000 / 2 349 000"},\n        ',
 'docs/t8-price.html': '{file:"docs/t8-pricelist.pdf", title:"Прайс T8 · 10.09.2026", kind:"Прайс", pages:"PDF tenet.ru", note:"Официальный: 1.6 Актив 3 099 000 · Прайм 3 299 000 · 2.0 Прайм 3 630 000 · Ультра 3 885 000"},\n        ',
}
def patch_index():
    p = Path("index.html"); s = p.read_text(encoding="utf-8"); o = s
    s = s.replace('title:"Прайс T7 · 01.09.2026", kind:"Прайс", pages:"3 стр. PDF", note:"Официальный лифлет: 1.6T 150 DCT7, Актив и Прайм, 2WD и 4WD"',
                  'title:"Прайс T7 · 08.10.2026", kind:"Прайс", pages:"PDF tenet.ru", note:"Официальный: РЦП 2 805 / 3 005 / 3 010 / 3 210 тыс., с выгодами от 2 625 000"')
    s = s.replace('title:"Прайс T8 · 01.09.2026", kind:"Прайс", pages:"TENET офиц.", note:"5 мест 2WD от 3 449 000 · 7 мест 4WD от 4 099 000"',
                  'title:"Цены T8 · 10.09.2026", kind:"Прайс", pages:"HTML", note:"РЦП и МЦП по прайсу tenet.ru; прайс 01.09 — архив"')
    for f, entry in DOCS.items():
        if entry.split('"')[1] not in s:
            s = s.replace('{file:"%s"' % f, entry + '{file:"%s"' % f, 1)
    t9 = '{file:"%s", title:"Прайс TENET T9 · 08.10.2026", kind:"Прайс", pages:"PDF tenet.ru · 12 МБ", note:"РЦП: Prime 5 мест 3 949 000 · Ultra 5 мест 4 299 000 · Ultra 7 мест 4 449 000"},\n        ' % (TCDN % "dbgp144s5adg00dgqn1g")
    if "dbgp144s5adg00dgqn1g" not in s:
        s = s.replace('{file:"docs/fleet-policy-081026.pdf"', t9 + '{file:"docs/fleet-policy-081026.pdf"', 1)
    for m, k in (("t4l", "Jolion, M6"), ("t7", "H3, Jolion"), ("t8", "F7, F7x, H7"), ("t9", "Dargo")):
        s = re.sub(r'(\{file:"docs/%s-rivals-price\.html"[^}]*note:")([^"]*)"' % m,
                   lambda mm: mm.group(1) + ("Официальные прайсы haval.ru (" + k + ") · сверено 29.10.2026" if "сверено" not in mm.group(2) else mm.group(2)) + '"', s, count=1)
    if s != o: p.write_text(s, encoding="utf-8")

if __name__ == "__main__":
    for m, keys in RIVAL_PAGES.items():
        try: put(f"docs/{m}-rivals-price.html", block(keys))
        except Exception as e: print("prices:", m, e)
    try:
        p = Path("docs/t8-price.html"); s = p.read_text(encoding="utf-8")
        if "<!--OFFICIAL-PRICES-->" in s:
            s = re.sub(r'<!--OFFICIAL-PRICES-->.*?<!--/OFFICIAL-PRICES-->', lambda m: T8, s, flags=re.S)
        else:
            s = s.replace('<div class="wrap">', '<div class="wrap">' + T8, 1)
        p.write_text(s, encoding="utf-8")
    except Exception as e: print("prices: t8", e)
    patch_index()
    print("prices: ok")

# OFFER_RIVALS (КП): только модели с официальным PDF haval.ru и датой. Решение Александра 29.10.2026.
RIVAL_FIX = [
 ('price:2499000,src:"haval.ru, Оптимум 2WD, каталог с 17.08.2026"',
  'price:2499000,src:"haval.ru, прайс-лист Jolion от 14.08.2026, МЦП Оптимум 2WD"'),
 ('price:2749000,price4:3099000,trim4:"Оптимум 4WD",src:"haval.ru: от 2 549 000 с лояльным трейд-ином 200 000, здесь РРЦ без него"',
  'price:2749000,price4:3099000,trim4:"Оптимум 4WD",src:"haval.ru, прайс-лист H3 от 17.08.2026, МЦП без лояльного трейд-ина 200 000"'),
 ('price:2899000,price4:3399000,trim4:"Оптимум 2.0 4WD",src:"haval.ru от 2 899 000 Оптимум 1.5 2WD; Оптимум 4WD 3 399 000"',
  'price:2999000,price4:3399000,trim4:"Оптимум 2.0 4WD",src:"haval.ru, прайс-лист F7 от 11.08.2026, МЦП: Оптимум 1.5 2WD 2 999 000; Оптимум 2.0 4WD 3 399 000"'),
 ('price:3799000,src:"haval.ru, Премиум от 3 799 000 уже с лояльным трейд-ином 200 000"',
  'price:3999000,src:"haval.ru, прайс-лист H7 от 27.10.2026, МЦП Премиум 3 999 000 (с лояльным трейд-ином −200 000)"'),
]
def patch_rivals():
    for fn in ("offer-fn.js", "index.html"):
        p = Path(fn)
        if not p.exists(): continue
        s = p.read_text(encoding="utf-8"); o = s
        for a, b in RIVAL_FIX: s = s.replace(a, b)
        if s != o: p.write_text(s, encoding="utf-8")

if __name__ == "__main__":
    try: patch_rivals(); print("prices: rivals ok")
    except Exception as e: print("prices: rivals", e)
