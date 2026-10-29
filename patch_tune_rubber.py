#!/usr/bin/env python3
"""Keep TUNE_RUBBER tire texts in sync with Drive «Резина Чери.xlsx» (лист Chery)
and TUNE_DO (доп. оборудование) with Drive «Прайс тюнинг.xlsx» (лист Чери)."""
from pathlib import Path

A = "&"  # entity prefix built at runtime so transport layers cannot decode it
ESC_GOOD = ('({"&":"' + A + 'amp;","<":"' + A + 'lt;",">":"' + A + 'gt;","\\"":"'
            + A + 'quot;","\'":"' + A + '#39;"}[m])')
ESC_BAD = '({"&":"&","<":"<",">":">","\\"":""","\'":"' + A + '#39;"}[m])'

# (old, new) pairs; each applied once, idempotent.
PAIRS = [
    (ESC_BAD, ESC_GOOD),
    ('["235/55 R19",15750,63000,"0 · под заказ"]',
     '["235/55 R19",15750,63000,"0 · под заказ 3 раб дня"]'),
    ('["Royal Black Royalstud II 235/50 R19 103T шип",15500,62000,"1"]',
     '["Royal Black Royalstud II 235/50 R19 103T, шип.",15500,62000,"1"]'),
    ('["Hankook 235/55R18 100T Winter I*cept X RW10 TL",15500,62000,"1"]',
     '["Автошина 235/55 R18 Tracmax 104T XL X-Privilo S500 TL (шип.)",12500,50000,"3"]'),
    # Drive 12.10.2026: T9 R20 Fortune в наличии 2
    ('["T9 R20",[["Fortune 245/50R20 105T Polaro Ice TL, 230 шип.",15500,62000,"1"]]]',
     '["T9 R20",[["Fortune 245/50R20 105T Polaro Ice TL, 230 шип.",15500,62000,"2"]]]'),
    # Drive 12.10.2026: Arrizo R17 + Hankook 225/45R18
    ('["Arrizo R17",[["Pirelli Formula 215/50R17 95T XL Ice TL, шип.",11100,44400,"1"]]]',
     '["Arrizo R17",[["Автошина Hankook 225/45R18 95T XL Winter i*Pike RS2 W429 TL (шип.)",18500,74000,"1"],["Pirelli Formula 215/50R17 95T XL Ice TL, шип.",11100,44400,"1"]]]'),
    # Drive 14.10.2026: шиномонтаж комплексный R16 6800, R17-R19 8000, R20 10600
    ('mount:[["R16",5300],["R17, R18, R19",6300],["R20",8600]]',
     'mount:[["R16",6800],["R17, R18, R19",8000],["R20",10600]]'),
    # Drive 16.10.2026: новые Ikon Tyres в T8 R19, T8 R18, T7 R18, T4L (группа «T4L / L6»)
    ('["T8 R19",[["Royal Black Royalstud II 235/50 R19 103T, шип.",15500,62000,"1"],["Fortune 235/50R19 103T Polaro Ice TL, шип.",15500,62000,"2"]]]',
     '["T8 R19",[["Royal Black Royalstud II 235/50 R19 103T, шип.",15500,62000,"1"],["Автошина Ikon Tyres 235/50 R19 103T XL Autograph Snow 3 SUV TL",21000,84000,"2"],["Fortune 235/50R19 103T Polaro Ice TL, шип.",15500,62000,"2"]]]'),
    ('["T8 R18",[["Pirelli Formula 235/55 R18 104T XL Ice TL, шип.",15500,62000,"1"],["Автошина 235/55 R18 Tracmax 104T XL X-Privilo S500 TL (шип.)",12500,50000,"3"]]]',
     '["T8 R18",[["Pirelli Formula 235/55 R18 104T XL Ice TL, шип.",15500,62000,"1"],["Автошина Ikon Tyres 235/55R18 104T XL Character Ice 7 SUV TL (шип.)",17500,70000,"2"],["Автошина 235/55 R18 Tracmax 104T XL X-Privilo S500 TL (шип.)",12500,50000,"3"]]]'),
    ('["T7 R18",[["Pirelli Formula 225/55 R18 102T XL Ice TL, шип.",14500,58000,"2"]',
     '["T7 R18",[["Автошина Ikon Tyres 225/55 R18 Ikon Character Ice 7 SUV 102T XL (шип.)",16000,64000,"3"],["Pirelli Formula 225/55 R18 102T XL Ice TL, шип.",14500,58000,"2"]'),
    ('["T4L",[["Fortune 225/60 R18 104T Polaro Ice TL, шип.",12000,48000,"2"],["Pirelli Formula 225/60 R18 104T XL Ice TL, шип.",15500,62000,"1"]]]',
     '["T4L / L6",[["Fortune 225/60 R18 104T Polaro Ice TL, шип.",12000,48000,"2"],["Pirelli Formula 225/60 R18 104T XL Ice TL, шип.",15500,62000,"1"],["Автошина 225/60 R18 Ikon 104T XL Character Ice 7 SUV TL /шипованная/",16000,64000,"3"]]]'),
    # Drive 20.10.2026: T9 R19 — Fortune 105T в наличии 1 (вместо «под заказ 3 раб дня»)
    ('["235/55 R19",15750,63000,"0 · под заказ 3 раб дня"]',
     '["Автошина 235/55 R19 Fortune 105T Polaro Ice TL (шип.)",14000,56000,"1"]'),
    # Drive 20.10.2026: шиномонтаж комплексный R17-R19 8300
    ('mount:[["R16",6800],["R17, R18, R19",8000],["R20",10600]]',
     'mount:[["R16",6800],["R17, R18, R19",8300],["R20",10600]]'),
    # Drive 20.10.2026: позиций «без цены» в файле больше нет
    ('notes:["Допускается на T4L резина от T7 R18 225/55.","В файле от 29.09 без цены: Fortune 225/55R19 103T Polaro Ice TL, 230 шип.","Sailun RoadX 225/55R18 98T RXFrost WH12 TL, 102 шип."]',
     'notes:["Допускается на T4L резина от T7 R18 225/55."]'),
    # Drive 21.10.2026: T8 R19 Ikon Autograph Snow 3 — «липучка» в названии
    ('["Автошина Ikon Tyres 235/50 R19 103T XL Autograph Snow 3 SUV TL",21000,84000,"2"]',
     '["Автошина Ikon Tyres 235/50 R19 103T XL Autograph Snow 3 SUV TL лип",21000,84000,"2"]'),
    # Drive 21.10.2026: T7 R18 Sailun RoadX 12 500 / 50 000
    ('["Sailun RoadX 225/55 R18 98T RXFrost WH12 TL, шип.",11000,44000,"2"]',
     '["Sailun RoadX 225/55 R18 98T RXFrost WH12 TL, шип.",12500,50000,"2"]'),
    # Drive 21.10.2026: T7 R19 / L6 Tracmax в наличии 2
    ('["Tracmax 225/55 R19 103T XL X-Privilo S500 TL, шип.",15500,62000,"4"]',
     '["Tracmax 225/55 R19 103T XL X-Privilo S500 TL, шип.",15500,62000,"2"]'),
    # Drive 21.10.2026: T4L / L6 Fortune 12 500 / 50 000
    ('["Fortune 225/60 R18 104T Polaro Ice TL, шип.",12000,48000,"2"]',
     '["Fortune 225/60 R18 104T Polaro Ice TL, шип.",12500,50000,"2"]'),
    # Drive 21.10.2026: T4 R17 / L4 — Lanvigator Ice Spider II убран из файла
    ('["T4 R17 / L4",[["Fortune 215/60R17 100T Polaro Ice TL, шип.",11000,44000,"3"],["Formula Ice Friction 215/60 R17 100T XL, липучка",9600,38400,"1"],["Lanvigator Ice Spider II 215/60 R17 100T шип XL",13500,54000,"1"]]]',
     '["T4 R17 / L4",[["Fortune 215/60R17 100T Polaro Ice TL, шип.",11000,44000,"3"],["Formula Ice Friction 215/60 R17 100T XL, липучка",9600,38400,"1"]]]'),
    # Drive 22.10.2026: T4L / L6 — Fortune 225/60 R18 убран из файла
    ('["T4L / L6",[["Fortune 225/60 R18 104T Polaro Ice TL, шип.",12500,50000,"2"],["Pirelli Formula 225/60 R18',
     '["T4L / L6",[["Pirelli Formula 225/60 R18'),
    # Drive 22.10.2026: шиномонтаж комплексный R16 5600, R17-R19 6600, R20 8600
    ('mount:[["R16",6800],["R17, R18, R19",8300],["R20",10600]]',
     'mount:[["R16",5600],["R17, R18, R19",6600],["R20",8600]]'),
]

# Drive «Прайс тюнинг.xlsx» 19.10.2026: колонки L4 / L6 (TENET PLUS) в TUNE_DO.
# Блок меняется целиком, чтобы не получить таблицу с разным числом столбцов.
TUNE_DO_OLD = """    const TUNE_COLS = ["Tiggo 7 Pro","Tiggo 8 Pro","Arrizo","Tiggo 9"];
    const TUNE_DO = [
      ["Защита",[
        ["Защита картера, КПП, приводного ремня",20600,null,null,null],
        ["Защита картера",null,9600,10841,13000],
        ["Защита радиатора (сетка)",13550,13550,12275,15300],
        ["Подкрылки задние",14520,14697,12500,null],
        ["Подкрылки передние",14260,14697,13300,null],
        ["Брызговики задние",4511,4225,4041,4600],
        ["Брызговики передние",4511,4225,4041,4600],
        ["Накладки на арки",4200,null,null,null]
      ]],
      ["Антишум / антикор",[
        ["Антикор/антишум, колёсные арки",19750,19750,16250,null],
        ["Антикор/антишум, арки и днище",33500,37400,33830,37400]
      ]],
      ["Ковры",[
        ["Ковры в салон",6388,5280,4907,7200],
        ["Ковры в багажник с фартуком",5269,null,null,null],
        ["Ковры в багажник складные",null,4600,null,null],
        ["Ковры в багажник",3875,3250,3100,4000]
      ]],
      ["Тонирование",[
        ["Тонирование задней части а/м",15000,15000,15000,16000]
      ]],
      ["Охранные системы",[
        ["Автосигнализация CESAR",55800,55800,null,null],
        ["Телематическая система S9",56000,null,null,null],
        ["Автосигнализация Starline S9",null,null,56000,null]
      ]]
    ];"""
TUNE_DO_NEW = """    const TUNE_COLS = ["Tiggo 7 Pro","Tiggo 8 Pro","Arrizo","Tiggo 9","L4","L6"];
    const TUNE_DO = [
      ["Защита",[
        ["Защита картера, КПП, приводного ремня",20600,null,null,null,null,null],
        ["Защита картера",9700,9600,10841,13000,8500,9700],
        ["Защита радиатора (сетка)",13550,13550,15300,15300,13550,13550],
        ["Защита бака 2WD",9600,null,null,null,null,8500],
        ["Защита бака 4WD",null,10400,null,10800,null,null],
        ["Подкрылки задние",14520,14697,12500,null,null,null],
        ["Подкрылки передние",14260,14697,13300,null,null,null],
        ["Брызговики задние",4511,4225,4041,4600,3600,3600],
        ["Брызговики передние",4511,4225,4041,4600,3600,3600],
        ["Накладки на арки",4200,null,null,null,null,null]
      ]],
      ["Антишум / антикор",[
        ["Антикор/антишум, колёсные арки",19750,19750,16250,null,19750,19750],
        ["Антикор/антишум, арки и днище",33500,37400,33830,37400,33500,33500]
      ]],
      ["Ковры",[
        ["Ковры в салон",6388,5280,4907,7200,3700,3700],
        ["Ковры в багажник с фартуком",5269,null,null,null,null,null],
        ["Ковры в багажник складные",null,4600,null,null,null,null],
        ["Ковры в багажник",3875,3250,4700,4000,1500,1500]
      ]],
      ["Тонирование",[
        ["Тонирование задней части а/м",15000,15000,15000,16000,15000,15000]
      ]],
      ["Охранные системы",[
        ["Автосигнализация CESAR",55800,55800,null,null,null,null],
        ["Телематическая система S9",56000,null,null,null,null,null],
        ["Автосигнализация Starline S9",null,null,56000,null,null,null]
      ]]
    ];"""
PAIRS += [
    (TUNE_DO_OLD, TUNE_DO_NEW),
    ('Столбец Tiggo 9 — это Tenet T9 из прайса. Прочерк',
     'Столбец Tiggo 9 — это Tenet T9 из прайса. L4 и L6 — TENET PLUS L4 / L6. Прочерк'),
]

# Drive 27.10.2026: убраны «Автошина» в названиях Ikon, убран Fortune T7 R18, T4 R17 / L4 — Triangle вместо Fortune, Formula Ice переименован
PAIRS += [
    ('["Автошина Ikon Tyres 235/50 R19 103T XL Autograph Snow 3 SUV TL лип",',
     '["Ikon Tyres 235/50 R19 103T XL Autograph Snow 3 SUV TL лип",'),
    ('["Автошина Ikon Tyres 225/55 R18 Ikon Character Ice 7 SUV 102T XL (шип.)",',
     '["Ikon Tyres 225/55 R18 Ikon Character Ice 7 SUV 102T XL (шип.)",'),
    ('["Sailun RoadX 225/55 R18 98T RXFrost WH12 TL, шип.",12500,50000,"2"],["Fortune 225/55R18 102T Polaro Ice TL, 220 шип.",11500,46000,"1"]]]',
     '["Sailun RoadX 225/55 R18 98T RXFrost WH12 TL, шип.",12500,50000,"2"]]]'),
    ('["Автошина 225/60 R18 Ikon 104T XL Character Ice 7 SUV TL /шипованная/",',
     '["225/60 R18 Ikon 104T XL Character Ice 7 SUV TL /шипованная/",'),
    ('["T4 R17 / L4",[["Fortune 215/60R17 100T Polaro Ice TL, шип.",11000,44000,"3"],["Formula Ice Friction 215/60 R17 100T XL, липучка",9600,38400,"1"]]]',
     '["T4 R17 / L4",[["Triangle 215/60R17 100T XL IcelynX TI501 TL M+S 3PMSF (шип.)",11500,46000,"2"],["Formula Ice 215/60 17  липучка",9600,38400,"1"]]]'),
]

# Drive 29.10.2026: T4L / L6 — Triangle TRIN PL01 липучка вместо Pirelli Formula 225/60 R18; шиномонтаж R16 6600, R17-R19 7250, R20 9850
PAIRS += [
    ('["T4L / L6",[["Pirelli Formula 225/60 R18 104T XL Ice TL, шип.",15500,62000,"1"],',
     '["T4L / L6",[["Автошины Triangle TRIN PL01 225/60 R18 104R липучка",11500,46000,"2"],'),
    ('mount:[["R16",5600],["R17, R18, R19",6600],["R20",8600]]',
     'mount:[["R16",6600],["R17, R18, R19",7250],["R20",9850]]'),
]

def patch(path: Path) -> bool:
    if not path.exists():
        return False
    t = path.read_text(encoding="utf-8")
    orig = t
    for old, new in PAIRS:
        if new in t:
            print(path, "already:", new[:50])
        elif old in t:
            t = t.replace(old, new, 1)
            print(path, "patched:", new[:50])
        else:
            print(path, "not found:", old[:50])
    if t != orig:
        path.write_text(t, encoding="utf-8")
        return True
    return False

def main():
    changed = False
    for p in (Path("index.html"), Path("_site/index.html")):
        changed = patch(p) or changed
    if not changed:
        print("no file changed")

if __name__ == "__main__":
    main()
