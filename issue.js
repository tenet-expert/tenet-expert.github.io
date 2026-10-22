/* График выдач · читает общий Google-график, чужие ячейки не переписывает */
var ISSUE_ID = "1lXlvHTVbrvvgX3XwdFw8Ktiaoat8OUl5IBdi0bTs1SE";
var ISSUE_SHEETS = ["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","НОЯБРЬ","Декабрь"];
var ISSUE_TYPES = ["Нал 1 час","Кредит 2 часа","НАЛ + ТИ 2 часа","Кредит + ТИ 3 часа"];
var ISSUE_BRANDS = ["Tenet","Chery","EXEED","Solaris"];
var ISSUE_MGRS = ["Бикулов","Назарян","Спицын","Сидоров","Лавров","Ахмадуллин","Демьянов","Тальков","Велиджанов","Леонтьев","Кокуркин","Хорошунов","Елчин"];
var ISSUE_STATE = { month: "", day: 0, form: null, busy: false, err: "", ok: "" };
var ISSUE_CACHE = {};

function isRop(){
  try {
    if (typeof state !== "undefined" && state && state.rop) return true;
    var blob = ((state && state.surname) || "") + " " + ((state && state.display) || "");
    blob = String(blob).toLowerCase().replace(/ё/g, "е");
    return blob.indexOf("спицын") >= 0 || blob.indexOf("леонтьев") >= 0;
  } catch (e) { return false; }
}

function issueEsc(s){
  return String(s == null ? "" : s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function issueHours(type){
  var m = String(type || "").match(/(\d+)\s*час/i);
  var n = m ? Number(m[1]) : 1;
  if (!n || n < 1) n = 1;
  if (n > 6) n = 6;
  return n;
}

function issueBlank(v){
  var s = String(v == null ? "" : v).trim();
  return !s || s === "-" || s === "—";
}

function issueTenet(brand){
  return /tenet|тенет/i.test(String(brand || ""));
}

function issueLocalKey(){ return "tenet-issue-local-v1"; }
function issueHookKey(){ return "tenet-issue-hook"; }

function issueLocalAll(){
  try { return JSON.parse(localStorage.getItem(issueLocalKey()) || "{}"); }
  catch (e) { return {}; }
}
function issueLocalSave(all){
  try { localStorage.setItem(issueLocalKey(), JSON.stringify(all)); } catch (e) {}
}
function issueHook(){
  try { return (localStorage.getItem(issueHookKey()) || "").trim(); }
  catch (e) { return ""; }
}

function issueSlotKey(sheet, day, time, side){
  return sheet + "|" + day + "|" + time + "|" + side;
}

function issueApplyLocal(sheet, slots){
  var all = issueLocalAll();
  Object.keys(all).forEach(function(k){
    var rec = all[k];
    if (!rec || rec.sheet !== sheet) return;
    var start = ISSUE_TIMES.indexOf(rec.time);
    if (start < 0) return;
    for (var i = 0; i < (rec.hours || 1); i++){
      var t = ISSUE_TIMES[start + i];
      if (!t) break;
      var hit = slots.filter(function(s){ return s.day === rec.day && s.time === t && s.side === rec.side; })[0];
      if (!hit) continue;
      if (i === 0 || issueBlank(hit.type)){
        hit.type = rec.type;
        hit.manager = rec.manager;
        hit.brand = rec.brand;
        if (i === 0) hit.client = rec.client;
        hit.local = true;
      }
    }
  });
}

var ISSUE_TIMES = ["9:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00"];

function issueParse(table, sheet){
  var slots = [];
  (table.rows || []).forEach(function(row, idx){
    var c = row.c || [];
    function val(i){
      var cell = c[i];
      if (!cell) return "";
      if (cell.f && i !== 1 && i !== 8) return String(cell.f);
      if (cell.v == null) return "";
      return String(cell.v);
    }
    function timeOf(i){
      var cell = c[i];
      if (!cell) return "";
      if (cell.f && /^\d{1,2}:\d{2}/.test(cell.f)) return cell.f.slice(0, 5).replace(/^(\d):/, "0$1:");
      return "";
    }
    var day = parseInt(val(0), 10);
    var time = timeOf(1);
    if (!day || !time) return;
    function pack(side, t, mgr, brand, client){
      return {
        day: day, time: time, side: side, row: idx + 3,
        type: issueBlank(t) ? "" : String(t).trim(),
        manager: issueBlank(mgr) ? "" : String(mgr).trim(),
        brand: issueBlank(brand) ? "" : String(brand).trim(),
        client: issueBlank(client) ? "" : String(client).trim()
      };
    }
    slots.push(pack("1", val(2), val(3), val(4), val(5)));
    slots.push(pack("2", val(9), val(10), val(11), val(12)));
  });
  issueApplyLocal(sheet, slots);
  return slots;
}

function issueLoad(sheet, done){
  var cb = "issueGvizCb";
  window.google = window.google || {};
  google.visualization = google.visualization || {};
  google.visualization.Query = google.visualization.Query || {};
  var seq = (window.__issueSeq = (window.__issueSeq || 0) + 1);
  google.visualization.Query.setResponse = function(resp){
    if (seq !== window.__issueSeq) return;
    if (!resp || !resp.table) { done(new Error("пустой ответ")); return; }
    ISSUE_CACHE[sheet] = issueParse(resp.table, sheet);
    done(null, ISSUE_CACHE[sheet]);
  };
  var old = document.getElementById("issueGviz");
  if (old) old.parentNode.removeChild(old);
  var s = document.createElement("script");
  s.id = "issueGviz";
  s.src = "https://docs.google.com/spreadsheets/d/" + ISSUE_ID + "/gviz/tq?tqx=out:json&sheet=" + encodeURIComponent(sheet) + "&t=" + Date.now();
  s.onerror = function(){ done(new Error("нет доступа к графику")); };
  document.head.appendChild(s);
  void cb;
}

function issueAt(slots, day, time, side){
  return slots.filter(function(s){ return s.day === day && s.time === time && s.side === side; })[0] || null;
}

function issueTaken(slot){
  return slot && !!(slot.type || slot.manager || slot.brand || slot.client);
}

function issueBlockOk(slots, day, time, side, hours){
  var start = ISSUE_TIMES.indexOf(time);
  if (start < 0) return "нет такого времени";
  if (start + hours > ISSUE_TIMES.length) return "не хватает часов до 19:00";
  for (var i = 0; i < hours; i++){
    var hit = issueAt(slots, day, ISSUE_TIMES[start + i], side);
    if (issueTaken(hit)) return ISSUE_TIMES[start + i] + " уже занято" + (hit.brand ? " · " + hit.brand : "") + (hit.manager ? " · " + hit.manager : "");
  }
  return "";
}

function issueJsonp(url, cb){
  var name = "issueHookCb_" + Date.now();
  var done = false;
  function finish(err, data){
    if (done) return;
    done = true;
    try { delete window[name]; } catch (e) { window[name] = undefined; }
    cb(err, data);
  }
  window[name] = function(data){ finish(null, data); };
  var s = document.createElement("script");
  s.src = url + (url.indexOf("?") >= 0 ? "&" : "?") + "callback=" + name;
  s.onerror = function(){ finish(new Error("связка не ответила")); };
  document.head.appendChild(s);
  setTimeout(function(){ if (!done) finish(new Error("связка молчит")); }, 12000);
}

var ISSUE_QUEUE = "5xamkp6g";
var ISSUE_QUEUE_KEY = "Jh6X6f8S";

function issueCells(rec){
  var cols = String(rec.side) === "2" ? ["J", "K", "L", "M"] : ["C", "D", "E", "F"];
  var cells = [];
  for (var i = 0; i < rec.hours; i++){
    var row = Number(rec.row) + i;
    cells.push({ a1: cols[0] + row, v: rec.type || "" });
    cells.push({ a1: cols[1] + row, v: rec.manager || "" });
    cells.push({ a1: cols[2] + row, v: rec.brand || "" });
    if (i === 0) cells.push({ a1: cols[3] + row, v: rec.client || "" });
  }
  return cells;
}

function issueFormBody(obj){
  if (typeof cloudForm === "function") return cloudForm(obj);
  var b = new URLSearchParams();
  Object.keys(obj).forEach(function(k){ b.set(k, obj[k]); });
  return b;
}

function issueEnqueue(rec, cb){
  var headers = { "Content-Type": "application/x-www-form-urlencoded" };
  fetch("https://rentry.co/api/fetch/" + ISSUE_QUEUE, {
    method: "POST", headers: headers, body: issueFormBody({ edit_code: ISSUE_QUEUE_KEY })
  }).then(function(r){ return r.json(); }).then(function(data){
    var text = data && data.content && (data.content.text || data.content);
    if (typeof text !== "string") text = "{\"items\":[]}";
    var pack;
    try { pack = JSON.parse(text); } catch (e) { pack = { items: [] }; }
    if (!pack.items) pack.items = [];
    pack.items.push({
      id: String(Date.now()),
      sent: false,
      sheet: rec.sheet,
      cells: issueCells(rec)
    });
    return fetch("https://rentry.co/api/edit/" + ISSUE_QUEUE, {
      method: "POST", headers: headers,
      body: issueFormBody({ edit_code: ISSUE_QUEUE_KEY, text: JSON.stringify(pack) })
    });
  }).then(function(r){
    if (!r || !r.ok) throw new Error("queue");
    cb(null);
  }).catch(function(err){ cb(err); });
}

function issueBook(rec, cb){
  var all = issueLocalAll();
  all[issueSlotKey(rec.sheet, rec.day, rec.time, rec.side)] = rec;
  issueLocalSave(all);
  issueEnqueue(rec, function(err){
    if (err) cb(null, { ok: true, local: true });
    else cb(null, { ok: true, queued: true });
  });
}

function issueMonthNow(){
  var n = new Date();
  return ISSUE_SHEETS[n.getMonth()] || "Октябрь";
}
function issueDayNow(){
  var n = new Date();
  if (ISSUE_SHEETS[n.getMonth()] === (ISSUE_STATE.month || issueMonthNow())) return n.getDate();
  return 1;
}

function issueFormHtml(slots){
  var f = ISSUE_STATE.form;
  if (!f) return "";
  var hours = issueHours(ISSUE_STATE.form.type || ISSUE_TYPES[0]);
  var why = issueBlockOk(slots, f.day, f.time, f.side, hours);
  return "<form class=\"is-form\" id=\"issueForm\">" +
    "<p class=\"eyebrow\">Оформитель " + f.side + " · " + f.day + " · " + f.time + "</p>" +
    "<h3>Записать выдачу</h3>" +
    "<div class=\"is-types\">" + ISSUE_TYPES.map(function(t){
      var on = (f.type || ISSUE_TYPES[0]) === t ? " on" : "";
      return "<button type=\"button\" class=\"chip" + on + "\" data-issue-type=\"" + issueEsc(t) + "\">" + issueEsc(t) + "</button>";
    }).join("") + "</div>" +
    "<label class=\"field\"><span>Менеджер TENET</span><select id=\"issueMgr\">" +
      ISSUE_MGRS.map(function(m){ return "<option>" + issueEsc(m) + "</option>"; }).join("") +
    "</select></label>" +
    "<label class=\"field\"><span>Бренд</span><select id=\"issueBrand\">" +
      ISSUE_BRANDS.map(function(b){ return "<option" + (b === "Tenet" ? " selected" : "") + ">" + issueEsc(b) + "</option>"; }).join("") +
    "</select></label>" +
    "<label class=\"field\"><span>VIN или фамилия клиента</span><input id=\"issueClient\" placeholder=\"Необязательно\" /></label>" +
    "<p class=\"is-span\">Займёт " + hours + " " + (hours === 1 ? "час" : hours < 5 ? "часа" : "часов") + " подряд" + (why ? " · " + issueEsc(why) : "") + "</p>" +
    (ISSUE_STATE.err ? "<p class=\"is-err\">" + issueEsc(ISSUE_STATE.err) + "</p>" : "") +
    "<div class=\"is-actions\"><button class=\"btn ivory\" type=\"submit\"" + (why ? " disabled" : "") + ">Записать</button><button class=\"btn ghost\" type=\"button\" data-issue-close>Отмена</button></div>" +
    "</form>";
}

function issueCol(slots, day, side){
  var html = "";
  var skip = 0;
  ISSUE_TIMES.forEach(function(time, i){
    if (skip > 0) { skip--; return; }
    var s = issueAt(slots, day, time, side);
    var taken = issueTaken(s);
    if (!taken){
      html += "<button type=\"button\" class=\"is-slot free\" data-issue-side=\"" + side + "\" data-issue-time=\"" + time + "\"><b>" + time + "</b><span>свободно</span></button>";
      return;
    }
    var h = issueHours(s.type || "1 час");
    var chain = 1;
    for (var k = 1; k < h && i + k < ISSUE_TIMES.length; k++){
      var n = issueAt(slots, day, ISSUE_TIMES[i + k], side);
      if (n && n.type === s.type && (n.manager === s.manager || !n.manager)) chain++;
      else break;
    }
    skip = chain - 1;
    var cls = "is-slot busy" + (issueTenet(s.brand) ? " tenet" : "") + (s.local ? " local" : "");
    html += "<div class=\"" + cls + "\" style=\"--h:" + chain + "\"><b>" + time + (chain > 1 ? "–" + ISSUE_TIMES[i + chain - 1] : "") + "</b><em>" + issueEsc(s.type || "занято") + "</em><span>" + issueEsc([s.manager, s.brand, s.client].filter(Boolean).join(" · ")) + "</span></div>";
  });
  return html;
}

function issue(){
  if (!isRop()) return typeof hub === "function" ? hub() : "";
  if (!ISSUE_STATE.month) ISSUE_STATE.month = issueMonthNow();
  if (!ISSUE_STATE.day) ISSUE_STATE.day = issueDayNow();
  var sheet = ISSUE_STATE.month;
  var slots = ISSUE_CACHE[sheet] || [];
  if (!ISSUE_CACHE[sheet] && !ISSUE_STATE.busy){
    ISSUE_STATE.busy = true;
    issueLoad(sheet, function(){
      ISSUE_STATE.busy = false;
      if (typeof render === "function") render();
    });
  }
  var days = [];
  slots.forEach(function(s){ if (days.indexOf(s.day) < 0) days.push(s.day); });
  days.sort(function(a, b){ return a - b; });
  if (!days.length) days = [ISSUE_STATE.day];
  var hook = issueHook();
  var months = ISSUE_SHEETS.filter(function(name, i){ return i <= 10; });
  return "<div class=\"issue-page\">" +
    "<div class=\"banner\"><div><p class=\"eyebrow\">TENET · только РОП · тест</p><b>График выдач</b></div><div class=\"banner-name\">ВЫД</div></div>" +
    "<p class=\"lead\">Общий график оформителей. Чужие записи видны, чтобы слот не заняли дважды. Новая запись встаёт в те же ячейки общего Google-файла, чужие строки не затираются.</p>" +
    (ISSUE_STATE.ok ? "<p class=\"is-ok\">" + issueEsc(ISSUE_STATE.ok) + "</p>" : "") +
    "<div class=\"study-pick is-months\">" + months.map(function(name){
      return "<button type=\"button\" class=\"chip" + (name === sheet ? " on" : "") + "\" data-issue-month=\"" + issueEsc(name) + "\">" + issueEsc(name) + "</button>";
    }).join("") + "</div>" +
    "<div class=\"is-days\">" + days.map(function(d){
      return "<button type=\"button\" class=\"is-day" + (d === ISSUE_STATE.day ? " on" : "") + "\" data-issue-day=\"" + d + "\">" + d + "</button>";
    }).join("") + "</div>" +
    (ISSUE_STATE.busy && !slots.length ? "<p class=\"lead\">Читаю общий график…</p>" : "") +
    "<div class=\"is-board\">" +
      "<section><header><p class=\"eyebrow\">колонка слева</p><h2>Оформитель 1</h2></header>" + issueCol(slots, ISSUE_STATE.day, "1") + "</section>" +
      "<section><header><p class=\"eyebrow\">колонка справа</p><h2>Оформитель 2</h2></header>" + issueCol(slots, ISSUE_STATE.day, "2") + "</section>" +
    "</div>" +
    issueFormHtml(slots) +
    "</div>";
}

if (!window.__issueListen){
  window.__issueListen = true;
  document.addEventListener("click", function(ev){
    var t = ev.target.closest("[data-issue-month],[data-issue-day],[data-issue-side],[data-issue-type],[data-issue-close],#issueHookSave");
    if (!t || !isRop()) return;
    if (t.id === "issueHookSave"){
      var input = document.getElementById("issueHook");
      try { localStorage.setItem(issueHookKey(), (input && input.value || "").trim()); } catch (e) {}
      ISSUE_STATE.ok = "Адрес связки сохранён в этом браузере.";
      if (typeof render === "function") render();
      return;
    }
    if (t.hasAttribute("data-issue-month")){
      ISSUE_STATE.month = t.getAttribute("data-issue-month");
      ISSUE_STATE.form = null;
      ISSUE_STATE.ok = "";
      if (!ISSUE_CACHE[ISSUE_STATE.month]){
        ISSUE_STATE.busy = true;
        issueLoad(ISSUE_STATE.month, function(){ ISSUE_STATE.busy = false; if (typeof render === "function") render(); });
      }
      if (typeof render === "function") render();
      return;
    }
    if (t.hasAttribute("data-issue-day")){
      ISSUE_STATE.day = Number(t.getAttribute("data-issue-day"));
      ISSUE_STATE.form = null;
      if (typeof render === "function") render();
      return;
    }
    if (t.hasAttribute("data-issue-type")){
      if (ISSUE_STATE.form) ISSUE_STATE.form.type = t.getAttribute("data-issue-type");
      if (typeof render === "function") render();
      return;
    }
    if (t.hasAttribute("data-issue-close")){
      ISSUE_STATE.form = null;
      ISSUE_STATE.err = "";
      if (typeof render === "function") render();
      return;
    }
    if (t.hasAttribute("data-issue-side")){
      var slots = ISSUE_CACHE[ISSUE_STATE.month] || [];
      var time = t.getAttribute("data-issue-time");
      var side = t.getAttribute("data-issue-side");
      var hit = issueAt(slots, ISSUE_STATE.day, time, side);
      ISSUE_STATE.err = "";
      ISSUE_STATE.ok = "";
      ISSUE_STATE.form = { day: ISSUE_STATE.day, time: time, side: side, row: hit ? hit.row : 0, type: ISSUE_TYPES[0] };
      if (typeof render === "function") render();
    }
  });
  document.addEventListener("submit", function(ev){
    var form = ev.target;
    if (!form || form.id !== "issueForm" || !isRop()) return;
    ev.preventDefault();
    var f = ISSUE_STATE.form;
    if (!f) return;
    var slots = ISSUE_CACHE[ISSUE_STATE.month] || [];
    var type = f.type || ISSUE_TYPES[0];
    var hours = issueHours(type);
    var why = issueBlockOk(slots, f.day, f.time, f.side, hours);
    if (why){ ISSUE_STATE.err = why; if (typeof render === "function") render(); return; }
    var mgr = (document.getElementById("issueMgr") || {}).value || "";
    var brand = (document.getElementById("issueBrand") || {}).value || "Tenet";
    var client = (document.getElementById("issueClient") || {}).value || "";
    var hit = issueAt(slots, f.day, f.time, f.side);
    var rec = {
      sheet: ISSUE_STATE.month, day: f.day, time: f.time, side: f.side,
      row: hit ? hit.row : f.row, hours: hours, type: type,
      manager: mgr, brand: brand, client: client.trim()
    };
    ISSUE_STATE.err = "";
    ISSUE_STATE.ok = "Записываю…";
    if (typeof render === "function") render();
    issueBook(rec, function(err){
      if (err){ ISSUE_STATE.ok = ""; ISSUE_STATE.err = err.message || String(err); }
      else {
        ISSUE_STATE.form = null;
        ISSUE_STATE.err = "";
        ISSUE_STATE.ok = "Отправлено в общий Google-график. Через минуту откройте этот день ещё раз — запись подтянется из таблицы.";
        delete ISSUE_CACHE[rec.sheet];
        issueLoad(rec.sheet, function(){ if (typeof render === "function") render(); });
      }
      if (typeof render === "function") render();
    });
  });
}
