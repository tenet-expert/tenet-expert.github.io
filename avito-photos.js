/* Фото для Авито в чек-листе дежурного.
   Список не зашит: страница читает photos-needed.json.
   TENET+ (Назарян, Бикулов, Ковалева) видит только L4/L6, остальные — прочие группы.
   stage: shoot — нужен комплект/съёмка; verify — соответствие не подтверждено;
   upload_error — ошибка загрузки, не съёмка; check_set — проверить общий комплект,
   это не пересъёмка. id групп не переписываются. */
(function(){
  if (window.__avitoPhotosBoot) return;
  window.__avitoPhotosBoot = true;

  var KEY = "tenet-avito-photo";
  var loadGen = 0;
  var STAGE_ORDER = ["shoot", "verify", "upload_error", "check_set"];
  var STAGE_META = {
    shoot: {
      title: "Нужен комплект/съёмка",
      lead: "Подходящий комплект не найден, фото VIN в текущих выгрузках нет.",
      check: true,
      open: true
    },
    verify: {
      title: "Проверить соответствие",
      lead: "Кандидат на Drive есть, но оттенок, комплектация, привод или места не подтверждены. Это не заявка на новую съёмку.",
      check: false,
      open: true
    },
    upload_error: {
      title: "Ошибка загрузки",
      lead: "В отчёте ошибка одного фото. Нужна повторная загрузка, не съёмка.",
      check: false,
      open: true
    },
    check_set: {
      title: "Проверить комплект и загрузку",
      lead: "Папка на Drive есть, фото VIN в текущих выгрузках нет. Проверить, можно ли использовать общий комплект. Это не список на пересъёмку и не подтверждение, что комплект занят.",
      check: false,
      open: false
    }
  };

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
    var left = [model, trim].filter(Boolean).join(" ");
    if (drive && left.toUpperCase().indexOf(drive.toUpperCase()) < 0) left = (left + " " + drive).trim();
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

  function stageOf(g){
    var s = String(g && g.stage || "");
    return STAGE_META[s] ? s : "shoot";
  }

  function carState(c){
    var s = String(c && c.state || "").trim();
    if (s) return s;
    var st = String(c && c.status || "");
    if (st === "way") return "в пути";
    if (st === "in") return "в салоне";
    return "";
  }

  function carsOf(g){
    return g && Array.isArray(g.cars) ? g.cars : [];
  }

  function tally(groups){
    var inn = 0, way = 0, n = 0;
    (groups || []).forEach(function(g){
      carsOf(g).forEach(function(c){
        n++;
        var s = carState(c);
        if (s.indexOf("пути") >= 0) way++;
        else if (s.indexOf("салон") >= 0) inn++;
      });
    });
    return { groups: (groups || []).length, cars: n, salon: inn, way: way };
  }

  function countLine(t){
    var bits = [t.groups + " гр.", t.cars + " авто"];
    if (t.salon) bits.push(t.salon + " в салоне");
    if (t.way) bits.push(t.way + " в пути");
    return bits.join(" · ");
  }

  function visibleGroups(data){
    var groups = data && Array.isArray(data.groups) ? data.groups : [];
    var plus = wantPlus();
    return groups.filter(function(g){ return isPlusGroup(g) === plus; });
  }

  function summaryFor(data){
    var s = data && data.summary;
    if (!s || typeof s !== "object") return null;
    if (wantPlus()) return s["TENET PLUS"] || s["TENET+"] || null;
    return s.TENET || null;
  }

  function folderOf(g){
    var f = g && g.photo_folder;
    if (!f || typeof f !== "object") return null;
    var url = String(f.url || "");
    if (!/^https:\/\/drive\.google\.com\//.test(url)) return null;
    return { url: url, name: String(f.name || "").trim() || "Папка Drive" };
  }

  function brandBlocks(data){
    var groups = visibleGroups(data);
    var picks = loadPicks();
    var blocks = [];
    STAGE_ORDER.forEach(function(stage){
      var list = groups.filter(function(g){ return stageOf(g) === stage; });
      if (!list.length && stage !== "shoot") return;
      var meta = STAGE_META[stage];
      var t = tally(list);
      blocks.push({
        stage: stage,
        title: meta.title,
        lead: meta.lead,
        collapsed: !meta.open,
        check: !!meta.check,
        groups: t.groups,
        cars: t.cars,
        salon: t.salon,
        way: t.way,
        count: list.length ? countLine(t) : "0",
        rows: list.map(function(g){
          var id = String(g && g.id || "");
          var cars = carsOf(g);
          var folder = folderOf(g);
          return {
            id: id,
            title: rowTitle(g),
            vins: cars.map(function(c){ return c && c.vin ? String(c.vin) : ""; }).filter(Boolean),
            states: cars.map(function(c){
              var vin = c && c.vin ? String(c.vin) : "";
              var st = carState(c);
              return vin ? (st ? vin + " · " + st : vin) : "";
            }).filter(Boolean),
            on: picks.indexOf(id) >= 0,
            stage: stage,
            reason: String(g && g.reason || "").trim(),
            folder: folder ? folder.name : "",
            folderUrl: folder ? folder.url : "",
            actionable: stage === "shoot"
          };
        })
      });
    });
    var summary = summaryFor(data);
    var feed = summary && typeof summary.feed_photos_present === "number" ? summary.feed_photos_present : null;
    var pending = groups.some(function(g){ return stageOf(g) !== "shoot"; });
    if (summary) {
      ["verify", "check_set", "upload_error"].forEach(function(k){
        if ((summary[k] || 0) > 0) pending = true;
      });
    }
    var shoot = blocks.filter(function(b){ return b.stage === "shoot"; })[0] || { rows: [] };
    return {
      ready: true,
      pending: pending,
      note: data && data.note ? String(data.note) : "",
      updated: data && data.updated ? String(data.updated) : "",
      subtitle: "в салоне и в пути",
      badge: shoot.rows.length ? (shoot.count || "") : "0",
      feedNote: feed == null ? "" : ("В выгрузке есть фото: " + feed + " авто. Это не подтверждение загрузки на Авито."),
      emptyText: "Съёмка по этому списку не требуется. Это не значит, что фото на Авито готовы.",
      rows: shoot.rows,
      blocks: blocks
    };
  }

  function ensureCss(){
    if (document.getElementById("avitoPhotosCss")) return;
    var st = document.createElement("style");
    st.id = "avitoPhotosCss";
    st.textContent = [
      ".cl-print{margin:6px 0 4px;display:flex;flex-direction:column;align-items:stretch;gap:6px}",
      ".cl-print .btn{width:100%;min-height:46px;font-size:15px}",
      ".cl-print .btn:disabled{opacity:.45;cursor:not-allowed}",
      ".cl-print-hint{margin:0;text-align:center;font:500 12px/1.3 Inter,Arial,sans-serif;color:#7a7166}",
      ".cl-print.is-ready .cl-print-hint{display:none}",
      ".cl-avito{margin:2px 0 10px}",
      ".cl-avito-card{background:#f3eee4;border:1px dashed #d9cbb6;border-radius:16px;overflow:hidden}",
      ".cl-avito-head{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:10px 12px 8px;font:700 12px/1.3 Inter,Arial,sans-serif;color:#5c5346}",
      ".cl-avito-count{font:800 11px/1.3 Inter,Arial,sans-serif;letter-spacing:.02em;color:#1c1a17;background:#fbf7f0;border:1px solid #eadfcf;border-radius:999px;padding:4px 8px;white-space:nowrap}",
      ".cl-avito-note{margin:0;padding:0 12px 8px;font:500 11px/1.35 Inter,Arial,sans-serif;color:#7a7166}",
      ".cl-avito-list{display:block}",
      ".cl-avito-sec{padding:8px 12px 4px;border-top:1px solid #eadfcf;background:#fff}",
      ".cl-avito-sec h3{margin:0;font:800 12px/1.3 Inter,Arial,sans-serif;color:#1c1a17}",
      ".cl-avito-sec.shoot h3{color:#1b5e20}",
      ".cl-avito-sec.verify h3{color:#8a5a00}",
      ".cl-avito-sec.upload_error h3{color:#8a3b12}",
      ".cl-avito-countline{display:block;margin-top:2px;font:700 11px/1.3 Inter,Arial,sans-serif;color:#5c5346}",
      ".cl-avito-lead{margin:4px 0 6px;font:500 11px/1.35 Inter,Arial,sans-serif;color:#7a7166}",
      ".cl-avito-empty{margin:0 0 8px;padding:0;font-size:13px;color:#7a7166}",
      ".cl-avito-item{border-top:1px solid #eadfcf;background:#fff}",
      ".cl-avito-row{display:flex;align-items:flex-start;gap:10px;margin:0;padding:9px 12px;cursor:pointer}",
      ".cl-avito-item .cl-avito-row{border-top:0;padding-bottom:4px}",
      ".cl-avito-row.is-on{background:#e8f5e9}",
      ".cl-avito-row input{appearance:none;-webkit-appearance:none;width:18px;height:18px;margin:1px 0 0;flex:none;border:1.5px solid #8d7f6a;border-radius:4px;background:#fff;cursor:pointer}",
      ".cl-avito-row input:checked{background:#e8f5e9;border-color:#1b5e20}",
      ".cl-avito-tick{width:18px;height:18px;margin:1px 0 0 -28px;pointer-events:none;display:inline-flex;align-items:center;justify-content:center;font:800 14px/1 Inter,Arial,sans-serif;color:transparent;flex:none}",
      ".cl-avito-row.is-on .cl-avito-tick{color:#145a1f}",
      ".cl-avito-main{min-width:0;flex:1}",
      ".cl-avito-main b{display:block;font-size:13.5px;font-weight:700;letter-spacing:-.02em;line-height:1.3;color:#1c1a17}",
      ".cl-avito-vins{margin-top:3px;display:flex;flex-wrap:wrap;gap:4px 8px}",
      ".cl-avito-vins code{font:500 11px/1.35 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#6d6458;background:transparent;border:0;padding:0;letter-spacing:.01em}",
      ".cl-avito-state{font-style:normal;font:700 10px/1.2 Inter,Arial,sans-serif;color:#5c5346;background:#f3eee4;border-radius:999px;padding:1px 6px}",
      ".cl-avito-state.is-way{color:#1b4f72;background:#e7f1f8}",
      ".cl-avito-reason{display:block;margin-top:3px;font:500 11px/1.35 Inter,Arial,sans-serif;color:#6d6458}",
      ".cl-avito-meta{margin:0;padding:0 12px 8px 40px;background:#fff}",
      ".cl-avito-item:not(:has(input)) .cl-avito-meta{padding-left:12px}",
      ".cl-avito-folder{font:600 11px/1.3 Inter,Arial,sans-serif;color:#1b5e20}",
      ".cl-avito-fold{border-top:1px solid #eadfcf;background:#fff;padding:8px 12px 4px}",
      ".cl-avito-fold summary{cursor:pointer;font:800 12px/1.3 Inter,Arial,sans-serif;color:#5c5346}",
      ".cl-avito-fold summary .cl-avito-countline{display:inline;margin-left:6px}",
      ".cl-avito-feed{margin:0;padding:8px 12px;font:500 11px/1.35 Inter,Arial,sans-serif;color:#6d6458;background:#fbf7f0;border-top:1px solid #eadfcf}",
      ".cl-avito-today{margin:0;padding:8px 12px;font:700 12px/1.35 Inter,Arial,sans-serif;color:#1b5e20;background:#f3faf6;border-top:1px solid #d7eadb}",
      ".cl-avito-upd{margin:0;padding:6px 12px 8px;font:500 11px/1.3 Inter,Arial,sans-serif;color:#9a9186;border-top:1px solid #f3eee4}",
      "@media print{",
      "html,body,.wrap,#app{height:auto!important;overflow:visible!important}",
      ".cl,.cl *{visibility:visible!important}",
      ".cl-log,.cl-log *{display:none!important;visibility:hidden!important}",
      ".cl-avito,.cl-avito-card,.cl-avito-list,.cl-avito-row,.cl-avito-main{overflow:visible!important;height:auto!important;max-height:none!important}",
      ".cl-avito{display:block!important;break-inside:auto;page-break-inside:auto;position:static!important}",
      ".cl-avito-fold .cl-avito-body{display:block!important}",
      ".cl-avito-row{break-inside:avoid;page-break-inside:avoid;-webkit-print-color-adjust:exact;print-color-adjust:exact}",
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

  function currentPack(){
    if (window.__avitoPhotosData) return brandBlocks(window.__avitoPhotosData);
    return { ready: false, pending: false, rows: [], blocks: null };
  }

  function syncPrint(){
    var btn = document.getElementById("dutyPrint");
    var bar = document.getElementById("dutyPrintBar");
    var hint = document.getElementById("dutyPrintHint");
    var pack = (typeof window.avitoPhotosForPrint === "function") ? window.avitoPhotosForPrint() : null;
    var ready = !!(pack && pack.ready);
    var rows = ready && Array.isArray(pack.rows) ? pack.rows : [];
    var picked = rows.some(function(r){ return r && r.on; });
    var none = ready && !rows.length;
    var on = ready && (picked || none);
    if (btn) btn.disabled = !on;
    if (bar) bar.classList.toggle("is-ready", !!(picked || (none && pack && !pack.pending)));
    if (hint) {
      if (!ready) {
        hint.hidden = false;
        hint.textContent = "Список фото загружается";
      } else if (rows.length && !picked) {
        hint.hidden = false;
        hint.textContent = "Отметьте хотя бы одну машину для съёмки";
      } else if (none && pack.pending) {
        hint.hidden = false;
        hint.textContent = "Съёмка не назначена. Проверки ниже не закрыты — это не «все фото готовы».";
      } else {
        hint.hidden = true;
        hint.textContent = "";
      }
    }
  }

  function vinHtml(row){
    var cars = row.states && row.states.length ? row.states : (row.vins || []);
    return cars.map(function(line){
      var parts = String(line).split(" · ");
      var vin = parts[0] || "";
      var state = parts.length > 1 ? parts.slice(1).join(" · ") : "";
      var mark = state ? " <em class=\"cl-avito-state" + (state.indexOf("пути") >= 0 ? " is-way" : "") + "\">" + esc(state) + "</em>" : "";
      return "<span><code>" + esc(vin) + "</code>" + mark + "</span>";
    }).join("");
  }

  function rowHtml(row, check){
    var on = !!(check && row.on);
    var body = "<span class=\"cl-avito-main\"><b>" + esc(row.title) + "</b><span class=\"cl-avito-vins\">" + vinHtml(row) + "</span>" +
      (row.reason ? "<span class=\"cl-avito-reason\">" + esc(row.reason) + "</span>" : "") + "</span>";
    var box = check
      ? "<label class=\"cl-avito-row" + (on ? " is-on" : "") + "\">" +
          "<input type=\"checkbox\" autocomplete=\"off\" data-avito-group=\"" + esc(row.id) + "\"" + (on ? " checked" : "") + " />" +
          "<span class=\"cl-avito-tick\" aria-hidden=\"true\">✓</span>" + body + "</label>"
      : "<div class=\"cl-avito-row\">" + body + "</div>";
    var link = row.folderUrl
      ? "<p class=\"cl-avito-meta\"><a class=\"cl-avito-folder\" href=\"" + esc(row.folderUrl) + "\" target=\"_blank\" rel=\"noopener noreferrer\">" + esc(row.folder || "Папка Drive") + "</a></p>"
      : "";
    return "<div class=\"cl-avito-item\">" + box + link + "</div>";
  }

  function renderList(data){
    var list = document.getElementById("avitoPhotosList");
    var upd = document.getElementById("avitoPhotosUpd");
    var today = document.getElementById("avitoPhotosToday");
    var note = document.getElementById("avitoPhotosNote");
    if (!list) return;
    var pack = brandBlocks(data);
    var count = document.getElementById("avitoPhotosCount");
    if (count) count.textContent = pack.badge || "";
    if (note) note.textContent = pack.note || "";
    if (upd) upd.textContent = pack.updated ? ("обновлено " + pack.updated) : "";
    var titles = [];
    (pack.rows || []).forEach(function(row){ if (row.on) titles.push(row.title); });
    if (today) {
      if (titles.length) {
        today.hidden = false;
        today.textContent = "Сегодня на съёмку: " + titles.join("; ");
      } else {
        today.hidden = true;
        today.textContent = "";
      }
    }
    var foldWas = false;
    var prevFold = list.querySelector(".cl-avito-fold");
    if (prevFold && prevFold.open) foldWas = true;
    var html = (pack.blocks || []).map(function(b){
      var body = b.rows.length
        ? b.rows.map(function(row){ return rowHtml(row, b.check); }).join("")
        : "<p class=\"cl-avito-empty\">" + esc(pack.emptyText) + "</p>";
      if (b.collapsed) {
        return "<details class=\"cl-avito-fold\"" + (foldWas ? " open" : "") + ">" +
          "<summary>" + esc(b.title) + "<span class=\"cl-avito-countline\">" + esc(b.count) + "</span></summary>" +
          "<p class=\"cl-avito-lead\">" + esc(b.lead) + "</p>" +
          "<div class=\"cl-avito-body\">" + body + "</div></details>";
      }
      return "<section class=\"cl-avito-sec " + esc(b.stage) + "\">" +
        "<h3>" + esc(b.title) + "</h3>" +
        "<span class=\"cl-avito-countline\">" + esc(b.count) + "</span>" +
        "<p class=\"cl-avito-lead\">" + esc(b.lead) + "</p>" + body + "</section>";
    }).join("");
    if (pack.feedNote) html += "<p class=\"cl-avito-feed\">" + esc(pack.feedNote) + "</p>";
    if (!html) html = "<p class=\"cl-avito-empty\">" + esc(pack.emptyText) + "</p>";
    list.innerHTML = html;
    syncPrint();
  }

  function load(){
    var n = ++loadGen;
    var box = document.getElementById("avitoPhotosList");
    if (box) box.innerHTML = '<p class="cl-avito-empty">Загрузка…</p>';
    fetch("photos-needed.json?" + Date.now()).then(function(r){
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    }).then(function(data){
      if (n !== loadGen) return;
      window.__avitoPhotosData = data;
      renderList(data);
    }).catch(function(){
      if (n !== loadGen) return;
      window.__avitoPhotosData = null;
      var list = document.getElementById("avitoPhotosList");
      var upd = document.getElementById("avitoPhotosUpd");
      if (upd) upd.textContent = "";
      if (list) list.innerHTML = '<p class="cl-avito-empty">Не удалось загрузить список. Это не значит, что все фото готовы.</p>';
      syncPrint();
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
    if (!window.__avitoPhotosData) return { ready: false, pending: false, rows: [], blocks: null };
    return brandBlocks(window.__avitoPhotosData);
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
        '<div class="cl-avito-head"><span>В салоне и в пути</span><span class="cl-avito-count" id="avitoPhotosCount"></span></div>' +
        '<p class="cl-avito-note" id="avitoPhotosNote"></p>' +
        '<div class="cl-avito-list" id="avitoPhotosList"><p class="cl-avito-empty">Загрузка…</p></div>' +
        '<p class="cl-avito-today" id="avitoPhotosToday" hidden></p>' +
        '<p class="cl-avito-upd" id="avitoPhotosUpd"></p>' +
      '</div>';
    sec.addEventListener("change", onChange);
    sec.addEventListener("click", function(ev){
      var a = ev.target && ev.target.closest ? ev.target.closest("a") : null;
      if (a) ev.stopPropagation();
    });
    var anchor = cl.querySelector("#dutyPrintBar") || cl.querySelector(".cl-log");
    if (anchor) cl.insertBefore(sec, anchor);
    else cl.appendChild(sec);
    syncPrint();
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
