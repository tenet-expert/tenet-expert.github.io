/* Фото для Авито в чек-листе дежурного.
   Список не зашит: каждое утро файл photos-needed.json подменяют пушем,
   страница читает его заново. Один выбор группы на календарный день Самары. */
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

  function loadPick(){
    try {
      var x = JSON.parse(localStorage.getItem(KEY) || "null");
      if (!x || typeof x !== "object") return null;
      if (x.date !== samaraDate() || !x.groupId) return null;
      return { date: String(x.date), groupId: String(x.groupId) };
    } catch (e) {
      return null;
    }
  }

  function savePick(groupId){
    try {
      if (!groupId) {
        localStorage.removeItem(KEY);
        return;
      }
      localStorage.setItem(KEY, JSON.stringify({ date: samaraDate(), groupId: String(groupId) }));
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

  function ensureCss(){
    if (document.getElementById("avitoPhotosCss")) return;
    var st = document.createElement("style");
    st.id = "avitoPhotosCss";
    st.textContent = [
      ".cl-avito{margin:2px 0 8px}",
      ".cl-avito .cl-sec-title{text-transform:none;letter-spacing:0;font-size:15px}",
      ".cl-avito-upd{margin:0 2px 6px;font:500 12px/1.35 Inter,Arial,sans-serif;color:#7a7166}",
      ".cl-avito-today{margin:0 2px 10px;font:700 13px/1.35 Inter,Arial,sans-serif;color:#1b5e20}",
      ".cl-avito-list{display:flex;flex-direction:column;gap:8px}",
      ".cl-avito-empty{margin:0;font-size:13px;color:#7a7166}",
      ".cl-avito-row{background:#fff;border:1px solid #eadfcf;border-radius:14px;padding:10px;display:flex;flex-wrap:wrap;gap:8px 12px;align-items:flex-start;justify-content:space-between}",
      ".cl-avito-row.is-on{background:#e8f5e9;border-color:#1b5e20}",
      ".cl-avito-row.is-off{opacity:.55}",
      ".cl-avito-main{min-width:0;flex:1}",
      ".cl-avito-main b{display:block;font-size:14px;letter-spacing:-.02em;line-height:1.3}",
      ".cl-avito-vins{margin-top:4px;display:flex;flex-wrap:wrap;gap:4px 8px}",
      ".cl-avito-vins code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;color:#1c1a17;background:#fbf7f0;border:1px solid #eadfcf;border-radius:6px;padding:1px 5px}",
      ".cl-avito-check{display:flex;align-items:center;gap:8px;font:600 12px/1.3 Inter,Arial,sans-serif;cursor:pointer;flex:none;margin:0}",
      ".cl-avito-check input{appearance:none;-webkit-appearance:none;width:18px;height:18px;margin:0;flex:none;border:1.5px solid #8d7f6a;border-radius:4px;background:#fff;cursor:pointer}",
      ".cl-avito-check input:checked{background-color:#e8f5e9;border-color:#1b5e20;background-image:url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 18 18'><path d='M4 9.2 7.2 12.4 14 5.6' fill='none' stroke='%23145a1f' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/></svg>\");background-size:18px 18px;background-repeat:no-repeat;background-position:center}",
      ".cl-avito-check input:disabled{cursor:not-allowed}",
      ".cl-avito-row.is-off .cl-avito-check{cursor:not-allowed}"
    ].join("");
    document.head.appendChild(st);
  }

  function renderList(data){
    var list = document.getElementById("avitoPhotosList");
    var upd = document.getElementById("avitoPhotosUpd");
    var today = document.getElementById("avitoPhotosToday");
    if (!list) return;
    var groups = data && Array.isArray(data.groups) ? data.groups : [];
    if (upd) upd.textContent = data && data.updated ? ("обновлено " + data.updated) : "";
    var pick = loadPick();
    var picked = null;
    if (pick) {
      for (var i = 0; i < groups.length; i++) {
        if (String(groups[i] && groups[i].id) === pick.groupId) { picked = groups[i]; break; }
      }
    }
    if (today) {
      if (pick) {
        today.hidden = false;
        today.textContent = "Сегодня выбрано: " + (picked ? rowTitle(picked) : pick.groupId);
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
      var on = !!(pick && pick.groupId === id);
      var off = !!(pick && !on);
      var cars = g && Array.isArray(g.cars) ? g.cars : [];
      var vins = cars.map(function(c){
        var vin = c && c.vin ? String(c.vin) : "";
        return vin ? "<code>" + esc(vin) + "</code>" : "";
      }).filter(Boolean).join("");
      return '<article class="cl-avito-row' + (on ? " is-on" : "") + (off ? " is-off" : "") + '">' +
        '<div class="cl-avito-main"><b>' + esc(rowTitle(g)) + '</b><div class="cl-avito-vins">' + vins + "</div></div>" +
        '<label class="cl-avito-check"><input type="checkbox" autocomplete="off" data-avito-group="' + esc(id) + '"' +
        (on ? " checked" : "") + (off ? " disabled" : "") + ' /><span>Готовлю фото для Авито</span></label></article>';
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
    var pick = loadPick();
    if (inp.checked) {
      if (pick && pick.groupId !== id) {
        inp.checked = false;
        return;
      }
      savePick(id);
    } else if (pick && pick.groupId === id) {
      savePick("");
    }
    if (window.__avitoPhotosData) renderList(window.__avitoPhotosData);
  }

  function mount(){
    var cl = document.querySelector("#app .cl");
    if (!cl || document.getElementById("avitoPhotos")) return;
    ensureCss();
    var sec = document.createElement("section");
    sec.className = "cl-sec cl-avito";
    sec.id = "avitoPhotos";
    sec.innerHTML =
      '<h2 class="cl-sec-title">Фото для Авито: в наличии, нет фото</h2>' +
      '<p class="cl-avito-upd" id="avitoPhotosUpd"></p>' +
      '<p class="cl-avito-today" id="avitoPhotosToday" hidden></p>' +
      '<div class="cl-avito-list" id="avitoPhotosList"><p class="cl-avito-empty">Загрузка…</p></div>';
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
