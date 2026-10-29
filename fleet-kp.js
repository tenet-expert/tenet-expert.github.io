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
  function fleetCalc(m, cat, ti, tuning){
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
    return {rrc, tuning, fleet, ti:tiAmt, sub:subOn?subRef:0, subOn, total: rrc+tuning-fleet-tiAmt, code, src, notes};
  }
  // opts: {mid, cat, ti, tuning, lessor, client}
  function fleetKpDoc(opts){
    const d = offerDeal();
    const m = (d.models||[]).find(x=>x.id===opts.mid) || d.m;
    if (d.m.id!==m.id) throw new Error("fleet-kp: trim mismatch "+d.m.id+" vs "+m.id);
    const cat = FLEET_KP_CATS[opts.cat] ? opts.cat : "c1";
    const label = FLEET_KP_CATS[cat][0];
    const tuning = Math.max(0, Math.round(Number(opts.tuning)||0));
    const c = fleetCalc(m, cat, !!opts.ti, tuning);
    const doc = offerDocNew(d);
    const rows = [["РРЦ", rubP(c.rrc)], ["Тюнинг", rubP(c.tuning)],
      ["Скидка флит ("+c.code+")", (c.fleet?"− ":"")+rubP(c.fleet)], ["Скидка ТИ", (c.ti?"− ":"")+rubP(c.ti)]];
    const total = ["Цена с уч. скидок и тюнинга", rubP(c.total)];
    const sub = c.subOn ? "+"+rubP(c.sub)+" субсидия — идёт в первый взнос" : null;
    const notes = ["Флит, категория "+label+" (ценовая категория "+c.code+" по политике корпоративных продаж TENET от 08.10.2026).",
      "Цена с уч. скидок и тюнинга = РРЦ + тюнинг − скидка флит − скидка ТИ."];
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
    const total = ["Цена с уч. тюнинга", rubP(t.fix+tuning)];
    const rows = [["Цена фикс (тестовый автомобиль)", rubP(t.fix)], ["Тюнинг", rubP(tuning)]];
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
      "Цена с уч. тюнинга = цена фикс + тюнинг.",
      "Справочно: РРЦ нового "+rubP(t.rrc)+", на автомобиле установлено доп. оборудования на "+rubP(t.tune)+"."];
    if (cat==="c1"||cat==="c2") notes.push("Ориентир ставки лизинга: Совкомбанк лизинг 22,5%, Сбер 24% годовых. Не оферта.");
    if (!base) notes.push("Оснащение — по данным автомобиля в салоне; лист оснащения этой модели на сайте не ведётся.");
    doc.sections.unshift({title:"Условия флита", lines:notes});
    doc.calc = {test:t.id, vin:t.vin, fix:t.fix, tuning, total:t.fix+tuning, rrc:t.rrc, fleet:0, ti:0, sub:0, subOn:false, notes:[]};
    return doc;
  }
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
      const u8 = await fleetKpBytes(doc);
      let s=""; for (let i=0;i<u8.length;i+=0x8000) s+=String.fromCharCode.apply(null, u8.subarray(i,i+0x8000));
      return {b64: btoa(s), file: offerFileName(doc), calc: doc.calc, meta: doc.meta};
    }
    const sel = document.getElementById("ofModel");
    if (sel && sel.value!==opts.mid) { sel.value=opts.mid; sel.dispatchEvent(new Event("change",{bubbles:true})); await new Promise(r=>setTimeout(r,500)); }
    const doc = fleetKpDoc(opts);
    const u8 = await fleetKpBytes(doc);
    let s=""; for (let i=0;i<u8.length;i+=0x8000) s+=String.fromCharCode.apply(null, u8.subarray(i,i+0x8000));
    return {b64: btoa(s), file: offerFileName(doc), calc: doc.calc, meta: doc.meta};
  }

  function fleetOpts(){
    const v = (id, def) => offerVal(id, def);
    return {mid: v("ofModel", null), cat: v("flCat","c1"), ti: v("flTi","1")==="1",
      test: v("flTest",""), tuning: Number(String(v("flTune","0")).replace(/\s+/g,""))||0, lessor: v("flLessor", FLEET_KP_LESSORS[0]), client: v("flClient","")};
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
      <p class="calc-note">Субсидия (только С1) не вычитается из цены — идёт в первый взнос. Менеджер по флиту: ${escape(FLEET_KP_MGR[0])}, ${escape(FLEET_KP_MGR[1])}.</p>`;
    return offerScreen("КП Флит", form, doc);
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
    ["flTest","flCat","flLessor","flClient","flTi","flTune"].forEach(id=>{ const el=document.getElementById(id); if(el) el.addEventListener("change", ()=>{ view="offer"; render(); }); });
  };
  window.fleetKpDoc = fleetKpDoc; window.fleetKpBytes = fleetKpBytes; window.fleetKpBase64 = fleetKpBase64;
  window.FLEET_KP_LESSORS = FLEET_KP_LESSORS; window.FLEET_KP_CATS = FLEET_KP_CATS;
})();
