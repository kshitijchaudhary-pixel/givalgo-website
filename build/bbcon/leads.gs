/**
 * bbcon lucky-draw leads → Google Sheet.
 *
 * A Google Apps Script web app bound to the leads spreadsheet. The entry form
 * (bbcon/index.html, live at givalgo.ai/bbcon) POSTs each entry here,
 * form-encoded; this appends a row to the "Leads" tab and answers
 * {"ok": true}. Setup and deploy steps: build/bbcon/README.md.
 *
 * The sheet also gets a "bbcon" menu:
 *   Draw 2 winners            the main draw
 *   Draw 1 replacement winner for a winner who never replies
 * Each email gets one chance however many times it was submitted, anyone
 * already drawn is left out, and @givalgo.ai addresses (staff, and our own
 * test entries) never win. Every pick is recorded on the "Draw log" tab.
 */

const LEADS_TAB = 'Leads';
const DRAW_TAB = 'Draw log';
const HEADERS = ['Submitted at', 'Full name', 'Email', 'Organization', 'Source', 'Repeat entry'];
const DRAW_HEADERS = ['Drawn at', 'Drawn by', 'Draw', 'Eligible entrants', 'Name', 'Email', 'Organization'];
const WINNERS = 2;
const INELIGIBLE_DOMAINS = ['givalgo.ai'];
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function doPost(e) {
  const p = (e && e.parameter) || {};
  // Honeypot: the form hides a "website" field that only bots fill in. Say
  // yes so they move on, and write nothing.
  if (p.website) return json_({ ok: true });

  const name = clip_(p.full_name, 120);
  const email = clip_(p.email, 254).toLowerCase();
  const org = clip_(p.organization, 160);
  const source = clip_(p.source, 40) || 'bbcon';
  if (name.length < 2 || org.length < 2 || !EMAIL_RE.test(email)) {
    return json_({ ok: false, error: 'invalid' });
  }

  const lock = LockService.getScriptLock();
  if (!lock.tryLock(15000)) return json_({ ok: false, error: 'busy' });
  try {
    const sheet = tab_(LEADS_TAB, HEADERS);
    const repeat = column_(sheet, 3).has(email);
    sheet.appendRow([new Date(), cell_(name), cell_(email), cell_(org), cell_(source), repeat ? 'yes' : '']);
  } finally {
    lock.releaseLock();
  }
  return json_({ ok: true });
}

// Opening the /exec URL in a browser is a quick "is it deployed?" check.
function doGet() {
  return json_({ ok: true, service: 'bbcon-leads' });
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('bbcon')
    .addItem('Draw ' + WINNERS + ' winners', 'drawWinners')
    .addItem('Draw 1 replacement winner', 'drawReplacement')
    .addToUi();
}

function drawWinners() {
  const ui = SpreadsheetApp.getUi();
  if (column_(tab_(DRAW_TAB, DRAW_HEADERS), 6).size) {
    const more = ui.alert('Winners already drawn',
      'The "' + DRAW_TAB + '" tab already has winners. Draw ' + WINNERS + ' more anyway?',
      ui.ButtonSet.YES_NO);
    if (more !== ui.Button.YES) return;
  }
  draw_(WINNERS, 'Winner');
}

function drawReplacement() {
  draw_(1, 'Replacement');
}

// Picks `count` different people at random from everyone eligible.
function draw_(count, kind) {
  const ui = SpreadsheetApp.getUi();
  const log = tab_(DRAW_TAB, DRAW_HEADERS);
  const drawn = column_(log, 6);
  const pool = entrants_().filter(function (e) {
    return !drawn.has(e.email) && INELIGIBLE_DOMAINS.indexOf(e.email.split('@')[1]) === -1;
  });
  if (pool.length < count) {
    ui.alert('Not enough entries', 'Only ' + pool.length + ' eligible entrant(s) left to draw from.', ui.ButtonSet.OK);
    return;
  }

  // Partial Fisher–Yates: the first `count` slots end up a uniform random pick.
  for (let i = 0; i < count; i++) {
    const j = i + Math.floor(Math.random() * (pool.length - i));
    const t = pool[i]; pool[i] = pool[j]; pool[j] = t;
  }
  const picked = pool.slice(0, count);

  const at = new Date();
  const by = Session.getActiveUser().getEmail();
  picked.forEach(function (w) {
    log.appendRow([at, by, kind, pool.length, cell_(w.name), cell_(w.email), cell_(w.org)]);
  });
  ui.alert('🎉 ' + (count === 1 ? kind : 'Winners') + ' (from ' + pool.length + ' eligible entrants)',
    picked.map(function (w) { return w.name + ' · ' + w.email + ' · ' + w.org; }).join('\n') +
    '\n\nRecorded on the "' + DRAW_TAB + '" tab.',
    ui.ButtonSet.OK);
}

// ── helpers ──

// Everyone who entered, one per email (their first entry).
function entrants_() {
  const sheet = tab_(LEADS_TAB, HEADERS);
  const n = sheet.getLastRow() - 1;
  const rows = n > 0 ? sheet.getRange(2, 1, n, 4).getValues() : [];
  const seen = new Set();
  const out = [];
  rows.forEach(function (r) {
    const email = String(r[2]).trim().toLowerCase();
    if (!email || seen.has(email)) return;
    seen.add(email);
    out.push({ name: String(r[1]), email: email, org: String(r[3]) });
  });
  return out;
}

function tab_(name, headers) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(name);
  if (!sheet) sheet = ss.insertSheet(name);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
    sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

// The lower-cased values of one column, header row excluded.
function column_(sheet, col) {
  const n = sheet.getLastRow() - 1;
  if (n < 1) return new Set();
  return new Set(sheet.getRange(2, col, n, 1).getValues().map(function (r) {
    return String(r[0]).trim().toLowerCase();
  }));
}

function clip_(v, max) {
  return String(v == null ? '' : v).replace(/\s+/g, ' ').trim().slice(0, max);
}

// Sheets treats a leading = + - @ as a formula. Entrant text is data, never a
// formula, so prefix those with an apostrophe (shown as plain text).
function cell_(v) {
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
