    let offerTab = "home";
    function offerVal(id, def){
      const el=document.getElementById(id);
      if(!el) return def;
      const v=String(el.value||"").trim();
      return v||def;
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
      const tabs=[
        ["home","Разделы"],
        ["new","КП Новый а/м"],
        ["service","КП Сервис"],
        ["lease","КП Лизинг"]
      ];
      return `<div class="down-mode" style="margin:0 0 14px">${tabs.map(([id,l])=>`<button type="button" class="chip ${offerTab===id?"on":""}" data-offer-tab="${id}">${l}</button>`).join("")}</div>`;
    }
    function offerHome(){
      const cards=[
        ["new","А","КП Новый а/м","Клиент, модель, цена, скидка, первый взнос и срок. Готовый текст."],
        ["service","С","КП Сервис","ТО, сезон, гарантия и пакеты ДЦ — стоимость и примечание."],
        ["lease","Л","КП Лизинг","Компания, флит / BFS, аванс и срок. Текст для юрлица."]
      ];
      return banner("Коммерческое предложение","TENET · Отдел продаж","КП")+`
        <p class="lead">Девятый раздел кабинета. Три шаблона: заполняете поля слева — справа письмо для WhatsApp или почты.</p>
        ${offerNav()}
        <div class="hub-grid">${cards.map(([id,mark,title,lead])=>`
          <button class="card hub-card" data-offer-tab="${id}" type="button">
            <span class="hub-mark">${mark}</span>
            <div class="txt"><h3>${title}</h3><p>${lead}</p></div>
          </button>`).join("")}</div>`;
    }
    function offerNew(){
      const models=typeof KM_MODELS!=="undefined"?KM_MODELS:[];
      const mid=offerVal("ofModel", models[0]?models[0].id:"t7a");
      const m=models.find(x=>x.id===mid)||models[0]||{id:"t7a",name:"TENET",rrc:0};
      const prevModel=offerVal("ofPrevModel", mid);
      const client=offerVal("ofClient","Уважаемый клиент");
      const color=offerVal("ofColor","на выбор");
      let price=Number(offerVal("ofPrice", String(m.rrc)))||m.rrc;
      if(prevModel!==mid) price=m.rrc;
      const disc=Number(offerVal("ofDisc","0"))||0;
      const down=Number(offerVal("ofDown","0"))||0;
      const months=Number(offerVal("ofMonths","60"))||60;
      const valid=offerVal("ofValid","7 дней");
      const out=Math.max(0, price-disc);
      const body=Math.max(0, out-down);
      const pay=typeof calcPay==="function"?Math.round(calcPay(out, down, months, 19.2)):0;
      const text=`Коммерческое предложение · новый автомобиль
ООО «ЭКСПЕРТ АВТО САМАРА» · TENET

Клиент: ${client}
Автомобиль: ${m.name}
Цвет: ${color}

РРЦ: ${rub(price)} ₽
Скидка: ${disc?rub(disc)+" ₽":"без скидки"}
Итого за автомобиль: ${rub(out)} ₽
Первый взнос: ${down?rub(down)+" ₽":"по согласованию"}
Срок кредита: ${months} мес.
Ориентир платежа (Совкомбанк 19,2%): ${pay?rub(pay)+" ₽ / мес.":"—"}

Предложение действует ${valid}.
Не оферта. Итоговые условия — в договоре салона.
Менеджер: ${offerMgr()}`;
      return banner("КП Новый а/м","Коммерческое предложение","КП")+`
        ${offerNav()}
        <div class="km-layout">
          <div class="card">
            <p class="eyebrow">Данные</p>
            <input type="hidden" id="ofPrevModel" value="${escape(mid)}" />
            <label class="field" style="max-width:none"><span>Клиент</span><input id="ofClient" value="${escape(client)}" /></label>
            <label class="field" style="max-width:none"><span>Комплектация</span>
              <select id="ofModel">${models.map(x=>`<option value="${x.id}" ${x.id===mid?"selected":""}>${escape(x.name)} · ${rub(x.rrc)}</option>`).join("")}</select>
            </label>
            <label class="field" style="max-width:none"><span>Цвет</span><input id="ofColor" value="${escape(color)}" /></label>
            <label class="field" style="max-width:none"><span>Цена, ₽</span><input id="ofPrice" inputmode="numeric" value="${price}" /></label>
            <label class="field" style="max-width:none"><span>Скидка, ₽</span><input id="ofDisc" inputmode="numeric" value="${disc}" /></label>
            <label class="field" style="max-width:none"><span>Первый взнос, ₽</span><input id="ofDown" inputmode="numeric" value="${down}" /></label>
            <label class="field" style="max-width:none"><span>Срок, мес.</span><input id="ofMonths" inputmode="numeric" value="${months}" /></label>
            <label class="field" style="max-width:none"><span>Срок действия</span><input id="ofValid" value="${escape(valid)}" /></label>
          </div>
          <div class="card">
            <p class="eyebrow">Текст КП</p>
            <pre id="ofTextNew" class="offer-sheet">${escape(text)}</pre>
            <p class="calc-note">Итого клиенту ${rub(out)} ₽${down?` · тело ${rub(body)} ₽`:""}.</p>
            <button type="button" class="btn ivory" data-offer-copy="ofTextNew">Скопировать</button>
          </div>
        </div>`;
    }
    function offerService(){
      const packs={"ТО-1":18900,"ТО-2":28900,"Сезонное ТО":12900,"Расширенная гарантия":45000,"Шиномонтаж + хранение":8900};
      const client=offerVal("osClient","Уважаемый клиент");
      const car=offerVal("osCar","TENET");
      const vin=offerVal("osVin","");
      const pack=offerVal("osPack","ТО-1");
      const prevPack=offerVal("osPrevPack", pack);
      let price=Number(offerVal("osPrice", String(packs[pack]||18900)))||0;
      if(prevPack!==pack && packs[pack]) price=packs[pack];
      const note=offerVal("osNote","Работы по регламенту импортёра.");
      const text=`Коммерческое предложение · сервис
ООО «ЭКСПЕРТ АВТО САМАРА» · TENET

Клиент: ${client}
Автомобиль: ${car}${vin?"\nVIN: "+vin:""}

Пакет: ${pack}
Стоимость: ${rub(price)} ₽
${note}

В пакет входят работы и расходники по выбранному регламенту.
Запись в сервис — у менеджера отдела продаж.
Менеджер: ${offerMgr()}`;
      return banner("КП Сервис","Коммерческое предложение","КП")+`
        ${offerNav()}
        <div class="km-layout">
          <div class="card">
            <p class="eyebrow">Данные</p>
            <input type="hidden" id="osPrevPack" value="${escape(pack)}" />
            <label class="field" style="max-width:none"><span>Клиент</span><input id="osClient" value="${escape(client)}" /></label>
            <label class="field" style="max-width:none"><span>Автомобиль</span><input id="osCar" value="${escape(car)}" /></label>
            <label class="field" style="max-width:none"><span>VIN</span><input id="osVin" value="${escape(vin)}" /></label>
            <label class="field" style="max-width:none"><span>Пакет</span>
              <select id="osPack">
                ${Object.keys(packs).map(p=>`<option ${p===pack?"selected":""}>${p}</option>`).join("")}
              </select>
            </label>
            <label class="field" style="max-width:none"><span>Стоимость, ₽</span><input id="osPrice" inputmode="numeric" value="${price}" /></label>
            <label class="field" style="max-width:none"><span>Примечание</span><input id="osNote" value="${escape(note)}" /></label>
          </div>
          <div class="card">
            <p class="eyebrow">Текст КП</p>
            <pre id="ofTextSvc" class="offer-sheet">${escape(text)}</pre>
            <button type="button" class="btn ivory" data-offer-copy="ofTextSvc">Скопировать</button>
          </div>
        </div>`;
    }
    function offerLease(){
      const fset=typeof FLEET_BFS!=="undefined"?FLEET_BFS:{};
      const ids=Object.keys(fset);
      const fid=offerVal("olModel", ids[0]||"t7a");
      const f=fset[fid]||{name:"TENET",rrc:0,tidy:0,an:0};
      const prev=offerVal("olPrevModel", fid);
      const company=offerVal("olCo","ООО «Компания»");
      const inn=offerVal("olInn","");
      const months=Number(offerVal("olMonths","36"))||36;
      const advPct=Number(offerVal("olAdv","20"))||20;
      let price=Number(offerVal("olPrice", String(f.tidy||f.rrc)))|| (f.tidy||f.rrc);
      if(prev!==fid) price=f.tidy||f.rrc||0;
      const adv=Math.round(price*advPct/100);
      const body=Math.max(0, price-adv);
      const text=`Коммерческое предложение · лизинг
ООО «ЭКСПЕРТ АВТО САМАРА» · TENET · BFS Совкомбанк лизинг

Лизингополучатель: ${company}${inn?"\nИНН: "+inn:""}
Автомобиль: ${f.name}
Цена AP / флит: ${rub(price)} ₽
РРЦ: ${rub(f.rrc||price)} ₽

Аванс: ${advPct}% · ${rub(adv)} ₽
Срок: ${months} мес.
Остаток к финансированию: ${rub(body)} ₽

Партнёры BFS: Каркаде, Т-Лизинг, Европлан, Сберлизинг, Газпромбанк Лизинг, Совкомбанк Лизинг.
График и удорожание считает лизинговая компания.
Менеджер: ${offerMgr()}`;
      return banner("КП Лизинг","Коммерческое предложение","КП")+`
        ${offerNav()}
        <div class="km-layout">
          <div class="card">
            <p class="eyebrow">Данные</p>
            <input type="hidden" id="olPrevModel" value="${escape(fid)}" />
            <label class="field" style="max-width:none"><span>Компания</span><input id="olCo" value="${escape(company)}" /></label>
            <label class="field" style="max-width:none"><span>ИНН</span><input id="olInn" value="${escape(inn)}" /></label>
            <label class="field" style="max-width:none"><span>Комплектация</span>
              <select id="olModel">${ids.map(id=>`<option value="${id}" ${id===fid?"selected":""}>${escape(fset[id].name)}</option>`).join("")}</select>
            </label>
            <label class="field" style="max-width:none"><span>Цена флит, ₽</span><input id="olPrice" inputmode="numeric" value="${price}" /></label>
            <label class="field" style="max-width:none"><span>Аванс, %</span><input id="olAdv" inputmode="numeric" value="${advPct}" /></label>
            <label class="field" style="max-width:none"><span>Срок, мес.</span><input id="olMonths" inputmode="numeric" value="${months}" /></label>
          </div>
          <div class="card">
            <p class="eyebrow">Текст КП</p>
            <pre id="ofTextLease" class="offer-sheet">${escape(text)}</pre>
            <p class="calc-note">Аванс ${rub(adv)} ₽ · к финансированию ${rub(body)} ₽.</p>
            <button type="button" class="btn ivory" data-offer-copy="ofTextLease">Скопировать</button>
          </div>
        </div>`;
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
      document.querySelectorAll("[data-offer-copy]").forEach(b=>b.onclick=()=>{
        offerCopy(b.dataset.offerCopy);
        b.textContent="Скопировано";
        setTimeout(()=>{ b.textContent="Скопировать"; }, 1200);
      });
      ["ofClient","ofModel","ofColor","ofPrice","ofDisc","ofDown","ofMonths","ofValid","osClient","osCar","osVin","osPack","osPrice","osNote","olCo","olInn","olModel","olPrice","olAdv","olMonths"].forEach(id=>{
        const el=document.getElementById(id);
        if(el) el.addEventListener("change", ()=>{ view="offer"; render(); });
      });
    }
