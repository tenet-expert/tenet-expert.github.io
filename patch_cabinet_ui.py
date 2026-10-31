#!/usr/bin/env python3
"""Cabinet UI: stock tiles, filters, round-trip, docs, checklist labels, terms chrome.

Idempotent. Runs at the end of the Pages build so a stock-json inject
(const STOCK = ...) cannot drop these edits. Does not touch prices, stock
rows, pins, rentry keys, calculator math, or photo-link data.
"""
from pathlib import Path
import json

CSS = r"""
/* cabinet-ui */
header.top{background:#f4f1ea;box-shadow:0 1px 0 rgba(17,17,20,.06)}
html{scroll-padding-top:84px}
.st-board{align-items:start;grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}
.st-trims{align-items:start;grid-template-columns:repeat(auto-fill,minmax(200px,1fr))}
.st-list{align-items:start;grid-template-columns:repeat(auto-fill,minmax(210px,1fr))}
.st-acc:not([open]),.st-trim:not([open]){aspect-ratio:auto;height:auto}
.st-acc>summary,.st-trim>summary{flex-direction:row;align-items:center;height:auto;min-height:0}
.st-acc.is-few>summary{padding:10px 12px}
.st-meta{margin-left:auto;margin-top:0;min-width:0;flex-wrap:wrap;justify-content:flex-end}
.st-count{white-space:normal;line-height:1.35;text-align:right}
.st-row{aspect-ratio:auto;height:auto;min-height:0}
.st-row.open{grid-column:auto;aspect-ratio:auto;min-height:0}
.st-swatch{height:8px}
.st-face{height:auto;gap:3px;padding:10px 12px 10px}
.st-name{font-size:15px;line-height:1.25;display:block;overflow:visible;white-space:normal;-webkit-line-clamp:unset}
.st-trim,.st-tail,.st-when{display:block;font:650 13px/1.35 Inter,system-ui,sans-serif;color:#2c2823;white-space:normal;overflow:visible}
.st-tail{letter-spacing:.04em;font-variant-numeric:tabular-nums}
.st-when{color:#4e473f;font-weight:600}
.st-more{display:none;margin:0 12px 12px;padding-top:10px;border-top:1px solid #eadfcf;font:600 15px/1.45 Inter,system-ui,sans-serif;color:#1c1a17}
.st-row.open .st-more{display:block}
.st-more .st-keep,.st-more .st-keep-price,.st-more .st-vin,.st-more .st-notes{display:block;margin:0 0 6px;color:#1c1a17;font-family:Inter,system-ui,sans-serif;font-size:15px;line-height:1.4;font-weight:650}
.st-more .st-keep-price{font-weight:800;font-variant-numeric:tabular-nums}
.st-more .st-vin{font-weight:750;letter-spacing:.02em;word-break:break-all;font-size:15px}
.st-more .st-notes{font-size:13px;font-weight:600;color:#3d3832}
.st-sticky{position:sticky;z-index:19;background:#f4f1ea;padding:8px 0 6px}
.st-inv{margin-top:8px}
.docs-page{padding-top:8px}
.docs-page .docs-card{scroll-margin-top:96px;margin-top:16px}
.doc-hint{color:#5c5348;font-weight:650}
.terms-spec{align-items:stretch}
.terms-spec>section{display:flex;flex-direction:column;height:100%;min-width:0}
.terms-spec .terms-cards{flex:1;align-content:stretch;grid-auto-rows:1fr}
.terms-spec .term-card,.terms-spec .term-group{height:100%;box-sizing:border-box}
.terms-top{align-items:stretch}
.terms-fold,.fleet-board.terms-fold{border:1px solid #e4d7c4;border-radius:16px;background:#fff;box-shadow:0 1px 0 rgba(17,17,20,.04)}
.terms-fold>summary,.fleet-board.terms-fold>summary{font:800 18px/1.2 Inter,system-ui,sans-serif;letter-spacing:-.02em;padding:14px 16px;display:flex;align-items:center;gap:8px;color:#1c1a17}
.fleet-board.terms-fold{background:#f7f4ef;margin:0 0 12px}
.terms-top .terms-fold{margin:0;height:100%;display:flex;flex-direction:column}
.terms-top .terms-fold:nth-child(1){background:#eef3f8;border-color:#d5e2ef}
.terms-top .terms-fold:nth-child(2){background:#eef6ee;border-color:#d3e6d4}
.terms-top .terms-fold:nth-child(1)>summary{color:#1f4e79}
.terms-top .terms-fold:nth-child(2)>summary{color:#1e5c24}
.fleet-board.terms-fold>summary{color:#6d4c2a}
@media(max-width:430px){
  html,body{overflow-x:hidden;max-width:100%}
  .wrap{overflow-x:hidden;max-width:100%}
  header.top,nav.desk{max-width:100%}
  nav.desk{width:100%;border-radius:16px}
  nav.desk button{padding:8px 10px}
  .st-board,.st-trims,.st-list{grid-template-columns:1fr}
  .banner,.card,.chip,.st-row,.km-disc,.km-pay,.pay-col{min-width:0;max-width:100%}
  .km-layout,.km-layout.km-3,.km-layout.km-4,.km-pays,.km-bottom,.km-contrast,.pay-split,.km-pv-row,.km-grid,.km-pair,.km-pair.is-2,.calc-grid,.terms-spec,.terms-top,.km-stage .km-layout{
    grid-template-columns:1fr !important;
  }
  .km-stage .km-layout>.km-disc,.km-stage .km-layout>.km-credit,.terms-spec .spec-tenet{grid-column:auto !important}
  .km-slot.s-test .km-grid,.km-slot.s-t7 .km-grid,.km-slot.s-t4 .km-line:last-child .km-grid{grid-template-columns:1fr !important}
  .bank-row{flex-wrap:wrap}
  .bank-row .pay,.pay,.calc-out,.st-count,.km-slot .chip,.km-slot .chip small,.km-grid .chip{white-space:normal}
  .km-vin-row{flex-wrap:wrap}
  .km-vin-row .st-vin-search,.km-vin-row .chip{width:100%;min-width:0}
  .study-pick{overflow:visible;max-width:100%}
  .model-row{display:grid;grid-template-columns:1fr 1fr;overflow:visible}
  .model-row .card{flex:none;width:auto;min-width:0}
  .tune-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;touch-action:pan-x pan-y}
  .tune-table{width:max-content;min-width:720px;table-layout:auto}
  .tune-table th,.tune-table td{white-space:nowrap;word-break:normal}
  .fleet-wrap,.lb-scroll{overflow:visible;max-width:100%}
  .fleet-sheet,.lb-mini{width:100%;table-layout:fixed}
  .fleet-sheet th,.fleet-sheet td,.lb-mini th,.lb-mini td{white-space:normal;word-break:break-word}
  .check-row{align-items:flex-start}
  .check-row span{min-width:0}
  input,textarea,select,button{max-width:100%}
  .pv-min{font-size:16px}
  .pv-min b{font-size:26px}
  .calc-out{font-size:32px;overflow-wrap:anywhere}
}
/* /cabinet-ui */
"""

STOCK_HELPERS = r"""
    function stockTrimName(t){
      const s=String(t||"").trim();
      return s||"Без комплектации";
    }
    function stockVinTail(vin){
      const v=String(vin||"").toUpperCase();
      if(!v) return "";
      return v.length<=8?v:v.slice(-8);
    }
    function stockStay(r){
      const note=String(r&&r.note||"");
      const m=note.match(/(\d{2})\.(\d{2})\.(\d{4})/);
      let days=null;
      if(m){
        const dt=new Date(Number(m[3]), Number(m[2])-1, Number(m[1]));
        const now=new Date();
        const a=new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const b=new Date(dt.getFullYear(), dt.getMonth(), dt.getDate());
        if(!isNaN(b.getTime())) days=Math.max(0, Math.round((a-b)/86400000));
      }
      const way=!!(r&&r.status==="way");
      const label=way?"в пути":(m?("в салоне с "+m[1]+"."+m[2]):"в салоне");
      const daysTxt=days==null?"":(days+" дн.");
      return {label:label, daysTxt:daysTxt, line:[label, daysTxt].filter(Boolean).join(" · ")};
    }
"""

STOCK_CARD = r"""    function stockCard(r){
      const price=stockRrc(r);
      const stay=stockStay(r);
      const tail=stockVinTail(r.vin);
      const reservedCls=r.reserved?" is-reserved":"";
      const reservedBadge=r.reserved?`<span class="st reserved">Забронирован</span>`:"";
      const tone=stockTone(r.color);
      const superOn=typeof EXCL_FIX!=="undefined"&&EXCL_FIX[r.vin]&&r.model==="t4l";
      const notes=[];
      if(typeof PANGO_ONLY!=="undefined"&&PANGO_ONLY[r.vin]) notes.push("спеццена · сотрудник · 1 хоз ГИБДД · 500 км · только PANGO");
      if(superOn) notes.push("СУПЕРСПЕЦ "+Math.round(EXCL_FIX[r.vin].cash/1000)+" нал / "+Math.round(EXCL_FIX[r.vin].ti/1000)+" с ТИ");
      if(typeof KM_FORK!=="undefined"&&KM_FORK[r.vin]) notes.push("КМ "+KM_FORK[r.vin].ti+" тыс. с трейд-ин · "+KM_FORK[r.vin].cash+" без");
      if(r.note) notes.push(r.note);
      const open=(typeof stockCardVin==="string" && stockCardVin && stockCardVin===r.vin)?" open":"";
      const priceTxt=price?rub(price)+" ₽":"—";
      const model=r.name||"";
      const trim=r.trim||"";
      return `<article class="st-row${tone?" "+tone:""}${reservedCls}${r.invoice?" is-invoice":""}${open}" data-st-card data-vin="${escape(r.vin||"")}">
        <div class="st-swatch" aria-hidden="true"></div>
        <div class="st-face">
          <b class="st-name">${escape(model)}${superOn?" · СУПЕРСПЕЦ":""}</b>
          <span class="st-trim">${escape(trim||"—")}</span>
          <span class="st-tail">${tail?escape(tail):""}</span>
          <span class="st-when">${escape(stay.line)}</span>
          <b class="st-price">${priceTxt}</b>
          <div class="st-flags-mini">${stockBadges(r)}${reservedBadge}</div>
        </div>
        <div class="st-more">
          <p class="st-keep"><b>${escape(model)}</b>${trim?" · "+escape(trim):""}</p>
          <p class="st-keep-price">${priceTxt}</p>
          <div class="st-flags-mini">${stockBadges(r)}${reservedBadge}</div>
          <p class="st-vin">${escape(r.vin||"")}</p>
          ${notes.length?`<p class="st-notes">${escape(notes.join(" · "))}</p>`:""}
          <button type="button" class="chip st-calc" data-km-vin="${escape(r.vin)}">Калькулятор</button>
        </div>
      </article>`;
    }
"""

NAV_OLD = '''      if(extra[active]) items.push([active, extra[active]]);
      }
      const html=items.map(([id,l])=>`<button class="${id===active?"on":""}" data-go="${id}">${l}</button>`).join("");'''

NAV_NEW = '''      if(extra[active]) items.push([active, extra[active]]);
      }
      if(active!=="login"){
        [["stock","Склад"],["calc","Калькулятор"]].forEach(pair=>{
          if(!items.some(x=>x[0]===pair[0])) items.push(pair);
        });
      }
      const html=items.map(([id,l])=>`<button class="${id===active?"on":""}" data-go="${id}">${l}</button>`).join("");'''

GO_OLD = '''    function goSection(id){
      if(isAo() && !["hub","calc","stock","terms","login"].includes(id)) id="hub";
      const attest=["home","study","quiz","play","rate","hist"];
      view=id;
      state.section = id==="hub" ? "hub" : (attest.includes(id) ? "attest" : id);
      save();
      render();
    }'''

GO_NEW = '''    function goSection(id){
      const prev=view;
      if(isAo() && !["hub","calc","stock","terms","login"].includes(id)) id="hub";
      if(id==="calc" && prev==="stock" && typeof stockLeaveForCalc==="function") stockLeaveForCalc();
      if(id==="stock" && prev!=="stock" && typeof stockApply==="function") stockApply(stockReadStore());
      const attest=["home","study","quiz","play","rate","hist"];
      view=id;
      state.section = id==="hub" ? "hub" : (attest.includes(id) ? "attest" : id);
      save();
      render();
      if(id==="stock" && prev!=="stock" && typeof stockPush==="function") stockPush();
      else if(id==="calc" && prev!=="stock" && typeof stockPushCalc==="function") stockPushCalc();
    }'''

STATE_FNS = r'''
    function stockReadStore(){
      try{ return JSON.parse(sessionStorage.getItem("tenet-stock-ui")||"null"); }catch(e){ return null; }
    }
    function stockSnap(){
      return {
        stockFilter: stockFilter||"all",
        stockStatus: stockStatus||"all",
        stockInv: (typeof stockInv==="string"?stockInv:"all")||"all",
        stockSort: (!stockSort||stockSort==="year")?"trim":stockSort,
        stockSortDir: stockSortDir===-1?-1:1,
        stockVin: stockVin||"",
        stockOpen: stockOpen||{},
        stockCardVin: (typeof stockCardVin==="string"?stockCardVin:"")||"",
        scroll: window.scrollY||0
      };
    }
    function stockWriteStore(snap){
      try{ sessionStorage.setItem("tenet-stock-ui", JSON.stringify(snap||stockSnap())); }catch(e){}
    }
    function stockApply(snap){
      if(!snap) return;
      stockFilter=snap.stockFilter||"all";
      stockStatus=snap.stockStatus||"all";
      stockInv=snap.stockInv||"all";
      stockSort=(!snap.stockSort||snap.stockSort==="year")?"trim":snap.stockSort;
      stockSortDir=snap.stockSortDir===-1?-1:1;
      stockVin=typeof snap.stockVin==="string"?snap.stockVin:"";
      stockOpen=(snap.stockOpen&&typeof snap.stockOpen==="object")?snap.stockOpen:{};
      stockCardVin=snap.stockCardVin||"";
      stockWantScroll=Number(snap.scroll)||0;
    }
    function stockHashUrl(hash){ return location.pathname+location.search+hash; }
    function stockSyncHist(){
      if(view!=="stock") return;
      const snap=stockSnap();
      stockWriteStore(snap);
      const st={tenetView:"stock", stock:snap};
      try{
        if((history.state||{}).tenetView==="stock" || location.hash==="#sklad") history.replaceState(st,"",stockHashUrl("#sklad"));
      }catch(e){}
    }
    function stockPush(){
      const snap=stockSnap();
      stockWriteStore(snap);
      try{ history.pushState({tenetView:"stock", stock:snap},"",stockHashUrl("#sklad")); }catch(e){}
    }
    function stockPushCalc(){
      try{ history.pushState({tenetView:"calc"},"",stockHashUrl("#calc")); }catch(e){}
    }
    function stockLeaveForCalc(){
      const snap=stockSnap();
      stockWriteStore(snap);
      try{ history.pushState({tenetView:"calc", stock:snap},"",stockHashUrl("#calc")); }catch(e){}
    }
'''

DOC_HINT_FN = r'''
    function docFileHint(d){
      const file=String(d&&d.file||"");
      const n=(typeof DOC_BYTES==="object"&&DOC_BYTES)?Number(DOC_BYTES[file]||0):0;
      const pdf=/\.pdf(\?|$)/i.test(file);
      const known=String((d&&d.kind)||"")+" "+String((d&&d.pages)||"");
      const type=pdf?(/pdf/i.test(known)?"":" · PDF"):(/html/i.test(known)?"":" · HTML");
      if(!n) return type;
      const mb=n/1048576;
      let size;
      if(mb>=10) size=Math.round(mb)+" МБ";
      else if(mb>=1) size=(Math.round(mb*10)/10).toFixed(1).replace(".",",")+" МБ";
      else size=Math.max(1, Math.round(n/1024))+" КБ";
      return type+" · "+size+(pdf&&mb>=8?" · большой файл":"");
    }
'''


def sub(text, old, new, label, optional=False):
    if new in text:
        print("already", label)
        return text
    if old not in text:
        if optional:
            print("skip", label)
            return text
        raise SystemExit("missing " + label)
    print("ok", label)
    return text.replace(old, new, 1)


def doc_bytes():
    out = {}
    docs = Path("docs")
    if not docs.is_dir():
        return out
    for p in sorted(docs.iterdir()):
        if p.is_file() and p.suffix.lower() in {".pdf", ".html"}:
            out["docs/" + p.name] = p.stat().st_size
    return out


def patch_css(html):
    if "/* cabinet-ui */" in html and "/* /cabinet-ui */" in html:
        pre, rest = html.split("/* cabinet-ui */", 1)
        _, post = rest.split("/* /cabinet-ui */", 1)
        html = pre + CSS.strip() + post
        print("css replaced")
        return html
    if "</style>" not in html:
        raise SystemExit("no style")
    html = html.replace("</style>", CSS + "\n</style>", 1)
    print("css inserted")
    return html


def patch_stock_logic(html, label):
    html = sub(html,
        '''      else if(key==="year") d=stockYear(a)-stockYear(b);
      else d=stockTrimRank(a.trim)-stockTrimRank(b.trim)||String(a.trim||"").localeCompare(String(b.trim||""),"ru");''',
        '''      else d=stockTrimName(a.trim).localeCompare(stockTrimName(b.trim),"ru");''',
        label+" cmp")
    html = sub(html,
        '''        if(key==="year") return (Math.max.apply(null,A.rows.map(stockYear))-Math.max.apply(null,B.rows.map(stockYear)))*dir;
        if(key==="color") return String((A.rows[0]&&A.rows[0].color)||"").localeCompare(String((B.rows[0]&&B.rows[0].color)||""),"ru")*dir;
        return (stockTrimRank(A.trim)-stockTrimRank(B.trim)||A.trim.localeCompare(B.trim,"ru"))*dir;''',
        '''        if(key==="color") return String((A.rows[0]&&A.rows[0].color)||"").localeCompare(String((B.rows[0]&&B.rows[0].color)||""),"ru")*dir;
        return stockTrimName(A.trim).localeCompare(stockTrimName(B.trim),"ru")*dir;''',
        label+" groups")
    if "function stockTrimName(" not in html:
        html = sub(html, "    function stockCmp(a,b){", STOCK_HELPERS + "    function stockCmp(a,b){", label+" helpers")
    else:
        print("already", label+" helpers")
    old_card_start = "    function stockCard(r){"
    old_card_end = "    const TEST_SALE = ["
    if "data-vin=" not in html.split("function stockCard", 1)[-1][:1800]:
        a = html.find(old_card_start)
        b = html.find(old_card_end)
        if a < 0 or b < a:
            raise SystemExit("stockCard bounds " + label)
        html = html[:a] + STOCK_CARD + "\n" + html[b:]
        print("ok", label+" card")
    else:
        print("already", label+" card")
    html = sub(html,
        '''      if(typeof stockSort!=="string") stockSort="trim";
      if(typeof stockSortDir!=="number") stockSortDir=1;
      if(typeof stockOpen!=="object" || !stockOpen) stockOpen={};''',
        '''      if(typeof stockSort!=="string" || stockSort==="year") stockSort="trim";
      if(typeof stockSortDir!=="number") stockSortDir=1;
      if(typeof stockOpen!=="object" || !stockOpen) stockOpen={};
      if(typeof stockInv!=="string") stockInv="all";
      if(typeof stockCardVin!=="string") stockCardVin="";''',
        label+" init")
    html = sub(html,
        '''      const list=sale.filter(x=>{
        if(q) return stockVinNorm(x.vin).indexOf(q)>=0;
        if(stockFilter!=="all" && x.model!==stockFilter) return false;
        if(stockStatus!=="all" && x.status!==stockStatus) return false;
        return true;
      });
      const scoped=stockFilter==="all"?sale:sale.filter(x=>x.model===stockFilter);
      const nIn=scoped.filter(x=>x.status==="in").length;
      const nWay=scoped.filter(x=>x.status==="way").length;''',
        '''      const invOk=x=>stockInv==="inv"?!!x.invoice:(stockInv==="direct"?!x.invoice:true);
      const list=sale.filter(x=>{
        if(q) return stockVinNorm(x.vin).indexOf(q)>=0;
        if(stockFilter!=="all" && x.model!==stockFilter) return false;
        if(stockStatus==="test") return false;
        if(stockStatus!=="all" && x.status!==stockStatus) return false;
        if(!invOk(x)) return false;
        return true;
      });
      const modelScoped=stockFilter==="all"?sale:sale.filter(x=>x.model===stockFilter);
      const statusScoped=modelScoped.filter(invOk);
      const scoped=statusScoped;
      const nIn=statusScoped.filter(x=>x.status==="in").length;
      const nWay=statusScoped.filter(x=>x.status==="way").length;
      const invScoped=modelScoped.filter(x=>stockStatus==="all"||stockStatus==="test"||x.status===stockStatus);
      const nInv=invScoped.filter(x=>!!x.invoice).length;
      const nDir=invScoped.filter(x=>!x.invoice).length;''',
        label+" filter")
    html = sub(html,
        '''      const sorts=[["price","Цена"],["color","Цвет"],["year","Год"],["trim","Комплектация"]];
      const sortBtns=sorts.map(([k,lab])=>{
        const on=stockSort===k;
        const arrow=on?(stockSortDir<0?" ↓":" ↑"):"";
        return `<button type="button" class="chip ${on?"on":""}" data-stock-sort="${k}">${lab}${arrow}</button>`;
      }).join("");''',
        '''      const sorts=[["price","Цена"],["color","Цвет"],["trim","Комплектация"]];
      const sortBtns=sorts.map(([k,lab])=>{
        const on=stockSort===k;
        const dir=on?stockSortDir:1;
        const arrow=dir<0?" ↓":" ↑";
        return `<button type="button" class="chip ${on?"on":""}" data-stock-sort="${k}">${lab}${arrow}</button>`;
      }).join("");''',
        label+" sorts")
    html = sub(html,
        '''            if(inn) bits.push(inn+" в наличии");
            if(way) bits.push(way+" в пути");
            if(stockSort==="price"){
              const prices=rows.map(stockRrc).filter(Boolean);
              if(prices.length) bits.unshift("от "+rub(Math.min.apply(null,prices))+" ₽");
            }else if(stockSort==="year"){
              const years=rows.map(stockYear).filter(Boolean);
              if(years.length) bits.unshift(String(Math.max.apply(null,years)));
            }else if(stockSort==="color"){
              const color=((rows.slice().sort(stockCmp)[0])||{}).color;
              if(color) bits.unshift(color);
            }
''',
        '''            if(inn) bits.push(inn+" в наличии");
            if(way) bits.push(way+" в пути");
''',
        label+" header")
    html = sub(html,
        '''            const tone=m.brand==="CHERY"?" chery":"";
            return `<details class="st-acc${tone}" data-acc="m:${id}" ${opened?"open":""}>''',
        '''            const tone=m.brand==="CHERY"?" chery":"";
            const few=rows.length<=4?" is-few":"";
            return `<details class="st-acc${tone}${few}" data-acc="m:${id}" ${opened?"open":""}>''',
        label+" few")
    html = sub(html,
        '''        <input id="stockVin" class="st-vin-search" type="search" inputmode="text" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="Поиск по VIN" value="${typed}">
        <div class="study-pick st-filters">''',
        '''        <div class="st-sticky"><input id="stockVin" class="st-vin-search" type="search" inputmode="text" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="Поиск по VIN" value="${typed}"></div>
        <div class="study-pick st-filters">''',
        label+" sticky")
    html = sub(html,
        '''        ${testOn?"":`<div class="study-pick st-filters st-sorts">''',
        '''        ${testOn?"":`<div class="study-pick st-filters st-inv">
          <button type="button" class="chip ${stockInv==="inv"?"on":""}" data-stock-inv="inv">Спец инвойс · ${nInv}</button>
          <button type="button" class="chip ${stockInv==="direct"?"on":""}" data-stock-inv="direct">Директ · ${nDir}</button>
        </div>`}
        ${testOn?"":`<div class="study-pick st-filters st-sorts">''',
        label+" inv chips")
    return html


def patch_index(html):
    html = patch_css(html)
    html = sub(html, "    let stockOpen = {};\n",
               "    let stockOpen = {};\n    let stockInv = \"all\";\n    let stockCardVin = \"\";\n    let stockWantScroll = null;\n",
               "lets", optional=True)
    if "function stockReadStore(" not in html:
        html = sub(html, "    function nav(active){", STATE_FNS + "    function nav(active){", "state fns")
    html = sub(html, NAV_OLD, NAV_NEW, "nav", optional=True)
    html = sub(html, GO_OLD, GO_NEW, "go")
    html = patch_stock_logic(html, "index")
    html = sub(html,
        '''        if(root) root.innerHTML=fn();
        bind();''',
        '''        if(root) root.innerHTML=fn();
        bind();
        if(view==="stock"){
          if(typeof stockSyncHist==="function") stockSyncHist();
          if(stockWantScroll!=null){
            const y=stockWantScroll; stockWantScroll=null;
            requestAnimationFrame(function(){ window.scrollTo(0, y); });
          }
          const head=document.querySelector("header.top");
          const bar=document.querySelector(".st-sticky");
          if(head&&bar) bar.style.top=(head.getBoundingClientRect().height+6)+"px";
        }''',
        "render hook")
    html = sub(html,
        '''      document.querySelectorAll("[data-stock-st]").forEach(b=>b.onclick=()=>{ stockStatus=b.dataset.stockSt; render(); });''',
        '''      document.querySelectorAll("[data-stock-st]").forEach(b=>b.onclick=()=>{ stockStatus=b.dataset.stockSt; render(); });
      document.querySelectorAll("[data-stock-inv]").forEach(b=>b.onclick=()=>{
        const k=b.dataset.stockInv||"all";
        stockInv = stockInv===k ? "all" : k;
        render();
      });''',
        "inv bind")
    html = sub(html,
        '''        else { stockSort=key; stockSortDir=(key==="year")?-1:1; }''',
        '''        else { stockSort=key; stockSortDir=1; }''',
        "sort dir")
    html = sub(html,
        '''      document.querySelectorAll("details[data-acc]").forEach(d=>{ d.ontoggle=()=>{ stockOpen[d.dataset.acc]=d.open; }; });
      document.querySelectorAll("[data-st-card]").forEach(el=>{
        el.onclick=(e)=>{
          if(e.target.closest(".st-calc")) return;
          el.classList.toggle("open");
        };
      });''',
        '''      document.querySelectorAll("details[data-acc]").forEach(d=>{ d.ontoggle=()=>{ stockOpen[d.dataset.acc]=d.open; if(typeof stockSyncHist==="function") stockSyncHist(); }; });
      document.querySelectorAll("[data-st-card]").forEach(el=>{
        el.onclick=(e)=>{
          if(e.target.closest(".st-calc")) return;
          const vin=el.getAttribute("data-vin")||"";
          stockCardVin = stockCardVin===vin ? "" : vin;
          document.querySelectorAll("[data-st-card]").forEach(x=>x.classList.toggle("open", !!stockCardVin && (x.getAttribute("data-vin")||"")===stockCardVin));
          if(typeof stockSyncHist==="function") stockSyncHist();
        };
      });
      const backStock=document.getElementById("backStock");
      if(backStock) backStock.onclick=()=>{
        const st=history.state||{};
        if(st.tenetView==="calc"){ history.back(); return; }
        if(typeof stockApply==="function") stockApply(stockReadStore());
        view="stock"; state.section="stock"; save(); render();
      };''',
        "card bind")
    html = sub(html,
        '''      document.querySelectorAll("[data-km-id]").forEach(b=>b.onclick=(e)=>{ e.preventDefault(); e.stopPropagation(); kmId=b.dataset.kmId; kmShown=""; const test=typeof testSaleOf==="function"?testSaleOf(kmId):null; kmVin=test?test.vin:""; kmVinQuery=test?test.vin:""; kmVinMiss=""; view="calc"; render(); });''',
        '''      document.querySelectorAll("[data-km-id]").forEach(b=>b.onclick=(e)=>{ e.preventDefault(); e.stopPropagation(); if(view==="stock" && typeof stockLeaveForCalc==="function") stockLeaveForCalc(); kmId=b.dataset.kmId; kmShown=""; const test=typeof testSaleOf==="function"?testSaleOf(kmId):null; kmVin=test?test.vin:""; kmVinQuery=test?test.vin:""; kmVinMiss=""; view="calc"; render(); });''',
        "km id")
    html = sub(html,
        '''      document.querySelectorAll("[data-km-vin]").forEach(b=>b.onclick=()=>{
        const vin=b.dataset.kmVin||"";''',
        '''      document.querySelectorAll("[data-km-vin]").forEach(b=>b.onclick=()=>{
        if(view==="stock" && typeof stockLeaveForCalc==="function") stockLeaveForCalc();
        const vin=b.dataset.kmVin||"";''',
        "km vin")
    html = sub(html,
        '''      return `<div class="card" style="margin-bottom:12px"><p class="eyebrow">Конкретный VIN</p><div class="km-vin-row">''',
        '''      return `<div class="card" style="margin-bottom:12px"><button type="button" class="btn ghost" id="backStock">← На склад</button><p class="eyebrow">Конкретный VIN</p><div class="km-vin-row">''',
        "back btn")
    if "function docFileHint(" not in html:
        blob = "    const DOC_BYTES = " + json.dumps(doc_bytes(), ensure_ascii=False, separators=(",", ":")) + ";\n" + DOC_HINT_FN
        html = sub(html, "    function docs(){", blob + "    function docs(){", "doc hint")
    html = sub(html,
        '''        ${Object.values(MODELS).filter(x=>x.id!=="t7l"&&x.id!=="t4"&&x.id!=="tt9").map(m=>{
          const list=DOCS[m.id]||[];
          return `<div class="card" style="margin-top:12px">
            <div class="eyebrow">${escape(m.brand)}</div>
            <h3 style="margin:4px 0 8px">${escape(m.name)}</h3>
            ${list.map(d=>{
              const isArg=/аргумент|тренинг|материал/i.test(d.kind||"");
              const locked=isArg && !unlocked;
              return `<div class="doc-mini">
                <b>${escape(d.title)}</b>
                <span>${escape(d.kind)} · ${escape(d.pages)}</span>''',
        '''        <div class="docs-page">${Object.values(MODELS).filter(x=>x.id!=="t7l"&&x.id!=="t4"&&x.id!=="tt9").map(m=>{
          const list=DOCS[m.id]||[];
          if(!list.length) return "";
          return `<div class="card docs-card">
            <div class="eyebrow">${escape(m.brand)}</div>
            <h3 style="margin:4px 0 8px">${escape(m.name)}</h3>
            ${list.map(d=>{
              const isArg=/аргумент|тренинг|материал/i.test(d.kind||"");
              const locked=isArg && !unlocked;
              return `<div class="doc-mini">
                <b>${escape(d.title)}</b>
                <span>${escape(d.kind)} · ${escape(d.pages)}<i class="doc-hint">${docFileHint(d)}</i></span>''',
        "docs list")
    html = sub(html,
        '''            }).join("")}
          </div>`;
        }).join("")}`;
    }''',
        '''            }).join("")}
          </div>`;
        }).join("")}</div>`;
    }''',
        "docs close")
    html = sub(html, '<details class="fleet-board">', '<details class="fleet-board terms-fold">', "fleet class")
    html = sub(html,
        '        tot+=2; if(d[car.id+"_km"]) on++; if(d[car.id+"_fuel"]) on++;',
        '        tot+=2; if(String(d[car.id+"_km"]==null?"":d[car.id+"_km"]).trim()) on++; { const fv=d[car.id+"_fuel"]; const fn=Number(fv); if(fv!=null && String(fv).trim()!=="" && Number.isFinite(fn) && fn>0) on++; }',
        "duty count")
    html = sub(html,
        '''      if(bar) bar.style.width=pct+"%";
      if(lab) lab.textContent=pct+"%";
    }''',
        '''      if(bar) bar.style.width=pct+"%";
      if(lab) lab.textContent=pct+"%";
      const eye=document.querySelector(".banner .eyebrow");
      if(eye && document.querySelector(".cl")) eye.textContent=p.on+" из "+p.tot;
    }''',
        "duty paint")
    html = sub(html,
        '''        const body=d[car.id+"_body"]||"ok";
        return `<article class="cl-car">
          <h3>${car.title}</h3>''',
        '''        const body=d[car.id+"_body"]||"";
        return `<article class="cl-car">
          <h3>${car.title}</h3>''',
        "duty body")
    html = sub(html,
        '''            <select data-duty="${car.id}_body">
              <option value="ok" ${body==="ok"?"selected":""}>чистый</option>''',
        '''            <select data-duty="${car.id}_body">
              <option value="" ${body?"":"selected"}>—</option>
              <option value="ok" ${body==="ok"?"selected":""}>чистый</option>''',
        "duty blank")
    html = sub(html, '{id:"t82",title:"Т8 2WD"},', '{id:"t82",title:"T8 2WD"},', "t82")
    html = sub(html, '{id:"t8",title:"Т8 4WD"},', '{id:"t8",title:"T8 4WD"},', "t8")
    html = sub(html, '{id:"t9",title:"Т9"},', '{id:"t9",title:"T9"},', "t9")
    boot = '''    if(state.authed && location.hash==="#sklad" && typeof stockApply==="function"){
      stockApply(stockReadStore()||{});
      view="stock"; state.section="stock";
    } else if(state.authed && location.hash==="#calc"){
      view="calc"; state.section="calc";
    }
    let stockScrollT=0;
    window.addEventListener("scroll", ()=>{
      if(view!=="stock" || typeof stockSyncHist!=="function") return;
      clearTimeout(stockScrollT);
      stockScrollT=setTimeout(stockSyncHist, 80);
    }, {passive:true});
    window.addEventListener("popstate", ()=>{
      if(document.getElementById("dutyPdfView")) return;
      if(location.hash==="#pdf") return;
      const st=history.state||{};
      if(st.tenetView==="stock" || location.hash==="#sklad"){
        if(typeof stockApply==="function") stockApply(stockReadStore()||st.stock);
        view="stock"; state.section="stock"; try{save();}catch(e){} render();
      } else if(st.tenetView==="calc" || location.hash==="#calc"){
        view="calc"; state.section="calc"; try{save();}catch(e){} render();
      }
    });
    try { render(); }'''
    html = sub(html, "    try { render(); }", boot, "boot")
    # base rules that otherwise keep square tiles / two-column expand
    html = html.replace(
        ".st-row.open{aspect-ratio:auto;grid-column:span 2;min-height:160px}",
        ".st-row.open{aspect-ratio:auto;grid-column:auto;min-height:0}",
    )
    html = html.replace(".st-acc:not([open]){aspect-ratio:1}", ".st-acc:not([open]){aspect-ratio:auto}")
    html = html.replace(".st-trim:not([open]){aspect-ratio:1}", ".st-trim:not([open]){aspect-ratio:auto}")
    html = html.replace(
        ".st-row{display:flex;flex-direction:column;aspect-ratio:1;",
        ".st-row{display:flex;flex-direction:column;aspect-ratio:auto;",
    )
    return html


def patch_stock_fn(text):
    if "function stock(" not in text:
        return text
    return patch_stock_logic(text, "stock-fn")


def patch_duty_file(text, label):
    text = sub(text, '{id:"t82",title:"Т8 2WD"}', '{id:"t82",title:"T8 2WD"}', label+" t82", optional=True)
    text = sub(text, '{id:"t8",title:"Т8 4WD"}', '{id:"t8",title:"T8 4WD"}', label+" t8", optional=True)
    text = sub(text, '{id:"t9",title:"Т9"}', '{id:"t9",title:"T9"}', label+" t9", optional=True)
    text = sub(text, 'const body=d[car.id+"_body"]||"ok";', 'const body=d[car.id+"_body"]||"";', label+" body", optional=True)
    text = sub(text,
        '''            <select data-duty="${car.id}_body">
              <option value="ok" ${body==="ok"?"selected":""}>чистый</option>''',
        '''            <select data-duty="${car.id}_body">
              <option value="" ${body?"":"selected"}>—</option>
              <option value="ok" ${body==="ok"?"selected":""}>чистый</option>''',
        label+" blank", optional=True)
    text = sub(text,
        '        tot+=2; if(d[car.id+"_km"]) on++; if(d[car.id+"_fuel"]) on++;',
        '        tot+=2; if(String(d[car.id+"_km"]==null?"":d[car.id+"_km"]).trim()) on++; { const fv=d[car.id+"_fuel"]; const fn=Number(fv); if(fv!=null && String(fv).trim()!=="" && Number.isFinite(fn) && fn>0) on++; }',
        label+" count", optional=True)
    text = sub(text,
        '''      if(bar) bar.style.width=pct+"%";
      if(lab) lab.textContent=pct+"%";
    }''',
        '''      if(bar) bar.style.width=pct+"%";
      if(lab) lab.textContent=pct+"%";
      const eye=document.querySelector(".banner .eyebrow");
      if(eye && document.querySelector(".cl")) eye.textContent=p.on+" из "+p.tot;
    }''',
        label+" paint", optional=True)
    return text


def patch_pages(text):
    line = "          if [ -f patch_cabinet_ui.py ]; then python3 patch_cabinet_ui.py || true; fi\n"
    if "patch_cabinet_ui.py" in text:
        print("pages already")
        return text
    needle = "          cp -f favicon.svg"
    if needle not in text:
        raise SystemExit("pages needle missing")
    return text.replace(needle, line + needle, 1)


def write(path, text):
    path.write_text(text, encoding="utf-8")
    print("wrote", path, len(text))


def main():
    index = Path("index.html")
    if index.exists() and index.stat().st_size > 1000:
        write(index, patch_index(index.read_text(encoding="utf-8")))
    site = Path("_site/index.html")
    if site.exists() and site.stat().st_size > 1000:
        # deployed copy is overwritten from root index during Pages; still keep local _site usable
        try:
            write(site, patch_index(site.read_text(encoding="utf-8")))
        except SystemExit as e:
            print("site skip", e)
    sf = Path("stock-fn.js")
    if sf.exists():
        write(sf, patch_stock_fn(sf.read_text(encoding="utf-8")))
    for name in ("duty-fn.js", "duty-ui-snippet.js", "duty-overlay.js"):
        p = Path(name)
        if p.exists():
            write(p, patch_duty_file(p.read_text(encoding="utf-8"), name))
    yml = Path(".github/workflows/pages.yml")
    if yml.exists():
        write(yml, patch_pages(yml.read_text(encoding="utf-8")))


if __name__ == "__main__":
    main()
