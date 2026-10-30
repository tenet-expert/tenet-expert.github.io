/* FLEET-KP: флит-КП в разделе КП (вкладка «Флит»). Источник: patch_fleet_kp.py. */
(function(){
  if (window.__fleetKpInit) return; window.__fleetKpInit = true;
  const FLEET_KP_CATS = {c1:["Лизинг С1","BFS"], c2:["Лизинг С2","RF"], ooo:["Безнал ООО","BF"], ip:["Безнал ИП","RF"]};
  const FLEET_KP_COL = {RF:2, BF:3, BFS:4};
  // Партнёры С1/BFS — «Флит цены» → BFS «Лизинговые компании из списка».
  const FLEET_KP_LESSORS = ["Каркаде","Т-Лизинг","Европлан","Сберлизинг","Газпромбанк Лизинг","Совкомбанк Лизинг"];
  const FLEET_KP_MGR = ["Корпоративный менеджер Павлова Оксана", "+7 963 915 35 00"];
  // Прайс T4L 09.10.2026: «Технологии и мультимедиа» — ◆ для Актив и Прайм.
  const T4L_MM = ["Технологии и мультимедиа", ["Радио","6 динамиков","Большой сенсорный емкостный дисплей 10.25”",
    "Цветной экран с бортовым компьютером в панели приборов 10.25”","Android Auto / Apple CarPlay (беспроводной)",
    "2 USB-разъема спереди","1 USB-разъем сзади","Телематика",
    "Система “Свободные руки” (Hands free) с Bluetooth-связью с мобильным телефоном"]];
  try {
    if (!window.__offerOfficial) ["t4la","t4lp"].forEach(id=>{
      const g = (typeof OFFER_FULL!=="undefined") && OFFER_FULL[id];
      if (Array.isArray(g) && !g.some(x=>x && x[0]===T4L_MM[0])) g.push([T4L_MM[0], T4L_MM[1].slice()]);
    });
  } catch(e) { console.warn("fleet-kp t4l mm", e); }

  function installPaint(){

  if (window.__fleetPaint) return true;
  const src = offerPaint.toString();
  const a = src.indexOf("(doc.rows||[]).forEach(([k,v])=>{");
  const b0 = src.indexOf("if(doc.total){", a);
  const b = src.indexOf("y+=48;", b0);
  const b2 = src.indexOf("}", b) + 1;
  if (a < 0 || b0 < 0 || b < 0) throw new Error("offerPaint layout changed");
  const custom = `
      const fleetContact=(label)=>{
        const C=doc.fleet.contact, bh=58; need(bh+16); y+=4;
        const t=y-18; ctx.fillStyle="#1d2b3a"; ctx.fillRect(pad, t, W-pad*2, bh);
        ctx.fillStyle="#c8102e"; ctx.fillRect(pad, t, 6, bh);
        font("700",11); ctx.fillStyle="#c9d3de"; ctx.fillText(label, pad+22, t+20);
        font("800",18); ctx.fillStyle="#ffffff"; ctx.fillText(C, pad+22, t+44);
        y=t+bh+28;
      };
      if(doc.fleet){
        fleetContact("КОНТАКТ ПО ФЛИТУ");
        const F=doc.fleet, n=F.rows.length;
        const cardH=24+34+(n-1)*30+10+44+(F.sub?32:0)+16;
        y+=14; need(cardH+8);
        const top=y-14, x0=pad, w0=W-pad*2, ix=pad+18, rx=W-pad-18;
        ctx.fillStyle="#fbf6ec"; ctx.fillRect(x0, top, w0, cardH);
        ctx.strokeStyle="#c9ab7c"; ctx.lineWidth=2; ctx.strokeRect(x0, top, w0, cardH); ctx.lineWidth=1;
        y=top+24+10;
        F.rows.forEach(([k,v],i)=>{
          const big=i===0;
          if(i>0){ ctx.strokeStyle="#eadfcf"; ctx.beginPath(); ctx.moveTo(ix, y-20); ctx.lineTo(rx, y-20); ctx.stroke(); }
          font(big?"700":"500", big?16:15); ctx.fillStyle=big?"#161618":"#3d3832"; ctx.fillText(k, ix, y);
          ctx.textAlign="right"; font(big?"800":"700", big?20:15); ctx.fillText(String(v), rx, y); ctx.textAlign="left";
          y+=big?34:30;
        });
        y+=2;
        const tTop=y-6, tx=pad+10, tw=W-pad*2-20;
        ctx.fillStyle="#efe4cf"; ctx.fillRect(tx, tTop, tw, 44);
        font("700",16); ctx.fillStyle="#161618"; ctx.fillText(F.total[0], tx+14, tTop+28);
        ctx.textAlign="right"; font("800",20); ctx.fillText(F.total[1], tx+tw-14, tTop+29); ctx.textAlign="left";
        if(F.sub){
          ctx.fillStyle="#1f8a4c"; ctx.fillRect(tx, tTop+44, tw, 32);
          font("800",15); ctx.fillStyle="#ffffff"; ctx.textAlign="right";
          ctx.fillText(F.sub, tx+tw-14, tTop+44+21); ctx.textAlign="left";
          font("700",13); ctx.fillText("БОНУС", tx+14, tTop+44+21);
        }
        y=top+cardH+30;
      } else {
      ` + src.slice(a, b2) + `
      }`;
  let full = src.slice(0, a) + custom + src.slice(b2);
  const E1 = 'pages.forEach((pg,i)=>{';
  const ei = full.lastIndexOf(E1);
  if (ei < 0) throw new Error("offerPaint end changed");
  full = full.slice(0, ei) + 'if(doc.fleet){ y+=12; fleetContact("ВАШ КОРПОРАТИВНЫЙ МЕНЕДЖЕР"); }\n      ' + full.slice(ei);
  const H1 = '"TENET  ·  ОТДЕЛ ПРОДАЖ  ·  +7 927 724 92 77"', F1 = '"Не оферта · ООО «ЭКСПЕРТ АВТО САМАРА»"';
  if (full.indexOf(H1) < 0 || full.indexOf(F1) < 0) throw new Error("offerPaint header/footer changed");
  full = full.split(H1).join('(doc.fleet ? (pages.length ? "TENET  ·  ФЛИТ" : "TENET  ·  КОРПОРАТИВНЫЙ МЕНЕДЖЕР ПАВЛОВА ОКСАНА  ·  +7 963 915 35 00") : ' + H1 + ')');
  window.offerPaint = (0, eval)("(" + full + ")");
  window.__fleetPaint = true;
  return true;

  }
  try { installPaint(); } catch(e) { console.warn("fleet-kp paint", e); }

  const rubP = n => rub(Math.round(n||0))+" ₽";
  const key = s => String(s||"").toLowerCase().replace("5-seat","5").replace("7-seat","7").replace(" мест","").replace(/[^a-z0-9]/g,"");
  function fleetRow(m){
    const cat = typeof FLEET_CAT!=="undefined" ? FLEET_CAT : [];
    const f = (typeof FLEET_BFS!=="undefined" && FLEET_BFS[m.id]) || null;
    let c = cat.filter(r=>r[1]===m.rrc);
    if (f && f.name) { const bn=key(f.name); c = c.filter(r=>bn.startsWith(key(r[0]))||key(r[0]).startsWith(bn)).length ? c.filter(r=>bn.startsWith(key(r[0]))||key(r[0]).startsWith(bn)) : c; }
    return c.length===1 ? c[0] : null;
  }
  function fleetCalc(m, cat, ti, tuning, dc){
    const code = FLEET_KP_CATS[cat][1], notes=[], row=fleetRow(m), f=(typeof FLEET_BFS!=="undefined"&&FLEET_BFS[m.id])||null;
    const rrc = m.rrc||0; let price, src;
    if (row) { price=row[FLEET_KP_COL[code]]; src="FLEET_CAT · "+code; }
    else if (code==="BFS" && f && f.tidy) { price=f.tidy; src="FLEET_BFS.tidy"; }
    else { price=rrc; src="нет"; notes.push("Для "+code+" флит-цены на сайте нет — скидка 0."); }
    const fleet=Math.max(0, rrc-price);
    const tiAmt = ti ? (typeof FLEET_TI==="number"?FLEET_TI:100000) : 0;
    const subRef = (row && row[5]) || 0;
    const subOn = cat==="c1" && subRef>0 && !!row;
    if (cat==="c1" && !subRef) notes.push("Субсидии для этой комплектации на сайте нет.");
    dc = Math.max(0, Math.round(Number(dc)||0));
    return {rrc, tuning, fleet, ti:tiAmt, dc, sub:subOn?subRef:0, subOn, total: rrc+tuning-fleet-tiAmt-dc, code, src, notes};
  }
  // opts: {mid, cat, ti, tuning, lessor, client}
  function fleetKpDoc(opts){
    const d = offerDeal();
    const m = (d.models||[]).find(x=>x.id===opts.mid) || d.m;
    if (d.m.id!==m.id) throw new Error("fleet-kp: trim mismatch "+d.m.id+" vs "+m.id);
    const cat = FLEET_KP_CATS[opts.cat] ? opts.cat : "c1";
    const label = FLEET_KP_CATS[cat][0];
    const tuning = Math.max(0, Math.round(Number(opts.tuning)||0));
    const c = fleetCalc(m, cat, !!opts.ti, tuning, opts.dc);
    const doc = offerDocNew(d);
    const rows = [["РРЦ", rubP(c.rrc)], ["Тюнинг", rubP(c.tuning)],
      ["Скидка флит ("+c.code+")", (c.fleet?"− ":"")+rubP(c.fleet)], ["Скидка ТИ", (c.ti?"− ":"")+rubP(c.ti)]];
    if (c.dc) rows.push(["Скидка ДЦ", "− "+rubP(c.dc)]);
    const total = ["Цена с уч. скидок и тюнинга", rubP(c.total)];
    const sub = c.subOn ? "+"+rubP(c.sub)+" субсидия — идёт в первый взнос" : null;
    const notes = ["Флит, категория "+label+" (ценовая категория "+c.code+" по политике корпоративных продаж TENET от 08.10.2026).",
      "Цена с уч. скидок и тюнинга = РРЦ + тюнинг − скидка флит − скидка ТИ"+(c.dc?" − скидка ДЦ":"")+"."];
    if (c.subOn) notes.push("Субсидия из цены не вычитается — она идёт в первый взнос.");
    if (cat==="c1"||cat==="c2") notes.push("Ориентир ставки лизинга: Совкомбанк лизинг 22,5%, Сбер 24% годовых. Не оферта.");
    c.notes.forEach(n=>notes.push(n));
    const lessor = cat==="c1" ? (opts.lessor || FLEET_KP_LESSORS[0]) : null;
    const today = new Date().toLocaleDateString("ru-RU");
    doc.kicker = "Флит · "+label;
    doc.rows = rows; doc.total = total;
    doc.fleet = {rows, total, sub, contact: FLEET_KP_MGR[0]+", "+FLEET_KP_MGR[1]};
    doc.file = "КП флит "+m.name+" "+label+(lessor?" "+lessor:"");
    doc.meta = (lessor?[["Лизинговая компания", lessor]]:(String(opts.client||"").trim()?[["Клиент", String(opts.client).trim()]]:[])).concat([["Категория", label],
      ["Трейд-ин", opts.ti?"да":"нет"], ["Дата", today]]);
    doc.sections = (doc.sections||[]).filter(s=>!s.deals && !s.cmp);
    doc.sections.unshift({title:"Условия флита", lines:notes});
    const st = fleetStockSection(m);
    if (st) doc.sections.splice(1, 0, st);
    doc.calc = c;
    return doc;
  }
  // Тестовые авто «Тесты в продаже» (TEST_SALE): цена фикс, без субсидии и без скидок флит/ТИ; итог = фикс + тюнинг.
  const FLEET_KP_TEST_TRIM = {tst9:"t9u", tsa8:"a8u", tst4:null};
  function fleetTests(){ return (typeof TEST_SALE!=="undefined" && Array.isArray(TEST_SALE)) ? TEST_SALE : []; }
  function fleetKpTestDoc(opts){
    const t = fleetTests().find(x=>x.id===opts.test);
    if (!t) throw new Error("fleet-kp: no test car "+opts.test);
    const cat = FLEET_KP_CATS[opts.cat] ? opts.cat : "c1";
    const label = FLEET_KP_CATS[cat][0];
    const tuning = Math.max(0, Math.round(Number(opts.tuning)||0));
    const base = FLEET_KP_TEST_TRIM[t.id];
    let doc;
    const sel = document.getElementById("ofModel");
    if (base && sel) {
      const prev = sel.value;
      if (![...sel.options].some(o=>o.value===base)) sel.add(new Option("", base));
      sel.value = base;
      try { const d = offerDeal(); doc = d.m && d.m.id===base ? offerDocNew(d) : null; } catch(e) { doc = null; }
      sel.value = prev;
      if (doc) doc.sections = (doc.sections||[]).filter(s=>!s.deals && !s.cmp);
    }
    if (!doc) doc = {title:"Коммерческое предложение", meta:[], sections:[], photos:[], note:""};
    const dc = Math.max(0, Math.round(Number(opts.dc)||0));
    const total = [dc ? "Цена с уч. скидок и тюнинга" : "Цена с уч. тюнинга", rubP(t.fix+tuning-dc)];
    const rows = [["Цена фикс (тестовый автомобиль)", rubP(t.fix)], ["Тюнинг", rubP(tuning)]];
    if (dc) rows.push(["Скидка ДЦ", "− "+rubP(dc)]);
    const lessor = cat==="c1" ? (opts.lessor || FLEET_KP_LESSORS[0]) : null;
    const client = String(opts.client||"").trim();
    doc.kicker = "Флит · "+label+" · тестовый автомобиль";
    doc.headline = t.model+" · VIN "+t.vin;
    doc.rows = rows; doc.total = total;
    doc.fleet = {rows, total, sub:null, contact: FLEET_KP_MGR[0]+", "+FLEET_KP_MGR[1]};
    doc.file = "КП флит тест "+t.short+" "+t.vin.slice(-6)+(lessor?" "+lessor:"");
    doc.meta = (lessor?[["Лизинговая компания", lessor]]:(client?[["Клиент", client]]:[])).concat([
      ["Категория", label], ["VIN", t.vin], ["Год / пробег", t.year+" · "+rub(t.km)+" км"], ["Дата", new Date().toLocaleDateString("ru-RU")]]);
    const notes = ["Тестовый автомобиль "+t.year+" г., пробег "+rub(t.km)+" км. Цена фикс — скидки флита и трейд-ина не применяются, субсидии нет.",
      dc ? "Цена с уч. скидок и тюнинга = цена фикс + тюнинг − скидка ДЦ." : "Цена с уч. тюнинга = цена фикс + тюнинг.",
      "Справочно: РРЦ нового "+rubP(t.rrc)+", на автомобиле установлено доп. оборудования на "+rubP(t.tune)+"."];
    if (cat==="c1"||cat==="c2") notes.push("Ориентир ставки лизинга: Совкомбанк лизинг 22,5%, Сбер 24% годовых. Не оферта.");
    if (!base) notes.push("Оснащение — по данным автомобиля в салоне; лист оснащения этой модели на сайте не ведётся.");
    doc.sections.unshift({title:"Условия флита", lines:notes});
    doc.sections.splice(1, 0, {title:"В наличии", lines:["VIN "+t.vin+" · "+t.year+" г. · пробег "+rub(t.km)+" км · тестовый автомобиль в салоне"]});
    doc.calc = {test:t.id, vin:t.vin, fix:t.fix, tuning, dc, total:t.fix+tuning-dc, rrc:t.rrc, fleet:0, ti:0, sub:0, subOn:false, notes:[]};
    return doc;
  }
  // «В наличии»: только чтение STOCK сайта (kmStockCars — без демо); в салоне и в пути.
  function fleetStockSection(m){
    let list = [];
    try { list = (typeof kmStockCars==="function" ? kmStockCars(m) : []) || []; } catch(e) { list = []; }
    list = list.filter(c=>c && (c.status==="in" || c.status==="way") && !c.sold && !c.reserved);
    list.sort((a,b)=>(a.status==="in"?0:1)-(b.status==="in"?0:1));
    if (!list.length) return {title:"В наличии", lines:["Подходящих автомобилей этой комплектации на складе сейчас нет — срок поставки уточняйте у менеджера."]};
    const yr = c => { try { if (typeof stockYear==="function") { const y=stockYear(c); if (y) return String(y); } } catch(e){} const p=String(c.prod||"").match(/(\d{4})/); return p?p[1]:""; };
    const MAX = 15;
    const lines = list.slice(0, MAX).map(c=>["VIN …"+String(c.vin||"").toUpperCase().slice(-8), c.color||"", yr(c)?yr(c)+" г.":"", c.status==="in"?"в салоне":"в пути"+(c.note?" ("+String(c.note).split("·").pop().trim()+")":"")].filter(Boolean).join(" · "));
    if (list.length > MAX) lines.push("и ещё "+(list.length-MAX)+" авто — уточняйте у менеджера");
    lines.unshift("Подходящих автомобилей: "+list.length+" (в салоне "+list.filter(c=>c.status==="in").length+", в пути "+list.filter(c=>c.status==="way").length+").");
    return {title:"В наличии", lines};
  }
  // Word (.docx) без внешних библиотек: ZIP (store) + WordprocessingML.
  const CRC_T = (()=>{ const t=new Uint32Array(256); for(let n=0;n<256;n++){ let c=n; for(let k=0;k<8;k++) c = c&1 ? 0xEDB88320^(c>>>1) : c>>>1; t[n]=c>>>0; } return t; })();
  const crc32 = u => { let c=0xFFFFFFFF; for(let i=0;i<u.length;i++) c=CRC_T[(c^u[i])&255]^(c>>>8); return (c^0xFFFFFFFF)>>>0; };
  function zipStore(files){
    const enc=new TextEncoder(), parts=[], cen=[]; let off=0;
    const le=(n,b)=>{ const a=[]; for(let i=0;i<b;i++) a.push((n>>>(8*i))&255); return a; };
    files.forEach(([name, text])=>{
      const nm=enc.encode(name), data=enc.encode(text), crc=crc32(data);
      const loc=new Uint8Array([].concat([0x50,0x4b,3,4],le(20,2),le(0x800,2),le(0,2),le(0,2),le(0x21,2),le(crc,4),le(data.length,4),le(data.length,4),le(nm.length,2),le(0,2)));
      parts.push(loc, nm, data);
      cen.push(new Uint8Array([].concat([0x50,0x4b,1,2],le(20,2),le(20,2),le(0x800,2),le(0,2),le(0,2),le(0x21,2),le(crc,4),le(data.length,4),le(data.length,4),le(nm.length,2),le(0,2),le(0,2),le(0,2),le(0,2),le(0,4),le(off,4))), nm);
      off += loc.length+nm.length+data.length;
    });
    const cs = cen.reduce((a,x)=>a+x.length,0);
    const end=new Uint8Array([].concat([0x50,0x4b,5,6],le(0,2),le(0,2),le(files.length,2),le(files.length,2),le(cs,4),le(off,4),le(0,2)));
    const all=parts.concat(cen,[end]), out=new Uint8Array(all.reduce((a,x)=>a+x.length,0)); let p=0;
    all.forEach(x=>{ out.set(x,p); p+=x.length; });
    return out;
  }
  function fleetKpDocx(doc){
    const x = s => String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
    const run = (t,o={}) => `<w:r><w:rPr>${o.b?"<w:b/>":""}${o.color?`<w:color w:val="${o.color}"/>`:""}<w:sz w:val="${(o.sz||10)*2}"/></w:rPr><w:t xml:space="preserve">${x(t)}</w:t></w:r>`;
    const para = (runs,o={}) => `<w:p><w:pPr>${o.shd?`<w:shd w:val="clear" w:color="auto" w:fill="${o.shd}"/>`:""}${o.jc?`<w:jc w:val="${o.jc}"/>`:""}<w:spacing w:before="${o.before||0}" w:after="${o.after==null?60:o.after}"/>${o.ind?`<w:ind w:left="${o.ind}"/>`:""}</w:pPr>${runs}</w:p>`;
    const P = (t,o={}) => para(run(t,o), o);
    const cell = (inner,w,fill) => `<w:tc><w:tcPr><w:tcW w:w="${w}" w:type="dxa"/>${fill?`<w:shd w:val="clear" w:color="auto" w:fill="${fill}"/>`:""}</w:tcPr>${inner}</w:tc>`;
    const table = (rows, ws, opt={}) => `<w:tbl><w:tblPr><w:tblW w:w="${ws.reduce((a,b)=>a+b,0)}" w:type="dxa"/><w:tblBorders>${["top","left","bottom","right","insideH","insideV"].map(b=>`<w:${b} w:val="single" w:sz="4" w:color="${opt.border||"C9AB7C"}"/>`).join("")}</w:tblBorders><w:tblCellMar><w:left w:w="100" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>${ws.map(w=>`<w:gridCol w:w="${w}"/>`).join("")}</w:tblGrid>${rows.map(r=>`<w:tr>${r}</w:tr>`).join("")}</w:tbl>`;
    const b = [];
    const F = doc.fleet;
    b.push(P(F ? "TENET  ·  КОРПОРАТИВНЫЙ МЕНЕДЖЕР ПАВЛОВА ОКСАНА  ·  "+FLEET_KP_MGR[1] : "TENET  ·  ОТДЕЛ ПРОДАЖ", {sz:9, color:"8A8178"}));
    b.push(P("ЭКСПЕРТ АВТО САМАРА", {b:1, sz:16}));
    if (doc.kicker) b.push(P(String(doc.kicker).toUpperCase(), {b:1, sz:9, color:"C8102E", before:120}));
    b.push(P(doc.title||"Коммерческое предложение", {b:1, sz:22}));
    if (doc.headline) b.push(P(doc.headline, {sz:12}));
    if ((doc.meta||[]).length) b.push(table(doc.meta.map(([k,v])=>cell(P(k,{sz:10,color:"6B645C"}),3200)+cell(P(v==null||v===""?"—":v,{b:1,sz:10}),6400)), [3200,6400], {border:"E5DED3"}));
    if (F) {
      b.push(P("КОНТАКТ ПО ФЛИТУ: "+F.contact, {b:1, sz:11, color:"FFFFFF", shd:"1D2B3A", before:160}));
      const rr = F.rows.map(([k,v],i)=>cell(P(k,{b:i===0,sz:i===0?12:11}),6000,"FBF6EC")+cell(P(v,{b:1,sz:i===0?13:11,jc:"right"}),3600,"FBF6EC"));
      rr.push(cell(P(F.total[0],{b:1,sz:12}),6000,"EFE4CF")+cell(P(F.total[1],{b:1,sz:14,jc:"right"}),3600,"EFE4CF"));
      if (F.sub) rr.push(cell(P("БОНУС",{b:1,sz:10,color:"FFFFFF"}),6000,"1F8A4C")+cell(P(F.sub,{b:1,sz:11,color:"FFFFFF",jc:"right"}),3600,"1F8A4C"));
      b.push(P("", {after:40})); b.push(table(rr, [6000,3600]));
    } else {
      (doc.rows||[]).forEach(([k,v])=>b.push(P(k+": "+v, {sz:11})));
      if (doc.total) b.push(P(doc.total[0]+": "+doc.total[1], {b:1, sz:13}));
    }
    (doc.sections||[]).forEach(sec=>{
      if (sec.deals || sec.cmp) return;
      b.push(P(String(sec.title||"").toUpperCase(), {b:1, sz:11, color:"C8102E", before:220}));
      (sec.lines||[]).forEach(l=>b.push(P("• "+l, {sz:10, ind:200})));
      if (sec.pairs) b.push(table(sec.pairs.map(([k,v])=>cell(P(k,{sz:10,color:"6B645C"}),3600)+cell(P(v,{sz:10}),6000)), [3600,6000], {border:"E5DED3"}));
      (sec.groups||[]).forEach(([g, items])=>{ b.push(P(g, {b:1, sz:11, before:100})); (items||[]).forEach(it=>b.push(P("• "+it, {sz:10, ind:200, after:20}))); });
      (sec.items||[]).forEach(it=>b.push(P("• "+(Array.isArray(it)?it.join(" — "):it), {sz:10, ind:200})));
    });
    if (doc.note) b.push(P(doc.note, {sz:9, color:"6B645C", before:120}));
    if (F) b.push(P("ВАШ КОРПОРАТИВНЫЙ МЕНЕДЖЕР: "+F.contact, {b:1, sz:12, color:"FFFFFF", shd:"1D2B3A", before:240}));
    b.push(P("Не оферта · ООО «ЭКСПЕРТ АВТО САМАРА»", {sz:9, color:"8A8178", before:200}));
    const W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"';
    const docXml = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document ${W}><w:body>${b.join("")}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1100" w:header="500" w:footer="500" w:gutter="0"/></w:sectPr></w:body></w:document>`;
    const styles = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles ${W}><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial" w:eastAsia="Arial"/><w:lang w:val="ru-RU"/></w:rPr></w:rPrDefault></w:docDefaults></w:styles>`;
    return zipStore([
      ["[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'],
      ["_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'],
      ["word/_rels/document.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'],
      ["word/styles.xml", styles],
      ["word/document.xml", docXml]]);
  }
  const fleetDocxName = doc => offerFileName(doc).replace(/\.pdf$/i,"")+".docx";
  const u8b64 = u8 => { let s=""; for (let i=0;i<u8.length;i+=0x8000) s+=String.fromCharCode.apply(null, u8.subarray(i,i+0x8000)); return btoa(s); };
  async function fleetKpBytes(doc){
    const imgs = await offerLoadImgs(doc.photos||[]);
    const pages = offerPaint(doc, imgs).map(cv=>({w:cv.width,h:cv.height,jpeg:offerJpeg(cv)}));
    const b = offerPdfBytes(pages);
    return b instanceof Uint8Array ? b : new Uint8Array(b);
  }
  // для бота: base64 PDF по параметрам (требует открытого раздела КП с выбранной комплектацией)
  async function fleetKpBase64(opts){
    if (opts.test) {
      const doc = fleetKpTestDoc(opts);
      return {b64: u8b64(await fleetKpBytes(doc)), docx: u8b64(fleetKpDocx(doc)), docxFile: fleetDocxName(doc), file: offerFileName(doc), calc: doc.calc, meta: doc.meta};
    }
    const sel = document.getElementById("ofModel");
    if (sel && sel.value!==opts.mid) { sel.value=opts.mid; sel.dispatchEvent(new Event("change",{bubbles:true})); await new Promise(r=>setTimeout(r,500)); }
    const doc = fleetKpDoc(opts);
    return {b64: u8b64(await fleetKpBytes(doc)), docx: u8b64(fleetKpDocx(doc)), docxFile: fleetDocxName(doc), file: offerFileName(doc), calc: doc.calc, meta: doc.meta};
  }

  function fleetOpts(){
    const v = (id, def) => offerVal(id, def);
    return {mid: v("ofModel", null), cat: v("flCat","c1"), ti: v("flTi","1")==="1",
      test: v("flTest",""), tuning: Number(String(v("flTune","0")).replace(/\s+/g,""))||0, dc: Math.max(0, Number(String(v("flDc","0")).replace(/\s+/g,""))||0), lessor: v("flLessor", FLEET_KP_LESSORS[0]), client: v("flClient","")};
  }
  // Tiggo 9 и Arrizo 8 во флит-КП не продаются (решение 29.10.2026).
  const FLEET_KP_SKIP = {t9:1, a8:1};
  const fleetOk = m => m && !FLEET_KP_SKIP[m.stock];
  function offerFleet(){
    const o = fleetOpts();
    let d = offerDeal();
    if (!fleetOk(d.m)) {
      const first = (d.models||[]).find(fleetOk), sel = document.getElementById("ofModel");
      if (first && sel) { if (![...sel.options].some(x=>x.value===first.id)) sel.add(new Option("", first.id)); sel.value = first.id; d = offerDeal(); }
    }
    d.models = (d.models||[]).filter(fleetOk);
    o.mid = d.m.id;
    const doc = o.test ? fleetKpTestDoc(o) : fleetKpDoc(o);
    const opt = (id, cur, list) => `<select id="${id}" class="of-select">${list.map(([k,l])=>`<option value="${escape(k)}"${k===cur?" selected":""}>${escape(l)}</option>`).join("")}</select>`;
    const tests = fleetTests();
    const form = `
      ${tests.length ? offerField("Автомобиль", opt("flTest", o.test, [["","Новый (выбрать комплектацию)"]].concat(tests.map(t=>[t.id, "Тест: "+t.model+" · "+t.vin+" · фикс "+rub(t.fix)+" ₽"])))) : ""}
      <div style="${o.test?"display:none":""}">${offerField("Комплектация", offerModelSelect("ofModel", d.models, d.mid))}</div>
      ${offerField("Категория", opt("flCat", o.cat, Object.keys(FLEET_KP_CATS).map(k=>[k, FLEET_KP_CATS[k][0]+" · "+FLEET_KP_CATS[k][1]])))}
      ${o.cat==="c1" ? offerField("Лизинговая компания (партнёр С1)", opt("flLessor", o.lessor, FLEET_KP_LESSORS.map(x=>[x,x])))
                     : offerField("Клиент", `<input id="flClient" value="${escape(o.client)}" />`)}
      ${o.test ? "" : offerField("Трейд-ин", opt("flTi", o.ti?"1":"0", [["1","С трейд-ином"],["0","Без трейд-ина"]]))}
      ${offerField("Тюнинг, ₽", `<input id="flTune" inputmode="numeric" value="${o.tuning}" />`)}
      ${offerField("Скидка ДЦ, ₽", `<input id="flDc" inputmode="numeric" value="${o.dc}" />`)}
      <p class="calc-note">Субсидия (только С1) не вычитается из цены — идёт в первый взнос. Менеджер по флиту: ${escape(FLEET_KP_MGR[0])}, ${escape(FLEET_KP_MGR[1])}.</p>`;
    const _act = offerActions;
    offerActions = function(){ const h=_act(); return h.replace('data-offer-pdf>Скачать PDF</button>', 'data-offer-pdf>Скачать PDF</button><button type="button" class="btn ghost" data-fleet-docx>Скачать Word</button>'); };
    try { return offerScreen("КП Флит", form, doc); } finally { offerActions = _act; }
  }
  const _nav = offerNav;
  offerNav = function(){
    const h = _nav();
    if (h.indexOf('data-offer-tab="fleet"')>=0) return h;
    const btn = `<button type="button" class="chip ${offerTab==="fleet"?"on":""}" data-offer-tab="fleet">КП Флит</button>`;
    const i = h.lastIndexOf("</div>");
    return i>=0 ? h.slice(0,i)+btn+h.slice(i) : h+btn;
  };
  const _offer = offer;
  offer = function(){
    if (offerTab==="lease") offerTab="fleet";
    if (offerTab==="fleet" && !(typeof needAuth==="function" && needAuth())) {
      try { return offerFleet(); } catch(e) { console.warn("fleet-kp", e); }
    }
    return _offer();
  };
  const _bind = offerBind;
  offerBind = function(){
    _bind();
    const wb=document.querySelector("[data-fleet-docx]");
    if (wb) wb.addEventListener("click", ()=>{ try {
      const doc=offerDocCurrent, blob=new Blob([fleetKpDocx(doc)], {type:"application/vnd.openxmlformats-officedocument.wordprocessingml.document"});
      const a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download=fleetDocxName(doc); document.body.appendChild(a); a.click();
      setTimeout(()=>{ URL.revokeObjectURL(a.href); a.remove(); }, 1500);
    } catch(e) { console.warn("fleet-kp docx", e); alert("Не удалось собрать Word: "+e.message); } });
    ["flTest","flCat","flLessor","flClient","flTi","flTune","flDc"].forEach(id=>{ const el=document.getElementById(id); if(el) el.addEventListener("change", ()=>{ view="offer"; render(); }); });
  };
  window.fleetKpDoc = fleetKpDoc; window.fleetKpBytes = fleetKpBytes; window.fleetKpBase64 = fleetKpBase64; window.fleetKpDocx = fleetKpDocx;
  window.FLEET_KP_LESSORS = FLEET_KP_LESSORS; window.FLEET_KP_CATS = FLEET_KP_CATS;
})();
