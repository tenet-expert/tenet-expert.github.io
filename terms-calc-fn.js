    const TERMS_DATE = "16.09.2026";
    const KM_CORRIDOR = [
      {model:"T4L",trim:"Все",km:"0 / 50",note:""},
      {model:"T7",trim:"Все",km:"30 / 80",note:"Антихром 0/50"},
      {model:"T8",trim:"Приоритет",km:"−30 / 0",note:"VIN из списка"},
      {model:"T8",trim:"Остальные",km:"0 / 30",note:""},
      {model:"T9",trim:"Все",km:"−30 / 0",note:""},
      {model:"A8",trim:"Все",km:"−30 / 0",note:""}
    ];
    const TERMS_BONUS = [
      {model:"T4L",trim:"Все",bonus:"2%"},
      {model:"T7",trim:"Любые",bonus:"2%"},
      {model:"T8",trim:"Все",bonus:"2%"},
      {model:"T9",trim:"Все",bonus:"2%"},
      {model:"A8",trim:"Любые",bonus:"2%"}
    ];
    const TERMS_MPT = [
      {line:"T7 2WD",rows:[
        ["до 14.03", "субс. бренда"],
        ["с 14.03 до 15.04", "МПТ"],
        ["с 16.04 до 7.05", "субс. бренда"],
        ["с 8.05 и далее", "МПТ"]
      ]},
      {line:"T7 4WD",rows:[
        ["до 7.04", "субс. бренда"],
        ["с 8.04 до 15.04", "МПТ"],
        ["с 16.04 до 7.05", "субс. бренда"],
        ["с 8.05 и далее", "МПТ"]
      ]}
    ];
    const TERMS_INV = [
      {model:"T4L",trim:"Active",price:"2 200 нал, 2 150 ТИ"},
      {model:"T4L",trim:"Prime",price:"2 300 нал, 2 250 ТИ"},
      {model:"T7",trim:"Prime 2WD",price:"2 550 нал, 2 450 ТИ"},
      {model:"T8",trim:"Prime 4WD",price:"3 100 нал, 3 000 ТИ"},
      {model:"T8",trim:"Ultra 4WD",price:"3 300 нал, 3 200 ТИ"}
    ];
    const TERMS_PRIO = [
      {model:"T4",vin:"EDEED31B1SE053704",trim:"Prime 4WD",year:"2025",color:"Белый",extra:"Сидоров",pay:500,bonus:1000,sold:true,seller:"Сидоров"},
      {model:"T7",vin:"EDXFB32B4TE041659",trim:"Active",year:"2026",color:"Чёрный",extra:"",pay:500,bonus:1000},
      {model:"T7",vin:"EDXFB32B2TE041658",trim:"Active",year:"2026",color:"Чёрный",extra:"",pay:500,bonus:1000},
      {model:"T7",vin:"EDXFB32B7TE062327",trim:"Active",year:"2026",color:"Чёрный",extra:"Антихром",pay:500,bonus:1000},
      {model:"T8",vin:"EDXGD34B1TE022143",trim:"Prime 4WD",year:"2026",color:"Светло-серый",extra:"",pay:500,bonus:2000},
      {model:"T8",vin:"EDXGD34B6TE031162",trim:"Prime 4WD",year:"2026",color:"Чёрный",extra:"",pay:500,bonus:2000},
      {model:"T8",vin:"EDXGD34B3TE031815",trim:"Ultra 4WD",year:"2026",color:"Белый",extra:"",pay:500,bonus:2000},
      {model:"Tiggo 9",vin:"EDEDD24B2SG003755",trim:"Ultra",year:"2025",color:"Светло-серый",extra:"",pay:500,bonus:3000},
      {model:"Tiggo 9",vin:"EDEDD24B3SG003926",trim:"Ultra",year:"2025",color:"Матовый",extra:"",pay:500,bonus:3000},
      {model:"Tiggo 9",vin:"EDEDD24B1SG002595",trim:"Ultra",year:"2025",color:"Чёрный",extra:"Новиков",pay:500,bonus:0,sold:true,seller:"Новиков"},
      {model:"Arrizo 8",vin:"LVVDC21B7SD594110",trim:"Prime",year:"2025",color:"Белый",extra:"",pay:500,bonus:3000},
      {model:"Arrizo 8",vin:"LVVDC21B0SD594112",trim:"Prime",year:"2025",color:"Белый",extra:"",pay:500,bonus:3000},
      {model:"Arrizo 8",vin:"LVVDC21B2SDJ34062",trim:"Prime",year:"2025",color:"Чёрный",extra:"",pay:500,bonus:3000},
      {model:"8 Pro Max",vin:"LVTDD24B5RD409189",trim:"Ultimate",year:"2024",color:"Белый",extra:"ТЕСТ // 2850",pay:500,bonus:10000}
    ];
    const KM_MODELS = [
      {id:"t4p",brand:"TENET",name:"T4 Prime 2025",stock:"t4",rrc:2449000,dealer:2369000,ti:100000,tiBack:80000,cr:0,crBack:0,bonus:0.03,vat:1.22,fee:0.01,kmMin:-30,kmMax:20,prioMin:-30,prioMax:20},
      {id:"t4la",brand:"TENET",name:"T4L Active",stock:"t4l",rrc:2329000,dealer:2234000,ti:0,tiBack:0,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:0,kmMax:50,prioMin:0,prioMax:50},
      {id:"t4lp",brand:"TENET",name:"T4L Prime",stock:"t4l",rrc:2479000,dealer:2389000,ti:0,tiBack:0,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:0,kmMax:50,prioMin:0,prioMax:50},
      {id:"t7a",brand:"TENET",name:"T7 Active 2WD",stock:"t7",rrc:2785000,dealer:2645000,ti:180000,tiBack:130000,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:30,kmMax:80,prioMin:30,prioMax:80},
      {id:"t7p",brand:"TENET",name:"T7 Prime 2WD",stock:"t7",rrc:2985000,dealer:2840000,ti:200000,tiBack:150000,cr:50000,crBack:30000,bonus:0.02,vat:1.22,fee:0.01,kmMin:30,kmMax:80,prioMin:30,prioMax:80},
      {id:"t7a4",brand:"TENET",name:"T7 Active 4WD",stock:"t7",rrc:2990000,dealer:2860000,ti:130000,tiBack:90000,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:30,kmMax:80,prioMin:30,prioMax:80},
      {id:"t7p4",brand:"TENET",name:"T7 Prime 4WD",stock:"t7",rrc:3190000,dealer:3045000,ti:150000,tiBack:110000,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:30,kmMax:80,prioMin:30,prioMax:80},
      {id:"t8a",brand:"TENET",name:"T8 Active 2WD",stock:"t8",rrc:3099000,dealer:2999000,ti:200000,tiBack:150000,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:0,kmMax:30,prioMin:-30,prioMax:0},
      {id:"t8p",brand:"TENET",name:"T8 Prime 2WD",stock:"t8",rrc:3299000,dealer:3149000,ti:200000,tiBack:150000,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:0,kmMax:30,prioMin:-30,prioMax:0},
      {id:"t8p4",brand:"TENET",name:"T8 Prime 4WD",stock:"t8",rrc:3630000,dealer:3465000,ti:150000,tiBack:100000,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:0,kmMax:30,prioMin:-30,prioMax:0},
      {id:"t8u4",brand:"TENET",name:"T8 Ultra 4WD",stock:"t8",rrc:3885000,dealer:3705000,ti:150000,tiBack:100000,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:0,kmMax:30,prioMin:-30,prioMax:0},
      {id:"ta8p",brand:"TENET",name:"A8 Prime 1.6",stock:"ta8",rrc:2999000,dealer:2874000,ti:0,tiBack:0,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:-30,kmMax:0,prioMin:-30,prioMax:0},
      {id:"ta8u",brand:"TENET",name:"A8 Ultra 2.0",stock:"ta8",rrc:3499000,dealer:3354000,ti:0,tiBack:0,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:-30,kmMax:0,prioMin:-30,prioMax:0},
      {id:"tt9p",brand:"TENET",name:"T9 Prime 5-seat",stock:"tt9",rrc:3949000,dealer:3799000,ti:200000,tiBack:130000,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:-30,kmMax:0,prioMin:-30,prioMax:0},
      {id:"tt9u",brand:"TENET",name:"T9 Ultra 5-seat",stock:"tt9",rrc:4299000,dealer:4099000,ti:200000,tiBack:130000,cr:0,crBack:0,bonus:0.02,vat:1.22,fee:0.01,kmMin:-30,kmMax:0,prioMin:-30,prioMax:0},
      {id:"t9p",brand:"CHERY",name:"Tiggo 9 Prime 4WD",stock:"t9",rrc:4335000,dealer:3895000,ti:300000,tiBack:250000,cr:0,crBack:0,bonus:0.02,vat:1.2,fee:0.02,kmMin:-30,kmMax:0,prioMin:-30,prioMax:0},
      {id:"t9u",brand:"CHERY",name:"Tiggo 9 Ultra 4WD",stock:"t9",rrc:4640000,dealer:4200000,ti:200000,tiBack:150000,cr:200000,crBack:0,bonus:0.02,vat:1.2,fee:0.02,kmMin:-30,kmMax:0,prioMin:-30,prioMax:0},
      {id:"a8a",brand:"CHERY",name:"Arrizo 8 Active",stock:"a8",rrc:2865000,dealer:2649000,ti:250000,tiBack:230000,cr:0,crBack:0,bonus:0.02,vat:1.2,fee:0.02,kmMin:-30,kmMax:0,prioMin:-30,prioMax:0},
      {id:"a8p",brand:"CHERY",name:"Arrizo 8 Prime",stock:"a8",rrc:3060000,dealer:2699000,ti:200000,tiBack:180000,cr:261000,crBack:0,bonus:0.02,vat:1.2,fee:0.02,kmMin:-30,kmMax:0,prioMin:-30,prioMax:0},
      {id:"a8u",brand:"CHERY",name:"Arrizo 8 Ultra Black",stock:"a8",rrc:3275000,dealer:2899000,ti:200000,tiBack:180000,cr:0,crBack:0,bonus:0.02,vat:1.2,fee:0.02,kmMin:-30,kmMax:0,prioMin:-30,prioMax:0},
      {id:"t7l",brand:"CHERY",name:"Tiggo 7 L Active",stock:"t7l",rrc:2735000,dealer:2620000,ti:100000,tiBack:70000,cr:0,crBack:0,bonus:0.02,vat:1.2,fee:0.02,kmMin:0,kmMax:30,prioMin:0,prioMax:30}
    ];
    const PRIO_VINS = new Set(["EDEED31B1SE053704", "EDXFB32B4TE041659", "EDXFB32B2TE041658", "EDXFB32B7TE062327", "EDXGD34B1TE022143", "EDXGD34B6TE031162", "EDXGD34B3TE031815", "EDEDD24B2SG003755", "EDEDD24B3SG003926", "EDEDD24B1SG002595", "LVVDC21B7SD594110", "LVVDC21B0SD594112", "LVVDC21B2SDJ34062", "LVTDD24B5RD409189"]);
    const KM_BANK_FEE = 30000;
    function kmBankRate(bankId, group, months, downPct){
      const terms=KM_BANK_MONTHS[bankId]||KM_BANK_MONTHS.sber;
      const n=Math.max(1, Number(months)||60);
      let idx=0;
      const exact=terms.indexOf(n);
      if(exact>=0) idx=exact;
      else if(n>=terms[terms.length-1]) idx=terms.length-1;
      else if(n<=terms[0]) idx=0;
      else {
        let best=Math.abs(terms[0]-n);
        for(let i=1;i<terms.length;i++){
          const d=Math.abs(terms[i]-n);
          if(d<best){ best=d; idx=i; }
        }
      }
      const band=kmDownBand(downPct);
      const table=(KM_BANK_RATES[bankId]||{})[group]||(KM_BANK_RATES[bankId]||{}).t4l_t7||{};
      const row=table[band]||table[10]||table[20]||[];
      let rate=row[idx];
      if(!(rate>=0)){
        for(let i=idx;i>=0;i--){ if(row[i]>=0){ rate=row[i]; break; } }
      }
      return {rate: Number(rate)||0, term: terms[idx], band, capped: terms[idx]!==n};
    }
    function mptParseProd(s){
      const m=String(s||"").match(/(\d{1,2})\.(\d{1,2})\.(\d{4})/);
      if(!m) return "";
      return m[3]+"-"+("0"+m[2]).slice(-2)+"-"+("0"+m[1]).slice(-2);
    }
    function mptKind(line, iso){
      const d=String(iso||"");
      if(line==="4wd"){
        if(d<"2026-04-08") return "sub";
        if(d<="2026-04-15") return "mpt";
        if(d<="2026-05-07") return "sub";
        return "mpt";
      }
      if(d<"2026-03-14") return "sub";
      if(d<"2026-04-15") return "mpt";
      if(d<="2026-05-07") return "sub";
      return "mpt";
    }
    function mptLabel(k){ return k==="mpt"?"МПТ":"субс. бренда"; }
    function mptCars(iso){
      const list=(typeof STOCK!=="undefined"?STOCK:[]).filter(c=>c.model==="t7" && mptParseProd(c.prod)===iso);
      if(!list.length) return `<small>В снимке склада нет T7 с этой датой производства.</small>`;
      return list.map(c=>{
        const wd=String(c.trim||"").toLowerCase().includes("4wd")?"4WD":"2WD";
        return `<small>${escape(c.trim||"")} · ${escape(c.color||"")} · ${wd} · ${escape(c.vin)}</small>`;
      }).join("");
    }
    function mptCal(){
      const year=2026;
      const month=Math.min(12, Math.max(3, Number(typeof mptMonth==="number"?mptMonth:3)||3));
      const names=["","Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"];
      const first=new Date(year, month-1, 1);
      const startDow=(first.getDay()+6)%7;
      const dim=new Date(year, month, 0).getDate();
      const cells=[];
      for(let i=0;i<startDow;i++) cells.push(0);
      for(let d=1;d<=dim;d++) cells.push(d);
      while(cells.length%7) cells.push(0);
      const isoOf=d=>year+"-"+String(month).padStart(2,"0")+"-"+String(d).padStart(2,"0");
      const pick=typeof mptDay==="string"?mptDay:"";
      const months=[3,4,5,6,7];
      const head=months.map(mo=>`<button type="button" class="chip ${mo===month?"on":""}" data-mpt-month="${mo}">${names[mo]}</button>`).join("");
      const grid=`<div class="mpt-wd">${["пн","вт","ср","чт","пт","сб","вс"].map(x=>`<span>${x}</span>`).join("")}</div>`+
        `<div class="mpt-grid">${cells.map(d=>{
          if(!d) return `<span class="mpt-cell empty"></span>`;
          const iso=isoOf(d);
          const k2=mptKind("2wd", iso);
          const k4=mptKind("4wd", iso);
          const on=pick===iso?" on":"";
          return `<button type="button" class="mpt-cell${on}" data-mpt-day="${iso}" title="${d}.${String(month).padStart(2,"0")}.${year}">
            <b>${d}</b>
            <i class="${k2}" title="2WD"></i>
            <i class="${k4}" title="4WD"></i>
          </button>`;
        }).join("")}</div>`;
      const panel=pick
        ? `<div class="mpt-info">
            <b>${pick.slice(8)}.${pick.slice(5,7)}.${pick.slice(0,4)} · дата производства</b>
            <div class="mpt-pair"><span>T7 2WD</span><em class="${mptKind("2wd",pick)}">${mptLabel(mptKind("2wd",pick))}</em></div>
            <div class="mpt-pair"><span>T7 4WD</span><em class="${mptKind("4wd",pick)}">${mptLabel(mptKind("4wd",pick))}</em></div>
            ${mptCars(pick)}
          </div>`
        : `<div class="mpt-info"><span>Нажмите день — правило для 2WD и 4WD. Верхняя точка на дате — 2WD, нижняя — 4WD.</span></div>`;
      return `<div class="mpt-cal">
        <div class="mpt-legend"><span class="mpt-dot mpt"></span> МПТ <span class="mpt-dot sub"></span> субс. бренда</div>
        <div class="study-pick">${head}</div>
        ${grid}
        ${panel}
        <div class="mpt-keys">${TERMS_MPT.map(g=>`<small><b>${escape(g.line)}</b> · ${g.rows.map(r=>escape(r[0])+" — "+escape(r[1])).join("; ")}</small>`).join("")}</div>
      </div>`;
    }
    const CORP_VINS = new Set([
      "EDXFB32B2TE041658","EDXFB32B4TE041659","EDXFB32B1TE087336",
      "EDXFB32B3TE091114","EDXFD32B4TE092587","EDXFD32B4TE092590",
      "EDXGB32B1TE110196","EDXGB32B8TE110275","EDXGB32B0TE089261",
      "EDXGB32B1TE104317","EDXGB32B4TE110225","EDXGB32BXTE087470"
    ]);
    const FLEET_BFS = {
      t9p:{name:"Tiggo 9 Prime 4WD",rrc:4335000,dealer:3895000,an:546000,client:3814800,prem:166900,km:49918,tidy:3789000,sub:241000,do:70000,casco:80000},
      t9u:{name:"Tiggo 9 Ultra 4WD",rrc:4640000,dealer:4200000,an:591000,client:4083200,prem:209600,km:48033,tidy:4049000,sub:241000,do:70000,casco:80000},
      a8a:{name:"Arrizo 8 Active",rrc:2865000,dealer:2649000,an:376000,client:2492550,prem:213750,km:44057,tidy:2489000,sub:150000,do:70000,casco:80000},
      a8p:{name:"Arrizo 8 Prime",rrc:3060000,dealer:2699000,an:491000,client:2570400,prem:189800,km:49016,tidy:2569000,sub:150000,do:70000,casco:80000},
      a8u:{name:"Arrizo 8 Ultra Black",rrc:3275000,dealer:2899000,an:596000,client:2685500,prem:279000,km:48361,tidy:2679000,sub:150000,do:70000,casco:80000},
      t4p:{name:"T4 Prime 2025",rrc:2449000,dealer:2369000,an:200000,client:2253080,prem:164900,km:36803,tidy:2249000,sub:120000,do:70000,casco:80000},
      t4la:{name:"T4L Active",rrc:2329000,dealer:2234000,an:140000,client:2189260,prem:91320,km:37967,tidy:2189000,sub:100000,do:70000,casco:80000},
      t4lp:{name:"T4L Prime",rrc:2479000,dealer:2389000,an:230000,client:2255890,prem:182690,km:34992,tidy:2249000,sub:100000,do:70000,casco:80000},
      t7a:{name:"T7 Active 2WD",rrc:2785000,dealer:2645000,an:396000,client:2395100,prem:305600,km:40656,tidy:2389000,sub:150000,do:70000,casco:80000},
      t7p:{name:"T7 Prime 2WD",rrc:2985000,dealer:2840000,an:456000,client:2537250,prem:362450,km:42172,tidy:2529000,sub:150000,do:70000,casco:80000},
      t7a4:{name:"T7 Active 4WD",rrc:2990000,dealer:2860000,an:461000,client:2541500,prem:378300,km:38770,tidy:2529000,sub:150000,do:70000,casco:80000},
      t7p4:{name:"T7 Prime 4WD",rrc:3190000,dealer:3045000,an:491000,client:2711500,prem:397300,km:42049,tidy:2699000,sub:150000,do:70000,casco:80000},
      t8a:{name:"T8 Active 2WD",rrc:3099000,dealer:2999000,an:310000,client:2789100,prem:271880,km:50721,tidy:2789000,sub:130000,do:70000,casco:80000},
      t8p:{name:"T8 Prime 2WD",rrc:3299000,dealer:3149000,an:430000,client:2870130,prem:344850,km:53156,tidy:2869000,sub:130000,do:70000,casco:80000},
      t8p4:{name:"T8 Prime 4WD",rrc:3630000,dealer:3465000,an:481000,client:3158100,prem:379500,km:52049,tidy:3149000,sub:130000,do:70000,casco:80000},
      t8u4:{name:"T8 Ultra 4WD",rrc:3885000,dealer:3705000,an:536000,client:3379950,prem:402750,km:38320,tidy:3349000,sub:130000,do:70000,casco:80000}
    };
    const FLEET_TI = 50000;
    function kmIsCorp(vin){
      const v=String(vin||"");
      if(CORP_VINS.has(v)) return true;
      const car=(typeof STOCK!=="undefined"?STOCK:[]).find(x=>x.vin===v);
      return !!(car && car.corp);
    }
    function fleetOf(id){
      return FLEET_BFS[id] || FLEET_BFS.t9u;
    }
    function fleetCreditBox(price){
      const downMode=(typeof kmStr==="function"?kmStr("cDownMode","pct"):"pct");
      const months=typeof kmVal==="function"?kmVal("cMonths", 60):60;
      let downPct=typeof kmVal==="function"?kmVal("cDownPct", 20):20;
      let down=typeof kmVal==="function"?kmVal("cDown", Math.round(price*0.2)):Math.round(price*0.2);
      if(downMode==="pct") down=Math.round(price*Math.max(0,downPct)/100);
      else downPct=price>0?Math.round(down*1000/price)/10:0;
      down=Math.max(0,Math.min(price,down));
      const pay=typeof calcPay==="function"?calcPay(price, down, months, 19.2):0;
      return `<div class="note-box" style="margin-top:12px">
        <p class="eyebrow" style="margin:0 0 6px">Кредит 19,2% · МПТ + Совкомбанк лизинг</p>
        <p class="calc-note">Доп. расчёт к лизингу. Цена ${rub(Math.round(price))} ₽.</p>
        <p class="eyebrow" style="margin-top:8px">Первый взнос</p>
        <div class="down-mode">
          <button type="button" class="chip ${downMode==="sum"?"on":""}" data-down-mode="sum">Сумма, ₽</button>
          <button type="button" class="chip ${downMode!=="sum"?"on":""}" data-down-mode="pct">Проценты</button>
        </div>
        <input type="hidden" id="cDownMode" value="${downMode==="sum"?"sum":"pct"}" />
        ${downMode==="sum"
          ?`<label class="field" style="max-width:none"><span>Первый взнос, ₽</span><input id="cDown" inputmode="numeric" value="${down}" /></label>`
          :`<label class="field" style="max-width:none"><span>Первый взнос, %</span><input id="cDownPct" inputmode="decimal" value="${downPct}" /></label>`}
        <p class="calc-note">${rub(down)} ₽ · ${downPct}% от цены</p>
        <label class="field" style="max-width:none"><span>Срок, мес.</span><input id="cMonths" inputmode="numeric" value="${months}" /></label>
        <div class="bank-row"><span><b>Платёж 19,2%</b><br/><small>${months} мес. · ПВ ${downPct}%</small></span><span class="pay">${rub(Math.round(pay))} ₽</span></div>
      </div>`;
    }
    function calcFleet(m){
      const f=fleetOf(m.id);
      const useFleet=kmVal("kmFleetDisc", false);
      const useMpt=kmVal("kmFleetMpt", false);
      const useTi=kmVal("kmUseTi", false);
      let price=f.rrc;
      const fleetCut=Math.max(0, f.rrc-(f.tidy||f.rrc));
      const steps=[];
      if(useFleet){ price=f.tidy; steps.push("флит −"+rub(fleetCut)); }
      if(useTi){ price=Math.max(0, price-FLEET_TI); steps.push("трейд-ин −"+rub(FLEET_TI)); }
      if(useMpt){ price=Math.round(price*0.9); steps.push("МПТ −10%"); }
      const car=(typeof STOCK!=="undefined"?STOCK:[]).find(x=>x.vin===kmVin);
      const mptCut=Math.round((useFleet?f.tidy:f.rrc)*(useTi?0.9:1)*0.1);
      return banner("Калькулятор","Флит · BFS Совкомбанк лизинг","TENET")+`
        <p class="lead">Корпоративный VIN. Стандартный кредит запрещён. Считаем BFS Совкомбанк лизинг.</p>
        ${kmChipGroups(m.id)}
        <div class="km-layout">
          <div class="card">
            <p class="eyebrow">BFS Совкомбанк лизинг · ${escape(f.name)}</p>
            ${car?`<p class="calc-note">${escape(car.vin)} · ${escape(car.color||"")} · ${escape(car.trim||"")}</p>`:""}
            <div class="note-box">Сбер / Альфа / Т-Банк нельзя. BFS: Каркаде, Т-Лизинг, Европлан, Сберлизинг, Газпромбанк Лизинг, Совкомбанк Лизинг.</div>
            <label class="check-row"><input id="kmFleetDisc" type="checkbox" ${useFleet?"checked":""} /> <span>Флит скидка ${rub(fleetCut)} · макс. выгода ${rub(f.an)}</span></label>
            <label class="check-row"><input id="kmUseTi" type="checkbox" ${useTi?"checked":""} /> <span>Трейд-ин ${rub(FLEET_TI)}</span></label>
            <label class="check-row"><input id="kmFleetMpt" type="checkbox" ${useMpt?"checked":""} /> <span>МПТ −10%</span></label>
            <div class="note-box" style="margin-top:14px">
              <p class="eyebrow" style="margin:0 0 6px">Итоговая цена</p>
              ${price<f.rrc?`<div class="calc-out" style="text-decoration:line-through;opacity:.42;margin-bottom:2px">${rub(f.rrc)} ₽</div>`:""}
              <div class="calc-out">${rub(Math.round(price))} ₽</div>
              <p class="calc-note">${steps.length?steps.join(" → "):"Базовая цена без скидок."}${useFleet?" · AP без тюнинга "+rub(f.tidy):""}</p>
            </div>
            ${useMpt?fleetCreditBox(price):""}
          </div>
          <div class="km-right">
            <div class="card">
              <p class="eyebrow">Лист «Флит» BFS</p>
              <div class="bank-row"><span>РРЦ</span><span class="pay">${rub(f.rrc)} ₽</span></div>
              <div class="bank-row"><span>Макс. выгода AN</span><span class="pay">${rub(f.an)} ₽</span></div>
              <div class="bank-row"><span>Цена AP без тюнинга</span><span class="pay">${rub(f.tidy)} ₽</span></div>
              ${useMpt
                ? `<div class="bank-row"><span>МПТ −10%</span><span class="pay">${rub(mptCut)} ₽</span></div>`
                : `<div class="bank-row"><span>Субсидия TENET</span><span class="pay">${rub(f.sub)} ₽</span></div>`}
              <p class="calc-note">${useMpt?"На цену действует МПТ −10%, не субсидия бренда.":"Порядок: флит скидка → трейд-ин → МПТ −10%."}</p>
            </div>
            ${kmSideList(m)}
          </div>
        </div>
        <div class="card dc-result ok">
          <p class="eyebrow">Доходность ДЦ · КМ без НДС · флит BFS</p>
          <div class="calc-out">${rub(f.km)} ₽</div>
          <p class="calc-note">КМ с листа «Флит», блок BFS. Пауза банка, ориентир 16.09.</p>
        </div>`;
    }
    function termCard(title, value, note){
      return `<article class="term-card"><b>${escape(title)}</b>${value?`<div class="num">${value}</div>`:""}${note?`<small>${note}</small>`:""}</article>`;
    }
    function termGroup(rows, valKey){
      const order=[], map={};
      rows.forEach(r=>{
        const k=r.model;
        if(!map[k]){ map[k]=[]; order.push(k); }
        map[k].push(r);
      });
      return order.map(model=>{
        const list=map[model];
        const body=list.map(r=>`<div class="term-row"><span>${escape(r.trim)}</span><b class="num">${escape(r[valKey]||"")}</b></div>${r.note?`<small>${escape(r.note)}</small>`:""}`).join("");
        return `<article class="term-card term-group"><b>${escape(model)}</b>${body}</article>`;
      }).join("");
    }
    function prioList(){
      const soldBy={};
      TERMS_PRIO.forEach(r=>{
        if(r.sold && r.seller) soldBy[r.seller]=(soldBy[r.seller]||0)+1;
      });
      return `<ol class="prio-list">`+TERMS_PRIO.map((r,i)=>{
        const sold=!!r.sold;
        const n=r.seller?soldBy[r.seller]||0:0;
        const mark=sold&&r.seller?`<span class="sold-mark">Продано · ${escape(r.seller)} <i>${n>=2?"2":"1"}</i></span>`:"";
        const extra=r.extra?` · ${escape(r.extra)}`:"";
        return `<li class="prio-item${sold?" sold":""}">
          <div class="prio-top"><b>${i+1}. ${escape(r.model)} · ${escape(r.trim)}</b>${mark}</div>
          <div class="prio-meta">${escape(r.vin)} · ${escape(r.color)} · ${escape(r.year)}${extra}</div>
          <div class="prio-pay">${r.pay?rub(r.pay):"—"} / ${r.bonus?rub(r.bonus):"—"}</div>
        </li>`;
      }).join("")+`</ol>`;
    }
    function kmTrimFit(m, car){
      const t=(car.trim||"").toLowerCase();
      const id=m.id;
      if(id==="t4la") return t.includes("актив");
      if(id==="t4lp") return t.includes("прайм");
      if(id==="t7a") return t.includes("актив") && !t.includes("4wd");
      if(id==="t7p") return t.includes("прайм") && !t.includes("4wd");
      if(id==="t7a4") return t.includes("актив") && t.includes("4wd");
      if(id==="t7p4") return t.includes("прайм") && t.includes("4wd");
      if(id==="t8a") return t.includes("актив");
      if(id==="t8p") return t.includes("прайм") && !t.includes("4wd");
      if(id==="t8p4") return t.includes("прайм") && t.includes("4wd");
      if(id==="t8u4") return t.includes("ультра");
      if(id==="t9p") return t.includes("прайм");
      if(id==="t9u") return t.includes("ультра");
      if(id==="a8a") return t.includes("актив");
      if(id==="a8p") return t.includes("прайм");
      if(id==="a8u") return t.includes("ультра");
      if(id==="t7l") return true;
      return true;
    }
    function kmIdFromCar(car){
      const t=(car.trim||"").toLowerCase();
      if(car.model==="t4") return "t4p";
      if(car.model==="t4l") return t.includes("прайм")?"t4lp":"t4la";
      if(car.model==="t7"){
        if(t.includes("4wd") && t.includes("прайм")) return "t7p4";
        if(t.includes("4wd")) return "t7a4";
        if(t.includes("прайм")) return "t7p";
        return "t7a";
      }
      if(car.model==="t8"){
        if(t.includes("ультра")) return "t8u4";
        if(t.includes("4wd")) return "t8p4";
        if(t.includes("прайм")) return "t8p";
        return "t8a";
      }
      if(car.model==="t9") return t.includes("прайм")?"t9p":"t9u";
      if(car.model==="a8"){
        if(t.includes("ультра")) return "a8u";
        if(t.includes("актив")) return "a8a";
        return "a8p";
      }
      if(car.model==="t7l") return "t7l";
      return "";
    }
    function kmLineOf(id){
      if(id==="t4p") return "T4";
      if(id==="t4la"||id==="t4lp") return "T4L";
      if(id==="t7a"||id==="t7p"||id==="t7a4"||id==="t7p4") return "T7";
      if(id==="t8a"||id==="t8p"||id==="t8p4"||id==="t8u4") return "T8";
      if(id==="ta8p"||id==="ta8u") return "TENET A8";
      if(id==="t9p"||id==="t9u") return "Tiggo 9";
      if(id==="a8a"||id==="a8p"||id==="a8u") return "Arrizo 8";
      if(id==="t7l") return "Tiggo 7 L";
      return "Другие";
    }
    function kmStockCars(m){
      const list=typeof STOCK!=="undefined"?STOCK:[];
      return list.filter(c=>c.model===m.stock && kmTrimFit(m,c));
    }
    function terms(){
      if(needAuth()) return login();
      return banner("Торговые условия","Файл «Торговые условия» · с "+TERMS_DATE,"TENET")+
        `<div class="terms-col">`+
        `<p class="lead">Клиенту называть рекомендованную цену. Максимум с выгодами — после расчёта РОП. КМ — коридор доходности без НДС, тыс. руб.</p>`+
        `<div class="note-box">Скидки импортёра не обещать, если их нет в прайсе. Цифры внутренние.</div>`+
        `<h2>Доходность</h2>`+
        `<div class="terms-cards">`+termGroup(KM_CORRIDOR,"km")+`</div>`+
        `<h2>Бонусы</h2>`+
        `<div class="terms-cards">`+termGroup(TERMS_BONUS,"bonus")+`</div>`+
        `<h2>Спец инвойс</h2>`+
        `<div class="terms-cards">`+TERMS_INV.map(r=>termCard(r.model+" · "+r.trim, escape(r.price), "")).join("")+`</div>`+
        `<h2>МПТ / субсидия TENET</h2>`+
        `<div class="terms-cards">`+TERMS_MPT.map(g=>`<article class="term-card"><b>${escape(g.line)}</b>`+g.rows.map(r=>`<small>${escape(r[0])} · <b>${escape(r[1])}</b></small>`).join("")+`</article>`).join("")+`</div>`+
        `<h2>Приоритет · ${TERMS_PRIO.length} авто</h2>`+
        `<p class="lead">Личный план 2 · командный план 12. Всего 14. Порядок как в файле.</p>`+
        prioList()+
        `<p class="lead">Доплата за 4WD на T7 — 205 000 ₽. Мотор T7 везде 1.6T 150.</p>`+
        `<div class="who-line"><button class="btn ivory" data-go="calc">В калькулятор</button><button class="btn ghost" data-go="docs">Документы</button></div>`+
        `</div>`;
    }
    function calcPay(price, down, months, rate){
      const S=Math.max(0, (Number(price)||0)-(Number(down)||0));
      const n=Math.max(1, Number(months)||12);
      const i=(Number(rate)||0)/100/12;
      if(i<=0) return S/n;
      const k=Math.pow(1+i,n);
      return S*i*k/(k-1);
    }
    function kmVal(id, def){
      const el=document.getElementById(id);
      if(!el) return def;
      if(el.type==="checkbox") return !!el.checked;
      const n=Number(String(el.value||"").replace(/\s+/g,""));
      return Number.isFinite(n)?n:def;
    }
    function kmStr(id, def){
      const el=document.getElementById(id);
      if(!el) return def;
      const v=String(el.value||"").trim();
      return v||def;
    }
    function kmChipGroups(active){
      const order=["T4","T4L","T7","T8","TENET A8","Tiggo 9","Arrizo 8","Tiggo 7 L"];
      const groups={};
      KM_MODELS.forEach(x=>{
        const g=kmLineOf(x.id);
        (groups[g]=groups[g]||[]).push(x);
      });
      return order.filter(g=>groups[g]).map(g=>`<div class="km-line"><p class="stock-h">${g}</p><div class="km-grid">${groups[g].map(x=>`<button type="button" class="chip ${x.id===active?"on":""}" data-km-id="${x.id}">${escape(x.name)}<small>${x.brand} · РРЦ ${rub(x.rrc)}</small></button>`).join("")}</div></div>`).join("");
    }
    function kmSideList(m){
      const cars=kmStockCars(m).slice().sort((a,b)=>{
        const pa=PRIO_VINS.has(a.vin)?0:1;
        const pb=PRIO_VINS.has(b.vin)?0:1;
        if(pa!==pb) return pa-pb;
        if(a.status!==b.status) return a.status==="in"?-1:1;
        return (a.color||"").localeCompare(b.color||"");
      });
      const inn=cars.filter(c=>c.status==="in").length;
      const way=cars.filter(c=>c.status==="way").length;
      if(!cars.length){
        return `<div class="card stock-side"><p class="eyebrow">Склад · ${escape(m.name)}</p><p class="lead" style="max-width:none">Нет этой комплектации в наличии и в пути.</p></div>`;
      }
      const block=(title, arr)=>!arr.length?"":`<p class="stock-h">${title} · ${arr.length}</p>`+arr.map(c=>{
        const prio=PRIO_VINS.has(c.vin);
        const on=kmVin===c.vin;
        const st=c.status==="in"?"в наличии":"в пути";
        return `<button type="button" class="stock-car${prio?" prio":""}${c.mpt?" mpt":""}${on?" on":""}" data-km-vin="${escape(c.vin)}">
          <b>${escape(c.color||"—")} · ${escape(c.trim||"")}${prio?" · приоритет":""}</b>
          ${c.mpt?`<span class="mpt-tag">Доступна гос программа −20%</span>`:""}
          <span class="vin">${escape(c.vin)}</span>
          <span class="stock-meta">${st}${c.invoice?" · спец инвойс":""}${c.mpt?" · МПТ":""}${c.note?" · "+escape(c.note):""}</span>
        </button>`;
      }).join("");
      return `<div class="card stock-side">
        <p class="eyebrow">Склад · ${escape(m.name)}</p>
        <p class="lead" style="max-width:none;margin:0 0 10px">Только эта комплектация. В наличии ${inn} · в пути ${way}.</p>
        ${block("В наличии", cars.filter(c=>c.status==="in"))}
        ${block("В пути", cars.filter(c=>c.status==="way"))}
      </div>`;
    }
    function kmPrioRecs(cur, carPrice, downPct, months, extras){
      const list=typeof STOCK!=="undefined"?STOCK:[];
      const refPay=typeof calcPay==="function"?calcPay(carPrice+extras, Math.round(carPrice*downPct/100), months, 10):0;
      const rows=list.filter(c=>PRIO_VINS.has(c.vin) && c.vin!==kmVin).map(c=>{
        const id=kmIdFromCar(c);
        const mm=KM_MODELS.find(x=>x.id===id);
        const price=mm?mm.rrc:carPrice;
        const group=typeof kmRateGroup==="function"?kmRateGroup(mm||cur):"t4l_t7";
        const look=typeof kmBankRate==="function"?kmBankRate("sber", group, months, downPct):{rate:10, term:months};
        const down=Math.round(price*Math.max(0,downPct)/100);
        const pay=calcPay(price+extras, down, look.term||months, look.rate);
        return {c, mm, price, pay, d:Math.abs(price-carPrice)+Math.abs(pay-refPay)};
      }).sort((a,b)=>a.d-b.d).slice(0,4);
      if(!rows.length) return "";
      return `<div class="card rec-box">
        <p class="eyebrow">Рекомендуем рассмотреть</p>
        <p class="lead" style="max-width:none;margin:0 0 10px">Приоритетные авто рядом по цене и платежу.</p>
        ${rows.map(r=>{
          const st=r.c.status==="in"?"в наличии":"в пути";
          return `<button type="button" class="stock-car prio rec${r.c.mpt?" mpt":""}" data-km-vin="${escape(r.c.vin)}">
            <b>${escape((r.mm&&r.mm.name)||r.c.name)} · ${escape(r.c.color||"—")}</b>
            ${r.c.mpt?`<span class="mpt-tag">Доступна гос программа −20%</span>`:""}
            <span class="vin">${escape(r.c.vin)} · ${escape(r.c.trim||"")} · ${st}</span>
            <span class="stock-meta">РРЦ ${rub(r.price)} · платёж ~${rub(Math.round(r.pay))} ₽ · приоритет</span>
          </button>`;
        }).join("")}
      </div>`;
    }
    function calcKm(){
      if(typeof kmId!=="string" || !KM_MODELS.some(x=>x.id===kmId)) kmId=KM_MODELS[0].id;
      if(typeof kmVin!=="string") kmVin="";
      const m=KM_MODELS.find(x=>x.id===kmId)||KM_MODELS[0];
      const fresh=(typeof kmShown==="undefined")||kmShown!==kmId;
      kmShown=kmId;
      const rrc=fresh?m.rrc:kmVal("kmRrc", m.rrc);
      const invoice=fresh?m.dealer:kmVal("kmInv", m.dealer);
      const useTi=kmVal("kmUseTi", false);
      const useLoan=kmVal("kmUseLoan", false);
      const hasDealCr=m.cr>0;
      const dealCrLabel=m.id==="t7p"?"Выгодный кредит":"Прямая скидка";
      const dealCrNeedsLoan=m.id==="t7p";
      const showDealCr=hasDealCr && (!dealCrNeedsLoan || useLoan);
      const useCr=showDealCr && kmVal("kmUseCr", false);
      const spec=kmVal("kmSpec", 0);
      const useDcTi=useTi && kmVal("kmUseDcTi", false);
      const useDcCr=useLoan && kmVal("kmUseDcCr", false);
      const dcTi=useDcTi?kmVal("kmDcTi", typeof KM_DC_DEF==="number"?KM_DC_DEF:100000):0;
      const dcCr=useDcCr?kmVal("kmDcCr", typeof KM_DC_DEF==="number"?KM_DC_DEF:100000):0;
      const addons=kmVal("kmDo", 70000);
      let casco=0, card=0, pack=0;
      if(useLoan){
        pack=kmVal("kmPack", 150000);
        casco=Math.min(pack, 80000);
        card=Math.max(0, pack-80000);
      }else{
        casco=kmVal("kmCasco", 80000);
        card=0;
      }
      const prio=PRIO_VINS.has(kmVin);
      const tiAmt=useTi?m.ti:0;
      const tiBack=useTi?m.tiBack:0;
      const crAmt=useCr?m.cr:0;
      const crBack=useCr?m.crBack:0;
      const lo=prio?m.prioMin:m.kmMin;
      const hi=prio?m.prioMax:m.kmMax;
      const discount=tiAmt+spec+dcTi+dcCr+crAmt;
      const bonus=invoice>0?(invoice/m.vat)*m.bonus:0;
      const margin=rrc-invoice;
      const carPrice=rrc-discount;
      const client=carPrice+addons;
      const iron=margin-discount+tiBack+crBack+bonus*1.2;
      const km=(addons*0.3+casco*0.3+card*0.8+iron)/m.vat-carPrice*m.fee;
      const kmK=km/1000;
      const ok=kmK+0.05>=lo && kmK-0.05<=hi;
      const price=Math.round(carPrice);
      const fee=typeof KM_BANK_FEE==="number"?KM_BANK_FEE:30000;
      const extras=useLoan?(addons+(pack||0)+fee):0;
      const downMode=kmStr("cDownMode","pct");
      const months=kmVal("cMonths", 60);
      let downPct=kmVal("cDownPct", 20);
      let down=kmVal("cDown", Math.round(price*0.2));
      if(fresh){ downPct=20; down=Math.round(price*0.2); }
      if(downMode==="pct") down=Math.round(price*Math.max(0,downPct)/100);
      else downPct=price>0?Math.round(down*1000/price)/10:0;
      down=Math.max(0, Math.min(price, down));
      const credit=Math.max(0,price-down+extras);
      const rateGroup=typeof kmRateGroup==="function"?kmRateGroup(m):"t4l_t7";
      const banks=(typeof KM_BANKS!=="undefined"?KM_BANKS:[]).map(b=>{
        const look=typeof kmBankRate==="function"?kmBankRate(b.id, rateGroup, months, downPct):{rate:b.rate||0, term:months, capped:false};
        const term=look.term||months;
        const pay=calcPay(price+extras, down, term, look.rate);
        return Object.assign({}, b, {rate:look.rate, term, capped:!!look.capped, pay, over:pay*term-credit});
      });
      return banner("Калькулятор","КМ и платёж · база "+TERMS_DATE,"TENET")+`
        <p class="lead">Сначала комплектация. Кредит и СЖ открываются галочкой «Кредит».</p>
        ${kmChipGroups(m.id)}
        <div class="km-layout">
          <div class="card">
            <p class="eyebrow">Калькулятор КМ · ${escape(m.name)}</p>
            <label class="field" style="max-width:none;margin-top:8px"><span>РРЦ, ₽ · из условий ${TERMS_DATE}</span><input id="kmRrc" inputmode="numeric" value="${rrc}" /></label>
            <label class="field" style="max-width:none"><span>Сумма счёта, ₽ · из условий ${TERMS_DATE}</span><input id="kmInv" inputmode="numeric" value="${invoice}" /></label>
            <label class="check-row"><input id="kmUseTi" type="checkbox" ${useTi?"checked":""} /> <span>Трейд-ин ${m.ti?rub(m.ti)+" / возмещение "+rub(m.tiBack):"нет в базе"}</span></label>
            <label class="check-row"><input id="kmUseLoan" type="checkbox" ${useLoan?"checked":""} /> <span>Кредит</span></label>
            ${showDealCr?`<label class="check-row"><input id="kmUseCr" type="checkbox" ${useCr?"checked":""} /> <span>${dealCrLabel} · ${rub(m.cr)}${m.crBack?` / возмещение ${rub(m.crBack)}`:""}</span></label>`:""}
            <label class="field" style="max-width:none"><span>Спецпредложение, ₽</span><input id="kmSpec" inputmode="numeric" value="${spec}" /></label>
            ${useTi?`<label class="check-row"><input id="kmUseDcTi" type="checkbox" ${useDcTi?"checked":""} /> <span>Скидка от ДЦ за трейд-ин ${rub(KM_DC_DEF)}</span></label>`:""}
            ${useTi&&useDcTi?`<label class="field" style="max-width:none"><span>Сумма скидки ДЦ за трейд-ин, ₽</span><input id="kmDcTi" inputmode="numeric" value="${dcTi||KM_DC_DEF}" /></label>`:""}
            ${useLoan?`<label class="check-row"><input id="kmUseDcCr" type="checkbox" ${useDcCr?"checked":""} /> <span>Скидка от ДЦ за кредит ${rub(KM_DC_DEF)}</span></label>`:""}
            ${useLoan&&useDcCr?`<label class="field" style="max-width:none"><span>Сумма скидки ДЦ за кредит, ₽</span><input id="kmDcCr" inputmode="numeric" value="${dcCr||KM_DC_DEF}" /></label>`:""}
            <label class="field" style="max-width:none"><span>Д/О, ₽</span><input id="kmDo" inputmode="numeric" value="${addons}" /></label>
            <div class="note-box" style="margin-top:14px">
              <p class="eyebrow" style="margin:0 0 6px">Итоговая цена для клиента</p>
              ${Math.round(rrc+addons)>Math.round(client)?`<div class="calc-out" style="text-decoration:line-through;opacity:.42;margin-bottom:2px">${rub(Math.round(rrc+addons))} ₽</div>`:""}
              <div class="calc-out">${rub(Math.round(client))} ₽</div>
              <p class="calc-note">Авто ${rub(Math.round(carPrice))} + Д/О ${rub(Math.round(addons))}. Каско не входит.${discount?` Скидка ${rub(Math.round(discount))}.`:""}</p>
            </div>
            ${useLoan
              ?`<label class="field" style="max-width:none"><span>Каско расширенное, ₽</span><input id="kmPack" inputmode="numeric" value="${pack}" /></label>`
              :`<label class="field" style="max-width:none"><span>КАСКО, ₽</span><input id="kmCasco" inputmode="numeric" value="${casco}" /></label>`}
            ${prio?`<div class="note-box">Приоритетный VIN ${escape(kmVin)}. Коридор ${lo} … ${hi} тыс.</div>`:""}
          </div>
          <div class="km-right">
            ${useLoan?`<div class="card">
              <p class="eyebrow">Кредит · ${escape(m.name)}</p>
              <p class="calc-note">ПВ от цены авто ${rub(price)} ₽, без Д/О и каско. В кредит входят авто − ПВ, Д/О, каско расширенное и комиссия банка.</p>
              <p class="eyebrow" style="margin-top:12px">Первый взнос</p>
              <div class="down-mode">
                <button type="button" class="chip ${downMode==="sum"?"on":""}" data-down-mode="sum">Сумма, ₽</button>
                <button type="button" class="chip ${downMode!=="sum"?"on":""}" data-down-mode="pct">Проценты</button>
              </div>
              <input type="hidden" id="cDownMode" value="${downMode==="sum"?"sum":"pct"}" />
              ${downMode==="sum"
                ?`<label class="field" style="max-width:none"><span>Первый взнос, ₽</span><input id="cDown" inputmode="numeric" value="${down}" /></label>`
                :`<label class="field" style="max-width:none"><span>Первый взнос, %</span><input id="cDownPct" inputmode="decimal" value="${downPct}" /></label>`}
              <p class="calc-note">${rub(down)} ₽ · ${downPct}% от цены авто</p>
              <label class="field" style="max-width:none"><span>Срок, мес.</span><input id="cMonths" inputmode="numeric" value="${months}" /></label>
              <p class="eyebrow" style="margin-top:16px">Платёж в месяц</p>
              ${banks.map(b=>{
                const yearsWant=Math.round(months/12);
                const yearsHave=Math.round(b.term/12);
                const note=b.capped?`нет ${yearsWant} ${yearsWant===1?"года":"лет"} · считаем ${b.term} мес. (${yearsHave} ${yearsHave===1?"год":yearsHave<5?"года":"лет"})`: `${b.term} мес.`;
                return `<div class="bank-row"><span><b>${escape(b.name)}</b><br/><small>${b.rate}% · ПВ ${downPct}% от авто · ${note} · переплата ~${rub(Math.round(b.over))}</small></span><span class="pay">${rub(Math.round(b.pay))} ₽</span></div>`;
              }).join("")}
              <p class="calc-note">Кредит ${rub(credit)} ₽ = авто ${rub(price)} − ПВ ${rub(down)} + Д/О ${rub(addons)} + каско ${rub(pack)} + комиссия банка. Ставки TENET ФИНАНС, ИП 1890/И.</p>
            </div>`:`<div class="card"><p class="eyebrow">Кредит</p><p class="lead" style="max-width:none">Включите галочку «Кредит», чтобы открыть расчёт платежа и каско расширенное.</p></div>`}
            ${typeof kmPrioRecs==="function"?kmPrioRecs(m, price, downPct, months, extras):""}
            ${kmSideList(m)}
          </div>
        </div>
        <div class="card dc-result ${ok?"ok":"bad"}">
          <p class="eyebrow">Доходность ДЦ · КМ без НДС</p>
          <div class="calc-out">${rub(Math.round(km))} ₽</div>
          <p class="calc-note">Коридор ${lo} … ${hi} тыс. · сейчас ${kmK.toFixed(1)} тыс. · ${ok?"в коридоре":"вне коридора"}</p>
          <div class="note-box">Цена авто <b>${rub(Math.round(carPrice))} ₽</b> · клиенту с Д/О <b>${rub(Math.round(client))} ₽</b><br/>Скидка ${rub(Math.round(discount))} · маржа 1С ${rub(Math.round(margin))}<br/>Бонус ${rub(Math.round(bonus))} (${Math.round(m.bonus*100)}%) · доход на железе ${rub(Math.round(iron))}<br/>НДС ${m.vat===1.22?"22%":"20%"} · сбор ${Math.round(m.fee*100)}% от цены авто${prio?" · приоритет":""}</div>
        </div>`;
    }
    function calc(){
      if(needAuth()) return login();
      calcMode="km";
      return calcKm();
    }
