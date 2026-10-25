#!/usr/bin/env python3
"""Sync trading-terms data in index.html from the canonical terms-calc-data.js.

Source of truth: sanchesefn/tenet-expert@main terms-calc-data.js (updated by the
ту-google-08 / ту-google-14 syncs). The live page is the root index.html (it is
copied over _site/index.html during the build), so the data constants embedded
there are replaced in place. Site-only code (EXCL_FIX, KM_FORK, kmBand, pangoOf,
stock list, TUNE_RUBBER, FLEET_BFS, ...) is left untouched; KM_MODELS rows that
exist only on the site (e.g. T9 7-seat) are kept. Any doubt -> no change.
"""
import os, re, shutil, subprocess, sys, tempfile, urllib.request
from pathlib import Path

SRC = os.environ.get("TERMS_SRC",
      "https://raw.githubusercontent.com/sanchesefn/tenet-expert/main/terms-calc-data.js")
DATA = ["TERMS_DATE", "KM_CORRIDOR", "TERMS_BONUS", "TERMS_MPT", "TERMS_INV",
        "PANGO_FIX", "PANGO_BUNDLE", "PANGO_RATE_A", "PANGO_RATE_B", "PANGO_NSS",
        "PANGO_VIN",
        "TERMS_PRIO", "KM_MODELS", "PRIO_VINS", "KM_DC_DEF", "KM_BANKS",
        "KM_BANK_MONTHS", "KM_BANK_RATES"]
TARGETS = [Path("index.html"), Path("_site/index.html")]


def span(text, name):
    """(start, end) of '    const NAME = ...;' at top level, bracket/string aware."""
    m = re.search(r"^    const " + name + r" = ", text, re.M)
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


ROW = re.compile(r'^\s*\{id:"([^"]+)".*$', re.M)


def merge_models(canon, site):
    c_rows = [(m.group(1), m.group(0).rstrip().rstrip(",") + ",") for m in ROW.finditer(canon)]
    s_rows = [(m.group(1), m.group(0).rstrip().rstrip(",") + ",") for m in ROW.finditer(site)]
    ids = {i for i, _ in c_rows}
    out = list(c_rows)
    prev = None
    for i, line in s_rows:
        if i not in ids:
            pos = next((k + 1 for k, (j, _) in enumerate(out) if j == prev), len(out))
            out.insert(pos, (i, line))
            ids.add(i)
            print("keep site-only model", i)
        prev = i
    lines = [l for _, l in out]
    lines[-1] = lines[-1].rstrip(",")
    return "    const KM_MODELS = [\n" + "\n".join(lines) + "\n    ];"


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


def ensure_t9(text):
    """T9 specials added 15.10 in the trade-terms sheet. Keep them if the remote source is behind."""
    if "tt9p:{cash:3500000" not in text and "t8u4:{cash:3300000,ti:3200000}" in text:
        text = text.replace(
            "t8u4:{cash:3300000,ti:3200000}",
            "t8u4:{cash:3300000,ti:3200000},\n      tt9p:{cash:3500000,ti:3400000},\n      tt9u:{cash:3800000,ti:3500000}",
            1,
        )
    needle = '{model:"T8",trim:"Ultra 4WD",price:"3 300 нал, 3 200 ТИ"}'
    if "3 500 нал, 3 400 ТИ" not in text and needle in text:
        text = text.replace(
            needle,
            needle + ',\n      {model:"T9",trim:"Prime 5 мест 4WD",price:"3 500 нал, 3 400 ТИ"},\n      {model:"T9",trim:"Ultra 5 мест 4WD",price:"3 800 нал, 3 500 ТИ"}',
            1,
        )
    return text


PLUS_ROW = re.compile(r'\{model:"(L4|L6)",trim:"([^"]*)"[^{}]*\}')


def move_plus_specs(text):
    """TENET+ specials (L4/L6) belong in TERMS_INV_PLUS ("Спец · TENET+"), not in
    TERMS_INV ("Спец · TENET"). The canonical source lists e.g. L4 Style in TERMS_INV,
    so after each sync move such rows over (canonical price wins for the same trim).
    PANGO_FIX is untouched, so the PANGO calculator keeps the same price."""
    s_inv = span(text, "TERMS_INV")
    s_plus = span(text, "TERMS_INV_PLUS")
    if not s_inv or not s_plus:
        return text
    inv = text[s_inv[0]:s_inv[1]]
    rows = [m.group(0) for m in PLUS_ROW.finditer(inv)]
    if not rows:
        return text
    inv_lines = [l for l in inv.split("\n") if not PLUS_ROW.search(l)]
    for k in range(len(inv_lines) - 1, -1, -1):
        if inv_lines[k].strip().startswith("{"):
            inv_lines[k] = inv_lines[k].rstrip().rstrip(",")
            break
    new_inv = "\n".join(inv_lines)
    plus = text[s_plus[0]:s_plus[1]]
    keep = [m.group(0) for m in PLUS_ROW.finditer(plus)]
    have = {PLUS_ROW.match(r).group(1) + "|" + PLUS_ROW.match(r).group(2): r for r in keep}
    for r in rows:
        key = PLUS_ROW.match(r).group(1) + "|" + PLUS_ROW.match(r).group(2)
        if key in have:
            keep[keep.index(have[key])] = r
        else:
            keep.insert(0, r)
        have[key] = r
    keep.sort(key=lambda r: (PLUS_ROW.match(r).group(1), 0))
    new_plus = "    const TERMS_INV_PLUS = [\n" + ",\n".join("      " + r for r in keep) + "\n    ];"
    a, b = (s_inv, s_plus) if s_inv[0] < s_plus[0] else (s_plus, s_inv)
    na, nb = (new_inv, new_plus) if s_inv[0] < s_plus[0] else (new_plus, new_inv)
    return text[:a[0]] + na + text[a[1]:b[0]] + nb + text[b[1]:]


def ensure_local(text):
    text = ensure_t9(text)
    text = text.replace(
        'vin:"EDEDD24B2SG003755",trim:"Ультра 4WD",year:"2025",color:"Светло-серый",extra:"",pay:500,bonus:3000,reserved:true,seller:"Спицын"',
        'vin:"EDEDD24B2SG003755",trim:"Ультра 4WD",year:"2025",color:"Светло-серый",extra:"",pay:500,bonus:3000,sold:true,seller:"Спицын"',
        1,
    )
    if "l4e:{cash:2350000" not in text and "tt9u:{cash:3800000,ti:3500000}" in text:
        text = text.replace(
            "tt9u:{cash:3800000,ti:3500000}",
            "tt9u:{cash:3800000,ti:3500000},\n      l4e:{cash:2350000,ti:2250000},\n      l6u:{cash:2600000,ti:2450000}",
            1,
        )
    text = move_plus_specs(text)
    return text


def main():
    try:
        canon = urllib.request.urlopen(SRC, timeout=30).read().decode("utf-8")
    except Exception as e:
        print("terms sync: fetch failed", e)
        return 0
    if len(canon) < 15000 or "PLACEHOLDER" in canon:
        print("terms sync: source looks wrong, size", len(canon))
        return 0
    blocks = {}
    for n in DATA:
        s = span(canon, n)
        if not s:
            print("terms sync: missing", n, "in source -> skip")
            return 0
        blocks[n] = canon[s[0]:s[1]]
    if len(ROW.findall(blocks["KM_MODELS"])) < 10:
        print("terms sync: too few KM_MODELS rows -> skip")
        return 0
    for p in TARGETS:
        if not p.exists() or p.stat().st_size < 100000:
            continue
        src = p.read_text(encoding="utf-8")
        out = src
        for n in DATA:
            s = span(out, n)
            if not s:
                print(p, "anchor missing", n, "-> skip file")
                out = None
                break
            new = merge_models(blocks[n], out[s[0]:s[1]]) if n == "KM_MODELS" else blocks[n]
            out = out[:s[0]] + new + out[s[1]:]
        if out is None:
            continue
        out = ensure_local(out)
        if out == src:
            print(p, "terms already in sync")
            continue
        if not js_ok(out):
            print(p, "JS check failed -> not written")
            continue
        p.write_text(out, encoding="utf-8")
        m = re.search(r'const TERMS_DATE = "([^"]*)"', out)
        print(p, "terms synced, TERMS_DATE", m.group(1) if m else "?")
    return 0


if __name__ == "__main__":
    sys.exit(main())
