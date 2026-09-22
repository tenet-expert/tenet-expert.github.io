    let offerTab = "home";
    function offerVal(id, def){
      const el=document.getElementById(id);
      if(!el) return def;
      const v=String(el.value||"").trim();
      return v||def;
    }
    function offerNum(id, def){
      const el=document.getElementById(id);
      if(!el) return def;
      const n=Number(String(el.value||"").replace(/\s+/g,""));
      return Number.isFinite(n)?n:def;
    }
    function offerOn(id){
      const el=document.getElementById(id);
      return !!(el && el.checked);
    }
    function offerMgr(){
      return (typeof state!=="undefined" && state.display) ? state.display : "отдел продаж";
    }
    function offerCopy(id){
      const el=document.getElementById(id);
      if(!el) return;
      const t=el.innerText||el.textContent||"";
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(t).catch(function(){
          const ta=document.createElement("textarea");
          ta.value=t; document.body.appendChild(ta); ta.select();
          try{ document.execCommand("copy"); }catch(e){}
          ta.remove();
        });
        return;
      }
      const ta=document.createElement("textarea");
      ta.value=t; document.body.appendChild(ta); ta.select();
      try{ document.execCommand("copy"); }catch(e){}
      ta.remove();
    }
    function offerNav(){
      const tabs=[["home","Разделы"],["new","КП Новый а/м"],["service","КП Сервис"],["lease","КП Лизинг"]];
      return `<div class="down-mode" style="margin:0 0 14px">${tabs.map(([id,l])=>`<button type="button" class="chip ${offerTab===id?"on":""}" data-offer-tab="${id}">${l}</button>`).join("")}</div>`;
    }
    function offerHome(){
      const cards=[["new","Н","КП Новый а/м","Прайс, скидки, каско, кредит / МПТ и PDF"],["service","С","КП Сервис","ТО, сезон, гарантия и пакеты ДЦ"],["lease","Л","КП Лизинг","Компания, флит / BFS, аванс и срок"]];
      return banner("Коммерческое предложение","TENET · Отдел продаж","КП")+`\n        <p class="lead">Три шаблона. Новый а/м тянет полный лист из прайса и считает условия как калькулятор.</p>\n        ${offerNav()}\n        <div class="hub-grid offer-grid">${cards.map(([id,mark,title,lead])=>`<button class="card hub-card" data-offer-tab="${id}" type="button"><span class="hub-mark">${mark}</span><div class="txt"><h3>${title}</h3><p>${lead}</p></div></button>`).join("")}</div>`;
    }
    function offerDeal(){
      const models=typeof KM_MODELS!=="undefined"?KM_MODELS:[];
      const mid=offerVal("ofModel", models[0]?models[0].id:"t7a");
      const m=models.find(x=>x.id===mid)||models[0]||{id:"t7a",name:"TENET",rrc:0,ti:0,cr:0};
      const prevModel=offerVal("ofPrevModel", mid);
      const client=offerVal("ofClient","Уважаемый клиент");
      const color=offerVal("ofColor","на выбор");
      let price=offerNum("ofPrice", m.rrc)||m.rrc;
      if(prevModel!==mid) price=m.rrc;
      const useTi=offerOn("ofTi");
      const useLoan=offerOn("ofLoan");
      const showDealCr=(m.cr||0)>0 && (m.id!=="t7p" || useLoan);
      const useCr=showDealCr && offerOn("ofCr");
      const spec=offerNum("ofSpec", 0)||0;
      const useDcTi=useTi && offerOn("ofDcTi");
      const useDcCr=useLoan && offerOn("ofDcCr");
      const dcDef=typeof KM_DC_DEF==="number"?KM_DC_DEF:100000;
      const dcTi=useDcTi?offerNum("ofDcTiAmt", dcDef)||0:0;
      const dcCr=useDcCr?offerNum("ofDcCrAmt", dcDef)||0:0;
      const addons=offerNum("ofDo", 0)||0;
      let casco=0, pack=0;
      if(useLoan){ pack=offerNum("ofPack", 150000)||0; casco=Math.min(pack, 80000); }
      else casco=offerNum("ofCasco", 0)||0;
      const months=offerNum("ofMonths", 60)||60;
      const downMode=offerVal("ofDownMode","pct");
      let downPct=offerNum("ofDownPct", 20);
      let down=offerNum("ofDown", Math.round(price*0.2));
      const tiAmt=useTi?(m.ti||0):0;
      const crAmt=useCr?(m.cr||0):0;
      const discount=tiAmt+spec+dcTi+dcCr+crAmt;
      const carPrice=Math.max(0, price-discount);
      if(downMode==="pct") down=Math.round(carPrice*Math.max(0,downPct)/100);
      else downPct=carPrice>0?Math.round(down*1000/carPrice)/10:0;
      down=Math.max(0, Math.min(carPrice, down));
      const fee=useLoan?(typeof KM_BANK_FEE==="number"?KM_BANK_FEE:30000):0;
      const extras=useLoan?(addons+pack+fee):0;
      const credit=Math.max(0, carPrice-down+extras);
      const clientPay=carPrice+addons+(useLoan?0:casco);
      const valid=offerVal("ofValid","7 дней");
      const packEq=typeof offerPack==="function"?offerPack(m.id):null;
      const equip=typeof offerPackText==="function"?offerPackText(packEq):"";
      const rateGroup=typeof kmRateGroup==="function"?kmRateGroup(m):"t4l_t7";
      const banks=(useLoan && typeof KM_BANKS!=="undefined"?KM_BANKS:[]).map(b=>{
        const look=typeof kmBankRate==="function"?kmBankRate(b.id, rateGroup, months, downPct):{rate:19.2, term:months};
        const term=look.term||months;
        const pay=typeof calcPay==="function"?calcPay(carPrice+extras, down, term, look.rate):0;
        return {name:b.name, rate:look.rate, term, pay:Math.round(pay), over:Math.round(pay*term-credit)};
      });
      let mptTxt="";
      if(useLoan && /^t7(a|p)/.test(m.id)){
        const f=typeof fleetOf==="function"?fleetOf(m.id):null;
        const mptTidy=f&&f.tidy?f.tidy:(f&&f.rrc?f.rrc:carPrice);
        const tiMpt=useTi?(typeof FLEET_TI==="number"?FLEET_TI:50000):0;
        const priceMpt=Math.round(Math.max(0, mptTidy-tiMpt)*0.9);
        const extraMpt=200000;
        const downMptShow=Math.max(0, Math.min(priceMpt, down));
        const downMptCar=Math.max(0, downMptShow-extraMpt);
        const creditMpt=Math.max(0, priceMpt-downMptCar);
        const mptTerm=Math.min(months, 84);
        const payMpt=typeof calcPay==="function"?Math.round(calcPay(priceMpt, downMptCar, mptTerm, 19.2)):0;
        mptTxt="Госпрограмма МПТ · Совкомбанк 19,2%\nФлит: "+rub(mptTidy)+" ₽"+(tiMpt?" · трейд-ин "+rub(tiMpt)+" ₽":"")+"\nЦена с МПТ −10%: "+rub(priceMpt)+" ₽\nПервый взнос: "+rub(downMptShow)+" ₽\nПВ в авто: "+rub(downMptCar)+" ₽\nТело: "+rub(creditMpt)+" ₽\nПлатёж: "+(payMpt?rub(payMpt)+" ₽ / мес. · "+mptTerm+" мес.":"—");
      }
      const discLines=[];
      if(tiAmt) discLines.push("Трейд-ин импортёра: − "+rub(tiAmt)+" ₽");
      if(useCr && crAmt) discLines.push((m.id==="t7p"?"Выгодный кредит":"Программа кредита")+": − "+rub(crAmt)+" ₽");
      if(spec) discLines.push("Спецпредложение: − "+rub(spec)+" ₽");
      if(dcTi) discLines.push("Скидка ДЦ за трейд-ин: − "+rub(dcTi)+" ₽");
      if(dcCr) discLines.push("Скидка ДЦ за кредит: − "+rub(dcCr)+" ₽");
      const bankLines=banks.map(b=>"• "+b.name+": "+b.rate+"% · "+b.term+" мес. · "+rub(b.pay)+" ₽ / мес.").join("\n");
      const text="Коммерческое предложение · новый автомобиль\nООО «ЭКСПЕРТ АВТО САМАРА» · TENET\n\nКлиент: "+client+"\nАвтомобиль: "+m.name+"\nЦвет: "+color+"\n\nРРЦ: "+rub(price)+" ₽\n"+(discLines.length?discLines.join("\n")+"\n":"")+"Итого за автомобиль: "+rub(carPrice)+" ₽\nДополнительное оборудование: "+(addons?rub(addons)+" ₽":"по согласованию")+"\n"+(useLoan?"Каско расширенное / пакет СЖ: "+rub(pack)+" ₽":(casco?"КАСКО: "+rub(casco)+" ₽":"КАСКО: не включено"))+"\nИтого клиенту: "+rub(clientPay)+" ₽\n"+(useLoan?"Первый взнос: "+rub(down)+" ₽ ("+downPct+"%)\nСрок: "+months+" мес.\nТело кредита: "+rub(credit)+" ₽\nКомиссия банка: "+rub(fee)+" ₽\nПлатежи:\n"+(bankLines||"—")+(mptTxt?"\n\n"+mptTxt:""):"Оплата: без кредита.")+"\n\nПредложение действует "+valid+".\nНе оферта. Итоговые условия — в договоре салона.\nМенеджер: "+offerMgr()+"\n"+equip;
      return {m, mid, models, client, color, price, useTi, useLoan, showDealCr, useCr, spec, useDcTi, useDcCr, dcDef, dcTi, dcCr, addons, casco, pack, months, downMode, downPct, down, carPrice, clientPay, credit, fee, extras, valid, packEq, text, banks, mptTxt, discount};
    }
    function offerNew(){
      const d=offerDeal();
      const banksHtml=d.useLoan && d.banks.length?`<div class="offer-banks">${d.banks.map(b=>`<div class="bank-row"><span><b>${escape(b.name)}</b><br/><small>${b.rate}% · ${b.term} мес.</small></span><span class="pay">${rub(b.pay)} ₽</span></div>`).join("")}</div>`:"";
      return banner("КП Новый а/м","Коммерческое предложение","КП")+`\n        ${offerNav()}\n        <div class="km-layout">\n          <div class="card">\n            <p class="eyebrow">Данные и условия</p>\n            <input type="hidden" id="ofPrevModel" value="${escape(d.mid)}" />\n            <label class="field" style="max-width:none"><span>Клиент</span><input id="ofClient" value="${escape(d.client)}" /></label>\n            <label class="field" style="max-width:none"><span>Комплектация</span><select id="ofModel">${d.models.map(x=>`<option value="${x.id}" ${x.id===d.mid?"selected":""}>${escape(x.name)} · ${rub(x.rrc)}</option>`).join("")}</select></label>\n            <label class="field" style="max-width:none"><span>Цвет</span><input id="ofColor" value="${escape(d.color)}" /></label>\n            <label class="field" style="max-width:none"><span>РРЦ, ₽</span><input id="ofPrice" inputmode="numeric" value="${d.price}" /></label>\n            <label class="check-row"><input id="ofTi" type="checkbox" ${d.useTi?"checked":""} /> <span>Трейд-ин ${d.m.ti?rub(d.m.ti):"нет в базе"}</span></label>\n            <label class="check-row"><input id="ofLoan" type="checkbox" ${d.useLoan?"checked":""} /> <span>Кредит</span></label>\n            ${d.showDealCr?`<label class="check-row"><input id="ofCr" type="checkbox" ${d.useCr?"checked":""} /> <span>${d.m.id==="t7p"?"Выгодный кредит":"Программа кредита"} · ${rub(d.m.cr||0)}</span></label>`:""}\n            <label class="field" style="max-width:none"><span>Спецпредложение, ₽</span><input id="ofSpec" inputmode="numeric" value="${d.spec}" /></label>\n            ${d.useTi?`<label class="check-row"><input id="ofDcTi" type="checkbox" ${d.useDcTi?"checked":""} /> <span>Скидка ДЦ за трейд-ин</span></label>`:""}\n            ${d.useTi&&d.useDcTi?`<label class="field" style="max-width:none"><span>Скидка ДЦ за трейд-ин, ₽</span><input id="ofDcTiAmt" inputmode="numeric" value="${d.dcTi||d.dcDef}" /></label>`:""}\n            ${d.useLoan?`<label class="check-row"><input id="ofDcCr" type="checkbox" ${d.useDcCr?"checked":""} /> <span>Скидка ДЦ за кредит</span></label>`:""}\n            ${d.useLoan&&d.useDcCr?`<label class="field" style="max-width:none"><span>Скидка ДЦ за кредит, ₽</span><input id="ofDcCrAmt" inputmode="numeric" value="${d.dcCr||d.dcDef}" /></label>`:""}\n            <label class="field" style="max-width:none"><span>Д/О, ₽</span><input id="ofDo" inputmode="numeric" value="${d.addons}" /></label>\n            ${d.useLoan?`<label class="field" style="max-width:none"><span>Каско расширенное / СЖ, ₽</span><input id="ofPack" inputmode="numeric" value="${d.pack}" /></label>`:`<label class="field" style="max-width:none"><span>КАСКО, ₽</span><input id="ofCasco" inputmode="numeric" value="${d.casco}" /></label>`}\n            ${d.useLoan?`<p class="eyebrow" style="margin-top:12px">Первый взнос</p><div class="down-mode"><button type="button" class="chip ${d.downMode==="sum"?"on":""}" data-offer-down="sum">Сумма, ₽</button><button type="button" class="chip ${d.downMode!=="sum"?"on":""}" data-offer-down="pct">Проценты</button></div><input type="hidden" id="ofDownMode" value="${d.downMode==="sum"?"sum":"pct"}" />${d.downMode==="sum"?`<label class="field" style="max-width:none"><span>Первый взнос, ₽</span><input id="ofDown" inputmode="numeric" value="${d.down}" /></label>`:`<label class="field" style="max-width:none"><span>Первый взнос, %</span><input id="ofDownPct" inputmode="decimal" value="${d.downPct}" /></label>`}<label class="field" style="max-width:none"><span>Срок, мес.</span><input id="ofMonths" inputmode="numeric" value="${d.months}" /></label>`:""}\n            <label class="field" style="max-width:none"><span>Срок действия</span><input id="ofValid" value="${escape(d.valid)}" /></label>\n          </div>\n          <div class="card">\n            <p class="eyebrow">Текст КП</p>\n            <pre id="ofTextNew" class="offer-sheet">${escape(d.text)}</pre>\n            <p class="calc-note">Авто ${rub(d.carPrice)} ₽${d.discount?` · скидка ${rub(d.discount)} ₽`:""}${d.useLoan?` · тело ${rub(d.credit)} ₽`:""}.</p>\n            ${banksHtml}\n            ${d.mptTxt?`<div class="note-box" style="margin-top:12px"><p class="eyebrow">МПТ</p><pre class="offer-sheet" style="max-height:none;margin:0">${escape(d.mptTxt)}</pre></div>`:""}\n            <div class="who-line" style="margin-top:12px"><button type="button" class="btn ivory" data-offer-copy="ofTextNew">Скопировать</button><button type="button" class="btn ghost" data-offer-pdf>PDF / печать</button></div>\n          </div>\n        </div>\n        <div class="card offer-equip-card" id="ofEquipCard"><p class="eyebrow">Лист оснащения</p><h3 style="margin:0 0 10px">${escape(d.m.name)}</h3>${typeof offerPackHtml==="function"?offerPackHtml(d.packEq):""}</div>\n        <div id="ofPrint" class="offer-print">${offerPrintHtml(d)}</div>`;
    }
    function offerPrintHtml(d){
      const spec=(d.packEq&&d.packEq.specs||[]).map(([k,v])=>`<tr><td>${escape(k)}</td><td>${escape(v)}</td></tr>`).join("");
      const eq=(d.packEq&&d.packEq.groups||[]).map(([title,items])=>`<h3>${escape(title)}</h3><ul>${items.map(it=>`<li>${escape(it)}</li>`).join("")}</ul>`).join("");
      const banks=(d.banks||[]).map(b=>`<tr><td>${escape(b.name)}</td><td>${b.rate}%</td><td>${b.term} мес.</td><td>${rub(b.pay)} ₽</td></tr>`).join("");
      return `<div class="offer-print-inner"><p class="offer-print-brand">ООО «ЭКСПЕРТ АВТО САМАРА» · TENET</p><h1>Коммерческое предложение</h1><p>Новый автомобиль · ${escape(d.m.name)} · цвет ${escape(d.color)}</p><p>Клиент: ${escape(d.client)} · менеджер: ${escape(offerMgr())}</p><table><tr><td>РРЦ</td><td>${rub(d.price)} ₽</td></tr>${d.discount?`<tr><td>Скидки</td><td>− ${rub(d.discount)} ₽</td></tr>`:""}<tr><td>Автомобиль</td><td>${rub(d.carPrice)} ₽</td></tr>${d.addons?`<tr><td>Д/О</td><td>${rub(d.addons)} ₽</td></tr>`:""}${d.useLoan?`<tr><td>Каско / СЖ</td><td>${rub(d.pack)} ₽</td></tr>`:(d.casco?`<tr><td>КАСКО</td><td>${rub(d.casco)} ₽</td></tr>`:"")}<tr><td>Итого клиенту</td><td><b>${rub(d.clientPay)} ₽</b></td></tr></table>${d.useLoan?`<h2>Кредит</h2><p>ПВ ${rub(d.down)} ₽ (${d.downPct}%) · срок ${d.months} мес. · тело ${rub(d.credit)} ₽</p><table><thead><tr><th>Банк</th><th>Ставка</th><th>Срок</th><th>Платёж</th></tr></thead><tbody>${banks}</tbody></table>${d.mptTxt?`<h2>МПТ</h2><pre>${escape(d.mptTxt)}</pre>`:""}`:""}<h2>Технические характеристики</h2><table>${spec}</table><h2>Оснащение</h2>${eq}<p class="offer-print-note">Источник: ${escape((d.packEq&&d.packEq.src)||"официальный прайс")}. Не оферта. Действует ${escape(d.valid)}.</p></div>`;
    }
    function offerPdf(){
      const src=document.getElementById("ofPrint");
      if(!src) return;
      const w=window.open("","offerpdf","width=900,height=1200");
      if(!w){ window.print(); return; }
      w.document.write('<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>КП TENET</title><style>@page{size:A4;margin:14mm}body{margin:0;font:13px/1.45 Inter,system-ui,sans-serif;color:#111}h1{font-size:22px;margin:0 0 6px}h2{font-size:15px;margin:18px 0 8px;text-transform:uppercase}table{width:100%;border-collapse:collapse;margin:0 0 12px}td,th{border-bottom:1px solid #ddd;padding:6px 8px;text-align:left}ul{margin:0 0 10px;padding:0 0 0 18px}pre{white-space:pre-wrap;font:12px/1.4 ui-monospace,Menlo,monospace}.offer-print-brand{letter-spacing:.16em;text-transform:uppercase;font-size:11px;color:#c81e2b;font-weight:700}.offer-print-note{color:#666;font-size:12px;margin-top:18px}</style></head><body>'+src.innerHTML+'</body></html>');
      w.document.close();
      setTimeout(function(){ try{ w.focus(); w.print(); }catch(e){} }, 250);
    }
    function offerSvcPacks(){
      return [
        {id:"to1",name:"ТО-1",price:18900,note:"Первое регламентное ТО",items:[["Масло ДВС","замена, оригинал / аналог по регламенту"],["Фильтр масла","замена"],["Фильтр салона","замена"],["Диагностика","ходовая, тормоза, уровни, ЭБУ"]]},
        {id:"to2",name:"ТО-2",price:28900,note:"Второе регламентное ТО",items:[["ТО-1","масло, фильтры масла и салона"],["Фильтр воздушный","замена"],["Свечи","по регламенту"],["Интервал","сброс в ЭБУ"]]},
        {id:"season",name:"Сезонное ТО",price:12900,note:"Подготовка к сезону",items:[["Диагностика","АКБ, щётки, жидкости"],["Шины","осмотр и давление"],["Тормоза","колодки и диски"]]},
        {id:"warranty",name:"Расширенная гарантия",price:45000,note:"+1 год, условия в договоре ДЦ",items:[["Срок","+12 месяцев к заводской"],["Покрытие","агрегаты по договору"],["Лимит","пробег по договору"]]},
        {id:"tyre",name:"Шиномонтаж + хранение",price:8900,note:"Сезонная смена и склад ДЦ",items:[["Шиномонтаж","4 колеса, балансировка"],["Хранение","сезон на складе"],["Запись","у сервис-менеджера"]]}
      ];
    }
    function offerPrintDoc(d){
      const rows=(d.rows||[]).map(([k,v])=>`<tr><td>${k}</td><td>${v}</td></tr>`).join("");
      const total=d.total?`<tr><td>${d.totalLabel||"Итого"}</td><td><b>${d.total}</b></td></tr>`:"";
      return `<div class="offer-print-inner"><p class="offer-print-brand">ООО «ЭКСПЕРТ АВТО САМАРА» · TENET</p><h1>Коммерческое предложение</h1><p>${d.lead||""}</p><p>${d.who||""}</p><table>${rows}${total}</table>${d.extra||""}<p class="offer-print-note">${d.note||"Не оферта. Итоговые условия — в договоре салона."}</p></div>`;
    }
    function offerService(){
      const models=typeof KM_MODELS!=="undefined"?KM_MODELS:[];
      const packs=offerSvcPacks();
      const mid=offerVal("osModel", models[0]?models[0].id:"t7a");
      const m=models.find(x=>x.id===mid)||models[0]||{id:"t7a",name:"TENET"};
      const client=offerVal("osClient","Уважаемый клиент");
      const vin=offerVal("osVin","");
      const packId=offerVal("osPack", packs[0].id);
      const prevPack=offerVal("osPrevPack", packId);
      const pack=packs.find(x=>x.id===packId)||packs[0];
      let price=(typeof offerNum==="function"?offerNum("osPrice", pack.price):Number(offerVal("osPrice", String(pack.price))))||pack.price;
      if(prevPack!==packId) price=pack.price;
      const valid=offerVal("osValid","7 дней");
      const note=prevPack!==packId?pack.note:offerVal("osNote", pack.note);
      const itemLines=pack.items.map(p=>"• "+p[0]+" — "+p[1]).join(`
`);
      const text=`Коммерческое предложение · сервис
ООО «ЭКСПЕРТ АВТО САМАРА» · TENET

Клиент: ${client}
Автомобиль: ${m.name}${vin?`
VIN: ${vin}`:""}

Пакет: ${pack.name}
Стоимость: ${rub(price)} ₽
${note}

Состав:
${itemLines}

Предложение действует ${valid}.
Не оферта. Итоговые условия — в заказ-наряде сервиса.
Менеджер: ${offerMgr()}`;
      const packHtml=`<p class="eyebrow">Лист оснащения</p><h3 style="margin:0 0 10px">${escape(pack.name)}</h3>`+pack.items.map(([k,v])=>`<p class="offer-eq-h">${escape(k)}</p><ul class="offer-eq"><li>${escape(v)}</li></ul>`).join("")+`<p class="calc-note">${escape(note)}</p>`;
      const print=offerPrintDoc({
        lead:"Сервис · "+escape(m.name)+" · "+escape(pack.name),
        who:"Клиент: "+escape(client)+" · менеджер: "+escape(offerMgr()),
        rows:[["Автомобиль",escape(m.name)],["VIN",escape(vin||"—")],["Пакет",escape(pack.name)],["Срок действия",escape(valid)]],
        totalLabel:"Стоимость пакета",
        total:rub(price)+" ₽",
        extra:"<h2>Состав</h2><ul>"+pack.items.map(([k,v])=>"<li><b>"+escape(k)+".</b> "+escape(v)+"</li>").join("")+"</ul>",
        note:"Не оферта. Итоговые условия — в заказ-наряде сервиса. Действует "+escape(valid)+"."
      });
      return banner("КП Сервис","Коммерческое предложение","КП")+`
        ${offerNav()}
        <div class="km-layout">
          <div class="card">
            <p class="eyebrow">Данные и условия</p>
            <input type="hidden" id="osPrevPack" value="${escape(packId)}" />
            <label class="field" style="max-width:none"><span>Клиент</span><input id="osClient" value="${escape(client)}" /></label>
            <label class="field" style="max-width:none"><span>Комплектация</span>
              <select id="osModel">${models.map(x=>`<option value="${x.id}" ${x.id===mid?"selected":""}>${escape(x.name)}</option>`).join("")}</select>
            </label>
            <label class="field" style="max-width:none"><span>VIN</span><input id="osVin" value="${escape(vin)}" /></label>
            <label class="field" style="max-width:none"><span>Пакет</span>
              <select id="osPack">${packs.map(p=>`<option value="${p.id}" ${p.id===packId?"selected":""}>${escape(p.name)} · ${rub(p.price)}</option>`).join("")}</select>
            </label>
            <label class="field" style="max-width:none"><span>Стоимость, ₽</span><input id="osPrice" inputmode="numeric" value="${price}" /></label>
            <label class="field" style="max-width:none"><span>Срок действия</span><input id="osValid" value="${escape(valid)}" /></label>
            <label class="field" style="max-width:none"><span>Примечание</span><input id="osNote" value="${escape(note)}" /></label>
          </div>
          <div class="card">
            <p class="eyebrow">Текст КП</p>
            <pre id="ofTextSvc" class="offer-sheet">${escape(text)}</pre>
            <p class="calc-note">${escape(pack.name)} · ${rub(price)} ₽.</p>
            <div class="who-line" style="margin-top:12px">
              <button type="button" class="btn ivory" data-offer-copy="ofTextSvc">Скопировать</button>
              <button type="button" class="btn ghost" data-offer-pdf>PDF / печать</button>
            </div>
          </div>
        </div>
        <div class="card offer-equip-card">${packHtml}</div>
        <div id="ofPrint" class="offer-print">${print}</div>`;
    }
    function offerLease(){
      const models=typeof KM_MODELS!=="undefined"?KM_MODELS:[];
      const fset=typeof FLEET_BFS!=="undefined"?FLEET_BFS:{};
      const fleetIds=Object.keys(fset);
      const options=fleetIds.length?fleetIds.map(id=>({id,name:(fset[id]&&fset[id].name)||id,rrc:(fset[id]&&(fset[id].rrc||fset[id].tidy))||0})):models;
      const fid=offerVal("olModel", options[0]?options[0].id:(models[0]?models[0].id:"t7a"));
      const m=models.find(x=>x.id===fid)||options.find(x=>x.id===fid)||{id:fid,name:"TENET",rrc:0};
      const f=fset[fid]||{name:m.name,rrc:m.rrc||0,tidy:m.rrc||0,an:0};
      const prev=offerVal("olPrevModel", fid);
      const company=offerVal("olCo","ООО «Компания»");
      const inn=offerVal("olInn","");
      const months=(typeof offerNum==="function"?offerNum("olMonths", 36):Number(offerVal("olMonths","36")))||36;
      const advPct=(typeof offerNum==="function"?offerNum("olAdv", 20):Number(offerVal("olAdv","20")))||20;
      const valid=offerVal("olValid","7 дней");
      const base=f.tidy||f.rrc||m.rrc||0;
      let price=(typeof offerNum==="function"?offerNum("olPrice", base):Number(offerVal("olPrice", String(base))))||base;
      if(prev!==fid) price=base;
      const adv=Math.round(price*advPct/100);
      const body=Math.max(0, price-adv);
      const partners="Каркаде, Т-Лизинг, Европлан, Сберлизинг, Газпромбанк Лизинг, Совкомбанк Лизинг";
      const text=`Коммерческое предложение · лизинг
ООО «ЭКСПЕРТ АВТО САМАРА» · TENET · BFS Совкомбанк лизинг

Лизингополучатель: ${company}${inn?`
ИНН: ${inn}`:""}
Автомобиль: ${f.name||m.name}
РРЦ: ${rub(f.rrc||m.rrc||price)} ₽
Цена AP / флит: ${rub(price)} ₽

Аванс: ${advPct}% · ${rub(adv)} ₽
Срок: ${months} мес.
Остаток к финансированию: ${rub(body)} ₽
${f.an?`Авансовый платёж BFS (ориентир): ${rub(f.an)} ₽
`:""}
Партнёры BFS: ${partners}.
График и удорожание считает лизинговая компания.

Предложение действует ${valid}.
Не оферта. Итоговые условия — в договоре лизинга.
Менеджер: ${offerMgr()}`;
      const packHtml=`<p class="eyebrow">Лист оснащения</p><h3 style="margin:0 0 10px">${escape(f.name||m.name)}</h3>
        <ul class="offer-eq">
          <li><b>РРЦ.</b> ${rub(f.rrc||m.rrc||price)} ₽</li>
          <li><b>Цена AP / флит.</b> ${rub(price)} ₽</li>
          <li><b>Аванс.</b> ${advPct}% · ${rub(adv)} ₽</li>
          <li><b>К финансированию.</b> ${rub(body)} ₽ · ${months} мес.</li>
          ${f.an?`<li><b>Ориентир платежа BFS.</b> ${rub(f.an)} ₽</li>`:""}
        </ul>
        <p class="offer-eq-h">Партнёры</p>
        <ul class="offer-eq"><li>${escape(partners)}</li></ul>
        <p class="calc-note">График и удорожание считает лизинговая компания.</p>`;
      const print=offerPrintDoc({
        lead:"Лизинг · "+escape(f.name||m.name)+" · BFS",
        who:"Лизингополучатель: "+escape(company)+(inn?" · ИНН "+escape(inn):"")+" · менеджер: "+escape(offerMgr()),
        rows:[["Автомобиль",escape(f.name||m.name)],["РРЦ",rub(f.rrc||m.rrc||price)+" ₽"],["Цена AP / флит",rub(price)+" ₽"],["Аванс",advPct+"% · "+rub(adv)+" ₽"],["Срок",months+" мес."],["К финансированию",rub(body)+" ₽"],["Срок действия",escape(valid)]],
        totalLabel:"Цена AP / флит",
        total:rub(price)+" ₽",
        extra:"<h2>Партнёры BFS</h2><p>"+escape(partners)+"</p>",
        note:"Не оферта. График считает лизинговая компания. Действует "+escape(valid)+"."
      });
      return banner("КП Лизинг","Коммерческое предложение","КП")+`
        ${offerNav()}
        <div class="km-layout">
          <div class="card">
            <p class="eyebrow">Данные и условия</p>
            <input type="hidden" id="olPrevModel" value="${escape(fid)}" />
            <label class="field" style="max-width:none"><span>Компания</span><input id="olCo" value="${escape(company)}" /></label>
            <label class="field" style="max-width:none"><span>ИНН</span><input id="olInn" value="${escape(inn)}" /></label>
            <label class="field" style="max-width:none"><span>Комплектация</span>
              <select id="olModel">${options.map(x=>`<option value="${x.id}" ${x.id===fid?"selected":""}>${escape(x.name)}${x.rrc?" · "+rub(x.rrc):""}</option>`).join("")}</select>
            </label>
            <label class="field" style="max-width:none"><span>Цена флит, ₽</span><input id="olPrice" inputmode="numeric" value="${price}" /></label>
            <label class="field" style="max-width:none"><span>Аванс, %</span><input id="olAdv" inputmode="numeric" value="${advPct}" /></label>
            <label class="field" style="max-width:none"><span>Срок, мес.</span><input id="olMonths" inputmode="numeric" value="${months}" /></label>
            <label class="field" style="max-width:none"><span>Срок действия</span><input id="olValid" value="${escape(valid)}" /></label>
          </div>
          <div class="card">
            <p class="eyebrow">Текст КП</p>
            <pre id="ofTextLease" class="offer-sheet">${escape(text)}</pre>
            <p class="calc-note">Аванс ${rub(adv)} ₽ · к финансированию ${rub(body)} ₽.</p>
            <div class="who-line" style="margin-top:12px">
              <button type="button" class="btn ivory" data-offer-copy="ofTextLease">Скопировать</button>
              <button type="button" class="btn ghost" data-offer-pdf>PDF / печать</button>
            </div>
          </div>
        </div>
        <div class="card offer-equip-card">${packHtml}</div>
        <div id="ofPrint" class="offer-print">${print}</div>`;
    }

    function offer(){
      if(needAuth()) return login();
      if(offerTab==="new") return offerNew();
      if(offerTab==="service") return offerService();
      if(offerTab==="lease") return offerLease();
      return offerHome();
    }
    function offerBind(){
      document.querySelectorAll("[data-offer-tab]").forEach(b=>b.onclick=()=>{ offerTab=b.dataset.offerTab||"home"; view="offer"; render(); });
      document.querySelectorAll("[data-offer-copy]").forEach(b=>b.onclick=()=>{ offerCopy(b.dataset.offerCopy); b.textContent="Скопировано"; setTimeout(()=>{ b.textContent="Скопировать"; }, 1200); });
      document.querySelectorAll("[data-offer-pdf]").forEach(b=>b.onclick=()=>offerPdf());
      document.querySelectorAll("[data-offer-down]").forEach(b=>b.onclick=()=>{ const hid=document.getElementById("ofDownMode"); if(hid) hid.value=b.dataset.offerDown||"pct"; view="offer"; render(); });
      ["ofClient","ofModel","ofColor","ofPrice","ofSpec","ofDo","ofPack","ofCasco","ofDown","ofDownPct","ofMonths","ofValid","ofTi","ofLoan","ofCr","ofDcTi","ofDcCr","ofDcTiAmt","ofDcCrAmt","osClient","osModel","osCar","osVin","osPack","osPrice","osNote","osValid","olCo","olInn","olModel","olPrice","olAdv","olMonths","olValid"].forEach(id=>{ const el=document.getElementById(id); if(el) el.addEventListener("change", ()=>{ view="offer"; render(); }); });
    }
