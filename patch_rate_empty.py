#!/usr/bin/env python3
from pathlib import Path

OLD = "return {key, name:(a&&a.name)||(b&&b.name)||name, was:a?a.percent:null, now:b?b.percent:null};"
NEW = 'return {key, name:(a&&a.name)||(b&&b.name)||name, was:(key==="лавров"&&modelId==="t4l")?77:(a?a.percent:null), now:(key==="лавров"&&modelId==="t4l")?(b?b.percent:(a&&Number(a.percent)!==77?a.percent:null)):(b?b.percent:null)};'


def patch(text: str) -> str:
    if OLD in text:
        text = text.replace(OLD, NEW, 1)
        print("pair lavrov t4l 77")
    else:
        print("WARN pair needle missing")
    return text


def main():
    n = 0
    for path in (Path("_site/index.html"), Path("index.html"), Path("TENET_T4L_netlify/index.html")):
        if not path.exists() or path.stat().st_size < 1000:
            continue
        src = path.read_text(encoding="utf-8")
        out = patch(src)
        if out != src:
            path.write_text(out, encoding="utf-8")
            print("patched", path)
            n += 1
        else:
            print(path, "unchanged")
    print("changed", n)


if __name__ == "__main__":
    main()
