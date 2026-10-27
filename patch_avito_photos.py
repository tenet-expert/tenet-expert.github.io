#!/usr/bin/env python3
"""Блок «Фото для Авито» в чек-листе дежурного.

Чек-лист дежурного подменяется на сборке (patch_duty_vert.py берёт duty()
из duty-ui-snippet.js). pages.yml этим токеном не правится, поэтому шаг
подключается в конце patch_issue.py — он последний в сборке Pages.

Список машин не зашивается в страницу: утренний пуш заменяет photos-needed.json,
а чек-лист читает его через fetch('photos-needed.json?'+Date.now()).
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
TAG = '<script src="avito-photos.js?v=5"></script>'
MARKER = "avito-photos.js"


def ensure_script(html: str) -> str:
    html = html.replace('<script src="avito-photos.js?v=1"></script>', TAG)
    html = html.replace('<script src="avito-photos.js?v=2"></script>', TAG)
    html = html.replace('<script src="avito-photos.js?v=3"></script>', TAG)
    html = html.replace('<script src="avito-photos.js?v=4"></script>', TAG)
    if MARKER in html:
        return html
    if "</body>" in html:
        return html.replace("</body>", TAG + "\n</body>", 1)
    return html + "\n" + TAG + "\n"


def main():
    site = ROOT / "_site"
    site.mkdir(exist_ok=True)
    src_json = ROOT / "photos-needed.json"
    src_js = ROOT / "avito-photos.js"
    if src_json.is_file():
        shutil.copyfile(src_json, site / "photos-needed.json")
        print("avito-photos: copied photos-needed.json", src_json.stat().st_size)
    else:
        print("avito-photos: photos-needed.json missing")
    if src_js.is_file():
        shutil.copyfile(src_js, site / "avito-photos.js")
        print("avito-photos: copied avito-photos.js", src_js.stat().st_size)
    else:
        print("avito-photos: avito-photos.js missing")
    for p in (ROOT / "index.html", site / "index.html"):
        if not p.is_file() or p.stat().st_size < 1000:
            print("avito-photos: skip", p)
            continue
        raw = p.read_text(encoding="utf-8")
        nxt = ensure_script(raw)
        if nxt != raw:
            p.write_text(nxt, encoding="utf-8")
            print("avito-photos: script tag", p)
        else:
            print("avito-photos: script already in", p)


if __name__ == "__main__":
    main()
