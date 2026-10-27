/* Фото для Авито в чек-листе дежурного.
   Список не зашит: каждое утро файл photos-needed.json подменяют пушем,
   страница читает его заново. Несколько групп на календарный день Самары.
   TENET+ (Назарян, Бикулов) видит только L4/L6, остальные — все прочие группы. */
(function(){
  if (window.__avitoPhotosBoot) return;
  window.__avitoPhotosBoot = true;

  var KEY = "tenet-avito-photo";
  var loadGen = 0;

  function samaraDate(){
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
    var p = function(n){ return String(n).padStart(2, "0"); };
    return t.getUTCFullYear() + "-" + p(t.getUTCMonth() + 1) + "-" + p(t.getUTCDate());
  }

  function loadPicks(){
    try {
      var x = JSON.parse(localStorage.getItem(KEY) || "null");
      if (!x || typeof x !== "object") return [];
      if (x.date !== samaraDate()) return [];
      var ids = [];
      if (Array.isArray(x.groupIds)) ids = x.groupIds;
      else if (x.groupId) ids = [x.groupId];
      var out = [];
      ids.forEach(function(id){
        id = String(id || "");
        if (id && out.indexOf(id) < 0) out.push(id);
      });
      return out;
    } catch (e) {
      return [];
    }
  }

  function savePicks(ids){
    try {
      var list = [];
      (ids || []).forEach(function(id){
        id = String(id || "");
        if (id && list.indexOf(id) < 0) list.push(id);
      });
      if (!list.length) {
        localStorage.removeItem(KEY);
        return;
      }
      localStorage.setItem(KEY, JSON.stringify({ date: samaraDate(), groupIds: list }));
    } catch (e) {}
  }

  function esc(s){
    return String(s == null ? "" : s).replace(/[&<>"']/g, function(m){
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m];
    });
  }

  function rowTitle(g){
    var model = String(g && g.model || "").trim();
    var trim = String(g && g.trim || "").trim();
    var drive = String(g && g.drive || "").trim();
    var color = String(g && g.color || "").trim();
    var left = [model, trim, drive].filter(Boolean).join(" ");
    return color ? left + ", " + color : left;
  }

  function wantPlus(){
    if (typeof window.dutyIsPlus === "function") {
      try { return !!window.dutyIsPlus(); } catch (e) {}
    }
    var cl = document.querySelector("#app .cl");
    if (cl && cl.getAttribute("data-duty-variant") === "plus") return true;
    return !!window.__dutyPlus;
  }

  function isPlusGroup(g){
    var brand = String(g && g.brand || "").toUpperCase().replace(/Ё/g, "Е");
    var model = String(g && g.model || "").toUpperCase().replace(/Ё/g, "Е").replace(/\s+/g, "");
    if (brand.indexOf("TENET") >= 0 && (brand.indexOf("+") >= 0 || brand.indexOf("PLUS") >= 0 || brand.indexOf("ПЛЮС") >= 0)) return true;
    if (model === "L4" || model === "L6" || model === "PL4" || model === "PL6") return true;
    return false;
  }

  function visibleGroups(data){
    var groups = data && Array.isArray(data.groups) ? data.groups : [];
    var plus = wantPlus();
    return groups.filter(function(g){ return isPlusGroup(g) === plus; });
  }

  function ensureCss(){
    if (document.getElementById("avitoPhotosCss")) return;
    var st = document.createElement("style");
    st.id = "avitoPhotosCss";
    st.textContent = [
      ".cl-avito{margin:2px 0 10px}",
      ".cl-avito-card{background:#f3eee4;border:1px dashed #d9cbb6;border-radius:16px;overflow:hidden}",
      ".cl-avito-head{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:10px 12px 8px;font:700 12px/1.3 Inter,Arial,sans-serif;color:#5c5346}",
      ".cl-avito-count{font:800 11px/1 Inter,Arial,sans-serif;letter-spacing:.02em;color:#1c1a17;background:#fbf7f0;border:1px solid #eadfcf;border-radius:999px;padding:4px 8px;white-space:nowrap}",
      ".cl-avito-list{display:grid;grid-template-columns:1fr}",
      "@media(min-width:900px){.cl-avito-list{grid-template-columns:1fr 1fr}}",
      ".cl-avito-empty{margin:0;padding:12px;font-size:13px;color:#7a7166}",
      ".cl-avito-row{display:flex;align-items:flex-start;gap:10px;margin:0;padding:9px 12px;border-top:1px solid #eadfcf;cursor:pointer;background:#fff}",
      ".cl-avito-row:first-child{border-top:0}",
      "@media(min-width:900px){.cl-avito-row:nth-child(odd){border-right:1px solid #f3eee4}.cl-avito-row:nth-child(-n+2){border-top:0}}",
      ".cl-avito-row.is-on{background:#e8f5e9}",
      ".cl-avito-row input{appearance:none;-webkit-appearance:none;width:18px;height:18px;margin:1px 0 0;flex:none;border:1.5px solid #8d7f6a;border-radius:4px;background:#fff;cursor:pointer}",
      ".cl-avito-row input:checked{background:#e8f5e9;border-color:#1b5e20}",
      ".cl-avito-tick{width:18px;height:18px;margin:1px 0 0 -28px;pointer-events:none;display:inline-flex;align-items:center;justify-content:center;font:800 14px/1 Inter,Arial,sans-serif;color:transparent;flex:none}",
      ".cl-avito-row.is-on .cl-avito-tick{color:#145a1f}",
      ".cl-avito-main{min-width:0;flex:1}",
      ".cl-avito-main b{display:block;font-size:13.5px;font-weight:700;letter-spacing:-.02em;line-height:1.3;color:#1c1a17}",
      ".cl-avito-vins{margin-top:3px;display:flex;flex-wrap:wrap;gap:2px 8px}",
      ".cl-avito-vins code{font:500 11px/1.35 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#6d6458;background:transparent;border:0;padding:0;letter-spacing:.01em}",
      ".cl-avito-today{margin:0;padding:8px 12px;font:700 12px/1.35 Inter,Arial,sans-serif;color:#1b5e20;background:#f3faf6;border-top:1px solid #d7eadb}",
      ".cl-avito-upd{margin:0;padding:6px 12px 8px;font:500 11px/1.3 Inter,Arial,sans-serif;color:#9a9186;border-top:1px solid #f3eee4}",
      "@media print{",
      "html,body,.wrap,#app{height:auto!important;overflow:visible!important}",
      ".cl,.cl *{visibility:visible!important}",
      ".cl-log,.cl-log *{display:none!important;visibility:hidden!important}",
      ".cl-avito,.cl-avito-card,.cl-avito-list,.cl-avito-row,.cl-avito-main{overflow:visible!important;height:auto!important;max-height:none!important}",
      ".cl-avito{display:block!important;break-inside:auto;page-break-inside:auto;position:static!important}",
      ".cl-avito-list{display:block!important;grid-template-columns:1fr!important}",
      ".cl-avito-row{break-inside:avoid;page-break-inside:avoid;border-right:0!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}",
      ".cl-avito-row.is-on{background:#e8f5e9!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}",
      ".cl-avito-row input{display:none!important}",
      ".cl-avito-tick{display:inline-flex!important;margin:0!important;width:3.6mm!important;height:3.6mm!important;border:1.5px solid #8d7f6a;border-radius:1px;font:800 11px/1 Inter,Arial,sans-serif;color:transparent;background:#fff}",
      ".cl-avito-row.is-on .cl-avito-tick{color:#145a1f!important;background:#e8f5e9!important;border-color:#1b5e20!important}",
      "#dutyPdfView,#dutyPdfView *{visibility:visible!important}",
      "#dutyPdfView{height:auto!important;overflow:visible!important}",
      "#dutyPdfView img{height:auto!important;max-height:none!important;object-fit:unset!important}",
      "}"
    ].join("");
    document.head.appendChild(st);
  }

  function renderList(data){
    var list = document.getElementById("avitoPhotosList");
    var upd = document.getElementById("avitoPhotosUpd");
    var today = document.getElementById("avitoPhotosToday");
    if (!list) return;
    var groups = visibleGroups(data);
    var count = document.getElementById("avitoPhotosCount");
    if (count) count.textContent = groups.length ? (groups.length + " шт.") : "";
    if (upd) upd.textContent = data && data.updated ? ("обновлено " + data.updated) : "";
    var picks = loadPicks();
    var titles = [];
    picks.forEach(function(id){
      for (var i = 0; i < groups.length; i++) {
        if (String(groups[i] && groups[i].id) === id) { titles.push(rowTitle(groups[i])); break; }
      }
    });
    if (today) {
      if (titles.length) {
        today.hidden = false;
        today.textContent = "Сегодня выбрано: " + titles.join("; ");
      } else {
        today.hidden = true;
        today.textContent = "";
      }
    }
    if (!groups.length) {
      list.innerHTML = '<p class="cl-avito-empty">Сейчас таких автомобилей нет.</p>';
      return;
    }
    list.innerHTML = groups.map(function(g){
      var id = String(g && g.id || "");
      var on = picks.indexOf(id) >= 0;
      var cars = g && Array.isArray(g.cars) ? g.cars : [];
      var vins = cars.map(function(c){
        var vin = c && c.vin ? String(c.vin) : "";
        return vin ? "<code>" + esc(vin) + "</code>" : "";
      }).filter(Boolean).join("");
      return '<label class="cl-avito-row' + (on ? " is-on" : "") + '">' +
        '<input type="checkbox" autocomplete="off" data-avito-group="' + esc(id) + '"' + (on ? " checked" : "") + ' />' +
        '<span class="cl-avito-tick" aria-hidden="true">✓</span>' +
        '<span class="cl-avito-main"><b>' + esc(rowTitle(g)) + '</b><span class="cl-avito-vins">' + vins + "</span></span></label>";
    }).join("");
  }

  function load(){
    var n = ++loadGen;
    var box = document.getElementById("avitoPhotosList");
    if (box) box.innerHTML = '<p class="cl-avito-empty">Загрузка…</p>';
    fetch('photos-needed.json?'+Date.now()).then(function(r){
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    }).then(function(data){
      if (n !== loadGen) return;
      window.__avitoPhotosData = data;
      renderList(data);
    }).catch(function(){
      if (n !== loadGen) return;
      var list = document.getElementById("avitoPhotosList");
      var upd = document.getElementById("avitoPhotosUpd");
      if (upd) upd.textContent = "";
      if (list) list.innerHTML = '<p class="cl-avito-empty">Не удалось загрузить список.</p>';
    });
  }

  function onChange(ev){
    var inp = ev.target;
    if (!inp || !inp.getAttribute) return;
    var id = inp.getAttribute("data-avito-group");
    if (!id) return;
    var picks = loadPicks();
    var i = picks.indexOf(id);
    if (inp.checked) {
      if (i < 0) picks.push(id);
    } else if (i >= 0) {
      picks.splice(i, 1);
    }
    savePicks(picks);
    if (window.__avitoPhotosData) renderList(window.__avitoPhotosData);
  }

  window.avitoPhotosForPrint = function(){
    var data = window.__avitoPhotosData;
    if (!data || !Array.isArray(data.groups)) return { ready: false, rows: [] };
    var groups = visibleGroups(data);
    var picks = loadPicks();
    return {
      ready: true,
      rows: groups.map(function(g){
        var id = String(g && g.id || "");
        var cars = g && Array.isArray(g.cars) ? g.cars : [];
        return {
          id: id,
          title: rowTitle(g),
          vins: cars.map(function(c){ return c && c.vin ? String(c.vin) : ""; }).filter(Boolean),
          on: picks.indexOf(id) >= 0
        };
      })
    };
  };
  window.avitoPhotosIsPlusGroup = isPlusGroup;

  function mount(){
    var cl = document.querySelector("#app .cl");
    if (!cl || document.getElementById("avitoPhotos")) return;
    ensureCss();
    var sec = document.createElement("section");
    sec.className = "cl-sec cl-avito";
    sec.id = "avitoPhotos";
    sec.innerHTML =
      '<h2 class="cl-sec-title">Фото для Авито</h2>' +
      '<div class="cl-avito-card">' +
        '<div class="cl-avito-head"><span>В наличии · нет фото на Drive</span><span class="cl-avito-count" id="avitoPhotosCount"></span></div>' +
        '<div class="cl-avito-list" id="avitoPhotosList"><p class="cl-avito-empty">Загрузка…</p></div>' +
        '<p class="cl-avito-today" id="avitoPhotosToday" hidden></p>' +
        '<p class="cl-avito-upd" id="avitoPhotosUpd"></p>' +
      '</div>';
    sec.addEventListener("change", onChange);
    var log = cl.querySelector(".cl-log");
    if (log) cl.insertBefore(sec, log);
    else cl.appendChild(sec);
    load();
  }

  function hook(){
    var app = document.getElementById("app");
    if (app && !app.__avitoWatch) {
      app.__avitoWatch = true;
      var obs = new MutationObserver(function(){ mount(); });
      obs.observe(app, { childList: true, subtree: true });
    }
    if (typeof window.dutyBind === "function" && !window.dutyBind.__avito) {
      var prev = window.dutyBind;
      var wrapped = function(){
        var r = prev.apply(this, arguments);
        try { mount(); } catch (e) {}
        return r;
      };
      wrapped.__avito = true;
      window.dutyBind = wrapped;
    }
    try { mount(); } catch (e) {}
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", hook);
  else hook();
})();
