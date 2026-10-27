#!/usr/bin/env python3
"""Build spec-invoice.json (VIN list of «Спец инвойс» cars) from Logicstars CSV exports.

Run by «Склад» after every Logicstars CSV export, from the repo root, and commit
spec-invoice.json together with stock-part1/part2:

    python3 scripts/spec_invoice.py --csv-dir ~/Downloads [--dry-run]

Spec rule (27.10.2026, А. Леонтьев: «по цене закупки ставь везде метку спец,
как правило такая машина в закупе дешевле на 15-20%»):
  * «Вид продажи» = «Спец. закупочная цена» (tab «Непроданные»)  -> spec;
  * otherwise purchase cost («Стоимость») / РРЦ <= 0.90            -> spec;
  * 0.90 < cost/РРЦ < 0.95                                          -> borderline, NOT flagged;
  * >= 0.95 (regular dealer price is 0.95-0.97 of РРЦ)              -> regular.
«Отложенные продажи» has no «Вид продажи» and no РРЦ, so РРЦ is taken from the
«Непроданные» rows of the same model+trim, then from stock.json / TENET+ list by VIN.
Only VINs are written: the purchase cost is never stored in the repo or on the site.
"""
import argparse, csv, json, re, sys
from datetime import datetime
from pathlib import Path

SPEC_MAX = 0.90
REGULAR_MIN = 0.95
SPEC_MARK = "спец. закупоч"  # LS cuts the value to «Спец. закупочная цен»
UNSOLD = ("Непроданные автомобили дилера.csv", "Непроданные автомобили дилера (1).csv", "Непроданные автомобили дилера (2).csv")
CORP = ("Корпоративные автомобили.csv",)
DEFERRED = ("Отложенные продажи.csv", "Отложенные продажи (1).csv", "Отложенные продажи (2).csv")


def rows(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8-sig") as f:
        return [r for r in csv.reader(f, delimiter=";") if r and r[0].strip().isdigit()]


def money(s):
    s = re.sub(r"[^\d,]", "", str(s or "")).replace(",", ".")
    try:
        return int(float(s)) if s else 0
    except ValueError:
        return 0


def site_rrc():
    out = {}
    for name in ("stock.json", "stock-part1.json", "stock-part2.json"):
        p = Path(name)
        if p.exists():
            try:
                for c in json.loads(p.read_text(encoding="utf-8")).get("cars") or []:
                    if c.get("vin") and c.get("rrc"):
                        out.setdefault(c["vin"], int(c["rrc"]))
            except Exception:
                pass
    p = Path("patch_fleet_dcti.py")
    if p.exists():
        for m in re.finditer(r'\{"vin": "(\w+)".*?"rrc": (\d+)\}', p.read_text(encoding="utf-8")):
            out.setdefault(m.group(1), int(m.group(2)))
    return out


def collect(d):
    cars, trim_rrc = {}, {}
    for f in UNSOLD:
        for r in rows(d / f):
            if len(r) < 21:
                continue
            cars[r[2]] = dict(model=r[6], trim=r[7], rrc=money(r[19]), cost=money(r[20]), vid=r[14], tab="unsold")
            if money(r[19]):
                trim_rrc[(r[6], r[7])] = money(r[19])
    for f in CORP:
        for r in rows(d / f):
            if len(r) < 17:
                continue
            cars.setdefault(r[1], dict(model=r[4], trim=r[5], rrc=money(r[11]), cost=money(r[12]), vid=r[16], tab="corp"))
    by_vin = site_rrc()
    for f in DEFERRED:
        for r in rows(d / f):
            if len(r) < 9:
                continue
            rrc = trim_rrc.get((r[4], r[5])) or by_vin.get(r[1]) or 0
            cars.setdefault(r[1], dict(model=r[4], trim=r[5], rrc=rrc, cost=money(r[8]), vid="", tab="deferred"))
    return cars


def classify(c):
    if SPEC_MARK in (c.get("vid") or "").lower():
        return "spec"
    if not c["rrc"] or not c["cost"]:
        return "unknown"
    k = c["cost"] / c["rrc"]
    if k <= SPEC_MAX:
        return "spec"
    if k < REGULAR_MIN:
        return "borderline"
    return "regular"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv-dir", default=str(Path.home() / "Downloads"))
    ap.add_argument("--out", default="spec-invoice.json")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    d = Path(a.csv_dir).expanduser()
    cars = collect(d)
    if len(cars) < 40:
        sys.exit(f"too few cars in {d}: {len(cars)} — spec-invoice.json not written")
    res = {v: classify(c) for v, c in cars.items()}
    spec = sorted(v for v, k in res.items() if k == "spec")
    border = sorted(v for v, k in res.items() if k == "borderline")
    unknown = sorted(v for v, k in res.items() if k == "unknown")
    out = {
        "updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "source": "Logicstars CSV: Непроданные (Вид продажи) + Отложенные/Корпоративные (закупка/РРЦ)",
        "rule": f"Вид продажи «Спец. закупочная цена» или закупка/РРЦ <= {SPEC_MAX:.2f}; {SPEC_MAX:.2f}–{REGULAR_MIN:.2f} — пограничные, без метки",
        "vins": spec,
        "borderline": border,
    }
    print("cars", len(cars), "spec", len(spec), "borderline", len(border), "unknown", len(unknown))
    for v in border:
        c = cars[v]
        print("  borderline", v, c["model"], c["trim"], round(c["cost"] / c["rrc"], 3))
    for v in unknown:
        print("  unknown (no РРЦ/cost)", v, cars[v]["model"], cars[v]["trim"])
    if not a.dry_run:
        Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("wrote", a.out)


if __name__ == "__main__":
    main()
