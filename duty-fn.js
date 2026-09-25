    function stockBlob(c){
      if(!c) return "";
      return [c.invoice,c.note,c.lease,c.tag,c.marks,c.label].map(x=>String(x||"")).join(" ").toLowerCase();
    }
    function stockHasSovcom(c){
      if(!c) return false;
      const s=stockBlob(c);
      if(s.includes("совком") || (s.includes("лизинг") && s.includes("совк"))) return true;
      if(c.sovcom || c.bfs) return true;
      if(typeof kmIsCorp==="function" && kmIsCorp(c.vin)) return true;
      return false;
    }
    function stockMptSovcom(c){ return !!(c && c.mpt && stockHasSovcom(c)); }
    function dutyToday(){
      const d=new Date();
      const p=n=>String(n).padStart(2,"0");
      return p(d.getDate())+"."+p(d.getMonth()+1)+"."+String(d.getFullYear()).slice(-2);
    }
    function dutyLoad(){
      try{
        const x=JSON.parse(localStorage.getItem("tenet-duty-v1")||"{}");
        return x && typeof x==="object"?x:{};
      }catch(e){ return {}; }
    }
    function dutySave(data){
      try{ localStorage.setItem("tenet-duty-v1", JSON.stringify(data||{})); }catch(e){}
    }
    function dutyLogLoad(){
      try{
        const x=JSON.parse(localStorage.getItem("tenet-duty-log")||"[]");
        return Array.isArray(x)?x:[];
      }catch(e){ return []; }
    }
    function dutyLogWrite(list){
      try{ localStorage.setItem("tenet-duty-log", JSON.stringify((list||[]).slice(0,80))); }catch(e){}
    }
    function dutyLogKey(d){
      return String(d.date||dutyToday())+"|"+String(d.manager||"").trim().toLowerCase();
    }
    function dutyArchive(d){
      const data=Object.assign({}, d||{});
      const rec={
        id:dutyLogKey(data),
        date:data.date||dutyToday(),
        manager:String(data.manager||"").trim()||"без фамилии",
        at:new Date().toISOString(),
        pct:(()=>{ const p=dutyCount(data); return p.tot?Math.round(p.on*100/p.tot):0; })(),
        data:data
      };
      const list=dutyLogLoad().filter(x=>x && x.id!==rec.id);
      list.unshift(rec);
      dutyLogWrite(list);
      return rec;
    }
    function dutyOpenSaved(id){
      const rec=dutyLogLoad().find(x=>x && x.id===id);
      if(!rec || !rec.data) return;
      dutySave(rec.data);
      if(typeof render==="function") render();
    }
    function dutyBodyWord(v){
      if(v==="pm") return "±";
      if(v==="no") return "грязный";
      return "чистый";
    }
    function dutyPdfClose(){
      const box=document.getElementById("dutyPdfView");
      if(!box) return;
      box.remove();
      document.body.style.overflow="";
      if(location.hash==="#pdf"){
        try{ history.replaceState(null,"",location.pathname+location.search+location.hash.replace("#pdf","")); }catch(e){}
      }
    }
    function dutyPdfOpen(src){
      dutyPdfClose();
      const box=document.createElement("div");
      box.id="dutyPdfView";
      box.style.cssText="position:fixed;inset:0;z-index:99999;background:#111;display:flex;flex-direction:column;";
      box.innerHTML='<div style="flex:none;display:flex;gap:8px;align-items:center;padding:calc(12px + env(safe-area-inset-top,0px)) 12px 12px;background:#111;color:#fff">'+
        '<button type="button" id="dutyPdfBack" style="min-height:44px;padding:0 16px;border:0;border-radius:12px;background:#f3eadc;color:#111;font:700 15px Inter,Arial,sans-serif">Назад</button>'+
        '<b style="flex:1;font:700 16px Inter,Arial,sans-serif">Чек-лист</b></div>'+
        '<div style="flex:1;overflow:auto;-webkit-overflow-scrolling:touch;background:#2a2a2a;padding:8px 8px 24px">'+
        '<img id="dutyPdfImg" alt="Чек-лист" style="width:100%;max-width:720px;display:block;margin:0 auto;background:#fff;border-radius:8px"/></div>';
      document.body.appendChild(box);
      document.body.style.overflow="hidden";
      box.querySelector("#dutyPdfImg").src=src;
      box.querySelector("#dutyPdfBack").onclick=function(){ dutyPdfClose(); };
      try{ if(location.hash!=="#pdf") history.pushState({dutyPdf:1},"", "#pdf"); }catch(e){}
    }
    if(!window.__dutyPdfHash){
      window.__dutyPdfHash=true;
      window.addEventListener("popstate", function(){ if(document.getElementById("dutyPdfView")) dutyPdfClose(); });
    }
    function dutyPdf(src){
      const d=src||dutyRead();
      const p=dutyCount(d);
      const pct=p.tot?Math.round(p.on*100/p.tot):0;
      const W=1240, H=1754;
      const c=document.createElement("canvas");
      c.width=W; c.height=H;
      const ctx=c.getContext("2d");
      ctx.fillStyle="#ffffff"; ctx.fillRect(0,0,W,H);
      const pad=40;
      const inner=W-pad*2;
      function roundRect(x,y,w,h,r){
        ctx.beginPath();
        ctx.moveTo(x+r,y);
        ctx.arcTo(x+w,y,x+w,y+h,r);
        ctx.arcTo(x+w,y+h,x,y+h,r);
        ctx.arcTo(x,y+h,x,y,r);
        ctx.arcTo(x,y,x+w,y,r);
        ctx.closePath();
      }
      function tick(x,y,state){
        const st=state==="bad"?"bad":(state==="ok"||state===true?"ok":"");
        if(st==="bad"){
          ctx.fillStyle="#ff8a80";
          ctx.fillRect(x-8, y-22, 280, 30);
        }
        ctx.lineWidth=1.6;
        ctx.strokeStyle="#2e7d32";
        ctx.strokeRect(x, y-15, 16, 16);
        if(st==="ok"){
          ctx.fillStyle="#1b5e20";
          ctx.fillRect(x, y-15, 16, 16);
          ctx.fillStyle="#fff";
          ctx.font="800 13px Inter, Arial, sans-serif";
          ctx.fillText("✓", x+2, y-2);
        }
        ctx.strokeStyle="#c62828";
        ctx.strokeRect(x+20, y-15, 16, 16);
        if(st==="bad"){
          ctx.fillStyle="#b71c1c";
          ctx.fillRect(x+20, y-15, 16, 16);
          ctx.fillStyle="#fff";
          ctx.font="800 13px Inter, Arial, sans-serif";
          ctx.fillText("×", x+22, y-2);
        }
      }
      ctx.fillStyle="#c81e2b";
      ctx.fillRect(pad, pad, 32, 32);
      ctx.fillStyle="#fff";
      ctx.font="800 18px Inter, Arial, sans-serif";
      ctx.fillText("T", pad+9, pad+23);
      ctx.fillStyle="#111";
      ctx.font="800 30px Inter, Arial, sans-serif";
      ctx.fillText("Чек-лист дежурного", pad+46, pad+26);
      ctx.font="600 17px Inter, Arial, sans-serif";
      ctx.fillStyle="#5c5346";
      ctx.fillText((d.manager||"—")+"  ·  "+(d.date||dutyToday())+"  ·  "+pct+"%  ·  "+p.on+" из "+p.tot, pad+46, pad+52);
      let y=pad+78;
      const carH=198;
      DUTY_CARS.forEach((car)=>{
        ctx.fillStyle="#f7f1e7";
        roundRect(pad, y, inner, carH, 14);
        ctx.fill();
        ctx.strokeStyle="#eadfcf"; ctx.lineWidth=1;
        roundRect(pad, y, inner, carH, 14);
        ctx.stroke();
        ctx.fillStyle="#111"; ctx.font="800 22px Inter, Arial, sans-serif";
        ctx.fillText(car.title, pad+20, y+34);
        const rows=[
          ["Омывающая", dutyTri(d[car.id+"_wash"])],
          ["Коврики и пороги", dutyTri(d[car.id+"_mats"])],
          ["Нет ошибок", dutyTri(d[car.id+"_err"])],
          ["Нет пыли", dutyTri(d[car.id+"_dust"])],
          ["Багажник", dutyTri(d[car.id+"_trunk"])],
          ["Кузов", dutyTri(d[car.id+"_body"])],
        ];
        rows.forEach((row,ri)=>{
          const col=ri%2;
          const line=Math.floor(ri/2);
          const cx=pad+20+col*((inner-40)/2);
          const cy=y+72+line*36;
          tick(cx, cy, row[1]);
          ctx.fillStyle=row[1]==="bad"?"#7f0000":"#111"; ctx.font="500 17px Inter, Arial, sans-serif";
          ctx.fillText(row[0], cx+44, cy);
        });
        ctx.fillStyle="#5c5346"; ctx.font="600 16px Inter, Arial, sans-serif";
        const meta="Пробег: "+(d[car.id+"_km"]||"—")+"     Топливо: "+(d[car.id+"_fuel"]?d[car.id+"_fuel"]+"%":"—");
        ctx.fillText(meta, pad+20, y+176);
        y+=carH+12;
      });
      function block(title, keys){
        const rows=Math.ceil(keys.length/3);
        const h=54+rows*40;
        ctx.fillStyle="#f7f1e7";
        roundRect(pad, y, inner, h, 14); ctx.fill();
        ctx.strokeStyle="#eadfcf"; ctx.lineWidth=1;
        roundRect(pad, y, inner, h, 14); ctx.stroke();
        ctx.fillStyle="#111"; ctx.font="800 20px Inter, Arial, sans-serif";
        ctx.fillText(title, pad+20, y+32);
        keys.forEach((pair,i)=>{
          const col=i%3;
          const line=Math.floor(i/3);
          const cx=pad+20+col*((inner-40)/3);
          const cy=y+68+line*38;
          tick(cx, cy, dutyTri(d[pair[0]]));
          ctx.fillStyle=dutyTri(d[pair[0]])==="bad"?"#7f0000":"#111"; ctx.font="500 16px Inter, Arial, sans-serif";
          ctx.fillText(pair[1], cx+44, cy);
        });
        y+=h+12;
      }
      block("Дилерский центр",[
        ["dc_light","Свет"],["dc_avito","Авито"],["dc_music","Музыка"],
        ["dc_price_avito","Цены Авито"],["dc_price_hold","Прайсхолдеры"],["dc_desk","Столы"],["dc_trash","Бумаги"]
      ]);
      block("Демонстрационные",[
        ["dm_body","Кузов"],["dm_mats","Коврики"],["dm_trunk","Багажник"],
        ["dm_dust","Пыль"],["dm_wheel","Колёса"],["dm_bat","АКБ"]
      ]);
      ctx.fillStyle="#5c5346"; ctx.font="500 16px Inter, Arial, sans-serif";
      ctx.fillText("Заметка: "+(d.note||"—"), pad, y+8);
      ctx.fillText("Подпись: "+(d.sign||d.manager||""), pad, y+36);
      ctx.fillStyle="#9a9186"; ctx.font="500 13px Inter, Arial, sans-serif";
      ctx.fillText("TENET · Отдел продаж · Эксперт Авто Самара", pad, H-28);
      dutyPdfOpen(c.toDataURL("image/png"));
    }
    function dutyRead(){
      const out=dutyLoad();
      document.querySelectorAll("[data-duty]").forEach(el=>{
        const k=el.getAttribute("data-duty");
        if(!k) return;
        if(el.type==="checkbox") out[k]=!!el.checked;
        else out[k]=el.value;
      });
      return out;
    }
    const DUTY_CARS=[
      {id:"t4l",title:"TENET T4L"},
      {id:"t8",title:"TENET T8"},
      {id:"a8",title:"Arrizo 8"},
      {id:"t7",title:"TENET T7"},
      {id:"t9",title:"Tiggo 9"}
    ];
    function dutyTri(v){
      if(v==="ok" || v==="bad") return v;
      if(v===true || v==="true") return "ok";
      if(v==="no") return "bad";
      return "";
    }
    function dutyOk(v){ return dutyTri(v)==="ok"; }
    function dutyCount(d){
      let tot=0, on=0;
      DUTY_CARS.forEach(car=>{
        ["_wash","_mats","_err","_dust","_trunk","_body"].forEach(s=>{ tot++; if(dutyOk(d[car.id+s])) on++; });
        tot+=2; if(d[car.id+"_km"]) on++; if(d[car.id+"_fuel"]) on++;
      });
      ["dc_light","dc_avito","dc_music","dc_price_avito","dc_price_hold","dc_desk","dc_trash","dm_body","dm_mats","dm_trunk","dm_dust","dm_wheel","dm_bat"].forEach(k=>{ tot++; if(dutyOk(d[k])) on++; });
      return {on, tot};
    }
    function dutyPaintProg(){
      const p=dutyCount(dutyRead());
      const pct=p.tot?Math.round(p.on*100/p.tot):0;
      const bar=document.querySelector(".cl-prog i");
      const lab=document.querySelector(".cl-prog span");
      if(bar) bar.style.width=pct+"%";
      if(lab) lab.textContent=pct+"%";
    }
    function dutyItem(k, label, raw){
      const st=dutyTri(raw);
      const cls=st==="bad"?" is-bad":(st==="ok"?" is-ok":"");
      return `<div class="cl-item${cls}">
        <span class="cl-lab">${label}</span>
        <span class="cl-pair">
          <button type="button" class="cl-sq ok${st==="ok"?" on":""}" data-duty-pick="${k}" data-val="ok" aria-label="Норма">✓</button>
          <button type="button" class="cl-sq bad${st==="bad"?" on":""}" data-duty-pick="${k}" data-val="bad" aria-label="Проблема">✕</button>
        </span>
        <input type="hidden" data-duty="${k}" value="${st}" />
      </div>`;
    }
    function duty(){
      if(needAuth()) return login();
      const d=dutyLoad();
      if(!d.date) d.date=dutyToday();
      const who=(typeof state!=="undefined" && state && state.display)?state.display:"";
      if(!d.manager && who) d.manager=who;
      const prog=dutyCount(d);
      const pct=prog.tot?Math.round(prog.on*100/prog.tot):0;
      const cards=DUTY_CARS.map(car=>{
        return `<article class="cl-car">
          <h3>${car.title}</h3>
          ${dutyItem(car.id+"_wash","Омывающая", d[car.id+"_wash"])}
          ${dutyItem(car.id+"_mats","Коврики и пороги", d[car.id+"_mats"])}
          ${dutyItem(car.id+"_err","Нет ошибок", d[car.id+"_err"])}
          ${dutyItem(car.id+"_dust","Нет пыли", d[car.id+"_dust"])}
          ${dutyItem(car.id+"_trunk","Багажник", d[car.id+"_trunk"])}
          ${dutyItem(car.id+"_body","Кузов", d[car.id+"_body"])}
          <div class="cl-nums">
            <label>Пробег<input data-duty="${car.id}_km" inputmode="numeric" value="${escape(d[car.id+"_km"]||"")}" /></label>
            <label>Топливо %<input data-duty="${car.id}_fuel" inputmode="numeric" value="${escape(d[car.id+"_fuel"]||"")}" /></label>
          </div>
        </article>`;
      }).join("");
      return banner("Чек-лист дежурного", prog.on+" из "+prog.tot,"TENET")+`
        <div class="cl">
          <div class="cl-bar">
            <input data-duty="manager" placeholder="Менеджер" value="${escape(d.manager||"")}" />
            <input data-duty="date" value="${escape(d.date||"")}" style="width:96px" />
            <input data-duty="sign" placeholder="Подпись" value="${escape(d.sign||d.manager||"")}" />
            <div class="cl-prog"><i style="width:${pct}%"></i><span>${pct}%</span></div>
            <button type="button" class="btn ivory" id="dutySave">Сохранить</button>
            <button type="button" class="btn ghost" id="dutyPrint">PDF</button>
            <button type="button" class="btn ghost" id="dutyClear">Сброс</button>
          </div>
          <div class="cl-cars">${cards}</div>
          <div class="cl-foot">
            <div class="cl-box"><b>Дилерский центр</b><div class="cl-chips">
              ${dutyItem("dc_light","Свет", d.dc_light)}
              ${dutyItem("dc_avito","Авито", d.dc_avito)}
              ${dutyItem("dc_music","Музыка", d.dc_music)}
              ${dutyItem("dc_price_avito","Цены Авито", d.dc_price_avito)}
              ${dutyItem("dc_price_hold","Прайсхолдеры", d.dc_price_hold)}
              ${dutyItem("dc_desk","Столы", d.dc_desk)}
              ${dutyItem("dc_trash","Бумаги", d.dc_trash)}
            </div></div>
            <div class="cl-box"><b>Демонстрационные</b><div class="cl-chips">
              ${dutyItem("dm_body","Кузов", d.dm_body)}
              ${dutyItem("dm_mats","Коврики", d.dm_mats)}
              ${dutyItem("dm_trunk","Багажник", d.dm_trunk)}
              ${dutyItem("dm_dust","Пыль", d.dm_dust)}
              ${dutyItem("dm_wheel","Колёса", d.dm_wheel)}
              ${dutyItem("dm_bat","АКБ", d.dm_bat)}
            </div>
            <input data-duty="note" placeholder="Заметка: помыть T7, T4L" value="${escape(d.note||"")}" style="width:100%;margin-top:8px;min-height:34px" />
            </div>
          </div>
          <div class="cl-log">
            <h3>Сохранённые чек-листы</h3>
            ${dutyLogLoad().length?dutyLogLoad().map(x=>`
              <button type="button" class="cl-log-row" data-duty-open="${escape(x.id)}">
                <span><b>${escape(x.date||"")}</b> · ${escape(x.manager||"")}</span>
                <small>${x.pct||0}% · открыть</small>
              </button>`).join(""):`<p class="lead" style="margin:0">Пока пусто. Нажмите «Сохранить» — запись появится здесь с датой и фамилией.</p>`}
          </div>
        </div>`;
    }
    function gibddSplitFio(s){
      const p=String(s||"").trim().split(/\s+/).filter(Boolean);
      return {last:p[0]||"", first:p[1]||"", mid:p.slice(2).join(" ")};
    }
    function gibddDob(s){
      const t=String(s||"").trim();
      const m=t.match(/^(\d{1,2})[.\/-](\d{1,2})[.\/-](\d{2,4})$/) || t.match(/^(\d{4})[.\/-](\d{1,2})[.\/-](\d{1,2})$/);
      if(!m) return t;
      if(m[1].length===4) return ("0"+m[3]).slice(-2)+"."+("0"+m[2]).slice(-2)+"."+m[1];
      const y=m[3].length===2?("20"+m[3]):m[3];
      return ("0"+m[1]).slice(-2)+"."+("0"+m[2]).slice(-2)+"."+y;
    }
    function gibddMaskDob(el){
      const raw=String(el.value||"").replace(/\D/g,"").slice(0,8);
      let out=raw.slice(0,2);
      if(raw.length>2) out+="."+raw.slice(2,4);
      if(raw.length>4) out+="."+raw.slice(4,8);
      el.value=out;
    }
    function gibddLoad(){
      try{ return JSON.parse(localStorage.getItem("tenet-gibdd-v1")||"{}"); }catch(e){ return {}; }
    }
    function gibddSaveForm(){
      const o={vin:(document.getElementById("gVin")||{}).value||"", fio:(document.getElementById("gFio")||{}).value||"", dob:(document.getElementById("gDob")||{}).value||""};
      try{ localStorage.setItem("tenet-gibdd-v1", JSON.stringify(o)); }catch(e){}
      return o;
    }
    function gibddLinks(form){
      const vin=String((form&&form.vin)||"").replace(/\s+/g,"").toUpperCase();
      const fio=String((form&&form.fio)||"").trim();
      const dob=gibddDob((form&&form.dob)||"");
      const nm=gibddSplitFio(fio);
      const fssp="https://fssp.gov.ru/iss/ip?is%5Blast_name%5D="+encodeURIComponent(nm.last)+
        "&is%5Bfirst_name%5D="+encodeURIComponent(nm.first)+
        "&is%5Bpatronymic%5D="+encodeURIComponent(nm.mid)+
        "&is%5Bdate%5D="+encodeURIComponent(dob)+
        "&is%5Bregion_id%5D%5B0%5D=-1";
      const zalog="https://www.reestr-zalogov.ru/search/index?vin="+encodeURIComponent(vin);
      const bankrot="https://fedresurs.ru/bankrupts?searchString="+encodeURIComponent(fio);
      const bankrotOld="https://bankrot.fedresurs.ru/Debtors.search.aspx?Name="+encodeURIComponent(fio);
      return {vin,fio,dob,nm,fssp,zalog,bankrot,bankrotOld};
    }
    function gibddCopy(text){
      const t=String(text||"");
      try{ navigator.clipboard.writeText(t); }catch(e){
        const a=document.createElement("textarea"); a.value=t; document.body.appendChild(a); a.select(); try{ document.execCommand("copy"); }catch(x){} a.remove();
      }
    }
    function gibddOpen(kind){
      const L=gibddLinks(gibddSaveForm());
      if(kind==="zalog"){ gibddCopy(L.vin); window.open(L.zalog,"_blank","noopener"); }
      if(kind==="fssp"){ gibddCopy([L.nm.last,L.nm.first,L.nm.mid,L.dob].filter(Boolean).join(" ")); window.open(L.fssp,"_blank","noopener"); }
      if(kind==="bankrot"){ gibddCopy(L.fio); window.open(L.bankrot,"_blank","noopener"); window.open(L.bankrotOld,"_blank","noopener"); }
    }
    async function gibddFetch(url){
      const ctrl=typeof AbortController==="function"?new AbortController():null;
      const t=setTimeout(()=>{ try{ if(ctrl) ctrl.abort(); }catch(e){} }, 8000);
      try{
        const r=await fetch(url,{signal:ctrl?ctrl.signal:undefined, cache:"no-store"});
        const text=await r.text();
        return {ok:r.ok, status:r.status, text:text.slice(0,12000)};
      }catch(e){
        return {ok:false, status:0, text:String(e&&e.message||e)};
      }finally{ clearTimeout(t); }
    }
    function gibddParseZalog(text, vin){
      const t=String(text||"");
      if(/ничего не найдено|не найдено уведомлен/i.test(t)) return {hit:false, n:0, detail:"Записей по VIN нет"};
      const recs=t.match(/20\d{2}-\d{3}-\d+/g)||[];
      if(recs.length) return {hit:true, n:recs.length, detail:"Найдены уведомления: "+recs.slice(0,6).join(", ")};
      return {hit:null, n:0, detail:"Нужна капча на сайте. VIN скопирован."};
    }
    function gibddParseFssp(text){
      const t=String(text||"");
      if(/Ничего не найдено|не найдено исполнительн/i.test(t)) return {hit:false, n:0, detail:"ИП не найдено"};
      const ips=t.match(/\d+\/\d+\/\d+-?И?П?/g)||[];
      if(ips.length) return {hit:true, n:ips.length, detail:"Найдены ИП: "+ips.slice(0,8).join(", ")};
      return {hit:null, n:0, detail:"ФССП просит капчу. Регион — Все. ФИО и дата в ссылке."};
    }
    function gibddParseBankrot(text, fio){
      const t=String(text||"");
      if(/ничего не найдено|не найдено сообщен/i.test(t)) return {hit:false, n:0, detail:"В реестре банкротов нет"};
      let recs=0;
      try{
        const j=JSON.parse(t);
        const arr=j.pageData||j.items||j.data||j.records||[];
        if(Array.isArray(arr)) recs=arr.length;
        if(j.total||j.totalCount) recs=Number(j.total||j.totalCount)||recs;
      }catch(e){
        const name=String(fio||"").split(/\s+/)[0];
        if(name && t.toLowerCase().includes(name.toLowerCase()) && /банкрот/i.test(t)) recs=1;
      }
      if(recs) return {hit:true, n:recs, detail:"Найдено записей: "+recs};
      return {hit:null, n:0, detail:"Откройте Федресурс — ФИО в поиске."};
    }
    function gibddVerdict(z,f,b){
      const bad=[];
      if(z&&z.hit) bad.push("залог");
      if(f&&f.hit) bad.push("ФССП");
      if(b&&b.hit) bad.push("банкротство");
      if(bad.length) return {ok:false, text:"Риск: "+bad.join(", ")};
      if([z,f,b].some(x=>x && x.hit===null)) return {ok:null, text:"Откройте реестры и пройдите капчу"};
      return {ok:true, text:"По автопроверке записей нет"};
    }
    async function gibddRun(){
      try{
        const form=gibddSaveForm();
        const L=gibddLinks(form);
        const box=document.getElementById("gOut");
        if(!L.vin || !L.nm.last || !L.nm.first || !L.dob){
          if(box) box.innerHTML=`<div class="note-box">Нужны VIN, фамилия, имя и дата рождения в формате ДД.ММ.ГГГГ.</div>`;
          return;
        }
        if(box) box.innerHTML=`<div class="note-box">Собираю сводку и ссылки с заполненными полями…</div>`;
        const [zRaw, fRaw, bRaw]=await Promise.all([
          gibddFetch(L.zalog),
          gibddFetch(L.fssp),
          gibddFetch("https://fedresurs.ru/backend/persons?limit=15&offset=0&searchString="+encodeURIComponent(L.fio))
        ]);
        const z=gibddParseZalog(zRaw.text, L.vin);
        const f=gibddParseFssp(fRaw.text);
        const b=gibddParseBankrot(bRaw.text, L.fio);
        const v=gibddVerdict(z,f,b);
        const pack={at:new Date().toISOString(), vin:L.vin, fio:L.fio, dob:L.dob, z, f, b, v, links:L};
        window.__gibddLast=pack;
        try{ localStorage.setItem("tenet-gibdd-last", JSON.stringify(pack)); }catch(e){}
        const row=(title, rec, kind)=>`<div class="bank-row"><span><b>${title}</b><br/><small>${escape(rec.detail||"")}</small></span><span class="pay">${rec.hit===true?"Есть":rec.hit===false?"Нет":"Сайт"}</span></div>
          <p class="calc-note"><button type="button" class="btn ghost" data-gopen="${kind}">Открыть и подставить данные</button></p>`;
        if(box) box.innerHTML=`<div class="card dc-result ${v.ok===true?"ok":v.ok===false?"bad":""}">
          <p class="eyebrow">Сводка</p>
          <div class="calc-out" style="font-size:22px">${escape(v.text)}</div>
          <p class="calc-note">${escape(L.vin)} · ${escape(L.fio)} · ${escape(L.dob)}</p>
          ${row("Реестр залогов · VIN", z, "zalog")}
          ${row("ФССП · все регионы", f, "fssp")}
          ${row("Реестр банкротов · ФИО", b, "bankrot")}
          <p class="calc-note">Сайты с другого домена не дают вставить значения скриптом. Открываем с параметрами в ссылке и копируем значение в буфер. Капчу всё равно нужно ввести руками.</p>
          <div class="who-line" style="margin-top:10px"><button type="button" class="btn ivory" id="gPdf">PDF</button></div>
        </div>`;
      }catch(err){
        const box=document.getElementById("gOut");
        if(box) box.innerHTML=`<div class="note-box">${escape(String(err&&err.message||err))}</div>`;
      }
    }
    function gibddPdf(pack){
      const p=pack||window.__gibddLast;
      if(!p) return;
      const c=document.createElement("canvas");
      c.width=1240; c.height=1754;
      const ctx=c.getContext("2d");
      ctx.fillStyle="#f6f1e8"; ctx.fillRect(0,0,c.width,c.height);
      ctx.fillStyle="#1a1a1a";
      ctx.font="700 36px Inter, Arial, sans-serif";
      ctx.fillText("Проверка трейд-ин", 72, 90);
      ctx.font="500 20px Inter, Arial, sans-serif";
      ctx.fillStyle="#5c5346";
      ctx.fillText("ЭКСПЕРТ АВТО САМАРА · "+new Date(p.at||Date.now()).toLocaleString("ru-RU"), 72, 128);
      ctx.fillStyle="#1a1a1a"; ctx.font="600 22px Inter, Arial, sans-serif";
      let y=190;
      ["VIN: "+p.vin,"ФИО: "+p.fio,"Дата рождения: "+p.dob,"","Итог: "+(p.v&&p.v.text||""),"","1. Залоги: "+(p.z&&p.z.detail||""),"2. ФССП: "+(p.f&&p.f.detail||""),"3. Банкроты: "+(p.b&&p.b.detail||""),"","Банкротство за 3 года — трейд-ин не принимаем."].forEach(ln=>{ ctx.fillText(String(ln).slice(0,78), 72, y); y+=36; });
      dutyPdfOpen(c.toDataURL("image/png"));
    }
    function gibdd(){
      if(needAuth()) return login();
      const g=gibddLoad();
      return banner("Проверки ГИБДД","Залог · ФССП · банкроты","TENET")+`
        <p class="lead">Дата — ДД.ММ.ГГГГ. «Открыть» передаёт VIN / ФИО / дату в ссылку реестра.</p>
        <div class="card">
          <div class="cl-bar">
            <label class="field" style="max-width:none"><span>VIN</span><input id="gVin" value="${escape(g.vin||"")}" placeholder="X7L…" /></label>
            <label class="field" style="max-width:none"><span>ФИО</span><input id="gFio" value="${escape(g.fio||"")}" placeholder="Иванов Иван Иванович" /></label>
            <label class="field" style="width:180px"><span>Дата рождения</span><input id="gDob" inputmode="numeric" maxlength="10" value="${escape(g.dob||"")}" placeholder="ДД.ММ.ГГГГ" /></label>
          </div>
          <div class="who-line"><button type="button" class="btn ivory" id="gRun">Проверить</button></div>
        </div>
        <div id="gOut"></div>`;
    }
    function dutyBind(){
      if(view==="duty"){
        const persist=()=>{ dutySave(dutyRead()); dutyPaintProg(); };
        document.querySelectorAll("[data-duty]").forEach(el=>{
          el.addEventListener("change", persist);
          el.addEventListener("input", persist);
        });
        document.querySelectorAll("[data-duty-pick]").forEach(btn=>{
          btn.addEventListener("click", ()=>{
            const row=btn.closest(".cl-item");
            if(!row) return;
            const val=btn.getAttribute("data-val");
            const hid=row.querySelector('input[type="hidden"]');
            const cur=hid?hid.value:"";
            const next=cur===val?"":val;
            if(hid) hid.value=next;
            row.classList.toggle("is-ok", next==="ok");
            row.classList.toggle("is-bad", next==="bad");
            row.querySelectorAll(".cl-sq").forEach(b=>b.classList.toggle("on", b.getAttribute("data-val")===next));
            persist();
          });
        });
        dutyPaintProg();
      }
      if(view==="gibdd"){
        const dob=document.getElementById("gDob");
        if(dob){
          dob.addEventListener("input", ()=>{ gibddMaskDob(dob); gibddSaveForm(); });
          dob.addEventListener("blur", ()=>{ dob.value=gibddDob(dob.value); gibddSaveForm(); });
        }
        ["gVin","gFio"].forEach(id=>{
          const el=document.getElementById(id);
          if(el) el.addEventListener("change", gibddSaveForm);
        });
      }
    }
    if(!window.__dutyClick){
      window.__dutyClick=true;
      document.addEventListener("click", function(ev){
        const open=ev.target && ev.target.closest ? ev.target.closest("[data-gopen]") : null;
        if(open){ ev.preventDefault(); gibddOpen(open.getAttribute("data-gopen")); return; }
        const t=ev.target && ev.target.closest ? ev.target.closest("#gRun,#gPdf,#gPdfLast,#dutySave,#dutyPrint,#dutyClear,#dutyPdfBack,[data-duty-open]") : ev.target;
        if(!t) return;
        if(t.id==="dutyPdfBack"){ ev.preventDefault(); dutyPdfClose(); return; }
        const openLog=t.closest ? t.closest("[data-duty-open]") : (t.getAttribute && t.getAttribute("data-duty-open")?t:null);
        if(openLog && openLog.getAttribute){
          ev.preventDefault();
          dutyOpenSaved(openLog.getAttribute("data-duty-open"));
          return;
        }
        if(!t.id) return;
        if(t.id==="gRun"){ ev.preventDefault(); gibddRun(); }
        if(t.id==="gPdf" || t.id==="gPdfLast"){ ev.preventDefault(); gibddPdf(window.__gibddLast); }
        if(t.id==="dutySave"){
          ev.preventDefault();
          const cur=dutyRead();
          dutySave(cur);
          dutyArchive(cur);
          dutyPaintProg();
          if(typeof render==="function") render();
        }
        if(t.id==="dutyPrint"){ ev.preventDefault(); const cur=dutyRead(); dutySave(cur); dutyPdf(cur); }
        if(t.id==="dutyClear"){ ev.preventDefault(); localStorage.removeItem("tenet-duty-v1"); if(typeof render==="function") render(); }
      });
    }
