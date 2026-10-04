'use strict';
/* Core: state, API, server-driven i18n, formatting, shells (phone tab bar / desktop sidebar), router, realtime. */

const ls = {
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage blocked */ } },
  del(k) { try { localStorage.removeItem(k); } catch (e) { /* storage blocked */ } }
};
const $ = (s, el) => (el || document).querySelector(s);
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const isDesk = () => window.innerWidth >= 900;
const uuid = () => (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2));

const S = {
  token: ls.get('token'), user: null, sub: null, shops: [], shopId: ls.get('shopId'), cfg: null,
  products: [], cart: {}, strings: {}, lang: ls.get('lang'), locale: 'en', feed: [], regions: null,
  range: 'week', period: 'monthly', selPlan: 'business', offline: false, route: { name: '', params: [] },
  pay: null, lastSale: null, selProduct: null, search: '', plansData: null, after: null, country: null
};
const LANGS = { en: 'English', sw: 'Kiswahili' };
const DEC = { TZS: 0, KES: 2, INR: 2, BRL: 2, USD: 2 };

/* ---------- Icons (SF Symbols style strokes) ---------- */
const ICON = {
  sell: 'M3 4h2.5l2.2 11h10.6L20.5 8H6.2M9 20h.01M18 20h.01',
  products: 'M12 3l8 4v10l-8 4-8-4V7zM4 7l8 4 8-4M12 11v10',
  insights: 'M5 20V11M12 20V4M19 20v-6',
  shops: 'M4 9l1.5-5h13L20 9v1a3 3 0 0 1-5.3 1.9A3 3 0 0 1 12 13a3 3 0 0 1-2.7-1.1A3 3 0 0 1 4 10zM5 14v6h14v-6',
  account: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21c1-4 4-6 8-6s7 2 8 6',
  history: 'M6 3h12v18l-3-2-3 2-3-2-3 2zM9 8h6M9 12h6',
  team: 'M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM3 20c0-3 3-5 6-5s6 2 6 5M16 11a3 3 0 0 0 0-6M17 15c2.5.3 4 2 4 5',
  float: 'M3 7h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM3 7l13-3v3M17 14h.01',
  overview: 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z',
  plus: 'M12 5v14M5 12h14',
  search: 'M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM20 20l-4-4',
  check: 'M5 12.5l4.5 4.5L19 7.5',
  back: 'M15 5l-7 7 7 7',
  share: 'M12 15V3M8 7l4-4 4 4M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7',
  cart: 'M3 4h2.5l2.2 11h10.6L20.5 8H6.2M9 20h.01M18 20h.01',
  shield: 'M12 3l7 3v5c0 5-3 8-7 10-4-2-7-5-7-10V6zM9 12l2 2 4-4',
  down: 'M12 5v14M5 12l7 7 7-7',
  up: 'M12 19V5M5 12l7-7 7 7',
  phone: 'M8 2h8a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zM11 18h2'
};
const ic = (n, size, sw) => `<svg width="${size || 24}" height="${size || 24}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw || 1.7}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${ICON[n]}"/></svg>`;
const chev = '<i class="chev"></i>';
const PALETTE = ['#E07B00', '#248A3D', '#0071E3', '#AF52DE', '#8E5A2B', '#B3261E', '#0A84A8', '#5E6C84'];
const hue = s => PALETTE[[...String(s)].reduce((a, c) => a + c.charCodeAt(0), 0) % PALETTE.length];
const initial = s => esc(String(s || '?').trim().charAt(0).toUpperCase());

/* ---------- i18n: strings come from the server, formatting from the browser's CLDR data ---------- */
function t(key, vars) {
  let s = S.strings[key];
  if (s === undefined) s = key;
  if (vars) s = s.replace(/\{(\w+)\}/g, (m, k) => (vars[k] !== undefined ? esc(vars[k]) : m));
  return s;
}
function tn(key, n, vars) {
  const k = n === 1 && S.strings[key + '.one'] !== undefined ? key + '.one' : key + '.other';
  return t(S.strings[k] !== undefined ? k : key, Object.assign({ n }, vars));
}
async function loadStrings() {
  const base = (navigator.language || 'en').split('-')[0];
  // The user's choice wins, then the browser language, then the shop's own locale.
  let lang = S.lang || (LANGS[base] ? base : (S.cfg && S.cfg.locale.split('-')[0])) || 'en';
  if (!LANGS[lang]) lang = 'en';
  S.lang = lang;
  const cached = ls.get('strings:' + lang);
  try {
    const r = await fetch('/api/i18n/' + lang);
    const data = await r.json();
    S.strings = data.strings;
    ls.set('strings:' + lang, JSON.stringify(S.strings));
  } catch (e) {
    S.strings = cached ? JSON.parse(cached) : {};
  }
  const loc = S.cfg && S.cfg.locales.find(l => l.startsWith(lang + '-'));
  S.locale = loc || (lang === 'sw' ? 'sw-TZ' : 'en-US');
  document.documentElement.lang = lang;
}
const decOf = c => (DEC[c] !== undefined ? DEC[c] : 2);
function money(minor, cur) {
  const c = cur || (S.cfg && S.cfg.currency.code) || 'USD';
  const d = decOf(c);
  return new Intl.NumberFormat(S.locale, { style: 'currency', currency: c, minimumFractionDigits: d, maximumFractionDigits: d }).format(minor / Math.pow(10, d));
}
function moneyShort(minor, cur) {
  const c = cur || (S.cfg && S.cfg.currency.code) || 'USD';
  return new Intl.NumberFormat(S.locale, { notation: 'compact', maximumFractionDigits: 1 }).format(minor / Math.pow(10, decOf(c)));
}
const toMinor = (str, cur) => Math.round(parseFloat(String(str).replace(/[^0-9.\-]/g, '') || '0') * Math.pow(10, decOf(cur || (S.cfg && S.cfg.currency.code))));
const fromMinor = (n, cur) => String(n / Math.pow(10, decOf(cur || (S.cfg && S.cfg.currency.code))));
const fmtTime = ms => new Intl.DateTimeFormat(S.locale, { hour: '2-digit', minute: '2-digit' }).format(ms);
const fmtDate = ms => new Intl.DateTimeFormat(S.locale, { day: 'numeric', month: 'short', year: 'numeric' }).format(ms);
function ago(ms) {
  const d = (Date.now() - ms) / 1000;
  const rtf = new Intl.RelativeTimeFormat(S.locale, { numeric: 'auto', style: 'short' });
  if (d < 45) return t('time.now');
  if (d < 3600) return rtf.format(-Math.round(d / 60), 'minute');
  if (d < 86400) return rtf.format(-Math.round(d / 3600), 'hour');
  return rtf.format(-Math.round(d / 86400), 'day');
}

/* ---------- API ---------- */
const deviceName = () => ls.get('device') || (isDesk() ? 'Web (desktop)' : 'Web (phone)');
async function api(path, o) {
  o = o || {};
  const headers = { 'Content-Type': 'application/json', 'X-Device': deviceName() };
  if (S.token) headers.Authorization = 'Bearer ' + S.token;
  let res;
  try {
    res = await fetch('/api' + path, { method: o.method || 'GET', headers, body: o.body ? JSON.stringify(o.body) : undefined });
  } catch (e) {
    S.offline = true; syncOfflineBanner();
    throw e;
  }
  S.offline = false; syncOfflineBanner();
  const text = await res.text();
  const data = text ? JSON.parse(text) : {};
  if (!res.ok) {
    const err = new Error((data.error && data.error.message) || res.statusText);
    err.code = data.error && data.error.code; err.status = res.status;
    if (res.status === 401 && S.token) { signOutLocal(); location.hash = '#/login'; }
    throw err;
  }
  return data;
}
const errMsg = e => (e && e.code && S.strings['error.' + e.code]) || (e && e.message) || t('error.generic');
function syncOfflineBanner() { document.body.classList.toggle('is-offline', !!S.offline); }

/* ---------- Toast and errors ---------- */
let toastTimer;
function toast(html) {
  const el = $('#toast');
  el.innerHTML = html;
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 3200);
}
function showErr(msg) {
  const el = $('#err');
  if (el) { el.className = 'err'; el.textContent = msg; el.setAttribute('role', 'alert'); }
  else toast((msg));
}

/* ---------- Session ---------- */
function signOutLocal() {
  S.token = null; S.user = null; S.sub = null; S.shops = []; S.cfg = null; S.shopId = null; S.cart = {}; S.feed = [];
  ls.del('token'); ls.del('shopId'); ls.del('me');
  if (S.ws) { const w = S.ws; S.ws = null; w.close(); }
}
async function bootstrap() {
  let me;
  try {
    me = await api('/me');
    ls.set('me', JSON.stringify(me));
  } catch (e) {
    // Offline: open from the last known account state so selling can continue.
    const cached = ls.get('me');
    if (e instanceof TypeError && cached) me = JSON.parse(cached); else throw e;
  }
  S.user = me.user; S.sub = me.subscription; S.shops = me.shops;
  if (S.shops.length && !S.shops.find(s => s.id === S.shopId)) S.shopId = S.shops[0].id;
  if (S.shopId) { ls.set('shopId', S.shopId); await loadCfg(); } else { S.cfg = null; }
  await loadStrings();
  connectWS();
  flushOutbox();
}
async function loadCfg() {
  try {
    S.cfg = await api('/shops/' + S.shopId + '/config');
    ls.set('cfg:' + S.shopId, JSON.stringify(S.cfg));
  } catch (e) {
    const c = ls.get('cfg:' + S.shopId);
    if (c && e instanceof TypeError) S.cfg = JSON.parse(c); else throw e;
  }
}
const isAgent = () => S.cfg && S.cfg.shop.type === 'mobile_money';
const myRole = () => { const s = S.shops.find(x => x.id === S.shopId); return s ? s.role : null; };
const canManage = () => ['owner', 'manager'].includes(myRole());
const homeRoute = () => (S.shops.length ? (isAgent() ? '#/float' : '#/sell') : (S.sub ? '#/setup' : '#/plans'));

/* ---------- Realtime ---------- */
function connectWS() {
  if (!S.token || S.ws) return;
  const ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws?token=' + encodeURIComponent(S.token));
  S.ws = ws;
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.type === 'activity') onActivity(m.activity);
  };
  ws.onclose = () => { if (S.ws === ws) { S.ws = null; if (S.token) setTimeout(connectWS, 2000); } };
}
function activityText(a) {
  const d = a.data || {};
  const v = { name: a.userName, item: d.name, shop: a.shopName };
  switch (a.kind) {
    case 'sale': return tn('act.sale', d.items, Object.assign(v, { items: d.items, total: money(d.total, d.currency), first: d.first, serial: d.serial || '' })) + (d.serial ? ' · ' + t('act.serial', { serial: d.serial }) : '');
    case 'void': return t('act.void', Object.assign(v, { number: d.number, total: money(d.total, d.currency) }));
    case 'price_change': return t('act.price_change', Object.assign(v, { from: money(d.from), to: money(d.to) }));
    case 'stock_adjust': return t('act.stock_adjust', Object.assign(v, { from: d.from, to: d.to }));
    case 'product_added': return t('act.product_added', v);
    case 'product_removed': return t('act.product_removed', v);
    case 'member_added': return t('act.member_added', Object.assign(v, { member: d.name, role: t('role.' + d.role) }));
    case 'shop_created': return t('act.shop_created', v);
    case 'low_stock': return t('act.low_stock', { item: d.name, n: d.stock });
    case 'low_float': return t('act.low_float', { network: netName(d.network) });
    case 'float_tx': return t('act.float_tx.' + d.kind, Object.assign(v, { network: netName(d.network), amount: money(d.amount, d.currency) }));
    case 'float_adjust': return t('act.float_adjust', Object.assign(v, { network: netName(d.network), amount: money(d.delta, d.currency) }));
    default: return a.kind;
  }
}
function netName(id) {
  if (id === 'cash') return t('float.cash');
  const n = S.cfg && S.cfg.networks.find(x => x.id === id);
  return n ? n.name : id;
}
function onActivity(a) {
  S.feed.unshift(a); S.feed = S.feed.slice(0, 100);
  if (S.user && a.userName !== S.user.name && a.kind !== 'low_stock') toast(activityText(a));
  softRefresh();
}
let refreshTimer;
function softRefresh() {
  const n = S.route.name;
  if (!['shops', 'team', 'insights', 'products', 'float', 'history', 'sell'].includes(n)) return;
  clearTimeout(refreshTimer);
  refreshTimer = setTimeout(() => {
    const a = document.activeElement;
    if (a && ['INPUT', 'SELECT', 'TEXTAREA'].includes(a.tagName) && a.id !== 'q') return;
    render(true);
  }, 250);
}

/* ---------- Offline outbox: sales are queued with their idempotency key and replayed ---------- */
const outbox = () => { try { return JSON.parse(ls.get('outbox') || '[]'); } catch (e) { return []; } };
function queueSale(item) { const q = outbox(); q.push(item); ls.set('outbox', JSON.stringify(q)); }
let flushing = false;
async function flushOutbox() {
  if (flushing || !S.token) return;
  flushing = true;
  try {
    let q = outbox();
    while (q.length) {
      const it = q[0];
      try {
        await api('/shops/' + it.shopId + '/sales', { method: 'POST', body: it.body });
      } catch (e) {
        if (e instanceof TypeError) break;
        if (e.status === 401) break;
      }
      q = outbox().slice(1); ls.set('outbox', JSON.stringify(q));
      if (!q.length) toast((t('offline.synced')));
    }
  } finally { flushing = false; }
}
window.addEventListener('online', flushOutbox);
setInterval(flushOutbox, 6000);

/* ---------- Shells ---------- */
const tabLinks = () => (isAgent()
  ? [['float', '#/float', 'nav.float'], ['history', '#/history', 'nav.history'], ['shops', '#/shops', 'nav.shops'], ['account', '#/account', 'nav.account']]
  : [['sell', '#/sell', 'nav.sell'], ['products', '#/products', 'nav.products'], ['insights', '#/insights', 'nav.insights'], ['shops', '#/shops', 'nav.shops'], ['account', '#/account', 'nav.account']]);
const sideLinks = () => (isAgent()
  ? [['float', '#/float', 'nav.float'], ['history', '#/history', 'nav.history']]
  : [['sell', '#/sell', 'nav.sell'], ['products', '#/products', 'nav.products'], ['insights', '#/insights', 'nav.insights'], ['history', '#/history', 'nav.receipts']]);
const offlineBar = () => `<div class="offline" role="status">${t('offline.banner')}</div>`;

function phone(o) {
  const tabs = o.tabs !== false;
  return `<div class="scr ${tabs ? 'tabs' : ''}">${offlineBar()}
    <div class="nav">${o.left || '<span></span>'}${o.mid ? `<span class="t">${o.mid}</span>` : ''}${o.right || '<span></span>'}</div>
    ${o.title ? `<h1 class="lt">${o.title}</h1>` : ''}
    <div class="body" id="body">${o.body}</div>${o.float || ''}
    ${tabs ? `<nav class="tab" aria-label="Main">${tabLinks().map(([k, h, l]) => `<a href="${h}" class="${o.active === k ? 'on' : ''}" ${o.active === k ? 'aria-current="page"' : ''}>${ic(k, 25, 1.6)}<span>${t(l)}</span></a>`).join('')}</nav>` : ''}
  </div>`;
}
function desk(o) {
  const shopBtns = S.shops.map(s => `<button class="si" data-act="switchShop" data-id="${s.id}" ${s.id === S.shopId ? 'style="font-weight:600"' : ''}><span class="dot ${s.id === S.shopId ? '' : 'off'}"></span>${esc(s.name)}</button>`).join('');
  return `<div class="win"><aside class="side"><div class="brand">Emt Shop</div>
    ${S.cfg ? `<div class="sg">${esc(S.cfg.shop.name).toUpperCase()}</div>${sideLinks().map(([k, h, l]) => `<a href="${h}" class="${o.active === k ? 'on' : ''}">${ic(k, 16, 1.8)}${t(l)}</a>`).join('')}` : ''}
    <div class="sg">${t('nav.allShops').toUpperCase()}</div>
    <a href="#/shops" class="${o.active === 'shops' ? 'on' : ''}">${ic('overview', 16, 1.8)}${t('nav.overview')}</a>
    <a href="#/team" class="${o.active === 'team' ? 'on' : ''}">${ic('team', 16, 1.8)}${t('nav.team')}</a>
    ${S.shops.length > 1 ? `<div class="sg">${t('nav.shops').toUpperCase()}</div>${shopBtns}` : ''}
    <div class="foot"><a href="#/account" class="${o.active === 'account' ? 'on' : ''}" style="margin-bottom:8px">${ic('account', 16, 1.8)}${t('nav.account')}</a>
      ${S.user ? esc(S.user.name) : ''}<br>${S.sub ? t('plan.' + S.sub.plan) : ''}</div></aside>
    <div class="mainw">${offlineBar()}
      <header class="tbar"><div><h1>${o.title}</h1>${o.sub ? `<div class="sub">${o.sub}</div>` : ''}</div><div class="grow"></div>${o.tools || ''}</header>
      <div class="content"><main class="pane" id="body">${o.body}</main>${o.insp ? `<aside class="insp" id="insp">${o.insp}</aside>` : ''}</div>
    </div></div>${o.overlay || ''}`;
}
/** One call renders the right shell for the viewport. */
function page(o) {
  if (isDesk()) return desk(Object.assign({}, o, { title: o.title || '' }));
  return phone(o);
}

/* ---------- Router ---------- */
const VIEWS = {};
const PUBLIC = ['', 'welcome', 'login', 'signup'];
let renderSeq = 0;
async function render(soft) {
  const seq = ++renderSeq;
  const r = S.route;
  if (!S.token && !PUBLIC.includes(r.name)) { location.hash = '#/welcome'; return; }
  if (S.token && !S.user) {
    try { await bootstrap(); } catch (e) { if (!(e instanceof TypeError)) { signOutLocal(); location.hash = '#/welcome'; return; } }
  }
  const fn = VIEWS[r.name || 'welcome'] || VIEWS.welcome;
  let html;
  const scroll = soft && $('#body') ? $('#body').scrollTop : 0;
  try { html = await fn(r.params); } catch (e) {
    if (e instanceof TypeError) html = page({ active: '', title: t('error.offline'), body: `<p class="pad sec">${t('error.offline.body')}</p>` });
    else html = page({ active: '', title: t('error.generic'), body: `<p class="pad red">${esc(errMsg(e))}</p>` });
  }
  if (seq !== renderSeq || html === undefined) return;
  $('#app').innerHTML = html;
  if (soft && $('#body')) $('#body').scrollTop = scroll;
  syncOfflineBanner();
  const after = S.after; S.after = null;
  if (after) after();
  if (!soft) { const h = $('h1'); if (h) { h.setAttribute('tabindex', '-1'); } }
}
async function onHash() {
  const parts = location.hash.replace(/^#\/?/, '').split('/');
  S.route = { name: parts[0] || '', params: parts.slice(1) };
  await render();
}
window.addEventListener('hashchange', onHash);
window.addEventListener('resize', (() => { let w = window.innerWidth >= 900; return () => { const n = window.innerWidth >= 900; if (n !== w) { w = n; render(true); } }; })());
