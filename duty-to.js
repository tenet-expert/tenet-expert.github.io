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

  function layout(plus){
    var lines = [];
    active(!!plus).forEach(function(r){
      if (r.phase === "soon") {
        lines.push({ label: soonLabel(r), key: "to_" + r.suffix + "_soon" });
        return;
      }
      lines.push({ head: true, label: r.vin + " · " + r.model });
      DUE_ITEMS.forEach(function(it){
        lines.push({ label: it.label, key: "to_" + r.suffix + "_" + it.key });
      });
    });
    var height = 0;
    if (lines.length) {
      height = 40;
      lines.forEach(function(line){ height += line.head ? 22 : 28; });
      height += 16;
    }
    return { lines: lines, height: height };
  }

  function keys(plus){
    var ks = [];
    layout(plus).lines.forEach(function(line){
      if (line.key) ks.push(line.key);
    });
    return ks;
  }

  function ensureCss(){
    if (document.getElementById("dutyToCss")) return;
    var st = document.createElement("style");
    st.id = "dutyToCss";
    st.textContent = [
      ".cl-to{margin:2px 0 10px}",
      ".cl-to .cl-box{display:block}",
      ".cl-to-car{padding:8px 0 2px;border-top:1px solid #eadfcf}",
      ".cl-to-car:first-child{border-top:0;padding-top:0}",
      ".cl-to-car b{display:block;margin:0 0 4px;font:700 13px/1.35 Inter,Arial,sans-serif;color:#1c1a17}",
      ".cl-to .cl-lab{white-space:normal;line-height:1.3}"
    ].join("");
    document.head.appendChild(st);
  }

  function section(d, plus, dutyItem){
    var list = active(!!plus);
    if (!list.length || typeof dutyItem !== "function") return "";
    ensureCss();
    var data = d || {};
    var blocks = list.map(function(r){
      if (r.phase === "soon") {
        return "<div class=\"cl-to-car\">" + dutyItem("to_" + r.suffix + "_soon", esc(soonLabel(r)), data["to_" + r.suffix + "_soon"]) + "</div>";
      }
      return "<div class=\"cl-to-car\"><b>" + esc(r.vin + " · " + r.model) + "</b>" +
        DUE_ITEMS.map(function(it){
          return dutyItem("to_" + r.suffix + "_" + it.key, esc(it.label), data["to_" + r.suffix + "_" + it.key]);
        }).join("") +
        "</div>";
    }).join("");
    return "<section class=\"cl-sec cl-to\" data-to-n=\"" + list.length + "\">" +
      "<h2 class=\"cl-sec-title\">ТО тестовых авто</h2>" +
      "<div class=\"cl-box\">" + blocks + "</div></section>";
  }

  window.DUTY_TO_SCHEDULE = DUTY_TO_SCHEDULE;
  window.dutyToISO = dutyToISO;
  window.dutyToToday = dutyToToday;
  window.dutyToLayout = layout;
  window.dutyToKeys = keys;
  window.dutyToSection = section;
})();
