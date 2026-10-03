#!/usr/bin/env python3
"""Priority scales are in terms-calc-ui-a.js. This adds the live Leaderboard."""
from pathlib import Path

CSS = """
.prio-scales{display:flex;flex-direction:column;gap:10px;margin:4px 0 16px}
.prio-people{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.prio-scale{background:#fff;border:1px solid var(--border);border-radius:12px;padding:10px 12px}
.prio-scale .row{display:flex;justify-content:space-between;gap:8px;align-items:baseline;font-size:14px}
.prio-scale .row span{color:#6d6458;font-weight:650;font-variant-numeric:tabular-nums}
.prio-scale.team{background:#1c1a17;color:#fff;border-color:#1c1a17}
.prio-scale.team .row span{color:#e7d7c3}
.prio-track{height:8px;border-radius:999px;background:#f3eadc;margin-top:8px;overflow:hidden}
.prio-scale.team .prio-track{background:rgba(255,255,255,.16)}
.prio-fill{height:100%;border-radius:999px;background:#8a6840;width:0}
.prio-scale.team .prio-fill{background:#e7d7c3}
.prio-scale.won .prio-fill{background:#2e7d32}
.prio-scale.team.won .prio-fill{background:#b7e0b2}
.lb-table{width:100%;border-collapse:collapse;font-size:13px}
.lb-table th,.lb-table td{padding:8px 8px;border-bottom:1px solid var(--border);text-align:right;white-space:nowrap}
.lb-table th:first-child,.lb-table td:first-child,.lb-table th:nth-child(2),.lb-table td:nth-child(2){text-align:left}
.lb-table th{font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:#6d6458}
.lb-row.me{background:#fbf7f1}
.lb-place{font-weight:800}
.lb-feed{display:flex;flex-direction:column;gap:8px;margin-top:8px}
.lb-hit{display:flex;justify-content:space-between;gap:10px;padding:10px 12px;border:1px solid var(--border);border-radius:12px;background:#fff}
.lb-hit b{display:block}
.lb-hit small{color:#6d6458}
@media(max-width:700px){.prio-people{grid-template-columns:1fr}}
"""

JS = r'''
    const BOARD_OCT = "1QJ0Wng-oItBWPDw03PKZ-hTAteaYOvUQVOm-6pautVc";
    const BOARD_SEP = "1PvC2EbyeIIewE2PFPKYOI7dxZAEbGAAiwy6jtxLM5kg";
    const BOARD_ROSTER = ["Ахмадуллин","Велиджанов","Демьянов","Лавров","Сидоров","Спицын","Тальков","Павлова","Извеков"];
    let boardTimer = 0;
    let boardMode = "day";
    let boardCache = null;
    function boardSurname(name){
      const s=String(name||"").trim();
      return s?s.split(/\s+/)[0]:"";
    }
    function boardDays(mm, last){
      const out=[];
      for(let d=1; d<=last; d++) out.push((d<10?"0":"")+d+"."+mm);
      return out;
    }
    function boardOctLast(){
      const now=new Date();
      if(now.getFullYear()===2026 && now.getMonth()===9) return now.getDate();
      if(now.getFullYear()>2026 || (now.getFullYear()===2026 && now.getMonth()>9)) return 31;
      return 0;
    }
    function boardWhen(cell){
      if(!cell) return "";
      if(Object.prototype.toString.call(cell.v)==="[object Date]") return String(cell.f||"");
      const f=String(cell.f||"");
      if(/^\d{1,2}\.\d{1,2}\.\d{4}/.test(f)) return f;
      const s=cell.v==null?"":String(cell.v);
      if(/^\d{1,2}\.\d{1,2}\.\d{4}/.test(s)) return s;
      const n=Number(cell.v);
      if(n>20000 && n<80000){
        const d=new Date(Math.round((n-25569)*86400000));
        const p=x=>x<10?"0"+x:String(x);
        return p(d.getUTCDate())+"."+p(d.getUTCMonth()+1)+"."+d.getUTCFullYear()+" "+p(d.getUTCHours())+":"+p(d.getUTCMinutes());
      }
      return "";
    }
    function boardFetch(fileId, sheet){
      return new Promise(resolve=>{
        const cb="boardCb_"+String(fileId).slice(0,4)+"_"+sheet.replace(/\W/g,"_");
        const s=document.createElement("script");
        const timer=setTimeout(()=>{ cleanup(); resolve({table:{rows:[]}}); }, 15000);
        function cleanup(){
          clearTimeout(timer);
          try{ delete window[cb]; }catch(e){}
          if(s.parentNode) s.parentNode.removeChild(s);
        }
        window[cb]=function(res){ cleanup(); resolve(res||{table:{rows:[]}}); };
        s.onerror=()=>{ cleanup(); resolve({table:{rows:[]}}); };
        s.src="https://docs.google.com/spreadsheets/d/"+fileId+"/gviz/tq?tqx=out:json;responseHandler:"+cb+"&sheet="+encodeURIComponent(sheet)+"&t="+Date.now();
        document.head.appendChild(s);
      });
    }
    async function boardFetchAll(fileId, days){
      const packs=[];
      for(let i=0;i<days.length;i+=6){
        const part=await Promise.all(days.slice(i,i+6).map(sheet=>boardFetch(fileId, sheet)));
        part.forEach(p=>packs.push(p));
      }
      return packs;
    }
    function boardRows(res){
      const rows=((res||{}).table||{}).rows||[];
      const out=[];
      rows.forEach(row=>{
        const c=row && row.c || [];
        const when=boardWhen(c[0]);
        if(!/^\d{2}\.\d{2}\.\d{4}/.test(when)) return;
        const text=i=>{
          const cell=c[i]||{};
          if(cell.f!=null && cell.f!=="") return String(cell.f);
          if(cell.v==null) return "";
          return String(cell.v);
        };
        const flag=i=>{
          const cell=c[i]||{};
          return cell.v===1 || cell.v==="1" ? 1 : 0;
        };
        const who=boardSurname(text(3));
        if(!who) return;
        out.push({
          when, who, client:text(1), model:text(4),
          visit:flag(5), call:flag(6), web:flag(7), meet:flag(8), service:flag(9),
          td:flag(10), contract:flag(11), issue:flag(12), note:text(13)
        });
      });
      return out;
    }
    function boardRank(rows){
      const blank=()=>({name:"",traffic:0,visit:0,call:0,web:0,meet:0,service:0,td:0,contract:0,issue:0});
      const map={};
      BOARD_ROSTER.forEach(n=>{ const p=blank(); p.name=n; map[n]=p; });
      rows.forEach(r=>{
        if(!map[r.who]){ const p=blank(); p.name=r.who; map[r.who]=p; }
        const p=map[r.who];
        if(r.visit||r.call||r.web) p.traffic++;
        p.visit+=r.visit; p.call+=r.call; p.web+=r.web; p.meet+=r.meet; p.service+=r.service;
        p.td+=r.td; p.contract+=r.contract; p.issue+=r.issue;
      });
      const list=Object.keys(map).map(k=>map[k]);
      list.sort((a,b)=>b.issue-a.issue || b.contract-a.contract || b.td-a.td || b.visit-a.visit || b.traffic-a.traffic || a.name.localeCompare(b.name,"ru"));
      const sum=list.reduce((s,p)=>({
        traffic:s.traffic+p.traffic, visit:s.visit+p.visit, td:s.td+p.td, contract:s.contract+p.contract, issue:s.issue+p.issue
      }), {traffic:0,visit:0,td:0,contract:0,issue:0});
      return {list, sum};
    }
    function boardTable(rows, eyebrow, title){
      const rank=boardRank(rows);
      const sum=rank.sum;
      return `<div class="card" style="margin-top:12px"><p class="eyebrow">${escape(eyebrow)}</p><h3 style="margin:4px 0 8px">${escape(title)} · ${sum.issue} выдач · ${sum.contract} контрактов · ${sum.td} тест-драйвов · ${sum.traffic} первичных</h3><div class="tune-scroll"><table class="lb-table"><thead><tr><th>#</th><th>Менеджер</th><th>Трафик</th><th>Визит</th><th>Звонок</th><th>Интернет</th><th>Встреча</th><th>ТД</th><th>Контракт</th><th>Выдача</th></tr></thead><tbody>`+
        rank.list.map((p,i)=>`<tr class="lb-row"><td class="lb-place">${i+1}</td><td><b>${escape(p.name)}</b></td><td>${p.traffic}</td><td>${p.visit}</td><td>${p.call}</td><td>${p.web}</td><td>${p.meet}</td><td>${p.td}</td><td>${p.contract}</td><td>${p.issue}</td></tr>`).join("")+
        `</tbody></table></div></div>`;
    }
    function boardKind(r){
      const bits=[];
      if(r.issue) bits.push("выдача");
      if(r.contract) bits.push("контракт");
      if(r.td) bits.push("тест-драйв");
      if(r.visit) bits.push("визит");
      if(r.call) bits.push("звонок");
      if(r.web) bits.push("интернет");
      if(r.meet) bits.push("встреча");
      if(r.service) bits.push("сервис");
      return bits.join(" · ")||"запись";
    }
    function boardTape(rows){
      return `<div class="card" style="margin-top:12px"><p class="eyebrow">Сегодня</p><h3 style="margin:4px 0 8px">Лента</h3><div class="lb-feed">`+
        (rows.length?rows.slice().reverse().map(r=>`<div class="lb-hit"><div><b>${escape(r.client||"Без имени")} · ${escape(r.model||"—")}</b><small>${escape(r.who)} · ${escape(boardKind(r))}${r.note?" · "+escape(r.note):""}</small></div><small>${escape(String(r.when||"").slice(11,16))}</small></div>`).join(""):`<p class="lead">За сегодня записей пока нет.</p>`)+
        `</div></div>`;
    }
    function boardHtml(cache){
      const today=new Date();
      const key=(today.getDate()<10?"0":"")+today.getDate()+"."+((today.getMonth()+1)<10?"0":"")+(today.getMonth()+1);
      const note=`<p class="tune-note">Обновлено ${escape(cache.stamp)}. Рейтинг: выдача, затем контракт, тест-драйв, визит, трафик.</p>`;
      if(boardMode==="prev") return note+boardTable(cache.sep, "Сентябрь", "Сентябрь");
      if(boardMode==="month") return note+boardTable(cache.oct, "Месяц", "Октябрь");
      const dayRows=(cache.oct||[]).filter(r=>String(r.when||"").indexOf(key)===0);
      return note+boardTable(dayRows, "Сегодня", key)+boardTape(dayRows);
    }
    async function boardLoad(){
      const root=document.getElementById("boardRoot");
      if(!root || view!=="board") return;
      try{
        if(!boardCache){
          root.innerHTML=`<div class="card"><p>Загружаю трафик…</p></div>`;
          const octPacks=await boardFetchAll(BOARD_OCT, boardDays("10", boardOctLast()));
          const sepPacks=await boardFetchAll(BOARD_SEP, boardDays("09", 30));
          const oct=[], sep=[];
          octPacks.forEach(p=>boardRows(p).forEach(r=>oct.push(r)));
          sepPacks.forEach(p=>boardRows(p).forEach(r=>sep.push(r)));
          boardCache={oct, sep, stamp:new Date().toLocaleString("ru-RU",{hour:"2-digit",minute:"2-digit",day:"2-digit",month:"2-digit"})};
        }
        root.innerHTML=boardHtml(boardCache);
      }catch(err){
        root.innerHTML=`<div class="card"><p>Не удалось прочитать трафик. ${escape(err&&err.message||"")}</p><button class="btn ivory" type="button" id="boardRetry">Ещё раз</button></div>`;
        const b=document.getElementById("boardRetry");
        if(b) b.onclick=()=>{ boardCache=null; boardLoad(); };
      }
    }
    function boardChips(){
      const items=[["day","Сегодня"],["month","Месяц"],["prev","Сентябрь"]];
      return `<div class="study-pick st-filters">`+items.map(([id,lab])=>`<button type="button" class="chip ${boardMode===id?"on":""}" data-board-mode="${id}">${lab}</button>`).join("")+`</div>`;
    }
    function board(){
      if(needAuth()) return login();
      clearInterval(boardTimer);
      boardTimer=setInterval(()=>{ if(view==="board"){ boardCache=null; boardLoad(); } }, 60000);
      setTimeout(()=>{
        document.querySelectorAll("[data-board-mode]").forEach(b=>{
          b.onclick=()=>{
            boardMode=b.dataset.boardMode||"day";
            document.querySelectorAll("[data-board-mode]").forEach(x=>x.classList.toggle("on", x===b));
            boardLoad();
          };
        });
        boardLoad();
      }, 40);
      return banner("Leaderboard","Трафик · онлайн","TENET")+`
        <p class="lead">Сегодня и месяц — из «Трафик октябрь». Сентябрь — из «Трафик сентябрь».</p>
        ${boardChips()}
        <div id="boardRoot"><div class="card"><p>Загружаю таблицу…</p></div></div>`;
    }
'''

def apply(path: Path):
    if not path.exists() or path.stat().st_size < 1000:
        print("skip", path)
        return
    html = path.read_text(encoding="utf-8")
    if ".prio-fill{" not in html:
        html = html.replace("</style>", CSS + "</style>", 1)
        print("css", path)
    card = '["board","L","Leaderboard","Трафик, контракты и выдача отдела"]'
    if '["board","L","Leaderboard"' not in html:
        for needle in (
            '["calc","%","Калькулятор","Платёж и калькулятор КМ от 10.09"],',
            '["calc","%","Калькулятор","Ежемесячный платёж с выбранной комплектации"],',
        ):
            if needle in html:
                html = html.replace(needle, needle + "\n        " + card + ",", 1)
                print("card", path)
                break
        else:
            print("hub card anchor missing", path)
    if "function board()" not in html:
        anchor = "    function render(){"
        if anchor not in html:
            print("render anchor missing", path)
        else:
            html = html.replace(anchor, JS + anchor, 1)
            print("fn", path)
    elif "const BOARD_SEP" not in html:
        a = html.find("    const BOARD_SHEET")
        if a < 0:
            a = html.find("    const BOARD_OCT")
        b = html.find("    function render(){", a if a >= 0 else 0)
        if a >= 0 and b > a:
            html = html[:a] + JS + html[b:]
            print("fn replaced", path)
    if "function board()" in html and "hub,board," not in html and "const map={login,hub," in html:
        html = html.replace("const map={login,hub,", "const map={login,hub,board,", 1)
        print("map", path)
    path.write_text(html, encoding="utf-8")

if __name__ == "__main__":
    for name in ("index.html", "_site/index.html"):
        apply(Path(name))
