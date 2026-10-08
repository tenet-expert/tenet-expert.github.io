(function(){
  function dutyPdfClose(){
    const box=document.getElementById("dutyPdfView");
    if(!box) return;
    box.remove();
    document.body.style.overflow="";
    if(location.hash==="#pdf"){
      try{ history.replaceState(null,"",location.pathname+location.search); }catch(e){}
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
  window.dutyPdfClose=dutyPdfClose;
  window.dutyPdfOpen=dutyPdfOpen;
  window.dutyPdf=function(src){
    if(typeof window.__dutyPagePdf==="function") return window.__dutyPagePdf(src);
    const d=src||(typeof dutyRead==="function"?dutyRead():{});
    const p=typeof dutyCount==="function"?dutyCount(d):{on:0,tot:0};
    const pct=p.tot?Math.round(p.on*100/p.tot):0;
    const cars=(typeof DUTY_CARS!=="undefined")?DUTY_CARS:[
      {id:"t4l",title:"T4L"},{id:"t7",title:"T7"},{id:"t82",title:"Т8 2WD"},
      {id:"t8",title:"Т8 4WD"},{id:"t9",title:"Т9"},{id:"a8",title:"Arrizo 8"}
    ];
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
    function tick(x,y,on){
      ctx.strokeStyle="#1a1a1a";
      ctx.lineWidth=1.6;
      ctx.strokeRect(x, y-15, 18, 18);
      if(on){
        ctx.fillStyle="#145a1f";
        ctx.font="800 16px Inter, Arial, sans-serif";
        ctx.fillText("\u2713", x+2, y);
      }
    }
    const bodyWord=(typeof dutyBodyWord==="function")?dutyBodyWord:function(v){ return v==="pm"?"\u00b1":v==="no"?"\u0433\u0440\u044f\u0437\u043d\u044b\u0439":"\u0447\u0438\u0441\u0442\u044b\u0439"; };
    const today=(typeof dutyToday==="function")?dutyToday():"";
    ctx.fillStyle="#c81e2b";
    ctx.fillRect(pad, pad, 32, 32);
    ctx.fillStyle="#fff";
    ctx.font="800 18px Inter, Arial, sans-serif";
    ctx.fillText("T", pad+9, pad+23);
    ctx.fillStyle="#111";
    ctx.font="800 30px Inter, Arial, sans-serif";
    ctx.fillText("\u0427\u0435\u043a-\u043b\u0438\u0441\u0442 \u0434\u0435\u0436\u0443\u0440\u043d\u043e\u0433\u043e", pad+46, pad+26);
    ctx.font="600 17px Inter, Arial, sans-serif";
    ctx.fillStyle="#5c5346";
    ctx.fillText((d.manager||"\u2014")+"  \u00b7  "+(d.date||today)+"  \u00b7  "+pct+"%  \u00b7  "+p.on+" \u0438\u0437 "+p.tot, pad+46, pad+52);
    let y=pad+70;
    function fitText(s, maxW){
      s=String(s||"").replace(/\s+/g," ").trim();
      if(!s) return "\u2014";
      if(ctx.measureText(s).width<=maxW) return s;
      let out=s;
      while(out.length>1 && ctx.measureText(out+"\u2026").width>maxW) out=out.slice(0,-1);
      return out+"\u2026";
    }
    ctx.fillStyle="#8a7d6e"; ctx.font="800 13px Inter, Arial, sans-serif";
    ctx.fillText("\u0422\u0415\u0421\u0422\u041e\u0412\u042b\u0415 \u0410\u0412\u0422\u041e\u041c\u041e\u0411\u0418\u041b\u0418", pad, y);
    ctx.strokeStyle="#eadfcf"; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(pad+210, y-4); ctx.lineTo(pad+inner, y-4); ctx.stroke();
    y+=16;
    const carH=214;
    cars.forEach(function(car){
      ctx.fillStyle="#f7f1e7";
      roundRect(pad, y, inner, carH, 14);
      ctx.fill();
      ctx.strokeStyle="#eadfcf"; ctx.lineWidth=1;
      roundRect(pad, y, inner, carH, 14);
      ctx.stroke();
      ctx.fillStyle="#111"; ctx.font="800 22px Inter, Arial, sans-serif";
      ctx.fillText(car.title, pad+20, y+34);
      const rows=[
        ["\u041e\u043c\u044b\u0432\u0430\u044e\u0449\u0430\u044f", !!d[car.id+"_wash"]],
        ["\u041a\u043e\u0432\u0440\u0438\u043a\u0438 \u0438 \u043f\u043e\u0440\u043e\u0433\u0438", !!d[car.id+"_mats"]],
        ["\u041d\u0435\u0442 \u043e\u0448\u0438\u0431\u043e\u043a", !!d[car.id+"_err"]],
        ["\u041d\u0435\u0442 \u043f\u044b\u043b\u0438", !!d[car.id+"_dust"]],
        ["\u0411\u0430\u0433\u0430\u0436\u043d\u0438\u043a", !!d[car.id+"_trunk"]]
      ];
      rows.forEach(function(row,ri){
        const col=ri%2;
        const line=Math.floor(ri/2);
        const cx=pad+20+col*((inner-40)/2);
        const cy=y+68+line*34;
        tick(cx, cy, row[1]);
        ctx.fillStyle="#111"; ctx.font="500 17px Inter, Arial, sans-serif";
        ctx.fillText(row[0], cx+28, cy);
      });
      ctx.fillStyle="#5c5346"; ctx.font="600 15px Inter, Arial, sans-serif";
      const meta="\u041a\u0443\u0437\u043e\u0432: "+bodyWord(d[car.id+"_body"]||"ok")+"     \u041f\u0440\u043e\u0431\u0435\u0433: "+(d[car.id+"_km"]||"\u2014")+"     \u0422\u043e\u043f\u043b\u0438\u0432\u043e: "+(d[car.id+"_fuel"]?d[car.id+"_fuel"]+"%":"\u2014");
      ctx.fillText(meta, pad+20, y+168);
      ctx.fillStyle="#fff";
      roundRect(pad+16, y+178, inner-32, 26, 6);
      ctx.fill();
      ctx.strokeStyle="#eadfcf"; ctx.lineWidth=1;
      roundRect(pad+16, y+178, inner-32, 26, 6);
      ctx.stroke();
      ctx.fillStyle="#8a7d6e"; ctx.font="500 14px Inter, Arial, sans-serif";
      ctx.fillText("\u041f\u0440\u0438\u043c\u0435\u0447\u0430\u043d\u0438\u0435: "+fitText(d[car.id+"_note"], inner-130), pad+24, y+196);
      y+=carH+10;
    });
    y+=8;
    ctx.fillStyle="#8a7d6e"; ctx.font="800 13px Inter, Arial, sans-serif";
    ctx.fillText("\u0421\u0410\u041b\u041e\u041d", pad, y);
    ctx.strokeStyle="#d9cbb6"; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(pad+70, y-4); ctx.lineTo(pad+inner, y-4); ctx.stroke();
    y+=16;
    function block(title, keys){
      const rows=Math.ceil(keys.length/3);
      const h=54+rows*40;
      ctx.fillStyle="#f7f1e7";
      roundRect(pad, y, inner, h, 14); ctx.fill();
      ctx.strokeStyle="#eadfcf"; ctx.lineWidth=1;
      roundRect(pad, y, inner, h, 14); ctx.stroke();
      ctx.fillStyle="#111"; ctx.font="800 20px Inter, Arial, sans-serif";
      ctx.fillText(title, pad+20, y+32);
      keys.forEach(function(pair,i){
        const col=i%3;
        const line=Math.floor(i/3);
        const cx=pad+20+col*((inner-40)/3);
        const cy=y+68+line*38;
        tick(cx, cy, !!d[pair[0]]);
        ctx.fillStyle="#111"; ctx.font="500 16px Inter, Arial, sans-serif";
        ctx.fillText(pair[1], cx+28, cy);
      });
      y+=h+12;
    }
    block("\u0414\u0438\u043b\u0435\u0440\u0441\u043a\u0438\u0439 \u0446\u0435\u043d\u0442\u0440",[
      ["dc_light","\u0421\u0432\u0435\u0442"],["dc_avito","\u0410\u0432\u0438\u0442\u043e"],["dc_music","\u041c\u0443\u0437\u044b\u043a\u0430"],
      ["dc_price_avito","\u0426\u0435\u043d\u044b \u0410\u0432\u0438\u0442\u043e"],["dc_price_hold","\u041f\u0440\u0430\u0439\u0441\u0445\u043e\u043b\u0434\u0435\u0440\u044b"],["dc_desk","\u0421\u0442\u043e\u043b\u044b"],["dc_trash","\u0411\u0443\u043c\u0430\u0433\u0438"]
    ]);
    block("\u0414\u0435\u043c\u043e\u043d\u0441\u0442\u0440\u0430\u0446\u0438\u043e\u043d\u043d\u044b\u0435",[
      ["dm_body","\u041a\u0443\u0437\u043e\u0432"],["dm_mats","\u041a\u043e\u0432\u0440\u0438\u043a\u0438"],["dm_trunk","\u0411\u0430\u0433\u0430\u0436\u043d\u0438\u043a"],
      ["dm_dust","\u041f\u044b\u043b\u044c"],["dm_wheel","\u041a\u043e\u043b\u0451\u0441\u0430"],["dm_bat","\u0410\u041a\u0411"]
    ]);
    ctx.fillStyle="#5c5346"; ctx.font="500 16px Inter, Arial, sans-serif";
    ctx.fillText("\u0417\u0430\u043c\u0435\u0442\u043a\u0430: "+(d.note||"\u2014"), pad, y+8);
    ctx.fillStyle="#9a9186"; ctx.font="500 13px Inter, Arial, sans-serif";
    ctx.fillText("TENET \u00b7 \u041e\u0442\u0434\u0435\u043b \u043f\u0440\u043e\u0434\u0430\u0436 \u00b7 \u042d\u043a\u0441\u043f\u0435\u0440\u0442 \u0410\u0432\u0442\u043e \u0421\u0430\u043c\u0430\u0440\u0430", pad, H-28);
    dutyPdfOpen(c.toDataURL("image/png"));
  };
})();

(function(){
  try{
    var SALES=[
      {when:"01.10.2026 12:00", who:"Демьянов", client:"Ахмеев", model:"T7"},
      {when:"02.10.2026 12:00", who:"Павлова", client:"А-Лизинг", model:"T7"},
      {when:"02.10.2026 12:01", who:"Тальков", client:"Базарова", model:"T4L"},
      {when:"04.10.2026 12:00", who:"Демьянов", client:"Мосольгин", model:"T7"},
      {when:"04.10.2026 12:01", who:"Лавров", client:"Антипов", model:"T4L"},
      {when:"05.10.2026 12:00", who:"Лавров", client:"Попов", model:"T8"},
      {when:"05.10.2026 12:01", who:"Спицын", client:"Ледкова", model:"T4L"},
      {when:"06.10.2026 12:00", who:"Спицын", client:"Антонов", model:"T8"},
      {when:"06.10.2026 12:01", who:"Спицын", client:"Шашков", model:"T4L"},
      {when:"07.10.2026 12:00", who:"Спицын", client:"Стрельников", model:"T7"}
    ];
    var OCT={
      "Ахмадуллин":{visit:2,call:2,web:3,td:0,issue:0,contract:0,cancel:0,service:0,ecredit:0,callVisit:0,webVisit:0,callContract:0,webContract:0},
      "Велиджанов":{visit:1,call:0,web:4,td:1,issue:0,contract:1,cancel:0,service:1,ecredit:1,callVisit:0,webVisit:0,callContract:0,webContract:0},
      "Демьянов":{visit:3,call:6,web:4,td:2,issue:2,contract:3,cancel:0,service:3,ecredit:2,callVisit:0,webVisit:0,callContract:0,webContract:1},
      "Лавров":{visit:4,call:6,web:5,td:3,issue:2,contract:3,cancel:1,service:3,ecredit:3,callVisit:0,webVisit:0,callContract:0,webContract:0},
      "Сидоров":{visit:6,call:6,web:5,td:7,issue:0,contract:2,cancel:1,service:4,ecredit:6,callVisit:0,webVisit:0,callContract:0,webContract:0},
      "Спицын":{visit:4,call:3,web:1,td:2,issue:4,contract:7,cancel:0,service:0,ecredit:3,callVisit:0,webVisit:1,callContract:2,webContract:0},
      "Тальков":{visit:8,call:5,web:13,td:5,issue:1,contract:2,cancel:0,service:1,ecredit:7,callVisit:0,webVisit:0,callContract:0,webContract:0}
    };
    var OTHER=[
      {name:"Павлова",visit:0,call:0,web:0,td:0,issue:1,contract:1,cancel:0,callVisit:0,webVisit:0,callContract:0,webContract:0},
      {name:"Елчин",visit:0,call:0,web:0,td:0,issue:0,contract:1,cancel:1,callVisit:1,webVisit:0,callContract:0,webContract:0},
      {name:"Леонтьев",visit:1,call:0,web:5,td:1,issue:0,contract:1,cancel:0,service:2,ecredit:1,callVisit:0,webVisit:2,callContract:0,webContract:1},
      {name:"Извеков",visit:1,call:0,web:0,td:0,issue:0,contract:0,cancel:0,service:1,ecredit:1,callVisit:0,webVisit:0,callContract:0,webContract:0},
      {name:"Клименко",visit:0,call:0,web:0,td:0,issue:0,contract:1,cancel:0,callVisit:0,webVisit:0,callContract:0,webContract:0},
      {name:"Бикулов",visit:0,call:0,web:0,td:2,issue:0,contract:0,cancel:0,callVisit:0,webVisit:0,callContract:0,webContract:0},
      {name:"Назарян",visit:0,call:0,web:0,td:1,issue:0,contract:0,cancel:0,callVisit:0,webVisit:0,callContract:0,webContract:0},
      {name:"Без менеджера",visit:0,call:1,web:1,td:0,issue:0,contract:0,cancel:0,callVisit:0,webVisit:0,callContract:0,webContract:0},
      {name:"Коропец",visit:0,call:0,web:0,td:0,issue:0,contract:0,cancel:0,service:0,ecredit:1,callVisit:0,webVisit:0,callContract:0,webContract:0}
    ];
    var KEYS=["visit","call","web","meet","td","contract","issue","cancel","service","ecredit","callVisit","webVisit","callContract","webContract","visitContract","traffic"];
    function blank(){
      var p={name:"",people:[],other:false};
      KEYS.forEach(function(k){ p[k]=0; });
      return p;
    }
    function fill(p, src){
      KEYS.forEach(function(k){ if(src[k]!=null) p[k]=src[k]; });
      p.traffic=(p.visit||0)+(p.call||0)+(p.web||0);
    }
    function monthRows(rows){
      var days={};
      (rows||[]).forEach(function(r){
        var d=String(r.when||"").slice(0,5);
        if(/^\d\d\.\d\d$/.test(d)) days[d]=1;
      });
      return Object.keys(days).length>=3;
    }
    function applyMonth(rank){
      var mains=[], bucket=null;
      rank.list.forEach(function(p){ if(p.other) bucket=p; else mains.push(p); });
      mains.forEach(function(p){ if(OCT[p.name]) fill(p, OCT[p.name]); });
      var kids=OTHER.map(function(o){ var p=blank(); p.name=o.name; fill(p,o); return p; });
      kids.sort(function(a,b){ return (b.issue-a.issue)||(b.contract-a.contract)||(b.td-a.td)||a.name.localeCompare(b.name,"ru"); });
      if(!bucket){ bucket=blank(); bucket.name="Другие"; bucket.other=true; }
      fill(bucket, {});
      kids.forEach(function(x){ KEYS.forEach(function(k){ bucket[k]=(bucket[k]||0)+(x[k]||0); }); });
      bucket.traffic=(bucket.visit||0)+(bucket.call||0)+(bucket.web||0);
      bucket.people=kids;
      bucket.other=true;
      mains.sort(function(a,b){ return (b.issue-a.issue)||(b.contract-a.contract)||(b.td-a.td)||(b.visit-a.visit)||a.name.localeCompare(b.name,"ru"); });
      rank.list=mains.concat([bucket]);
      var order=mains.concat([bucket]).concat(kids);
      var total=blank(); total.name="Итого";
      mains.concat(kids).forEach(function(p){ KEYS.forEach(function(k){ total[k]+=p[k]||0; }); });
      order.push(total);
      order.forEach(function(p){ p.active=Math.max(0,(p.contract||0)-(p.issue||0)-(p.cancel||0)); });
      window.__octCancel=order.map(function(p){ return p.cancel||0; });
      window.__octActive=order.map(function(p){ return p.active||0; });
      window.__octPipe=order.map(function(p){ return (p.active||0)+(p.issue||0); });
      window.__octPlan=order.map(function(p){
        if(p.name==="Итого") return 65;
        if(p.name==="Спицын") return 5;
        if(p.other) return 0;
        if(OCT[p.name]) return 10;
        return 0;
      });
    }
    function hook(){
      try{
        if(!document.getElementById("octFit")){
          var st=document.createElement("style");
          st.id="octFit";
          st.textContent=".lb-pair{gap:8px}.lb-pair .lb-block{overflow-x:hidden;padding:8px 6px 4px;min-width:0}.lb-block.e{flex:0.7}.lb-block.f{flex:1.78}.lb-pair .lb-scroll{overflow-x:hidden}.lb-pair .lb-rep{table-layout:fixed;width:100%;font-size:11px}.lb-pair .lb-rep th,.lb-pair .lb-rep td{padding:3px 2px}.lb-pair .lb-rep th{font-size:9px;letter-spacing:0;line-height:1.1}.lb-pair .lb-rep td:first-child,.lb-pair .lb-rep th:first-child{overflow:hidden;text-overflow:ellipsis}";
          (document.head||document.documentElement).appendChild(st);
        }
        if(typeof boardEnsure==="function" && !boardEnsure.__sales){
          var orig=boardEnsure;
          var wrapped=function(){
            return Promise.resolve().then(function(){ return orig(); }).then(function(cache){
              try{
                if(cache && cache.oct && !cache.oct.__sales){
                  cache.oct.forEach(function(r){ if(r) r.issue=0; });
                  SALES.forEach(function(s){
                    cache.oct.push({when:s.when, who:s.who, client:s.client, model:s.model, visit:0, call:0, web:0, meet:0, service:0, td:0, contract:0, issue:1, note:"вкладка Продажи"});
                  });
                  cache.oct.__sales=1;
                }
              }catch(e){}
              return cache;
            });
          };
          wrapped.__sales=1;
          boardEnsure=wrapped;
        }
        if(typeof boardRank==="function" && !boardRank.__oct){
          var origRank=boardRank;
          var wrappedRank=function(rows, roster){
            var rank=origRank(rows, roster);
            try{ if(rank && monthRows(rows) && roster && roster.indexOf("Велиджанов")>=0) applyMonth(rank); }catch(e){}
            return rank;
          };
          wrappedRank.__oct=1;
          boardRank=wrappedRank;
        }
        if(typeof boardReportHtml==="function" && !boardReportHtml.__oct){
          var origRep=boardReportHtml;
          var wrappedRep=function(){
            var html=origRep();
            try{
              html=html.replace("Расторжения в журнале октября не ведутся.","Октябрь снят со скринов 1–7: визиты, звонки и интернет — первичные, без задвоенных. Контракт = действующий резерв + выдача + расторжение. Действующие — резерв, ещё не выдан. Выдачи+К = действующие + выдачи, без расторжений, из них считается прогноз. Оценки и e-credit — из воронки 1–7. Расторжения: Елчин T8, Лавров T9, Сидоров T7.");
              var nums=window.__octCancel||[];
              var act=window.__octActive||[];
              var pipe=window.__octPipe||[];
              var plans=window.__octPlan||[];
              var i=0;
              function paceOf(n, plan){
                var now=new Date();
                var days=new Date(now.getFullYear(), now.getMonth()+1, 0).getDate();
                var passed=Math.min(days, Math.max(1, now.getDate()));
                var f=Math.round((n||0)*days/passed);
                if(!plan) return {n:String(f), p:"–"};
                var v=100*f/plan;
                var s=Math.abs(v-Math.round(v))<0.05?String(Math.round(v)):v.toFixed(1).replace(".",",");
                return {n:String(f), p:s+"%"};
              }
              html=html.replace(/<td>–<\/td><td>–<\/td><td>–<\/td><td>[^<]*<\/td><td>[^<]*<\/td>/g, function(){
                var n=nums[i], a=act[i], k=pipe[i], plan=plans[i];
                i++;
                if(n==null) return "<td>–</td><td>–</td><td>–</td><td>–</td><td>–</td>";
                var pc=paceOf(k||0, plan||0);
                return "<td>"+n+"</td><td>"+(a==null?"–":a)+"</td><td>"+(k==null?"–":k)+"</td><td>"+pc.n+"</td><td>"+pc.p+"</td>";
              });
            }catch(e){}
            return html;
          };
          wrappedRep.__oct=1;
          boardReportHtml=wrappedRep;
        }
      }catch(e){}
    }
    hook();
    var n=0;
    var timer=setInterval(function(){ hook(); if(++n>20) clearInterval(timer); }, 300);
    setTimeout(function(){ try{ if(typeof boardLoad==="function") boardLoad(); }catch(e){} }, 500);
  }catch(e){}
})();
