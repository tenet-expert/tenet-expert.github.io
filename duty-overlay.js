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
    const d=src||(typeof dutyRead==="function"?dutyRead():{});
    const p=typeof dutyCount==="function"?dutyCount(d):{on:0,tot:0};
    const pct=p.tot?Math.round(p.on*100/p.tot):0;
    const cars=(typeof DUTY_CARS!=="undefined")?DUTY_CARS:[
      {id:"t4l",title:"TENET T4L"},{id:"t8",title:"TENET T8"},{id:"a8",title:"Arrizo 8"},
      {id:"t7",title:"TENET T7"},{id:"t9",title:"Tiggo 9"}
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
        ctx.fillText("✓", x+2, y);
      }
    }
    const bodyWord=(typeof dutyBodyWord==="function")?dutyBodyWord:function(v){ return v==="pm"?"±":v==="no"?"грязный":"чистый"; };
    const today=(typeof dutyToday==="function")?dutyToday():"";
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
    ctx.fillText((d.manager||"—")+"  ·  "+(d.date||today)+"  ·  "+pct+"%  ·  "+p.on+" из "+p.tot, pad+46, pad+52);
    let y=pad+70;
    function fitText(s, maxW){
      s=String(s||"").replace(/\s+/g," ").trim();
      if(!s) return "—";
      if(ctx.measureText(s).width<=maxW) return s;
      let out=s;
      while(out.length>1 && ctx.measureText(out+"…").width>maxW) out=out.slice(0,-1);
      return out+"…";
    }
    ctx.fillStyle="#8a7d6e"; ctx.font="800 13px Inter, Arial, sans-serif";
    ctx.fillText("ТЕСТОВЫЕ АВТОМОБИЛИ", pad, y);
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
        ["Омывающая", !!d[car.id+"_wash"]],
        ["Коврики и пороги", !!d[car.id+"_mats"]],
        ["Нет ошибок", !!d[car.id+"_err"]],
        ["Нет пыли", !!d[car.id+"_dust"]],
        ["Багажник", !!d[car.id+"_trunk"]]
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
      const meta="Кузов: "+bodyWord(d[car.id+"_body"]||"ok")+"     Пробег: "+(d[car.id+"_km"]||"—")+"     Топливо: "+(d[car.id+"_fuel"]?d[car.id+"_fuel"]+"%":"—");
      ctx.fillText(meta, pad+20, y+168);
      ctx.fillStyle="#fff";
      roundRect(pad+16, y+178, inner-32, 26, 6);
      ctx.fill();
      ctx.strokeStyle="#eadfcf"; ctx.lineWidth=1;
      roundRect(pad+16, y+178, inner-32, 26, 6);
      ctx.stroke();
      ctx.fillStyle="#8a7d6e"; ctx.font="500 14px Inter, Arial, sans-serif";
      ctx.fillText("Примечание: "+fitText(d[car.id+"_note"], inner-130), pad+24, y+196);
      y+=carH+10;
    });
    y+=8;
    ctx.fillStyle="#8a7d6e"; ctx.font="800 13px Inter, Arial, sans-serif";
    ctx.fillText("САЛОН", pad, y);
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
  };
})();
