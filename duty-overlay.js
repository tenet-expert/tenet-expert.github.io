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
