/**
 * Одноразовая связка. Вставить в Расширения → Apps Script у общего графика
 * и развернуть как веб-приложение: доступ «все».
 * Пишет только в пустые ячейки слота. Чужие выдачи не затирает.
 */
var ISSUE_SSID = "1lXlvHTVbrvvgX3XwdFw8Ktiaoat8OUl5IBdi0bTs1SE";

function doGet(e) {
  var p = e && e.parameter ? e.parameter : {};
  var cb = p.callback || "issueHookCb";
  var out;
  try { out = issueHandle_(p); }
  catch (err) { out = { ok: false, error: String(err) }; }
  return ContentService
    .createTextOutput(cb + "(" + JSON.stringify(out) + ")")
    .setMimeType(ContentService.MimeType.JAVASCRIPT);
}

function issueHandle_(p) {
  if (p.action !== "book") return { ok: false, error: "action" };
  var ss = SpreadsheetApp.openById(ISSUE_SSID);
  var sh = ss.getSheetByName(p.sheet);
  if (!sh) return { ok: false, error: "нет листа" };
  var row = Number(p.row);
  var hours = Number(p.hours) || 1;
  if (!row || hours < 1 || hours > 6) return { ok: false, error: "слот" };
  var side = String(p.side) === "2" ? 2 : 1;
  var cols = side === 1
    ? { type: 3, mgr: 4, brand: 5, who: 6 }
    : { type: 10, mgr: 11, brand: 12, who: 13 };
  for (var i = 0; i < hours; i++) {
    var v = String(sh.getRange(row + i, cols.type).getDisplayValue() || "").trim();
    if (v && v !== "-" && v !== "—") return { ok: false, error: "слот занят" };
  }
  for (var j = 0; j < hours; j++) {
    sh.getRange(row + j, cols.type).setValue(p.type || "");
    sh.getRange(row + j, cols.mgr).setValue(p.manager || "");
    sh.getRange(row + j, cols.brand).setValue(p.brand || "");
    if (j === 0) sh.getRange(row + j, cols.who).setValue(p.client || "");
  }
  return { ok: true };
}
