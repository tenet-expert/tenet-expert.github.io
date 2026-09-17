#!/usr/bin/env python3
"""Lavrov T4L first exam stays 77 in «было»; later 96 goes to «стало»."""
from pathlib import Path
import json

PAIR_OLD = (
    "      function pair(key, name, modelId){\n"
    "        const a=bestMap(1, modelId)[key];\n"
    "        const b=bestMap(2, modelId)[key];\n"
    "        return {key, name:(a&&a.name)||(b&&b.name)||name, was:a?a.percent:null, now:b?b.percent:null};\n"
    "      }"
)

PAIR_NEW = """      function pair(key, name, modelId){
        const seedRows=(typeof RATE_SEED!==\"undefined\" && Array.isArray(RATE_SEED))?RATE_SEED:[];
        const seed=seedRows.find(s=>s && Number(s.exam||1)===1 && (s.model||\"t4l\")===modelId && (typeof staffKey===\"function\"?staffKey(s.surname||s.display):String(s.surname||\"\").toLowerCase())===key);
        const a=bestMap(1, modelId)[key];
        const b=bestMap(2, modelId)[key];
        const was=seed && seed.percent!=null ? Number(seed.percent) : (a?a.percent:null);
        let now=b?b.percent:null;
        if(seed && a && Number(a.percent)!=Number(seed.percent)){
          if(now==null || Number(a.percent)>Number(now||0)) now=a.percent;
        }
        return {key, name:(seed&&seed.display)||(a&&a.name)||(b&&b.name)||name, was:was, now:now};
      }"""

RATE_ALL_OLD = "      const local=Object.values(state.locks||{});\n      const all=[...remoteLocks, ...local].filter(r=>r && r.surname);"
RATE_ALL_NEW = """      const seed=(typeof RATE_SEED!==\"undefined\" && Array.isArray(RATE_SEED))?RATE_SEED:[];
      const cached=(typeof loadCloudCache===\"function\")?loadCloudCache():[];
      const local=Object.values(state.locks||{});
      const merged=(typeof mergeCloud===\"function\")
        ? mergeCloud(mergeCloud(seed, cached), mergeCloud(remoteLocks||[], local))
        : seed.concat(cached, remoteLocks||[], local);
      const all=merged.filter(r=>r && r.surname);"""

FLUSH_OLD = """        const rem=(remoteLocks||[]).find(x=>isExamRow(x) && x.surname===rec.surname && x.model===rec.model && Number(x.exam||1)===Number(rec.exam||1));
        if(!rem || rem.status===\"running\" || Number(rem.percent||0)<Number(rec.percent||0)){
          await upsertLock(Object.assign({}, rec, {status:\"done\"}));
        }"""

FLUSH_NEW = """        const rem=(remoteLocks||[]).find(x=>isExamRow(x) && x.surname===rec.surname && x.model===rec.model && Number(x.exam||1)===Number(rec.exam||1));
        const seedHit=(typeof RATE_SEED!==\"undefined\" && Array.isArray(RATE_SEED))
          ? RATE_SEED.find(s=>s && !s.type && Number(s.exam||1)===1 && s.model===rec.model && (s.surname===rec.surname || (typeof staffKey===\"function\" && staffKey(s.surname)===staffKey(rec.surname))))
          : null;
        if(seedHit && Number(rec.exam||1)===1 && Number(rec.percent)!=Number(seedHit.percent)){
          if(Number(rec.percent||0)>Number(seedHit.percent||0)){
            await upsertLock(Object.assign({}, rec, {exam:2, status:\"done\"}));
          }
          continue;
        }
        if(rem && (rem.locked || rem.official) && Number(rec.exam||1)===1){
          if(Number(rec.percent||0)!=Number(rem.percent||0) && Number(rec.percent||0)>Number(rem.percent||0)){
            await upsertLock(Object.assign({}, rec, {exam:2, status:\"done\"}));
          }
          continue;
        }
        if(!rem || rem.status===\"running\" || Number(rem.percent||0)<Number(rec.percent||0)){
          await upsertLock(Object.assign({}, rec, {status:\"done\"}));
        }"""


def seed_js():
    for p in (Path(\"rating-seed.json\"), Path(__file__).with_name(\"rating-seed.json\")):
        if p.exists():
            data = json.loads(p.read_text(encoding=\"utf-8\"))
            return \"    const RATE_SEED = \" + json.dumps(data, ensure_ascii=False) + \";\"
    return \"\"


def patch(text: str) -> str:
    if PAIR_OLD in text:
        text = text.replace(PAIR_OLD, PAIR_NEW, 1)
        print(\"pair() official first exam\")
    else:
        print(\"WARN: pair() not found\")
    if RATE_ALL_OLD in text:
        text = text.replace(RATE_ALL_OLD, RATE_ALL_NEW, 1)
        print(\"rate() merge seed\")
    if FLUSH_OLD in text:
        text = text.replace(FLUSH_OLD, FLUSH_NEW, 1)
        print(\"flushLocalDone protect seed\")
    js = seed_js()
    if js and \"const RATE_SEED =\" in text:
        text2, n = __import__(\"re\").subn(
            r\"    const RATE_SEED = \\[.*?\\];\",
            js,
            text,
            count=1,
        )
        if n:
            text = text2
            print(\"RATE_SEED refreshed\")
    return text


def main():
    n = 0
    for path in (
        Path(\"_site/index.html\"),
        Path(\"index.html\"),
        Path(\"TENET_T4L_netlify/index.html\"),
    ):
        if not path.exists() or path.stat().st_size < 1000:
            continue
        src = path.read_text(encoding=\"utf-8\")
        out = patch(src)
        if out != src:
            path.write_text(out, encoding=\"utf-8\")
            print(\"patched\", path)
            n += 1
        else:
            print(path, \"unchanged\")
    print(\"changed\", n)


if __name__ == \"__main__\":
    main()
