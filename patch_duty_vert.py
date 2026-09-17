#!/usr/bin/env python3
"""Stack duty checklist PDF and print layout vertically."""
from pathlib import Path
import re

PDF = r'''    function dutyPdf(src){
      const d=src||dutyRead();
      const p=dutyCount(d);
      const pct=p.tot?Math.round(p.on*100/p.tot):0;
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
      ctx.fillText((d.manager||"—")+"  ·  "+(d.date||dutyToday())+"  ·  "+pct+"%  ·  "+p.on+" из "+p.tot, pad+46, pad+52);
      let y=pad+78;
      const carH=198;
      DUTY_CARS.forEach((car)=>{
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
          ["Багажник", !!d[car.id+"_trunk"]],
        ];
        rows.forEach((row,ri)=>{
          const col=ri%2;
          const line=Math.floor(ri/2);
          const cx=pad+20+col*((inner-40)/2);
          const cy=y+72+line*36;
          tick(cx, cy, row[1]);
          ctx.fillStyle="#111"; ctx.font="500 17px Inter, Arial, sans-serif";
          ctx.fillText(row[0], cx+28, cy);
        });
        ctx.fillStyle="#5c5346"; ctx.font="600 16px Inter, Arial, sans-serif";
        const meta="Кузов: "+dutyBodyWord(d[car.id+"_body"]||"ok")+"     Пробег: "+(d[car.id+"_km"]||"—")+"     Топливо: "+(d[car.id+"_fuel"]?d[car.id+"_fuel"]+"%":"—");
        ctx.fillText(meta, pad+20, y+176);
        y+=carH+12;
      });
      function block(title, keys){
        const rows=Math.ceil(keys.length/3);
        const h=54+rows*40;
        ctx.fillStyle="#f7f1e7";
        roundRect(pad, y, inner, h, 14); ctx.fill();
        ctx.strokeStyle="#eadfcf"; ctx.lineWidth=1;
        roundRect(pad, y, inner, h, 14); ctx.stroke();
        ctx.fillStyle="#111"; ctx.font="800 20px Inter, Arial, sans-serif";
        ctx.fillText(title, pad+20, y+32);
        keys.forEach((pair,i)=>{
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
      const w=window.open("");
      if(!w) return;
      const name="checklist-"+(d.date||dutyToday()).replace(/\./g,"-");
      w.document.write("<title>"+name+"</title><style>@page{size:A4 portrait;margin:8mm}html,body{margin:0;background:#fff}img{width:100%;max-width:100%;display:block}</style><img src='"+c.toDataURL("image/png")+"' />");
      w.document.close();
      setTimeout(()=>{ try{ w.print(); }catch(e){} }, 400);
    }
'''

def fix(html: str) -> str:
    if "function dutyPdf(src){" in html:
        html, n = re.subn(
            r"    function dutyPdf\(src\)\{[\s\S]*?\n    function dutyRead\(",
            lambda _m: PDF + "    function dutyRead(",
            html,
            count=1,
        )
        print("dutyPdf replaced", n)
    html = html.replace(
        ".cl-cars{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}",
        ".cl-cars{display:grid;grid-template-columns:1fr;gap:8px}",
    )
    html = html.replace(
        "@media (max-width:1100px){.cl-cars{grid-template-columns:repeat(3,minmax(0,1fr))}}",
        "@media (min-width:900px){.cl-cars{grid-template-columns:1fr 1fr}}",
    )
    html = html.replace(
        "@media (max-width:720px){.cl-cars{grid-template-columns:1fr 1fr}}",
        "@media (min-width:1280px){.cl-cars{grid-template-columns:repeat(3,minmax(0,1fr))}}",
    )
    html = html.replace(
        ".cl-foot{display:grid;grid-template-columns:1fr 1fr;gap:8px}",
        ".cl-foot{display:grid;grid-template-columns:1fr;gap:8px}",
    )
    html = html.replace(
        ".cl-cars{grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:4px}",
        ".cl-cars{grid-template-columns:1fr!important;gap:6px}",
    )
    return html

def main():
    for p in (Path("_site/index.html"), Path("index.html"), Path("TENET_T4L_netlify/index.html")):
        if not p.exists() or p.stat().st_size < 10000:
            continue
        html = p.read_text(encoding="utf-8")
        out = fix(html)
        p.write_text(out, encoding="utf-8")
        print("patched", p, p.stat().st_size, "vertical", "const carH=198" in out)

if __name__ == "__main__":
    main()
