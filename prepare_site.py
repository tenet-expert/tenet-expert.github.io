from pathlib import Path
import json, re, urllib.parse, urllib.request

parts = sorted(Path("parts").glob("p*.txt"))
if parts:
    html = "".join(p.read_text() for p in parts)
else:
    html = Path("TENET_T4L_netlify/index.html").read_text()

html = html.replace(
    'let view = state.surname ? "home" : "login";',
    'let view = (state.surname && state.authed) ? (state.section || "hub") : "login";'
)
html = html.replace(
    'if(state.surname && userRun() && !done)',
    'if(state.authed && state.surname && userRun() && !done)'
)
html = html.replace(
    'stopTick(); state.surname=""; state.display=""; save();',
    'stopTick(); state.surname=""; state.display=""; state.authed=false; save();'
)

login = Path("login-fn.js")
if login.exists():
    extra = login.read_text()
    a = html.find("    function login(){")
    b = html.find("    function homeLeadText(){")
    if a >= 0 and b > a:
        html = html[:a] + extra + html[b:]

ask = Path("ask-pin-fn.js")
if ask.exists():
    extra = ask.read_text()
    if not extra.endswith("\n"):
        extra += "\n"
    needle = '      const logout=document.getElementById("logout");'
    if needle in html:
        html = html.replace(needle, extra + needle, 1)
    else:
        print("askPin bind not found")

old_login = '''const doLogin=document.getElementById("doLogin");\n      if(doLogin) doLogin.onclick=async()=>{\n        const v=(document.getElementById("surname").value||"").trim();\n        const err=document.getElementById("loginErr");\n        if(v.length<2){ err.textContent="Введите фамилию."; return; }\n        state.surname=norm(v); state.display=v.replace(/\\s+/g," "); save();\n        await refreshLocks();\n        if(userRun()){ resumeExam(userRun()); return; }\n        view="home"; render();\n      };'''
new_login = '''const doLogin=document.getElementById("doLogin");\n      if(doLogin) doLogin.onclick=async()=>{\n        const v=(document.getElementById("surname").value||"").trim();\n        const pinRaw=((document.getElementById("loginPin")||{}).value||"").trim();\n        const err=document.getElementById("loginErr");\n        if(!err) return;\n        if(v.length<2){ err.textContent="Введите фамилию."; return; }\n        if(!pinRaw){ err.textContent="Введите личный код от РОП."; return; }\n        err.textContent="Проверяю код…";\n        const sn=norm(v);\n        const baked=await bakedPin(sn);\n        await refreshLocks();\n        const rec=(remoteLocks||[]).find(x=>x && x.type==="login" && x.surname===sn);\n        const cloud=rec && rec.code;\n        const ok=pinEq(pinRaw, cloud) || pinEq(pinRaw, baked);\n        if(!ok){\n          if(!syncOk && !baked){ err.textContent="Нет связи с сервером кодов. Откройте сайт в Chrome или Safari — не из Telegram — и повторите."; return; }\n          if(!cloud && !baked){ err.textContent="Код для этой фамилии ещё не выдан. Нажмите «Запросить код у РОП»."; return; }\n          err.textContent="Неверный код. Только цифры, без пробелов. Откройте сайт в Chrome / Safari, не из Telegram."; return;\n        }\n        state.surname=sn; state.display=v.replace(/\\s+/g," "); state.authed=true; save();\n        if(userRun()){ resumeExam(userRun()); return; }\n        view="home"; render();\n      };'''
if old_login in html:
    html = html.replace(old_login, new_login)
else:
    print("doLogin block not found (ok if already patched in source)")

patch = Path("study-fn.js")
if patch.exists():
    extra = patch.read_text()
    a = html.find("    function study(){")
    b = html.find("    function brief(){")
    if a >= 0 and b > a:
        html = html[:a] + extra + html[b:]

unlock = Path("unlock-fn.js")
if unlock.exists():
    extra = unlock.read_text()
    a = html.find("    function tryUnlock(code){")
    b = html.find("    function compactPaper(){")
    if a >= 0 and b > a:
        html = html[:a] + extra + html[b:]

css_path = Path("theme.css")
if css_path.exists() and css_path.stat().st_size > 1000:
    css = css_path.read_text()
    a = html.find("<style>")
    b = html.find("</style>") + 8
    if a >= 0 and b > a:
        html = html[:a] + "<style>\n" + css + "\n</style>" + html[b:]
else:
    print("skip tiny/missing theme.css")

EXTRA_CSS = """
.terms-col{max-width:1080px}
.terms-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:8px 0 22px}
.term-card{border:1px solid var(--border);background:#fff;border-radius:12px;padding:12px 14px;box-shadow:var(--shadow)}
.term-card b{display:block;font-size:15px;letter-spacing:-.02em}
.term-card .num{font-weight:800;margin-top:6px;font-variant-numeric:tabular-nums}
.term-card small{display:block;color:var(--muted);font-size:12px;line-height:1.35;margin-top:6px}
.km-line{margin:4px 0 12px}
.km-line .stock-h{margin:10px 0 6px}
.km-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:8px;margin:0}
.km-grid .chip{width:100%;text-align:left;white-space:normal;line-height:1.25;padding:10px 12px;min-height:54px}
.km-grid .chip small{display:block;opacity:.72;font-size:11px;font-weight:600;margin-top:3px}
.check-row{display:flex;gap:12px;align-items:center;margin-top:14px;padding:14px 16px;border:1px solid var(--border);border-radius:12px;background:#fff;cursor:pointer}
.check-row input{width:22px;height:22px;accent-color:var(--primary);flex:0 0 22px}
.check-row span{font-size:15px;font-weight:600;line-height:1.3}
.km-layout{display:grid;gap:14px;margin-top:8px}
@media(min-width:960px){.km-layout{grid-template-columns:minmax(0,1.05fr) minmax(300px,.95fr);align-items:start}}
.km-right{display:flex;flex-direction:column;gap:14px}
.stock-side{max-height:520px;overflow:auto}
.stock-h{margin:12px 0 8px;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:700}
.stock-car{width:100%;text-align:left;border:1px solid var(--border);background:#fff;border-radius:12px;padding:10px 12px;margin:0 0 8px;display:block}
.stock-car.on{border-color:var(--fg);box-shadow:0 0 0 1px var(--fg)}
.stock-car.prio{background:#fff6d8;border-color:#e0b84a}
.stock-car.prio.on{border-color:#b88912;box-shadow:0 0 0 1px #b88912}
.stock-car b{display:block;font-size:13px;letter-spacing:-.02em}
.stock-car .vin{display:block;margin-top:3px}
.stock-meta{display:block;margin-top:4px;font-size:12px;color:var(--muted);line-height:1.35}
.dc-result{margin-top:14px}
"""
if ".terms-cards{" not in html or ".km-right{" not in html:
    html = html.replace("</style>", EXTRA_CSS + "\n</style>", 1)
    print("extra css injected")

head = html[: html.find("<style>")] if "<style>" in html else html[:400]
if "<title>" in head and "</title>" not in head:
    i = html.find("<style>")
    html = html[:i] + "</title>\n  " + html[i:]

ICONS_HEAD = """
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="icon" href="favicon-32.png" type="image/png" sizes="32x32">
  <link rel="shortcut icon" href="favicon.ico">
  <link rel="apple-touch-icon" href="apple-touch-icon.png" sizes="180x180">
  <link rel="manifest" href="manifest.webmanifest">
  <meta name="theme-color" content="#c81e2b">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="TENET">
  <meta name="application-name" content="TENET">
  <meta name="mobile-web-app-capable" content="yes">
"""
if "apple-touch-icon.png" not in html:
    html = html.replace("</title>", "</title>\n" + ICONS_HEAD, 1)
    print("icons head injected")

pins = {}
try:
    body = urllib.parse.urlencode({"edit_code": "4fmBrr2H"}).encode()
    req = urllib.request.Request("https://rentry.co/api/fetch/o6nq7rki", data=body, headers={"Content-Type":"application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode())
    content = data.get("content")
    text = content.get("text") if isinstance(content, dict) else (content if isinstance(content, str) else "[]")
    lst = json.loads(text or "[]")
    for x in lst:
        if x and x.get("type")=="login" and x.get("surname") and x.get("code"):
            pins[str(x["surname"]).replace("ё","е").replace("Ё","е").lower()] = str(x["code"])
    print("baked pins", pins)
except Exception as e:
    print("pins fetch fail", e)

if pins:
    html = re.sub(r"const LOGIN_PINS = \{.*?\};", "const LOGIN_PINS = " + json.dumps(pins, ensure_ascii=False) + ";", html, count=1, flags=re.S)
MPT_VINS={"EDXFB32B2TE041658","EDXFB32B4TE041659","EDXFB32B7TE062327","EDXFD32B3TE070113","EDXFB32B3TE091114","EDXFB32B1TE087336","EDXFD32B4TE092590","EDXFD32B4TE092587"}
m=re.search(r"const STOCK = (\[.*?\]);\s*\n\s*const ST_LABEL", html, re.S)
if not m:
    m=re.search(r"const STOCK = (\[.*?\]);", html, re.S)
if m:
    stock=json.loads(m.group(1))
    for x in stock:
        x["mpt"]=x.get("vin") in MPT_VINS
        salon=str(x.get("salon") or "")
        if "коричнев" in salon.lower().replace("ё","е"):
            x["salon"]="Brown"
        if x.get("vin")=="EDEEB31B8TE003261":
            x["model"]="t4"
            x["name"]="T4"
        t=str(x.get("trim") or "").lower()
        mid=str(x.get("model") or "")
        rrc=None
        if mid=="t4": rrc=2449000
        elif mid=="t4l": rrc=2479000 if "прайм" in t else 2329000
        elif mid=="t7":
            if "4wd" in t and "прайм" in t: rrc=3190000
            elif "4wd" in t: rrc=2990000
            elif "прайм" in t: rrc=2985000
            else: rrc=2785000
        elif mid=="t8":
            if "ультра" in t: rrc=3885000
            elif "4wd" in t: rrc=3630000
            elif "прайм" in t: rrc=3299000
            else: rrc=3099000
        elif mid=="t9": rrc=4335000 if "прайм" in t else 4640000
        elif mid=="a8":
            if "ультра" in t: rrc=3275000
            elif "актив" in t: rrc=2865000
            else: rrc=3060000
        elif mid=="t7l": rrc=2735000
        if rrc: x["rrc"]=rrc
    if not any(x.get("vin")=="EDEDB21B7SD723791" for x in stock):
        stock.append({"vin":"EDEDB21B7SD723791","model":"t7l","name":"Tiggo 7 L","trim":"Актив","color":"Серебристый","status":"in","note":"В салоне · с 06.08.2026","invoice":False,"salon":"","prod":"","rrc":2735000,"mpt":False})
    html=html[:m.start(1)]+json.dumps(stock, ensure_ascii=False)+html[m.end(1):]
    print("stock patched", sum(1 for x in stock if x.get("mpt")), "mpt", len(stock), "cars")

if 't7l:' not in html:
    html=html.replace(
        'a8:  {id:"a8", brand:"CHERY", name:"Arrizo 8"',
        't7l: {id:"t7l", brand:"CHERY", name:"Tiggo 7 L", rivals:"Jolion, X70, Dashing", examN:0, img:"cars/t9.jpg"},\n      a8:  {id:"a8", brand:"CHERY", name:"Arrizo 8"'
    )
if 'id:"t4"' not in html:
    html=html.replace(
        't4l: {id:"t4l", brand:"TENET", name:"T4L"',
        't4:  {id:"t4", brand:"TENET", name:"T4", rivals:"", examN:0, img:"cars/t4l.jpg"},\n      t4l: {id:"t4l", brand:"TENET", name:"T4L"'
    )
html=html.replace('Object.values(MODELS)', 'Object.values(MODELS).filter(x=>x.id!=="t7l"&&x.id!=="t4")')
html=html.replace(
    '<p style="color:var(--muted);font-size:13px">Облако рейтинга: ${syncOk?"онлайн, все видят одни результаты":"пока не отвечает — нажмите обновить"}. <button class="btn ghost" id="syncNow">Обновить</button></p>',
    ''
)
html=html.replace(
    '${r.invoice?` <span class="st inv">Спец инвойс</span>`:""}</td>',
    '${r.invoice?` <span class="st inv">Спец инвойс</span>`:""}${r.mpt?` <span class="st mpt">МПТ</span>`:""}</td>'
)
if ".st.mpt{" not in html:
    html=html.replace("</style>", ".st.mpt{background:#cfe8d1;color:#1b5e20;}\n</style>", 1)
if ".stock-car.mpt{" not in html:
    html=html.replace("</style>", ".stock-car.mpt{border-color:#2e7d32;background:#e8f5e9}.mpt-tag{display:block;color:#1b5e20;font-weight:700;font-size:12px;margin:4px 0 2px}\n</style>", 1)

html=html.replace(
    '["terms","₽","Торговые условия","Прайс 01.09.2026, трейд-ин и кредит T7"]',
    '["terms","₽","Торговые условия","Доходность, бонусы, МПТ, спец инвойс, приоритет"]'
)
html=html.replace(
    '["calc","%","Калькулятор","Ежемесячный платёж с выбранной комплектации"]',
    '["calc","%","Калькулятор","Платёж и калькулятор КМ от 10.09"]'
)
if "let calcMode" not in html:
    html=html.replace(
        'let stockStatus = "all";',
        'let stockStatus = "all";\n    let calcMode = "pay";\n    let kmId = "t4lp";\n    let kmShown = "";\n    let kmVin = "";'
    )
if "let kmVin" not in html:
    html=html.replace(
        'let kmShown = "";',
        'let kmShown = "";\n    let kmVin = "";'
    )
if "let mptDay" not in html:
    html=html.replace(
        'let kmVin = "";',
        'let kmVin = "";\n    let mptMonth = 3;\n    let mptDay = "";'
    )
if 'if(model==="t7l")' not in html:
    html=html.replace(
        'let stockStatus = "all";',
        'let stockStatus = "all";\n    if(model==="t7l") model="t7";'
    )

tc = Path("terms-calc-fn.js")
if tc.exists():
    extra = tc.read_text()
    if not extra.endswith("\n"):
        extra += "\n"
    a = html.find("    function terms(){")
    b = html.find("    function stock(){")
    if a >= 0 and b > a:
        html = html[:a] + extra + html[b:]
        print("terms-calc spliced", len(extra))
    else:
        print("terms/stock anchors not found", a, b)

sf = Path("stock-fn.js")
if sf.exists():
    extra = sf.read_text()
    if not extra.endswith("\n"):
        extra += "\n"
    a = html.find("    function salonLabel(")
    if a < 0:
        a = html.find("    function stock(){")
    b = html.find("    function docs(){")
    if a >= 0 and b > a:
        html = html[:a] + extra + html[b:]
        print("stock fn spliced", len(extra))
    else:
        print("stock/docs anchors not found", a, b)

BIND_IDS = '["kmRrc","kmInv","kmUseTi","kmUseLoan","kmUseCr","kmSpec","kmUseDcTi","kmUseDcCr","kmDcTi","kmDcCr","kmDo","kmPack","kmCasco","cDown","cDownPct","cDownMode","cMonths"]'
NEW_BIND = '''      document.querySelectorAll("[data-calc-mode]").forEach(b=>b.onclick=()=>{ calcMode=b.dataset.calcMode; view="calc"; render(); });
      document.querySelectorAll("[data-km-id]").forEach(b=>b.onclick=()=>{ kmId=b.dataset.kmId; kmShown=""; kmVin=""; view="calc"; render(); });
      document.querySelectorAll("[data-down-mode]").forEach(b=>b.onclick=()=>{
        const el=document.getElementById("cDownMode");
        if(el) el.value=b.dataset.downMode||"pct";
        view="calc"; render();
      });
      document.querySelectorAll("[data-km-vin]").forEach(b=>b.onclick=()=>{
        const vin=b.dataset.kmVin||"";
        kmVin=vin;
        const car=(typeof STOCK!=="undefined"?STOCK:[]).find(x=>x.vin===vin);
        if(car && typeof kmIdFromCar==="function"){
          const nid=kmIdFromCar(car);
          if(nid && nid!==kmId){ kmId=nid; kmShown=""; }
        }
        view="calc"; render();
      });
      ''' + BIND_IDS + '''.forEach(id=>{
        const el=document.getElementById(id);
        if(el) el.addEventListener("change", ()=>{ view="calc"; render(); });
      });
'''
if 'querySelectorAll("[data-km-id]")' not in html:
    for needle in (
        '      const cPreset=document.getElementById("cPreset");',
        '      document.querySelectorAll("[data-go]").forEach(b=>b.onclick=()=>{',
    ):
        if needle in html:
            html = html.replace(needle, NEW_BIND + needle, 1)
            print("calc bind inserted")
            break
    else:
        print("calc bind not found")
else:
    print("calc bind already in html")
if 'querySelectorAll("[data-mpt-day]")' not in html:
    html=html.replace(
        'document.querySelectorAll("[data-km-id]")',
        'document.querySelectorAll("[data-mpt-day]").forEach(b=>b.onclick=()=>{ mptDay=b.dataset.mptDay||""; view="terms"; render(); });\n      document.querySelectorAll("[data-mpt-month]").forEach(b=>b.onclick=()=>{ mptMonth=Number(b.dataset.mptMonth)||3; view="terms"; render(); });\n      document.querySelectorAll("[data-km-id]")',
        1
    )

html=html.replace(
    '{model:"T4",vin:"EDEED31B1SE053704",trim:"Prime 4WD",year:"2025",color:"Белый",extra:"Сидоров",pay:500,bonus:1000}',
    '{model:"T4",vin:"EDEED31B1SE053704",trim:"Prime 4WD",year:"2025",color:"Белый",extra:"",seller:"Сидоров",sold:true,pay:500,bonus:1000}'
)
html=html.replace(
    '{model:"Tiggo 9",vin:"EDEDD24B1SG002595",trim:"Ultra",year:"2025",color:"Чёрный",extra:"Новиков",pay:500,bonus:0}',
    '{model:"Tiggo 9",vin:"EDEDD24B1SG002595",trim:"Ultra",year:"2025",color:"Чёрный",extra:"",seller:"Новиков",sold:true,pay:500,bonus:0}'
)
html=html.replace('      {model:"T4",trim:"T4 2025",km:"−30 / 20",note:""},\n','')
html=html.replace('      {model:"T4",trim:"T4 2025",bonus:"3%"},\n','')
html=html.replace(
    '`<div class="terms-cards">`+TERMS_MPT.map(g=>`<article class="term-card"><b>${escape(g.line)}</b>`+g.rows.map(r=>`<small>${escape(r[0])} · <b>${escape(r[1])}</b></small>`).join("")+`</article>`).join("")+`</div>`+',
    '`<p class="lead">По дате производства T7. Зелёный — МПТ, песочный — субсидия бренда. Нажмите день.</p>`+mptCal()+'
)
html=html.replace(
    "      persistRun(true);\n      next(); closing=false;",
    "      if(idx+1>=paper.length){ finish(); return; }\n      persistRun(true);\n      next(); closing=false;"
)
html=html.replace(
    "answers[idx]={id:q.id,ok:false,cat:q.cat,p:q.p,x:q.x};",
    "answers[idx]={id:q.id,ok:false,cat:q.cat,p:q.p,x:q.x,pick:(selected||[]).map(id=>((q.o||[]).find(p=>p[0]===id)||[id,\"не выбран\"])[1])};"
)
html=html.replace(
    "answers[idx]={id:q.id,ok:!!ok,cat:q.cat,p:q.p,x:q.x};",
    "answers[idx]={id:q.id,ok:!!ok,cat:q.cat,p:q.p,x:q.x,pick:(selected||[]).map(id=>((q.o||[]).find(p=>p[0]===id)||[id,id])[1])};"
)
html=html.replace(
    "missed=rows.filter(r=>!r.ok).map(r=>({id:r.id,p:r.p,x:r.x}));",
    "missed=rows.filter(r=>!r.ok).map(r=>({id:r.id,p:r.p,x:r.x,pick:r.pick||[]}));"
)
html=html.replace(
    "missed.map(x=>`<div class=\"card\" style=\"margin:8px 0\"><b>${escape(x.p)}</b><p>${escape(x.x)}</p></div>`).join(\"\")",
    "missed.map(x=>`<div class=\"card\" style=\"margin:8px 0\"><b>${escape(x.p)}</b><p style=\"margin:8px 0 0\"><span class=\"eyebrow\">Ответ</span><br>${escape((x.pick&&x.pick.length?x.pick.join(\"; \"):\"не выбран\"))}</p><p>${escape(x.x)}</p></div>`).join(\"\")"
)
if "let reviewExamN" not in html:
    html=html.replace(
        'let stockStatus = "all";',
        'let stockStatus = "all";\n    let reviewExamN = 1;'
    )
html=html.replace(
    "percent:pct,at:item.date,attempts:(prev.attempts||0)+1,status:\"done\"};",
    "percent:pct,ok:correct,n:paper.length,missed:missed.map(r=>({id:r.id,p:r.p,x:r.x,pick:r.pick||[]})),at:item.date,attempts:(prev.attempts||0)+1,status:\"done\"};"
)
html=html.replace(
    "if(body.status===\"running\" && rec.run) body.run = rec.run;",
    "if(body.status===\"running\" && rec.run) body.run = rec.run;\n      if(Array.isArray(rec.missed)) body.missed=rec.missed;\n      if(rec.ok!=null) body.ok=rec.ok;\n      if(rec.n!=null) body.n=rec.n;"
)
html=html.replace(
    "login,hub,home,study,quiz:brief,play,rate,hist:rate,terms,calc,stock,docs",
    "login,hub,home,study,quiz:brief,play,rate,hist:rate,review,terms,calc,stock,docs"
)
if "function review(){" not in html:
    html=html.replace(
        "function home(){",
        "function review(){\n"
        "      if(!state.surname) return login();\n"
        "      const rec=examRec(reviewExamN||1);\n"
        "      const miss=(rec&&rec.missed)||[];\n"
        "      const title=Number(reviewExamN)===2?\"Разбор пересдачи\":\"Разбор первой попытки\";\n"
        "      const mname=((MODELS[(rec&&rec.model)||model]||{}).name)||((rec&&rec.model)||model);\n"
        "      return banner(title, rec?((rec.percent!=null?rec.percent+\"% · \":\"\")+mname):\"\", \"TENET\")+`\n"
        "        <p class=\"lead\">${rec?escape(rec.display||state.display)+(rec.ok!=null&&rec.n?\" · \"+rec.ok+\" из \"+rec.n:\"\")+(rec.at?\" · \"+String(rec.at).slice(0,10):\"\"):\"Нет сохранённой попытки.\"}</p>\n"
        "        ${miss.length?miss.map(x=>`<div class=\"card\" style=\"margin:8px 0\"><b>${escape(x.p||\"\")}</b><p style=\"margin:8px 0 0\"><span class=\"eyebrow\">Ответ</span><br>${escape((x.pick&&x.pick.length?x.pick.join(\"; \"):\"не выбран\"))}</p><p>${escape(x.x||\"\")}</p></div>`).join(\"\"):`<div class=\"card\"><p>Разбор этой попытки не сохранился. Новые прохождения после обновления сайта будут открываться здесь даже после закрытия вкладки.</p></div>`}\n"
        "        <div style=\"margin-top:16px\"><button class=\"btn ghost\" data-go=\"home\">К модели</button></div>`;\n"
        "    }\n"
        "    function home(){"
    )
html=html.replace(
    ': `<div class="card ok"><h3>Аттестация №1 · ${e1?e1.percent+"%":""}</h3><p>Результат закреплён.${e2?" Стало "+e2.percent+"%.":" Пересдача — по коду РОП."}</p></div>`;',
    ': `<div class="card ok"><h3>Аттестация №1 · ${e1?e1.percent+"%":""}</h3><p>Результат закреплён.${e2?" Стало "+e2.percent+"%.":" Пересдача — по коду РОП."}</p></div>`+`<button class="card ok" data-review="1"><h3>Разбор первой попытки</h3><p>Ошибки и ваши ответы. Доступен после обновления страницы.</p></button>`;'
)
html=html.replace(
    '? `<div class="card ok"><h3>Аттестация сдана · ${e1.percent}%</h3><p>Эксперт. Закреплено в рейтинге. Пересдача не нужна.</p></div>`',
    '? `<div class="card ok"><h3>Аттестация сдана · ${e1.percent}%</h3><p>Эксперт. Закреплено в рейтинге. Пересдача не нужна.</p></div>`+`<button class="card ok" data-review="1"><h3>Разбор первой попытки</h3><p>Ошибки и ваши ответы.</p></button>`'
)
if 'querySelectorAll("[data-review]")' not in html:
    html=html.replace(
        'document.querySelectorAll("[data-go]")',
        'document.querySelectorAll("[data-review]").forEach(b=>b.onclick=()=>{ reviewExamN=Number(b.dataset.review)||1; view="review"; render(); });\n      document.querySelectorAll("[data-go]")',
        1
    )

Path("_site").mkdir(exist_ok=True)
Path("_site/index.html").write_text(html)
Path("_site/pins.json").write_text(json.dumps(pins, ensure_ascii=False))
print("wrote site", len(html))
