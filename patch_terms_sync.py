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
