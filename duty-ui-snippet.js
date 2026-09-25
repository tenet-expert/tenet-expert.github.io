    function duty(){
      if(needAuth()) return login();
      const d=dutyLoad();
      if(!d._archive) d.date=dutyToday();
      else if(!d.date) d.date=dutyToday();
      const who=(typeof state!=="undefined" && state && state.display)?state.display:"";
      const name=String(d.manager||who||"").trim().split(/\s+/).filter(Boolean).filter((p,i,a)=>a.findIndex(x=>x.toLowerCase()===p.toLowerCase())===i).join(" ");
      if(!d._archive) d.manager=name;
      const prog=dutyCount(d);
      const pct=prog.tot?Math.round(prog.on*100/prog.tot):0;
      const cards=DUTY_CARS.map(car=>{
        const body=d[car.id+"_body"]||"ok";
        return `<article class="cl-car">
          <h3>${car.title}</h3>
          ${dutyItem(car.id+"_wash","Омывающая", d[car.id+"_wash"])}
          ${dutyItem(car.id+"_mats","Коврики и пороги", d[car.id+"_mats"])}
          ${dutyItem(car.id+"_err","Нет ошибок", d[car.id+"_err"])}
          ${dutyItem(car.id+"_dust","Нет пыли", d[car.id+"_dust"])}
          ${dutyItem(car.id+"_trunk","Багажник", d[car.id+"_trunk"])}
          <label class="cl-item" style="display:block">Кузов
            <select data-duty="${car.id}_body">
              <option value="ok" ${body==="ok"?"selected":""}>чистый</option>
              <option value="pm" ${body==="pm"?"selected":""}>±</option>
              <option value="no" ${body==="no"?"selected":""}>грязный</option>
            </select>
          </label>
          <div class="cl-nums">
            <label>Пробег<input data-duty="${car.id}_km" inputmode="numeric" value="${escape(d[car.id+"_km"]||"")}" /></label>
            <label>Топливо %<input data-duty="${car.id}_fuel" inputmode="numeric" value="${escape(d[car.id+"_fuel"]||"")}" /></label>
          </div>
          <label class="cl-note-lab">Примечание
            <textarea data-duty="${car.id}_note" class="cl-note" rows="2" placeholder="Царапина, не заводится, помыть…">${escape(d[car.id+"_note"]||"")}</textarea>
          </label>
        </article>`;
      }).join("");
      return banner("Чек-лист дежурного", prog.on+" из "+prog.tot,"TENET")+`
        <div class="cl">
          <div class="cl-bar">
            <input data-duty="manager" placeholder="Менеджер" value="${escape(d.manager||"")}" />
            <input data-duty="date" readonly value="${escape(d.date||dutyToday())}" style="width:96px" />
            <div class="cl-prog"><i style="width:${pct}%"></i><span>${pct}%</span></div>
            <button type="button" class="btn ivory" id="dutySave">Сохранить</button>
            <button type="button" class="btn ghost" id="dutyPrint">На рабочий стол</button>
            <button type="button" class="btn ghost" id="dutyClear">Сброс</button>
          </div>
          <section class="cl-sec">
            <h2 class="cl-sec-title">Тестовые автомобили</h2>
            <div class="cl-cars">${cards}</div>
          </section>
          <section class="cl-sec cl-salon">
            <h2 class="cl-sec-title">Салон</h2>
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
            <input data-duty="note" placeholder="Общая заметка по салону" value="${escape(d.note||"")}" class="cl-note" />
            </div>
            </div>
          </section>
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
