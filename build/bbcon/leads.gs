/**
 * bbcon lucky-draw leads → Google Sheet.
 *
 * A Google Apps Script web app bound to the leads spreadsheet. The entry form
 * (bbcon/index.html, live at givalgo.ai/bbcon) POSTs each entry here,
 * form-encoded; this appends a row to the "Leads" tab and answers
 * {"ok": true}. Setup and deploy steps: build/bbcon/README.md.
 *
 * Only people who scanned the booth QR code can enter. The code carries an
 * entry key (givalgo.ai/bbcon/#<key>); entries without the current key are
 * refused. The key is kept in this script's properties, never in the website
 * repo (which is public). The sheet gets a "bbcon" menu:
 *   Open entries / new booth link  makes a new key and shows the booth link
 *                                  (any older QR code stops working)
 *   Show booth link                shows the current link again
 *   Close entries                  refuses every entry until reopened
 *   Draw 2 winners                 the main draw
 *   Draw 1 replacement winner      for a winner who never replies
 * Each email gets one chance however many times it was submitted, anyone
 * already drawn is left out, and @givalgo.ai addresses (staff, and our own
 * test entries) never win. Every pick is recorded on the "Draw log" tab.
 */

const LEADS_TAB = 'Leads';
const DRAW_TAB = 'Draw log';
const HEADERS = ['Submitted at', 'Full name', 'Email', 'Organization', 'Source', 'Repeat entry', 'Discover use'];
const DRAW_HEADERS = ['Drawn at', 'Drawn by', 'Draw', 'Eligible entrants', 'Name', 'Email', 'Organization'];
const WINNERS = 2;
const INELIGIBLE_DOMAINS = ['givalgo.ai'];
const BOOTH_URL = 'https://givalgo.ai/bbcon/booth/';
const KEY_PROP = 'ENTRY_KEY';
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function doPost(e) {
  const p = (e && e.parameter) || {};
  // Honeypot: the form hides a "website" field that only bots fill in. Say
  // yes so they move on, and write nothing.
  if (p.website) return json_({ ok: true });

  // No key means entries are closed (or not opened yet). A wrong key is an
  // old QR code or someone who never scanned one.
  const key = entryKey_();
  if (!key) return json_({ ok: false, error: 'closed' });
  if (String(p.k || '').toLowerCase() !== key) return json_({ ok: false, error: 'key' });

  const name = clip_(p.full_name, 120);
  const email = clip_(p.email, 254).toLowerCase();
  const org = clip_(p.organization, 160);
  const source = clip_(p.source, 40) || 'bbcon';
  // "; "-separated answers to "What would you use Discover for?". Not
  // required here, so an older copy of the form can still submit.
  const uses = clip_(p.uses, 300);
  if (name.length < 2 || org.length < 2 || !EMAIL_RE.test(email)) {
    return json_({ ok: false, error: 'invalid' });
  }

  const lock = LockService.getScriptLock();
  if (!lock.tryLock(15000)) return json_({ ok: false, error: 'busy' });
  try {
    const sheet = tab_(LEADS_TAB, HEADERS);
    const repeat = column_(sheet, 3).has(email);
    sheet.appendRow([new Date(), cell_(name), cell_(email), cell_(org), cell_(source), repeat ? 'yes' : '', cell_(uses)]);
  } finally {
    lock.releaseLock();
  }
  return json_({ ok: true });
}

// Opening the /exec URL in a browser is a quick "is it deployed?" check.
function doGet() {
  return json_({ ok: true, service: 'bbcon-leads', entries_open: !!entryKey_() });
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('bbcon')
    .addItem('Open entries / new booth link', 'openEntries')
    .addItem('Show booth link', 'showBoothLink')
    .addItem('Close entries', 'closeEntries')
    .addSeparator()
    .addItem('Draw ' + WINNERS + ' winners', 'drawWinners')
    .addItem('Draw 1 replacement winner', 'drawReplacement')
    .addToUi();
}

function openEntries() {
  const ui = SpreadsheetApp.getUi();
  if (entryKey_()) {
    const ok = ui.alert('Replace the entry key?',
      'Entries are already open. A new key means the QR code on the booth screen (and any printed ' +
      'copy) stops working until you open the new booth link. Continue?', ui.ButtonSet.YES_NO);
    if (ok !== ui.Button.YES) return;
  }
  // 8 hex characters from a random UUID: about 4 billion possibilities, far
  // beyond what anyone could try against this script during the event. Kept
  // short so the QR code stays small and quick to scan.
  const key = Utilities.getUuid().replace(/-/g, '').slice(0, 8);
  PropertiesService.getScriptProperties().setProperty(KEY_PROP, key);
  showBoothLink();
}

function showBoothLink() {
  const ui = SpreadsheetApp.getUi();
  const key = entryKey_();
  if (!key) {
    ui.alert('Entries are closed', 'Use bbcon → Open entries / new booth link first.', ui.ButtonSet.OK);
    return;
  }
  ui.alert('Booth link',
    'Open this on the booth screen, full screen:\n\n' + BOOTH_URL + '#' + key +
    '\n\nIts QR code carries the entry key. Only share it with people staffing the booth.',
    ui.ButtonSet.OK);
}

function closeEntries() {
  const ui = SpreadsheetApp.getUi();
  const ok = ui.alert('Close entries?',
    'Every entry is refused until you open entries again, which makes a new QR code.', ui.ButtonSet.YES_NO);
  if (ok !== ui.Button.YES) return;
  PropertiesService.getScriptProperties().deleteProperty(KEY_PROP);
  ui.alert('Entries closed', 'The form now tells visitors the draw isn\'t taking entries.', ui.ButtonSet.OK);
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

function entryKey_() {
  return (PropertiesService.getScriptProperties().getProperty(KEY_PROP) || '').toLowerCase();
}

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
  } else if (sheet.getLastColumn() < headers.length) {
    // A column was added after this tab was made (like "Discover use"):
    // extend the header row so the new values land under a name.
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold');
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
