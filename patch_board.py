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


.lb-rep-bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:6;background:var(--bg);padding:6px 0 8px}
.lb-rep-bar span{display:flex;gap:6px}
.lb-zoom{overflow:auto;-webkit-overflow-scrolling:touch}
.lb-sheet{width:1480px;background:#fff;border:1px solid var(--border);border-radius:12px;padding:16px 14px 12px}
.lb-rep-h{margin:0 0 6px;font-size:12px;font-weight:750;letter-spacing:.04em;text-transform:uppercase;color:#6d6458}
.lb-blocks{display:flex;flex-direction:column;gap:18px}
.lb-block{border:1px solid #e4dfd4;border-radius:14px;padding:12px 12px 8px}
.lb-block.a{background:#f7f4ee;border-color:#d9cbb6}
.lb-block.b{background:#f3f6f1;border-color:#c9d7c4;align-self:flex-start}
.lb-pair{display:flex;gap:18px;align-items:flex-start}
.lb-block.c{background:#f7f1e6;border-color:#e0cba8;flex:1}
.lb-block.d{background:#eef3f6;border-color:#c5d4de;flex:1}
.lb-rep tr.sum td{font-weight:800;border-top:2px solid #1c1a17}
.lb-bad{color:#c62828;font-weight:800}
.lb-mid{color:#b8860b;font-weight:800}
.lb-ok{color:#2e7d32;font-weight:800}
.lb-fold{display:none}
.lb-fold.open{display:block}
.lb-fold-btn{cursor:pointer}
.lb-fold-btn>b::before{content:"▸ ";color:#8a6840}
.lb-fold-btn.open>b::before{content:"▾ "}
.lb-line.sub>b{font-weight:650}
.lb-fold-empty{margin:0;padding:6px 0 8px 8px;color:#6d6458;font-size:12px}
tr.lb-fold-row{display:none}
tr.lb-fold-row.open{display:table-row}
.lb-rep{width:100%;border-collapse:collapse;font-size:13px}
.lb-rep.lb-rep-sm{width:auto}
.lb-rep.lb-rep-sm th,.lb-rep.lb-rep-sm td{width:1%;padding-left:10px;padding-right:10px}
.lb-rep th,.lb-rep td{border-bottom:1px solid #e4dfd4;padding:6px 4px;text-align:right;white-space:nowrap}
.lb-rep th{white-space:normal;line-height:1.15;vertical-align:bottom}
.lb-rep th:first-child,.lb-rep td:first-child{text-align:left}
.lb-rep th{font-size:10px;letter-spacing:.03em;text-transform:uppercase;color:#6d6458;font-weight:700}
.lb-rep tr.other td{color:#6d6458}
.lb-rep-note{margin:8px 0 0;font-size:11px;color:#6d6458}

.lb-phone{display:none}
.lb-sum{margin:0 0 8px;color:#6d6458;font-size:13px}
.lb-card h3{margin:2px 0 4px}
.lb-hit{display:block}
.lb-hit-top{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.lb-feed-label{margin:12px 0 0;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#6d6458;font-weight:700}
.lb-scale{display:grid;grid-template-columns:repeat(var(--n,4),minmax(0,1fr));gap:4px;margin-top:8px}
.lb-scale span{min-width:0;font-size:10px;line-height:1.15;text-align:center;color:#8a8175;background:#f3eadc;border-radius:7px;padding:6px 2px}
.lb-scale span.on{color:#fff;font-weight:700}
.lb-scale span.on.s0{background:#c4a574;color:#1c1a17}
.lb-scale span.on.s1{background:#8a6840}
.lb-scale span.on.s2{background:#5c4630}
.lb-scale span.on.s3{background:#1c1a17}
.lb-scale span.on.s4{background:#1c1a17}
.lb-scale span:last-child.on.now{background:#2e7d32;color:#fff}
@media(max-width:720px){
  .lb-desk{display:none}
  .lb-phone{display:block}
  .lb-modes{overflow:visible;flex-wrap:wrap;padding-bottom:0}
  .lb-card{margin-top:8px;padding:12px 10px 8px}
  .lb-card h3{font-size:18px;line-height:1.15}
  .lb-sum{font-size:12px;line-height:1.3;margin:0 0 8px}
  .lb-key,.lb-line{display:grid;grid-template-columns:104px minmax(0,1fr) 7px minmax(0,1fr) minmax(0,1fr) minmax(0,1fr) 7px minmax(0,1fr) minmax(0,1fr) 7px minmax(0,1fr) minmax(0,1fr);column-gap:0;align-items:center}
  .lb-key s,.lb-line s{display:block;height:16px;border-left:1px solid #cfc6b8;text-decoration:none}
  .lb-line>i,.lb-key>span:not(:first-child){padding:4px 0}
  .lb-line>i.g2,.lb-key>span.g2{background:#f7f1e6}
  .lb-line>i.g3,.lb-key>span.g3{background:#f3eee6}
  .lb-line>i.g4,.lb-key>span.g4{background:#eef3ee}
  .lb-key{color:#6d6458;font-size:9px;font-weight:700;letter-spacing:0;text-transform:uppercase;padding-bottom:2px;text-align:center}
  .lb-key>span:first-child{text-align:left}
  .lb-line{padding:7px 0;border-bottom:1px solid var(--border);text-align:center;font-variant-numeric:tabular-nums;font-size:14px;font-weight:750}
  .lb-line>b{font-size:13px;font-weight:750;text-align:left;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .lb-line>i{font-style:normal}
  .lb-line>i:last-child{font-weight:800}
  .lb-line.other>b,.lb-line.other>i{color:#6d6458}
}
"""

JS = r'''
    const BOARD_OCT = "1QJ0Wng-oItBWPDw03PKZ-hTAteaYOvUQVOm-6pautVc";
    const BOARD_SEP = "1PvC2EbyeIIewE2PFPKYOI7dxZAEbGAAiwy6jtxLM5kg";
    const BOARD_ROSTER = ["Ахмадуллин","Велиджанов","Демьянов","Лавров","Сидоров","Спицын","Тальков"];
    const BOARD_ROSTER_SEP = ["Ахмадуллин","Коропец","Демьянов","Лавров","Сидоров","Спицын","Тальков"];
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
    const BOARD_PLAN = 10;
    const BOARD_PLAN_TEAM = 70;
    function boardBlank(){
      return {name:"",traffic:0,visit:0,call:0,web:0,meet:0,service:0,td:0,contract:0,issue:0,visitContract:0,callVisit:0,callContract:0,webVisit:0,webContract:0,other:false,people:[]};
    }
    function boardAdd(p, r){
      if(r.visit||r.call||r.web) p.traffic++;
      p.visit+=r.visit; p.call+=r.call; p.web+=r.web; p.meet+=r.meet; p.service+=r.service;
      p.td+=r.td; p.contract+=r.contract; p.issue+=r.issue;
      if(r.visit&&r.contract) p.visitContract++;
      if(r.call&&r.visit) p.callVisit++;
      if(r.call&&r.contract) p.callContract++;
      if(r.web&&r.visit) p.webVisit++;
      if(r.web&&r.contract) p.webContract++;
    }
    function boardPct(num, den){
      if(!den) return "–";
      const v=100*num/den;
      const s=Math.abs(v-Math.round(v))<0.05?String(Math.round(v)):v.toFixed(1).replace(".",",");
      return s+"%";
    }
    function boardCmp(a,b){
      return b.issue-a.issue || b.contract-a.contract || b.td-a.td || b.visit-a.visit || b.traffic-a.traffic || a.name.localeCompare(b.name,"ru");
    }
    function boardRank(rows, roster){
      const blank=boardBlank;
      const map={};
      (roster||BOARD_ROSTER).forEach(n=>{ const p=blank(); p.name=n; map[n]=p; });
      const other=blank(); other.name="Другие"; other.other=true;
      const extras={};
      rows.forEach(r=>{
        if(map[r.who]) boardAdd(map[r.who], r);
        else {
          if(!extras[r.who]){ extras[r.who]=blank(); extras[r.who].name=r.who; }
          boardAdd(extras[r.who], r);
          boardAdd(other, r);
        }
      });
      other.people=Object.keys(extras).map(k=>extras[k]).sort(boardCmp);
      const list=Object.keys(map).map(k=>map[k]);
      list.sort(boardCmp);
      list.push(other);
      const sum=list.reduce((s,p)=>({
        traffic:s.traffic+p.traffic, visit:s.visit+p.visit, td:s.td+p.td, contract:s.contract+p.contract, issue:s.issue+p.issue
      }), {traffic:0,visit:0,td:0,contract:0,issue:0});
      return {list, sum};
    }
    function boardLine(p, sub){
      const n=[p.traffic,p.visit,p.call,p.web,p.meet,p.td,p.contract,p.issue];
      const c=(v,g)=>`<i class="g${g}">${v}</i>`;
      const cls=(p.other?" other lb-fold-btn":"")+(sub?" sub":"");
      const attr=p.other?` data-lb-fold="phone"`:"";
      return `<div class="lb-line${cls}"${attr}><b>${escape(p.name)}</b>${c(n[0],1)}<s></s>${c(n[2],2)}${c(n[1],2)}${c(n[3],2)}<s></s>${c(n[4],3)}${c(n[5],3)}<s></s>${c(n[6],4)}${c(n[7],4)}</div>`;
    }
    function boardDeskCells(p){
      return `<td>${p.traffic}</td><td>${p.visit}</td><td>${p.call}</td><td>${p.web}</td><td>${p.meet}</td><td>${p.td}</td><td>${p.contract}</td><td>${p.issue}</td>`;
    }
    function boardTable(rows, eyebrow, title, roster){
      const rank=boardRank(rows, roster);
      const sum=rank.sum;
      const body=rank.list.map((p,i)=>{
        const main=`<tr class="lb-row${p.other?" other lb-fold-btn":""}"${p.other?` data-lb-fold="desk"`:""}><td class="lb-place">${p.other?"—":i+1}</td><td><b>${escape(p.name)}</b></td>${boardDeskCells(p)}</tr>`;
        if(!p.other) return main;
        const kids=(p.people||[]).map(x=>`<tr class="lb-row lb-fold-row" data-lb-panel="desk"><td></td><td><b>${escape(x.name)}</b></td>${boardDeskCells(x)}</tr>`).join("")
          || `<tr class="lb-fold-row" data-lb-panel="desk"><td></td><td colspan="9">Нет других менеджеров</td></tr>`;
        return main+kids;
      }).join("");
      const phone=rank.list.map(p=>{
        if(!p.other) return boardLine(p);
        const kids=(p.people||[]).map(x=>boardLine(x,true)).join("") || `<p class="lb-fold-empty">Нет других менеджеров</p>`;
        return boardLine(p)+`<div class="lb-fold" data-lb-panel="phone">${kids}</div>`;
      }).join("");
      return `<div class="card lb-card"><p class="eyebrow">${escape(eyebrow)}</p><h3>${escape(title)}</h3><p class="lb-sum">${sum.issue} выдач · ${sum.contract} контрактов · ${sum.td} тест-драйвов · ${sum.traffic} первичных</p><div class="lb-desk tune-scroll"><table class="lb-table"><thead><tr><th>#</th><th>Менеджер</th><th>Трафик</th><th>Визит</th><th>Звонок</th><th>Интернет</th><th>Встреча</th><th>ТД</th><th>Контракт</th><th>Выдача</th></tr></thead><tbody>${body}</tbody></table></div><div class="lb-phone" data-lb="groups"><div class="lb-key"><span></span><span class="g1">Тр</span><s></s><span class="g2">З</span><span class="g2">В</span><span class="g2">И</span><s></s><span class="g3">Вс</span><span class="g3">ТД</span><s></s><span class="g4">К</span><span class="g4">Вдч</span></div>${phone}</div></div>`;
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
    function boardDayKey(shift){
      const d=new Date();
      d.setHours(12,0,0,0);
      d.setDate(d.getDate()+shift);
      const dd=d.getDate(), mo=d.getMonth()+1;
      return (dd<10?"0":"")+dd+"."+(mo<10?"0":"")+mo;
    }
    function boardSlice(cache, key){
      const src=key.slice(3)==="09"?(cache.sep||[]):(cache.oct||[]);
      return src.filter(r=>String(r.when||"").indexOf(key)===0);
    }
    function boardScale(r){
      const far=r.issue?4:r.contract?3:r.td?2:r.visit?1:0;
      let labels, done;
      if(r.visit){
        labels=["Визит","ТД","Контракт","Выдача"];
        done=Math.max(far,1);
      }else if(r.call||r.web){
        labels=[r.call?"Звонок":"Интернет","Визит","ТД","Контракт","Выдача"];
        done=far+1;
      }else{
        labels=["Запись","ТД","Контракт","Выдача"];
        done=far?far:1;
      }
      return `<div class="lb-scale" style="--n:${labels.length}">`+labels.map((lab,i)=>`<span class="${i<done?"on s"+i:""}${i===done-1?" now":""}">${lab}</span>`).join("")+`</div>`;
    }
    function boardHit(r){
      return `<div class="lb-hit"><div class="lb-hit-top"><div><b>${escape(r.who||"—")} · ${escape(r.model||"—")}</b><small>${escape(r.client||"Без имени")} · ${escape(boardKind(r))}${r.note?" · "+escape(r.note):""}</small></div><small>${escape(String(r.when||"").slice(11,16))}</small></div>${boardScale(r)}</div>`;
    }
    function boardTape(rows, title){
      const byTime=(a,b)=>String(b.when||"").localeCompare(String(a.when||""));
      const visits=rows.filter(r=>r.visit).sort(byTime);
      const leads=rows.filter(r=>!r.visit&&(r.call||r.web)).sort(byTime);
      const rest=rows.filter(r=>!r.visit&&!r.call&&!r.web).sort(byTime);
      const block=(lab,list)=>list.length?`<p class="lb-feed-label">${lab}</p>`+list.map(boardHit).join(""):"";
      const body=rows.length?block("Визиты",visits)+block("Звонки и интернет",leads)+block("Остальное",rest):`<p class="lead">Записей пока нет.</p>`;
      return `<div class="card" style="margin-top:12px"><p class="eyebrow">${escape(title)}</p><h3 style="margin:4px 0 8px">Лента</h3><div class="lb-feed">${body}</div></div>`;
    }
    function boardHtml(cache){
      const note=`<p class="tune-note">Обновлено ${escape(cache.stamp)}. Рейтинг: выдача, затем контракт, тест-драйв, визит, трафик.</p>`;
      const btn=`<div style="margin:12px 0"><button class="btn ivory" type="button" id="boardOpenReport">Расширенный отчёт</button></div>`;
      if(boardMode==="prev") return note+boardTable(cache.sep, "Предыдущий месяц", "Сентябрь", BOARD_ROSTER_SEP)+btn;
      if(boardMode==="month") return note+boardTable(cache.oct, "Месяц", "Октябрь")+btn;
      const yest=boardMode==="yday";
      const key=boardDayKey(yest?-1:0);
      const rows=boardSlice(cache, key);
      const label=yest?"Вчера":"Сегодня";
      return note+boardTable(rows, label, key)+btn+boardTape(rows, label);
    }
    async function boardEnsure(){
      if(boardCache) return boardCache;
      const octPacks=await boardFetchAll(BOARD_OCT, boardDays("10", boardOctLast()));
      const sepPacks=await boardFetchAll(BOARD_SEP, boardDays("09", 30));
      const oct=[], sep=[];
      octPacks.forEach(p=>boardRows(p).forEach(r=>oct.push(r)));
      sepPacks.forEach(p=>boardRows(p).forEach(r=>sep.push(r)));
      boardCache={oct, sep, stamp:new Date().toLocaleString("ru-RU",{hour:"2-digit",minute:"2-digit",day:"2-digit",month:"2-digit"})};
      return boardCache;
    }
    async function boardLoad(){
      const root=document.getElementById("boardRoot");
      if(!root || view!=="board") return;
      try{
        if(!boardCache) root.innerHTML=`<div class="card"><p>Загружаю трафик…</p></div>`;
        await boardEnsure();
        root.innerHTML=boardHtml(boardCache);
        boardBindFolds(root);
        const open=document.getElementById("boardOpenReport");
        if(open) open.onclick=()=>{ view="boardrep"; state.section="boardrep"; try{save();}catch(e){} render(); };
      }catch(err){
        root.innerHTML=`<div class="card"><p>Не удалось прочитать трафик. ${escape(err&&err.message||"")}</p><button class="btn ivory" type="button" id="boardRetry">Ещё раз</button></div>`;
        const b=document.getElementById("boardRetry");
        if(b) b.onclick=()=>{ boardCache=null; boardLoad(); };
      }
    }
    function boardChips(){
      const items=[["day","Сегодня"],["yday","Вчера"],["month","Месяц"],["prev","Предыдущий месяц"]];
      return `<div class="study-pick st-filters lb-modes">`+items.map(([id,lab])=>`<button type="button" class="chip ${boardMode===id?"on":""}" data-board-mode="${id}">${lab}</button>`).join("")+`</div>`;
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
        <p class="lead">Сегодня, вчера и месяц — из «Трафик октябрь». Предыдущий месяц — из «Трафик сентябрь».</p>
        ${boardChips()}
        <div id="boardRoot"><div class="card"><p>Загружаю таблицу…</p></div></div>`;
    }
    let boardZoom = 1;
    let boardZoomMin = 0.2;
    function boardPeriod(){
      const cache=boardCache||{oct:[],sep:[]};
      if(boardMode==="prev") return {rows:cache.sep||[], roster:BOARD_ROSTER_SEP, title:"Сентябрь", sub:"Предыдущий месяц"};
      if(boardMode==="month") return {rows:cache.oct||[], roster:BOARD_ROSTER, title:"Октябрь", sub:"Месяц"};
      const yest=boardMode==="yday";
      const key=boardDayKey(yest?-1:0);
      return {rows:boardSlice(cache, key), roster:BOARD_ROSTER, title:key, sub:yest?"Вчера":"Сегодня"};
    }
    function boardPace(fact, plan){
      if(boardMode!=="month" && boardMode!=="prev") return {n:"–", p:"–"};
      let days, passed;
      if(boardMode==="prev"){ days=30; passed=30; }
      else {
        const now=new Date();
        days=new Date(now.getFullYear(), now.getMonth()+1, 0).getDate();
        passed=Math.min(days, Math.max(1, now.getDate()));
      }
      const n=Math.round(fact*days/passed);
      return {n:String(n), p:boardPct(n, plan)};
    }
    function boardReportHtml(){
      const per=boardPeriod();
      const rank=boardRank(per.rows, per.roster);
      const bucket=rank.list.find(p=>p.other)||boardBlank();
      const people=rank.list.filter(p=>!p.other).concat(bucket.people||[]).sort(boardCmp);
      const total=people.reduce((s,p)=>{
        ["traffic","visit","call","web","meet","td","contract","issue","visitContract","callVisit","callContract","webVisit","webContract"].forEach(k=>s[k]+=p[k]||0);
        return s;
      }, boardBlank());
      total.name="Итого";
      const planN=BOARD_PLAN_TEAM;
      const planOf=p=>rank.list.some(n=>!n.other&&n.name===p.name)?BOARD_PLAN:0;
      const ch=p=>p.visit+p.call+p.web;
      const mark=(num,den,kind)=>{
        const text=boardPct(num, den);
        if(text==="–") return text;
        const v=100*num/den;
        const cls=kind==="td"?(v<70?"lb-bad":""):(v<10?"lb-bad":v<15?"lb-mid":"lb-ok");
        return cls?`<span class="${cls}">${text}</span>`:text;
      };
      const mainHead=["Менеджер","План","Факт","% плана","Контракты","Расторж.","Действ.","Выдачи+К","Прогноз","Прогноз %","Трафик","% трафика","% визитов","% зв+инт","Конв. в контракт","Конв. в выдачу","Визиты","Контракт с визита","Конв. визита"];
      const rowMain=(p, plan)=>{
        const pace=boardPace(p.issue, plan);
        const prim=ch(p), tPrim=ch(total);
        return `<tr class="${p.name==="Итого"?"sum":""}"><td>${escape(p.name)}</td><td>${plan||"–"}</td><td>${p.issue}</td><td>${boardPct(p.issue, plan)}</td><td>${p.contract}</td><td>–</td><td>–</td><td>–</td><td>${pace.n}</td><td>${pace.p}</td><td>${prim}</td><td>${boardPct(prim, tPrim)}</td><td>${boardPct(p.visit, total.visit)}</td><td>${boardPct(p.call+p.web, total.call+total.web)}</td><td>${mark(p.contract, prim, "conv")}</td><td>${boardPct(p.issue, prim)}</td><td>${p.visit}</td><td>${p.visitContract}</td><td>${boardPct(p.visitContract, p.visit)}</td></tr>`;
      };
      const tdHead=["Менеджер","План","Факт","Визиты перв.+втор","%"];
      const rowTd=p=>`<tr class="${p.name==="Итого"?"sum":""}"><td>${escape(p.name)}</td><td>70%</td><td>${p.td}</td><td>${p.visit+p.meet}</td><td>${mark(p.td, p.visit+p.meet, "td")}</td></tr>`;
      const callHead=["Менеджер","Звонки","Визит со звонка","% в визит","Контракт со звонка","% в контракт"];
      const webHead=["Менеджер","Интернет","Визит с инт.","% в визит","Контракт с инт.","% в контракт"];
      const rowCall=p=>`<tr class="${p.name==="Итого"?"sum":""}"><td>${escape(p.name)}</td><td>${p.call}</td><td>${p.callVisit}</td><td>${boardPct(p.callVisit, p.call)}</td><td>${p.callContract}</td><td>${mark(p.callContract, p.call, "conv")}</td></tr>`;
      const rowWeb=p=>`<tr class="${p.name==="Итого"?"sum":""}"><td>${escape(p.name)}</td><td>${p.web}</td><td>${p.webVisit}</td><td>${boardPct(p.webVisit, p.web)}</td><td>${p.webContract}</td><td>${mark(p.webContract, p.web, "conv")}</td></tr>`;
      const all=people.concat([total]);
      const planNote=`Личный план — ${BOARD_PLAN}, общий — ${BOARD_PLAN_TEAM}.`;
      const thead=h=>`<thead><tr>${h.map(x=>`<th>${x}</th>`).join("")}</tr></thead>`;
      return `<p class="eyebrow" style="margin:0 0 4px">${escape(per.sub)}</p><h2 style="margin:0 0 10px">${escape(per.title)}</h2>
        <div class="lb-blocks">
          <section class="lb-block a"><p class="lb-rep-h">Выдачи и трафик</p><table class="lb-rep">${thead(mainHead)}<tbody>${people.map(p=>rowMain(p, planOf(p))).join("")}${rowMain(total, planN)}</tbody></table></section>
          <section class="lb-block b"><p class="lb-rep-h">Тест-драйвы</p><table class="lb-rep lb-rep-sm">${thead(tdHead)}<tbody>${all.map(rowTd).join("")}</tbody></table></section>
          <div class="lb-pair">
            <section class="lb-block c"><p class="lb-rep-h">Звонки в визит</p><table class="lb-rep">${thead(callHead)}<tbody>${all.map(rowCall).join("")}</tbody></table></section>
            <section class="lb-block d"><p class="lb-rep-h">Интернет в визит</p><table class="lb-rep">${thead(webHead)}<tbody>${all.map(rowWeb).join("")}</tbody></table></section>
          </div>
        </div>
        <p class="lb-rep-note">Как в «ОП CHERY». ${planNote} Трафик — визиты + звонки + интернет. Конв. в контракт: меньше 10% красным, меньше 15% жёлтым, иначе зелёным. ТД ниже 70% — красным. Расторжения, действующие контракты и «выдачи+контракты» в журнале трафика не ведутся. Обновлено ${escape((boardCache&&boardCache.stamp)||"")}</p>`;
    }
    function boardBindFolds(root){
      if(!root) return;
      root.querySelectorAll("[data-lb-fold]").forEach(el=>{
        el.onclick=()=>{
          const id=el.getAttribute("data-lb-fold");
          const open=!el.classList.contains("open");
          root.querySelectorAll(`[data-lb-fold="${id}"]`).forEach(x=>x.classList.toggle("open", open));
          root.querySelectorAll(`[data-lb-panel="${id}"]`).forEach(x=>x.classList.toggle("open", open));
        };
      });
    }
    function boardApplyZoom(){
      const sheet=document.getElementById("lbSheet");
      const space=document.getElementById("lbSpace");
      if(!sheet||!space) return;
      sheet.style.transform="scale("+boardZoom+")";
      sheet.style.transformOrigin="top left";
      space.style.width=Math.ceil(sheet.offsetWidth*boardZoom)+"px";
      space.style.height=Math.ceil(sheet.offsetHeight*boardZoom)+"px";
    }
    function boardFit(){
      const sheet=document.getElementById("lbSheet");
      const box=document.getElementById("lbZoom");
      if(!sheet||!box) return;
      const availW=Math.max(280, box.clientWidth-4);
      const availH=Math.max(220, window.innerHeight-132);
      boardZoom=Math.min(availW/sheet.offsetWidth, availH/sheet.offsetHeight);
      boardZoomMin=boardZoom;
      boardApplyZoom();
    }
    function boardrep(){
      if(needAuth()) return login();
      setTimeout(()=>{
        const back=document.getElementById("lbBack");
        if(back) back.onclick=()=>{ view="board"; state.section="board"; try{save();}catch(e){} render(); };
        const box=document.getElementById("lbZoom");
        let pinch=null;
        const dist=ev=>{ const a=ev.touches[0], b=ev.touches[1]; return Math.hypot(a.clientX-b.clientX, a.clientY-b.clientY); };
        const clamp=z=>Math.min(3, Math.max(boardZoomMin||0.2, z));
        if(box){
          box.addEventListener("wheel", ev=>{
            ev.preventDefault();
            boardZoom=clamp(boardZoom*(ev.deltaY<0?1.12:1/1.12));
            boardApplyZoom();
          }, {passive:false});
          box.addEventListener("touchstart", ev=>{ if(ev.touches.length===2) pinch={d:dist(ev), z:boardZoom}; }, {passive:true});
          box.addEventListener("touchmove", ev=>{ if(pinch && ev.touches.length===2){ boardZoom=clamp(pinch.z*dist(ev)/pinch.d); boardApplyZoom(); } }, {passive:true});
          box.addEventListener("touchend", ()=>{ pinch=null; });
        }
        const paint=()=>{ const sheet=document.getElementById("lbSheet"); if(sheet) sheet.innerHTML=boardReportHtml(); boardFit(); };
        if(!boardCache){
          const sheet=document.getElementById("lbSheet");
          if(sheet) sheet.innerHTML="<p>Загружаю отчёт…</p>";
          boardEnsure().then(paint).catch(()=>{ const s=document.getElementById("lbSheet"); if(s) s.innerHTML="<p>Не удалось прочитать трафик.</p>"; });
        }else paint();
      }, 30);
      return `<div class="lb-rep-page">
        <div class="lb-rep-bar">
          <button class="btn ghost" type="button" id="lbBack">К рейтингу</button>
        </div>
        <p class="tune-note">Лист на один экран. Приблизить — колёсиком или двумя пальцами, затем листать.</p>
        <div class="lb-zoom" id="lbZoom"><div id="lbSpace"><div class="lb-sheet" id="lbSheet"></div></div></div>
      </div>`;
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
    if 'data-go="board"]::before' not in html and "</style>" in html:
        html = html.replace(
            "</style>",
            '.hub-card[data-go="board"]::before{background-image:url("hub/board.jpg?v=2");background-position:50% 62%;background-size:cover;}\n</style>',
            1,
        )
        print("board preview", path)
    if ".lb-phone{display:none}" not in html and "</style>" in html:
        html = html.replace("</style>", """.lb-phone{display:none}
@media(max-width:720px){
  .lb-desk{display:none}
  .lb-phone{display:block}
  .lb-modes{overflow:visible;flex-wrap:wrap}
  .lb-card{padding:10px 10px 6px}
  .lb-card h3{font-size:18px}
  .lb-line{display:grid;grid-template-columns:14px minmax(0,1fr) auto;gap:6px;align-items:center;padding:5px 0;border-bottom:1px solid var(--border);font-size:13px}
  .lb-line b{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .lb-nums{display:grid;grid-template-columns:repeat(8,16px);text-align:right;font-variant-numeric:tabular-nums;font-size:12px}
  .lb-nums i{font-style:normal}
  .lb-nums i:last-child{font-weight:800}
  .lb-key .lb-nums{font-size:8px;font-weight:700}
}
</style>""", 1)
        print("board phone", path)
    if ".lb-row.other" not in html and "</style>" in html:
        html = html.replace("</style>", ".lb-row.other{background:#fbf7f1}\n.lb-row.other td{color:#6d6458}\n</style>", 1)
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
    elif "const BOARD_SEP" not in html or 'data-board-mode="yday"' not in html or "function boardrep" not in html:
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
