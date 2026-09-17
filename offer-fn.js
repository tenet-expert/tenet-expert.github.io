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
