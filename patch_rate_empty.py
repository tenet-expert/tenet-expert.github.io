#!/usr/bin/env python3
"""Rating always shows seed results; cloud cannot wipe the board empty."""
from pathlib import Path
import re

RATE_ALL_OLD = "      const local=Object.values(state.locks||{});\n      const all=[...remoteLocks, ...local].filter(r=>r && r.surname);"
RATE_ALL_NEW = """      const seed=(typeof RATE_SEED!==\"undefined\" && Array.isArray(RATE_SEED))?RATE_SEED:[];
      const cached=(typeof loadCloudCache===\"function\")?loadCloudCache():[];
      const local=Object.values(state.locks||{});
      const merged=(typeof mergeCloud===\"function\")
        ? mergeCloud(mergeCloud(seed, cached), mergeCloud(remoteLocks||[], local))
        : seed.concat(cached, remoteLocks||[], local);
      const all=merged.filter(r=>r && r.surname);"""

REFRESH_OLD = """    async function refreshLocks(){
      try {
        remoteLocks = await pullList();
        syncOk = true;
        saveCloudCache(remoteLocks);
        await flushLocalDone();
      } catch(e) {
        syncOk = false;
        remoteLocks = remoteLocks || [];
      }
    }"""

REFRESH_NEW = """    async function refreshLocks(){
      const seed=(typeof RATE_SEED!==\"undefined\" && Array.isArray(RATE_SEED))?RATE_SEED:[];
      const cached=(typeof loadCloudCache===\"function\")?loadCloudCache():[];
      let base=seed.concat(cached, remoteLocks||[]);
      if(typeof mergeCloud===\"function\") base=mergeCloud(mergeCloud(seed, cached), remoteLocks||[]);
      try {
        const extra = await pullList();
        remoteLocks = typeof mergeCloud===\"function\" ? mergeCloud(base, extra) : base.concat(extra||[]);
        if(remoteLocks && remoteLocks.length) syncOk = true;
        if(typeof saveCloudCache===\"function\") saveCloudCache(remoteLocks);
        await flushLocalDone();
      } catch(e) {
        syncOk = false;
        remoteLocks = base;
      }
    }"""

INIT_MARK = "    function mergeCloud(base, extra){"
INIT_AFTER = """    function bootRating(){
      try{
        const seed=(typeof RATE_SEED!==\"undefined\" && Array.isArray(RATE_SEED))?RATE_SEED:[];
        const cached=(typeof loadCloudCache===\"function\")?loadCloudCache():[];
        remoteLocks = typeof mergeCloud===\"function\" ? mergeCloud(seed, mergeCloud(cached, remoteLocks||[])) : seed.concat(cached, remoteLocks||[]);
      }catch(e){
        if(typeof RATE_SEED!==\"undefined\" && Array.isArray(RATE_SEED) && !(remoteLocks&&remoteLocks.length)) remoteLocks=RATE_SEED.slice();
      }
    }
    bootRating();
    function mergeCloud(base, extra){"""


def patch(text: str) -> str:
    if RATE_ALL_OLD in text:
        text = text.replace(RATE_ALL_OLD, RATE_ALL_NEW, 1)
        print("rate() merge seed")
    elif "const seed=(typeof RATE_SEED" not in text:
        text2, n = re.subn(
            r"const local=Object\\.values\\(state\\.locks\\|\\|\\{\\}\\);\\s*const all=\\[\\.\\.\\.remoteLocks, \\.\\.\\.local\\]\\.filter\\(r=>r && r\\.surname\\);",
            RATE_ALL_NEW.strip(),
            text,
            count=1,
        )
        if n:
            text = text2
            print("rate() merge seed via regex")
        else:
            print("WARN: rate() all= not found")
    if REFRESH_OLD in text:
        text = text.replace(REFRESH_OLD, REFRESH_NEW, 1)
        print("refreshLocks merge seed")
    elif "async function refreshLocks" in text and "mergeCloud(mergeCloud(seed, cached), remoteLocks" not in text:
        text2, n = re.subn(
            r"async function refreshLocks\\(\\)\\{[\\s\\S]*?remoteLocks = remoteLocks \\|\\| \\[\\];\\n      \\}\\n    \",
            REFRESH_NEW,
            text,
            count=1,
        )
        if n:
            text = text2
            print("refreshLocks merge seed via regex")
        else:
            print("WARN: refreshLocks not found")
    if "function bootRating()" not in text and INIT_MARK in text:
        text = text.replace(INIT_MARK, INIT_AFTER, 1)
        print("bootRating")
    if '"лавров"' in text and "percent\": 77" not in text and "percent: 77" not in text:
        print("WARN: Lavrov 77 missing from this file")
    return text


def main():
    n = 0
    for path in (
        Path("_site/index.html"),
        Path("index.html"),
        Path("TENET_T4L_netlify/index.html"),
    ):
        if not path.exists() or path.stat().st_size < 1000:
            continue
        src = path.read_text(encoding="utf-8")
        out = patch(src)
        if out != src:
            path.write_text(out, encoding="utf-8")
            print("patched", path, path.stat().st_size)
            n += 1
        else:
            print(path, "unchanged")
    print("changed", n)


if __name__ == "__main__":
    main()
