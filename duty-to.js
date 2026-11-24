/* ТО тестовых авто в чек-листе дежурного.
   График правится в одном массиве DUTY_TO_SCHEDULE: окончание VIN и дата срока.
   Даты — календарь Europe/Samara (UTC+4).
   За 2 дня до срока показывается один пункт, в день срока — три галочки,
   на следующий день пункты пропадают.
   Проверка с подменой даты: ?dutyDate=2026-11-29 или window.__dutyDateOverride. */
(function(){
  var DUTY_TO_SCHEDULE = [
    { suffix: "110108", due: "2026-11-29" },
    { suffix: "109064", due: "2026-11-29" },
    { suffix: "092948", due: "2026-12-02" },
    { suffix: "040024", due: "2026-12-10" }
  ];

  /* Полные VIN и модели — из склада (stock.json на 29.09–01.10.2026 и patch_stock_src.py).
     В текущем stock.json демо-VIN вырезаны, поэтому подписи лежат здесь.
     plus: false — чек-лист TENET, не TENET+. */
  var DUTY_TO_KNOWN = {
    "110108": { vin: "EDXGB32B0TE110108", model: "T8 Прайм 5 мест 2WD", plus: false },
    "109064": { vin: "EDXGD34B2TE109064", model: "T8 Прайм 7 мест 4WD", plus: false },
    "092948": { vin: "EDEHD24B9TE092948", model: "T9 Ультра 4WD", plus: false },
    "040024": { vin: "EDXDC24B0TG040024", model: "A8 2.0T 8AT Ultra", plus: false }
  };

  var DUE_ITEMS = [
    { key: "done", label: "ТО проведено?" },
    { key: "set", label: "Проверить все настройки и звуки, не сбросились ли" },
    { key: "tire", label: "Проверить давление в шинах" }
  ];

  try {
    var q = new URLSearchParams(location.search).get("dutyDate");
    if (q && /^\d{4}-\d{2}-\d{2}$/.test(q)) window.__dutyDateOverride = q;
  } catch (e) {}

  function pad(n){ return String(n).padStart(2, "0"); }

  function dutyToISO(){
    var o = window.__dutyDateOverride;
    if (o && /^\d{4}-\d{2}-\d{2}$/.test(String(o))) return String(o);
    try {
      var s = new Intl.DateTimeFormat("en-CA", {
        timeZone: "Europe/Samara",
        year: "numeric",
        month: "2-digit",
        day: "2-digit"
      }).format(new Date());
      if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;
    } catch (e) {}
    var t = new Date(Date.now() + 4 * 60 * 60 * 1000);
    return t.getUTCFullYear() + "-" + pad(t.getUTCMonth() + 1) + "-" + pad(t.getUTCDate());
  }

  function dutyToToday(){
    var p = dutyToISO().split("-");
    return p[2] + "." + p[1] + "." + p[0].slice(-2);
  }

  function addDays(iso, days){
    var p = iso.split("-");
    var t = Date.UTC(+p[0], +p[1] - 1, +p[2]) + days * 86400000;
    var d = new Date(t);
    return d.getUTCFullYear() + "-" + pad(d.getUTCMonth() + 1) + "-" + pad(d.getUTCDate());
  }

  function phaseOf(due, today){
    var start = addDays(due, -2);
    if (today < start) return "";
    if (today < due) return "soon";
    if (today === due) return "due";
    return "";
  }

  function esc(s){
    return String(s == null ? "" : s).replace(/[&<>"']/g, function(m){
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m];
    });
  }

  function lists(){
    var out = [];
    if (Array.isArray(window.__dutyStock)) out.push(window.__dutyStock);
    if (Array.isArray(window.__dutyStockFile)) out.push(window.__dutyStockFile);
    return out;
  }

  function isPlusCar(c){
    var brand = String(c && c.brand || "").toUpperCase().replace(/Ё/g, "Е");
    var model = String(c && (c.model || c.name) || "").toUpperCase().replace(/Ё/g, "Е").replace(/\s+/g, "");
    if (brand.indexOf("TENET") >= 0 && (brand.indexOf("+") >= 0 || brand.indexOf("PLUS") >= 0 || brand.indexOf("ПЛЮС") >= 0)) return true;
    if (model === "PL4" || model === "PL6" || model === "L4" || model === "L6") return true;
    return false;
  }

  function modelOf(c, fallback){
    var name = String(c && (c.name || c.model) || "").trim();
    var trim = String(c && c.trim || "").trim();
    var left = [name, trim].filter(Boolean).join(" ");
    return left || fallback || "модель не найдена в данных";
  }

  function resolve(suffix){
    var known = DUTY_TO_KNOWN[suffix] || null;
    var hits = [];
    lists().forEach(function(list){
      list.forEach(function(c){
        var vin = String(c && c.vin || "").toUpperCase();
        if (vin && vin.slice(-String(suffix).length) === String(suffix)) hits.push(c);
      });
    });
    var hit = null;
    if (known) {
      hits.forEach(function(c){
        if (String(c.vin || "").toUpperCase() === known.vin) hit = c;
      });
    }
    if (!hit && hits.length === 1) hit = hits[0];
    if (hit) {
      return {
        vin: String(hit.vin).toUpperCase(),
        model: modelOf(hit, known && known.model),
        plus: isPlusCar(hit),
        missing: false
      };
    }
    if (known) return { vin: known.vin, model: known.model, plus: !!known.plus, missing: false };
    return { vin: "…" + suffix, model: "модель не найдена в данных", plus: false, missing: true };
  }

  function active(plus){
    var today = dutyToISO();
    var out = [];
    DUTY_TO_SCHEDULE.forEach(function(row){
      var phase = phaseOf(row.due, today);
      if (!phase) return;
      var car = resolve(row.suffix);
      if (!!car.plus !== !!plus) return;
      out.push({
        suffix: String(row.suffix),
        due: row.due,
        phase: phase,
        vin: car.vin,
        model: car.model,
        missing: !!car.missing
      });
    });
    return out;
  }

  function soonLabel(r){
    return "Провести ТО на тестовом авто (" + r.vin + ", " + r.model + ")";
  }

  function cardsOf(plus){
    return active(!!plus).map(function(r){
      var lines = r.phase === "soon"
        ? [{ label: soonLabel(r), key: "to_" + r.suffix + "_soon", tall: true }]
        : DUE_ITEMS.map(function(it){
            return { label: it.label, key: "to_" + r.suffix + "_" + it.key };
          });
      return { title: r.model, sub: r.vin, lines: lines };
    });
  }

  function cardH(card){
    var h = 16 + 22 + 16;
    (card.lines || []).forEach(function(line){ h += line.tall ? 42 : 28; });
    return h + 12;
  }

  function blockHeight(cards){
    if (!cards.length) return 0;
    var h = 28;
    for (var i = 0; i < cards.length; i += 2) {
      var a = cardH(cards[i]);
      var b = cards[i + 1] ? cardH(cards[i + 1]) : 0;
      h += Math.max(a, b) + 14;
    }
    return h;
  }

  function layout(plus){
    var cards = cardsOf(plus);
    var lines = [];
    cards.forEach(function(card){
      lines.push({ head: true, label: card.sub + " · " + card.title });
      card.lines.forEach(function(line){ lines.push(line); });
    });
    return { lines: lines, cards: cards, height: blockHeight(cards) };
  }

  function keys(plus){
    var ks = [];
    cardsOf(plus).forEach(function(card){
      card.lines.forEach(function(line){ if (line.key) ks.push(line.key); });
    });
    return ks;
  }

  function tri(v){
    if (v === "ok" || v === "bad") return v;
    if (v === true || v === "true") return "ok";
    if (v === "no") return "bad";
    return "";
  }

  function splitLabel(label, maxChars){
    var s = String(label || "");
    if (s.length <= maxChars) return [s];
    var cut = s.lastIndexOf(" ", maxChars);
    if (cut < 12) cut = maxChars;
    var a = s.slice(0, cut).trim();
    var b = s.slice(cut).trim();
    if (b.length > maxChars) b = b.slice(0, Math.max(1, maxChars - 1)) + "…";
    return [a, b];
  }

  function paintItem(ctx, rr, x, y, w, label, raw, tall){
    var maxChars = Math.max(18, Math.floor((w - 70) / 7.2));
    var parts = tall ? splitLabel(label, maxChars) : [String(label || "")];
    var h = tall ? 42 : 28;
    var st = tri(raw);
    if (st && rr) {
      ctx.fillStyle = st === "bad" ? "#ff8a80" : "#e8f5e9";
      rr(x, y, w, h - 4, 7);
      ctx.fill();
    }
    ctx.fillStyle = st === "bad" ? "#7f0000" : "#1c1a17";
    ctx.font = "500 13px Inter, Arial, sans-serif";
    ctx.textAlign = "left";
    parts.forEach(function(line, i){
      ctx.fillText(line, x + 8, y + 16 + i * 16);
    });
    function mark(mx, kind, on){
      if (!rr) return;
      rr(mx, y + 4, 18, 18, 4);
      if (on) {
        ctx.fillStyle = kind === "ok" ? "#2e7d32" : "#c62828";
        ctx.fill();
        ctx.fillStyle = "#fff";
        ctx.font = "800 13px Inter, Arial, sans-serif";
        ctx.fillText(kind === "ok" ? "✓" : "×", mx + (kind === "ok" ? 3 : 4), y + 18);
      } else {
        ctx.strokeStyle = kind === "ok" ? "#2e7d32" : "#c62828";
        ctx.lineWidth = 1.4;
        ctx.stroke();
      }
    }
    mark(x + w - 46, "ok", st === "ok");
    mark(x + w - 24, "bad", st === "bad");
  }

  function paintCard(ctx, panel, rr, card, data, x, y, w, h){
    if (typeof panel === "function") panel(x, y, w, h);
    ctx.fillStyle = "#161618";
    ctx.font = "800 16px Inter, Arial, sans-serif";
    ctx.textAlign = "left";
    ctx.fillText(String(card.title || ""), x + 16, y + 28);
    ctx.fillStyle = "#6d6458";
    ctx.font = "600 12px ui-monospace, Menlo, Consolas, monospace";
    ctx.fillText(String(card.sub || ""), x + 16, y + 46);
    var iy = y + 58;
    (card.lines || []).forEach(function(line){
      paintItem(ctx, rr, x + 14, iy, w - 28, line.label, data[line.key], !!line.tall);
      iy += line.tall ? 42 : 28;
    });
  }

  function dutyToPaint(ctx, opt){
    opt = opt || {};
    var lay = layout(!!opt.plus);
    if (!lay.cards.length) return 0;
    var x0 = opt.x || 0;
    var y = opt.y || 0;
    var w = opt.w || 600;
    var gap = 14;
    var data = opt.data || {};
    var y0 = y;
    ctx.fillStyle = "#8a7d6e";
    ctx.font = "800 13px Inter, Arial, sans-serif";
    ctx.textAlign = "left";
    ctx.fillText("ТО ТЕСТОВЫХ АВТО", x0, y + 14);
    y += 28;
    var colW = (w - gap) / 2;
    for (var i = 0; i < lay.cards.length; i += 2) {
      var left = lay.cards[i];
      var right = lay.cards[i + 1] || null;
      var h = Math.max(cardH(left), right ? cardH(right) : 0);
      paintCard(ctx, opt.panel, opt.rr, left, data, x0, y, colW, h);
      if (right) paintCard(ctx, opt.panel, opt.rr, right, data, x0 + colW + gap, y, colW, h);
      y += h + gap;
    }
    return y - y0;
  }

  function ensureCss(){
    if (document.getElementById("dutyToCss")) return;
    var st = document.createElement("style");
    st.id = "dutyToCss";
    st.textContent = [
      ".cl-to{margin:2px 0 10px}",
      ".cl-to-grid{display:grid;grid-template-columns:1fr;gap:8px}",
      "@media (min-width:700px){.cl-to-grid{grid-template-columns:1fr 1fr}}",
      ".cl-to-card h3{margin:0 0 2px}",
      ".cl-to-vin{margin:0 0 8px;font:600 11px/1.3 ui-monospace,Menlo,Consolas,monospace;color:#6d6458;word-break:break-all}",
      ".cl-to .cl-lab{white-space:normal;line-height:1.3}",
      "@media print{",
      ".cl-to-grid{display:grid!important;grid-template-columns:1fr 1fr!important;gap:2.5mm!important}",
      ".cl-to-card{break-inside:avoid;page-break-inside:avoid}",
      "}"
    ].join("");
    document.head.appendChild(st);
  }

  function section(d, plus, dutyItem){
    var list = active(!!plus);
    if (!list.length || typeof dutyItem !== "function") return "";
    ensureCss();
    var data = d || {};
    var blocks = list.map(function(r){
      var body = r.phase === "soon"
        ? dutyItem("to_" + r.suffix + "_soon", esc(soonLabel(r)), data["to_" + r.suffix + "_soon"])
        : DUE_ITEMS.map(function(it){
            return dutyItem("to_" + r.suffix + "_" + it.key, esc(it.label), data["to_" + r.suffix + "_" + it.key]);
          }).join("");
      return "<article class=\"cl-car cl-to-card\">" +
        "<h3>" + esc(r.model) + "</h3>" +
        "<p class=\"cl-to-vin\">" + esc(r.vin) + "</p>" +
        body + "</article>";
    }).join("");
    return "<section class=\"cl-sec cl-to\" data-to-n=\"" + list.length + "\">" +
      "<h2 class=\"cl-sec-title\">ТО тестовых авто</h2>" +
      "<div class=\"cl-to-grid\">" + blocks + "</div></section>";
  }

  window.DUTY_TO_SCHEDULE = DUTY_TO_SCHEDULE;
  window.dutyToISO = dutyToISO;
  window.dutyToToday = dutyToToday;
  window.dutyToLayout = layout;
  window.dutyToKeys = keys;
  window.dutyToSection = section;
  window.dutyToPaint = dutyToPaint;
})();
