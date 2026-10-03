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
    const BOARD_SHEET = "1QJ0Wng-oItBWPDw03PKZ-hTAteaYOvUQVOm-6pautVc";
    const BOARD_ROSTER = ["Ахмадуллин","Велиджанов","Демьянов","Лавров","Сидоров","Спицын","Тальков","Павлова","Извеков"];
    let boardTimer = 0;
    function boardSurname(name){
      const s=String(name||"").trim();
      return s?s.split(/\s+/)[0]:"";
    }
    function boardDays(){
      const now=new Date();
      let last=31;
      if(now.getFullYear()===2026 && now.getMonth()===9) last=now.getDate();
      else if(now.getFullYear()<2026 || (now.getFullYear()===2026 && now.getMonth()<9)) last=0;
      const out=[];
      for(let d=1; d<=last; d++) out.push((d<10?"0":"")+d+".10");
      return out;
    }
    function boardFetch(sheet){
      return new Promise((resolve, reject)=>{
        const cb="boardCb_"+sheet.replace(/\W/g,"_");
        const s=document.createElement("script");
        const timer=setTimeout(()=>{ cleanup(); reject(new Error(sheet)); }, 12000);
        function cleanup(){
          clearTimeout(timer);
          try{ delete window[cb]; }catch(e){}
          if(s.parentNode) s.parentNode.removeChild(s);
        }
        window[cb]=function(res){ cleanup(); resolve(res||{}); };
        s.onerror=()=>{ cleanup(); reject(new Error(sheet)); };
        s.src="https://docs.google.com/spreadsheets/d/"+BOARD_SHEET+"/gviz/tq?tqx=out:json;responseHandler:"+cb+"&sheet="+encodeURIComponent(sheet)+"&t="+Date.now();
        document.head.appendChild(s);
      });
    }
    function boardRows(res){
      const rows=((res||{}).table||{}).rows||[];
      const out=[];
      rows.forEach(row=>{
        const c=row && row.c || [];
        const t=c[0]||{};
        const isDate=Object.prototype.toString.call(t.v)==="[object Date]" || /^\d{2}\.\d{2}\.\d{4}/.test(String(t.f||""));
        if(!isDate) return;
        const text=i=>{
          const cell=c[i]||{};
          if(cell.f!=null && cell.f!=="") return String(cell.f);
          if(cell.v==null) return "";
          if(Object.prototype.toString.call(cell.v)==="[object Date]") return String(cell.f||"");
          return String(cell.v);
        };
        const flag=i=>{
          const cell=c[i]||{};
          return cell.v===1 || cell.v==="1" ? 1 : 0;
        };
        const who=boardSurname(text(3));
        if(!who) return;
        out.push({
          when:text(0), who, client:text(1), model:text(4),
          visit:flag(5), call:flag(6), web:flag(7), meet:flag(8), service:flag(9),
          td:flag(10), contract:flag(11), issue:flag(12), note:text(13)
        });
      });
      return out;
    }
    function boardHtml(rows, stamp){
      const map={};
      BOARD_ROSTER.forEach(n=>{ map[n]={name:n,traffic:0,visit:0,call:0,web:0,meet:0,service:0,td:0,contract:0,issue:0}; });
      rows.forEach(r=>{
        if(!map[r.who]) map[r.who]={name:r.who,traffic:0,visit:0,call:0,web:0,meet:0,service:0,td:0,contract:0,issue:0};
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
      const head=`<div class="card"><p class="eyebrow">Октябрь · файл «Трафик октябрь»</p><h3 style="margin:4px 0 8px">Отдел · ${sum.issue} выдач · ${sum.contract} контрактов · ${sum.td} тест-драйвов · ${sum.traffic} первичных</h3><p class="tune-note">Обновлено ${escape(stamp)}. Рейтинг: выдача, затем контракт, тест-драйв, визит, трафик. Телефоны не показываем.</p><div class="tune-scroll"><table class="lb-table"><thead><tr><th>#</th><th>Менеджер</th><th>Трафик</th><th>Визит</th><th>Звонок</th><th>Интернет</th><th>Встреча</th><th>ТД</th><th>Контракт</th><th>Выдача</th></tr></thead><tbody>`+
        list.map((p,i)=>`<tr class="lb-row"><td class="lb-place">${i+1}</td><td><b>${escape(p.name)}</b></td><td>${p.traffic}</td><td>${p.visit}</td><td>${p.call}</td><td>${p.web}</td><td>${p.meet}</td><td>${p.td}</td><td>${p.contract}</td><td>${p.issue}</td></tr>`).join("")+
        `</tbody></table></div></div>`;
      const today=new Date();
      const key=(today.getDate()<10?"0":"")+today.getDate()+"."+((today.getMonth()+1)<10?"0":"")+(today.getMonth()+1);
      let feed=rows.filter(r=>String(r.when||"").indexOf(key)===0);
      let feedTitle="Сегодня";
      if(!feed.length && rows.length){
        const last=String(rows[rows.length-1].when||"").slice(0,5);
        feed=rows.filter(r=>String(r.when||"").indexOf(last)===0);
        feedTitle="Последний день с записями · "+last;
      }
      const kind=r=>{
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
      };
      const tape=`<div class="card" style="margin-top:12px"><p class="eyebrow">${escape(feedTitle)}</p><h3 style="margin:4px 0 8px">Живая лента</h3><div class="lb-feed">`+
        (feed.length?feed.slice().reverse().map(r=>`<div class="lb-hit"><div><b>${escape(r.client||"Без имени")} · ${escape(r.model||"—")}</b><small>${escape(r.who)} · ${escape(kind(r))}${r.note?" · "+escape(r.note):""}</small></div><small>${escape(String(r.when||"").slice(11,16))}</small></div>`).join(""):`<p class="lead">Записей пока нет.</p>`)+
        `</div></div>`;
      return head+tape;
    }
    async function boardLoad(){
      const root=document.getElementById("boardRoot");
      if(!root || view!=="board") return;
      try{
        const days=boardDays();
        const packs=await Promise.all(days.map(boardFetch));
        const rows=[];
        packs.forEach(p=>boardRows(p).forEach(r=>rows.push(r)));
        const stamp=new Date().toLocaleString("ru-RU",{hour:"2-digit",minute:"2-digit",day:"2-digit",month:"2-digit"});
        root.innerHTML=boardHtml(rows, stamp);
      }catch(err){
        root.innerHTML=`<div class="card"><p>Не удалось прочитать «Трафик октябрь». ${escape(err&&err.message||"")}</p><button class="btn ivory" data-go="board" type="button">Ещё раз</button></div>`;
        document.querySelectorAll("[data-go]").forEach(b=>b.onclick=()=>{ view=b.dataset.go; state.section=view; try{save();}catch(e){} render(); });
      }
    }
    function board(){
      if(needAuth()) return login();
      clearInterval(boardTimer);
      boardTimer=setInterval(()=>{ if(view==="board") boardLoad(); }, 60000);
      setTimeout(boardLoad, 40);
      return banner("Leaderboard","Трафик октябрь · онлайн","TENET")+`
        <p class="lead">Вся работа отдела из файла «Трафик октябрь». Цифры подтягиваются сами, раз в минуту.</p>
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
    if 'data-go="board"' not in html and card not in html:
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
    if "function board()" in html and "hub,board," not in html and "const map={login,hub," in html:
        html = html.replace("const map={login,hub,", "const map={login,hub,board,", 1)
        print("map", path)
    path.write_text(html, encoding="utf-8")

if __name__ == "__main__":
    for name in ("index.html", "_site/index.html"):
        apply(Path(name))
