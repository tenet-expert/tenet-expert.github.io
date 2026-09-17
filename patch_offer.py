from pathlib import Path
import base64

ROOT = Path(".")
src = ROOT / "offer-fn.js"
fn = src.read_text(encoding="utf-8") if src.exists() else ""

css = """
.hub-card[data-go="offer"]::before{
  background-image:url("hub/offer.jpg?v=2");
  background-position:50% 48%;
  background-size:cover;
}
.hub-card[data-offer-tab="new"]::before{
  background-image:url("hub/offer-new.jpg?v=2");
  background-position:48% 52%;
  background-size:cover;
}
.hub-card[data-offer-tab="service"]::before{
  background-image:url("hub/offer-service.jpg?v=2");
  background-position:50% 46%;
  background-size:cover;
}
.hub-card[data-offer-tab="lease"]::before{
  background-image:url("hub/offer-lease.jpg?v=2");
  background-position:50% 58%;
  background-size:cover;
}
.offer-sheet{
  white-space:pre-wrap;
  font:13px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  background:#fff;
  border:1px solid var(--border);
  border-radius:12px;
  padding:14px;
  margin:0 0 12px;
}
"""

def write_jpgs():
    names = ["offer", "offer-new", "offer-service", "offer-lease"]
    dirs = [ROOT / "hub", ROOT / "_site" / "hub", ROOT / "hub_b64"]
    for name in names:
        raw = None
        for d in dirs:
            for cand in (d / f"{name}.jpg.b64", d / f"{name}.b64"):
                if cand.exists() and cand.stat().st_size > 1000:
                    raw = base64.b64decode(cand.read_text(encoding="utf-8").strip())
                    break
            if raw:
                break
        jpg = ROOT / "hub" / f"{name}.jpg"
        if not raw and jpg.exists():
            raw = jpg.read_bytes()
        if not raw:
            print("no preview", name)
            continue
        for out in (ROOT / "hub" / f"{name}.jpg", ROOT / "_site" / "hub" / f"{name}.jpg"):
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(raw)
            print("jpg", out, out.stat().st_size)

write_jpgs()

HUB_OLD = '        ["gibdd","Г","Проверки ГИБДД","ФССП, залоги, банкроты"]'
HUB_NEW = HUB_OLD + '\n        ,["offer","КП","Коммерческое предложение","Новый а/м, сервис и лизинг"]'

NAV_OLD = 'const extra={terms:"Условия",calc:"Калькулятор",stock:"Склад",docs:"Документы",epts:"ЭПТС",duty:"Чек-лист",gibdd:"ГИБДД"};'
NAV_NEW = 'const extra={terms:"Условия",calc:"Калькулятор",stock:"Склад",docs:"Документы",epts:"ЭПТС",duty:"Чек-лист",gibdd:"ГИБДД",offer:"КП"};'

MAP_OLD = "const map={login,hub,home,study,quiz:brief,play,rate,hist:rate,review,terms,calc,stock,docs,epts,duty,gibdd};"
MAP_NEW = "const map={login,hub,home,study,quiz:brief,play,rate,hist:rate,review,terms,calc,stock,docs,epts,duty,gibdd,offer};"

BIND_OLD = '      document.querySelectorAll("[data-go]").forEach(b=>b.onclick=()=>{'
BIND_NEW = '      if(typeof offerBind==="function") offerBind();\n      document.querySelectorAll("[data-go]").forEach(b=>b.onclick=()=>{'

CSS_OLD_GRAD = """.hub-card[data-go=\"offer\"]::before{\n  background-image:linear-gradient(135deg,#1f4e79 0%,#8d6e3c 55%,#e8d5b0 100%);\n  background-position:50% 50%;\n}"""

for p in (Path("index.html"), Path("_site/index.html")):
    if not p.exists() or p.stat().st_size < 1000:
        print("skip", p)
        continue
    html = p.read_text(encoding="utf-8")
    if CSS_OLD_GRAD in html:
        html = html.replace(CSS_OLD_GRAD, css.strip(), 1)
        print(p, "css upgrade")
    elif 'hub/offer.jpg' not in html:
        html = html.replace("</style>", css + "\n</style>", 1)
        print(p, "css")
    if '["offer","КП"' not in html:
        html = html.replace(HUB_OLD, HUB_NEW, 1)
        print(p, "hub card")
    html = html.replace(NAV_OLD, NAV_NEW, 1)
    html = html.replace(MAP_OLD, MAP_NEW, 1)
    if "offerBind()" not in html:
        html = html.replace(BIND_OLD, BIND_NEW, 1)
        print(p, "bind")
    if "function offer()" not in html and fn:
        anchor = "    function docs(){"
        if anchor in html:
            html = html.replace(anchor, fn + "\n    function docs(){", 1)
            print(p, "functions")
        else:
            html = html.replace("</script>", fn + "\n</script>", 1)
            print(p, "functions at script end")
    p.write_text(html, encoding="utf-8")
    print("offer patched", p, p.stat().st_size)
