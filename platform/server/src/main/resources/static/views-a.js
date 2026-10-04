'use strict';
/* Views, part 1: welcome, sign up / in, plans, shop setup, sell, payment, receipt. */
const ACT = {};   // click handlers by data-act
const INPUT = {}; // input handlers by data-input
const SUPPORTED = ['TZ', 'KE', 'IN', 'BR', 'US'];
const guessCountry = () => {
  try { const r = new Intl.Locale(navigator.language).region; if (SUPPORTED.includes(r)) return r; } catch (e) { /* ignore */ }
  return 'TZ';
};
const backLink = (href, label) => `<a href="${href}">${ic('back', 20, 2.2)}${esc(label)}</a>`;
const val = id => { const el = document.getElementById(id); return el ? el.value : ''; };
const segHtml = (items, cur, act) => `<div class="seg" role="tablist">${items.map(([k, label]) => `<button role="tab" aria-selected="${k === cur}" class="${k === cur ? 'on' : ''}" data-act="${act}" data-id="${k}">${label}</button>`).join('')}</div>`;
const radio = on => `<span class="radio ${on ? 'on' : ''}">${ic('check', 12, 3.5)}</span>`;
const sw = on => `<span class="sw ${on ? 'on' : ''}" role="switch" aria-checked="${!!on}"></span>`;

/* ---------- Welcome ---------- */
VIEWS.welcome = async () => {
  if (S.token) { if (!S.user) await bootstrap(); location.hash = homeRoute(); return undefined; }
  await loadStrings();
  const feats = [['sell', '#0071E3', 'welcome.f1'], ['shops', '#E07B00', 'welcome.f2'], ['float', '#248A3D', 'welcome.f3']];
  return `<div class="welcome"><div>
    <h1>${t('welcome.title')}</h1>
    ${feats.map(([i, c, k]) => `<div class="feat"><div class="ic" style="color:${c}">${ic(i, 34, 1.6)}</div><div><b>${t(k + '.t')}</b><span>${t(k + '.d')}</span></div></div>`).join('')}
    <div class="stack" style="margin-top:auto;align-items:center;padding-top:24px">
      <span class="tint">${ic('shield', 26, 1.6)}</span>
      <p class="xs sec" style="text-align:center">${t('welcome.privacy')}</p>
      <a class="btn" href="#/signup">${t('welcome.continue')}</a>
      <span class="sm sec">${t('welcome.have')} <a href="#/login" class="b">${t('welcome.signin')}</a></span>
      <button class="sm tint" data-act="setLang" data-id="${S.lang === 'sw' ? 'en' : 'sw'}">${LANGS[S.lang === 'sw' ? 'en' : 'sw']}</button>
    </div></div></div>`;
};

/* ---------- Sign up / in ---------- */
function authView(mode) {
  const up = mode === 'signup';
  return `<div class="center"><div class="auth" data-enter="${up ? 'doSignup' : 'doLogin'}">
    <p style="margin-bottom:16px">${backLink('#/welcome', t('back'))}</p>
    <h1 class="plansh1" style="margin-bottom:20px">${up ? t('signup.title') : t('login.title')}</h1>
    <div class="grp">
      ${up ? `<label class="row"><span>${t('field.name')}</span><input id="f-name" autocomplete="name" autocapitalize="words"></label>` : ''}
      <label class="row"><span>${t('field.email')}</span><input id="f-email" type="email" autocomplete="email" inputmode="email" placeholder="you@example.com"></label>
      <label class="row"><span>${t('field.password')}</span><input id="f-pass" type="password" autocomplete="${up ? 'new-password' : 'current-password'}" placeholder="${up ? t('field.password.hint') : ''}"></label>
    </div>
    <div id="err"></div>
    <div class="stack" style="margin-top:20px"><button class="btn" data-act="${up ? 'doSignup' : 'doLogin'}">${up ? t('signup.cta') : t('login.cta')}</button>
    <a class="btn plain" href="${up ? '#/login' : '#/signup'}">${up ? t('signup.have') : t('login.new')}</a></div>
  </div></div>`;
}
VIEWS.signup = async () => { await loadStrings(); return authView('signup'); };
VIEWS.login = async () => { await loadStrings(); return authView('login'); };
async function afterAuth(r) {
  S.token = r.token; ls.set('token', r.token); S.user = null; S.shopId = null;
  await bootstrap();
  location.hash = homeRoute();
}
ACT.doSignup = async () => {
  try { await afterAuth(await api('/auth/signup', { method: 'POST', body: { name: val('f-name'), email: val('f-email'), password: val('f-pass') } })); }
  catch (e) { showErr(errMsg(e)); }
};
ACT.doLogin = async () => {
  try { await afterAuth(await api('/auth/login', { method: 'POST', body: { email: val('f-email'), password: val('f-pass') } })); }
  catch (e) { showErr(errMsg(e)); }
};
ACT.setLang = async el => {
  S.lang = el.dataset.id; ls.set('lang', S.lang);
  await loadStrings(); render(true);
};

/* ---------- Plans (subscription) ---------- */
function limLines(l) {
  const out = [];
  out.push(l.products == null ? t('lim.products.unlimited') : tn('lim.products', l.products));
  out.push(l.registers == null ? t('lim.registers.unlimited') : tn('lim.registers', l.registers));
  out.push(l.shops == null ? t('lim.shops.unlimited') : tn('lim.shops', l.shops));
  out.push(l.staff == null ? t('lim.staff.unlimited') : (l.staff === 0 ? t('lim.staff.none') : tn('lim.staff', l.staff)));
  return out;
}
VIEWS.plans = async () => {
  await loadStrings();
  const country = (S.cfg && S.cfg.shop.country) || S.country || guessCountry();
  S.regions = S.regions || await api('/regions');
  S.plansData = await api('/billing/plans?country=' + country);
  const d = S.plansData;
  const active = S.sub && S.sub.active;
  if (active && !S.planInit) { S.selPlan = S.sub.plan; S.planInit = true; }
  const price = p => money(S.period === 'yearly' ? Math.round(p.yearly / 12) : p.monthly, d.currency);
  const cards = d.plans.map(p => {
    const on = p.id === S.selPlan;
    return `<button class="plan ${on ? 'on' : ''}" role="radio" aria-checked="${on}" data-act="selPlan" data-id="${p.id}">
      ${radio(on)}
      <span class="grow" style="display:flex;flex-direction:column"><span class="b" style="font-size:19px">${t('plan.' + p.id)}</span><span class="sm sec">${t('plan.' + p.id + '.blurb')}</span>
      <span class="feats">${limLines(p.limits).map(x => `<span>${ic('check', 14, 2.6)} ${x}</span>`).join('')}</span></span>
      <span class="right"><b>${price(p)}</b><br><span class="xs sec">${t('plans.permonth')}</span></span></button>`;
  }).join('');
  const sel = d.plans.find(p => p.id === S.selPlan);
  const cta = active ? (S.sub.plan === S.selPlan && S.sub.period === S.period ? t('plans.current') : t('plans.switch')) : t('plans.trial', { days: d.trialDays });
  const body = `<div class="plans"><div class="pad" style="padding-top:8px"><h1 class="plansh1">${t('plans.title')}</h1><p class="sec" style="text-align:center;margin:6px 0 16px">${t('plans.sub', { days: d.trialDays })}</p></div>
    <div style="max-width:320px;margin:0 auto 12px;width:calc(100% - 32px)"><div class="grp" style="margin:0"><label class="row"><span>${t('field.country')}</span><select id="pl-country" data-change="planCountry">${S.regions.regions.map(r => `<option value="${r.code}" ${r.code === country ? 'selected' : ''}>${esc(r.name)}</option>`).join('')}</select></label></div></div>
    <div style="max-width:320px;margin:0 auto 4px;width:calc(100% - 32px)">${segHtml([['monthly', t('plans.monthly')], ['yearly', t('plans.yearly') + ' · ' + t('plans.save')]], S.period, 'setPeriod')}</div>
    <div class="cards" role="radiogroup">${cards}</div>
    <div id="err"></div>
    <div class="pad" style="max-width:420px;margin:20px auto 0;width:100%"><button class="btn" data-act="subscribe" ${active && S.sub.plan === S.selPlan && S.sub.period === S.period ? 'disabled' : ''}>${cta}</button>
    <p class="xs sec" style="text-align:center;margin-top:10px">${t('plans.legal')}</p></div></div>`;
  return `<div style="height:100%;overflow:auto;background:var(--bg)"><div style="padding:max(env(safe-area-inset-top),10px) 16px 0">${backLink(S.shops.length ? '#/account' : '#/welcome', t('back'))}</div>${body}</div>`;
};
ACT.planCountry = el => { S.country = el.value; render(true); };
ACT.selPlan = el => { S.selPlan = el.dataset.id; render(true); };
ACT.setPeriod = el => { S.period = el.dataset.id; render(true); };
ACT.subscribe = async () => {
  try {
    const r = await api('/billing/subscribe', { method: 'POST', body: { plan: S.selPlan, period: S.period, channel: 'web' } });
    S.sub = r.subscription;
    toast((t('plans.done', { plan: t('plan.' + S.sub.plan) })));
    location.hash = S.shops.length ? '#/account' : '#/setup';
  } catch (e) { showErr(errMsg(e)); }
};

/* ---------- Shop setup ---------- */
const SHOP_TYPES = ['retail', 'grocery', 'mobile_money', 'phones', 'restaurant'];
VIEWS.setup = async () => {
  if (!S.sub) { location.hash = '#/plans'; return undefined; }
  S.regions = S.regions || await api('/regions');
  const st = S.setup = S.setup || { name: '', type: 'retail', country: (S.cfg && S.cfg.shop.country) || S.country || guessCountry(), till: '', demo: true };
  const reg = S.regions.regions.find(r => r.code === st.country);
  const langName = LANGS[reg.locales[0].split('-')[0]] || reg.locales[0];
  const body = `<div data-enter="createShop">
    <div class="sh">${t('setup.name')}</div>
    <div class="grp"><label class="row"><span>${t('field.name')}</span><input id="s-name" data-input="setup.name" value="${esc(st.name)}" placeholder="${t('setup.name.ph')}" autocapitalize="words"></label></div>
    <div class="sh">${t('setup.type')}</div>
    <div class="grp" role="radiogroup">${SHOP_TYPES.map(k => `<button class="row" role="radio" aria-checked="${st.type === k}" data-act="setType" data-id="${k}"><span class="grow"><div>${t('type.' + k)}</div><div class="sm sec">${t('type.' + k + '.d')}</div></span><span class="tint" style="opacity:${st.type === k ? 1 : 0}">${ic('check', 20, 2.6)}</span></button>`).join('')}</div>
    <div class="sf">${t('setup.type.foot')}</div>
    <div class="sh">${t('setup.region')}</div>
    <div class="grp">
      <label class="row"><span>${t('field.country')}</span><select id="s-country" data-change="setupCountry">${S.regions.regions.map(r => `<option value="${r.code}" ${r.code === st.country ? 'selected' : ''}>${esc(r.name)}</option>`).join('')}</select></label>
      <div class="row"><span>${t('field.currency')}</span><span class="val">${reg.currency}</span></div>
      <div class="row"><span>${t('field.language')}</span><span class="val">${esc(langName)}</span></div>
      ${['TZ', 'KE'].includes(st.country) ? `<label class="row"><span>${t(st.country === 'TZ' ? 'field.lipa' : 'field.till')}</span><input id="s-till" data-input="setup.till" value="${esc(st.till)}" placeholder="5123 4567" inputmode="numeric"></label>` : ''}
    </div>
    <div class="sf">${t('setup.region.foot')}</div>
    <div class="grp" style="margin-top:20px"><button class="row" data-act="toggleDemo" role="switch" aria-checked="${st.demo}"><span class="grow"><div>${t('setup.demo')}</div><div class="sm sec">${t('setup.demo.d')}</div></span>${sw(st.demo)}</button></div>
    <div id="err"></div>
    <div class="pad" style="margin-top:20px;max-width:420px"><button class="btn" data-act="createShop">${t('setup.create')}</button></div></div>`;
  if (isDesk()) return `<div style="height:100%;overflow:auto"><div style="max-width:560px;margin:0 auto;padding:32px 24px"><h1 class="plansh1" style="text-align:left;font-size:34px;margin-bottom:8px">${t('setup.title')}</h1>${body}</div></div>`;
  return `<div class="scr">${offlineBar()}<div class="nav">${S.shops.length ? backLink('#/shops', t('back')) : backLink('#/plans', t('nav.plans'))}<span></span></div><h1 class="lt">${t('setup.title')}</h1><div class="body">${body}</div></div>`;
};
INPUT['setup.name'] = v => { S.setup.name = v; };
INPUT['setup.till'] = v => { S.setup.till = v; };
ACT.setType = el => { S.setup.type = el.dataset.id; render(true); };
ACT.toggleDemo = () => { S.setup.demo = !S.setup.demo; render(true); };
ACT.setupCountry = el => { S.setup.country = el.value; S.country = el.value; render(true); };
ACT.createShop = async () => {
  const st = S.setup;
  st.name = val('s-name') || st.name;
  try {
    const cfg = await api('/shops', { method: 'POST', body: { name: st.name, type: st.type, country: st.country, till: st.till } });
    if (st.demo) await api('/shops/' + cfg.shop.id + '/demo-data', { method: 'POST' });
    S.shopId = cfg.shop.id; ls.set('shopId', S.shopId);
    S.setup = null; S.user = null;
    await bootstrap();
    toast((t('setup.done', { name: cfg.shop.name })));
    location.hash = homeRoute();
  } catch (e) {
    if (e.code && e.code.startsWith('PLAN_LIMIT')) { showErr(errMsg(e)); return; }
    showErr(errMsg(e));
  }
};

/* ---------- Sell ---------- */
async function loadProducts() {
  try {
    const r = await api('/shops/' + S.shopId + '/products');
    S.products = r.products; ls.set('products:' + S.shopId, JSON.stringify(S.products));
  } catch (e) {
    const c = ls.get('products:' + S.shopId);
    if (e instanceof TypeError && c) S.products = JSON.parse(c); else throw e;
  }
}
const cartLines = () => Object.entries(S.cart).map(([id, qty]) => ({ p: S.products.find(x => x.id === id), qty })).filter(l => l.p);
const cartCount = () => cartLines().reduce((a, l) => a + l.qty, 0);
const cartTotal = () => cartLines().reduce((a, l) => a + l.qty * l.p.price, 0);
const vatOf = total => { const b = S.cfg.tax.bps; return b > 0 ? Math.floor((total * b + (10000 + b) / 2) / (10000 + b)) : 0; };
const stockLine = p => `<span class="${p.stock <= p.lowAt ? 'red' : 'sec'}">${p.stock <= 0 ? t('stock.out') : tn('stock.left', p.stock)}</span>`;
const filtered = () => {
  const q = S.search.trim().toLowerCase();
  return q ? S.products.filter(p => p.name.toLowerCase().includes(q) || (p.barcode || '').includes(q)) : S.products;
};
function stepper(p) {
  const q = S.cart[p.id] || 0;
  if (!q) return `<button class="add" data-act="inc" data-id="${p.id}" aria-label="${t('sell.add')} ${esc(p.name)}" ${p.stock <= 0 ? 'disabled' : ''}>+</button>`;
  return `<div class="step"><button data-act="dec" data-id="${p.id}" aria-label="${t('sell.remove')}">−</button><span aria-live="polite">${q}</span><button data-act="inc" data-id="${p.id}" aria-label="${t('sell.add')}" ${q >= p.stock ? 'disabled' : ''}>+</button></div>`;
}
const sellRows = () => filtered().map(p => `<div class="row thumbs"><div class="thumb" style="background:${hue(p.name)}">${initial(p.name)}</div><div class="grow"><div>${esc(p.name)}</div><div class="sm"><span class="sec">${money(p.price)}</span> · ${stockLine(p)}</div></div>${stepper(p)}</div>`).join('');
const sellTiles = () => filtered().map(p => `<button class="tile" data-act="inc" data-id="${p.id}" ${p.stock <= 0 || (S.cart[p.id] || 0) >= p.stock ? 'disabled' : ''}><div class="big" style="background:${hue(p.name)}">${initial(p.name)}</div><b>${esc(p.name)}</b><div style="display:flex;justify-content:space-between"><span class="sec">${money(p.price)}</span>${stockLine(p)}</div>${S.cart[p.id] ? `<span class="tint b">× ${S.cart[p.id]}</span>` : ''}</button>`).join('');
function orderPanel() {
  const lines = cartLines();
  const total = cartTotal();
  return `<div class="b" style="font-size:15px;margin-bottom:8px">${t('sell.order')}</div>
    ${lines.length ? lines.map(l => `<div style="display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--sep)"><div class="grow"><div>${esc(l.p.name)}</div><div class="xs sec">${l.qty} × ${money(l.p.price)}</div></div><b>${money(l.qty * l.p.price)}</b>${stepper(l.p)}</div>`).join('') : `<p class="sec sm" style="padding:12px 0">${t('sell.empty')}</p>`}
    <div style="margin-top:16px" class="stack"><div class="sm sec" style="display:flex;justify-content:space-between"><span>${t('tax.included', { name: S.cfg.tax.name, rate: S.cfg.tax.bps / 100 })}</span><span>${money(vatOf(total))}</span></div>
    <div style="display:flex;justify-content:space-between;font-size:22px;line-height:28px;font-weight:700"><span>${t('total')}</span><span>${money(total)}</span></div>
    <button class="btn" style="height:44px" data-act="checkout" ${lines.length ? '' : 'disabled'}>${t('sell.charge', { total: money(total) })}</button></div>`;
}
VIEWS.sell = async () => {
  if (isAgent()) { location.hash = '#/float'; return undefined; }
  await loadProducts();
  const search = `<div class="search">${ic('search', 16, 2.2)}<input id="q" data-input="search" value="${esc(S.search)}" placeholder="${t('sell.search')}" aria-label="${t('sell.search')}" autocomplete="off"></div>`;
  if (isDesk()) {
    return desk({
      active: 'sell', title: t('sell.register'), sub: esc(S.cfg.shop.name),
      tools: search.replace('class="search"', 'class="search" style="width:240px"'),
      body: `<div class="tiles" id="list">${sellTiles()}</div>`, insp: `<div id="order">${orderPanel()}</div>`,
      overlay: S.route.name === 'sell' ? '' : ''
    });
  }
  const n = cartCount();
  return phone({
    active: 'sell', title: t('nav.sell'),
    left: `<a href="#/shops" class="b" aria-label="${t('nav.shops')}">${esc(S.cfg.shop.name)}<svg width="10" height="14" viewBox="0 0 10 14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 5l3-3 3 3M2 9l3 3 3-3"/></svg></a>`,
    body: `${search}<div class="grp" id="list">${sellRows()}</div>`,
    float: n ? `<button class="cartbar" data-act="checkout"><span>${tn('sell.review', n)}</span><span>${money(cartTotal())}</span></button>` : ''
  });
};
function refreshSell() {
  const l = $('#list'); if (!l) return;
  l.innerHTML = isDesk() ? sellTiles() : sellRows();
  const o = $('#order'); if (o) o.innerHTML = orderPanel();
  const bar = $('.cartbar'), n = cartCount();
  if (!isDesk()) {
    if (bar && !n) bar.remove();
    else if (n) {
      const html = `<span>${tn('sell.review', n)}</span><span>${money(cartTotal())}</span>`;
      if (bar) bar.innerHTML = html; else $('.scr').insertAdjacentHTML('beforeend', `<button class="cartbar" data-act="checkout">${html}</button>`);
    }
  }
}
INPUT.search = v => {
  S.search = v;
  if (S.route.name === 'sell') {
    const exact = S.products.find(p => p.barcode && p.barcode === v.trim());
    if (exact) { S.cart[exact.id] = Math.min((S.cart[exact.id] || 0) + 1, exact.stock); S.search = ''; const q = $('#q'); if (q) q.value = ''; }
    refreshSell();
  } else if (S.route.name === 'products') refreshProducts();
};
ACT.inc = el => { const p = S.products.find(x => x.id === el.dataset.id); if (!p) return; S.cart[p.id] = Math.min((S.cart[p.id] || 0) + 1, p.stock); refreshSell(); };
ACT.dec = el => { const id = el.dataset.id; if (S.cart[id] > 1) S.cart[id]--; else delete S.cart[id]; refreshSell(); };
ACT.checkout = () => {
  if (!cartCount()) return;
  const t0 = S.cfg.tenders[0];
  S.pay = { tender: t0.id, network: (t0.networks[0] || {}).id || null, key: uuid(), cash: '', busy: false };
  location.hash = '#/pay';
};

/* ---------- Payment ---------- */
function payBody() {
  const p = S.pay, total = cartTotal(), tenders = S.cfg.tenders;
  const cur = tenders.find(x => x.id === p.tender);
  let panel = '';
  if (p.tender === 'cash') {
    const recv = toMinor(p.cash || '0');
    panel = `<div class="sh">${t('pay.cash')}</div><div class="grp"><label class="row"><span>${t('pay.received')}</span><input id="p-cash" data-input="pay.cash" value="${esc(p.cash)}" inputmode="decimal" placeholder="${fromMinor(total)}"></label>
      <div class="row"><span>${t('pay.change')}</span><span class="val ${recv >= total && p.cash ? 'green b' : ''}">${p.cash && recv >= total ? money(recv - total) : '—'}</span></div></div>`;
  } else if (cur.networks.length) {
    panel = `<div class="sh">${t('tender.' + p.tender)}</div><div class="grp" role="radiogroup">${cur.networks.map(n => `<button class="row" role="radio" aria-checked="${p.network === n.id}" data-act="setNetwork" data-id="${n.id}">${radio(p.network === n.id)}<span class="grow">${esc(n.name)}</span></button>`).join('')}</div>
      <div class="grp" style="margin-top:12px"><div class="row"><span>${t('pay.to')}</span><span class="val b" style="letter-spacing:1px;color:var(--label)">${esc(S.cfg.shop.till || t('pay.till.none'))}</span></div>
      <div class="row"><span>${t('pay.business')}</span><span class="val">${esc(S.cfg.shop.name)}</span></div>
      <div class="row"><span class="spin" aria-hidden="true"></span><span class="sec">${t('pay.waiting')}</span></div></div><div class="sf">${t('pay.waiting.foot')}</div>`;
  } else if (p.tender === 'card') {
    panel = `<div class="sh">${t('tender.card')}</div><div class="grp"><div class="row"><span class="spin" aria-hidden="true"></span><span class="sec">${t('pay.card.wait')}</span></div></div>`;
  } else {
    panel = `<div class="sh">${t('tender.credit')}</div><div class="grp"><label class="row"><span>${t('field.customer')}</span><input id="p-cust" placeholder="${t('field.customer.ph')}"></label></div>`;
  }
  const short = p.tender === 'cash' && p.cash && toMinor(p.cash) < total;
  return `<div data-enter="confirmPay">
    <div class="bigamt"><div class="sm sec">${t('pay.due')}</div><div class="n">${money(total)}</div><div class="sm sec">${tn('pay.items', cartCount())} · ${t('tax.included', { name: S.cfg.tax.name, rate: S.cfg.tax.bps / 100 })} ${money(vatOf(total))}</div></div>
    <div class="sh">${t('pay.with')}</div>
    <div class="grp" role="radiogroup">${tenders.map(x => `<button class="row" role="radio" aria-checked="${p.tender === x.id}" data-act="setTender" data-id="${x.id}">${radio(p.tender === x.id)}<span class="grow"><div>${t('tender.' + x.id)}</div><div class="sm sec">${x.networks.length ? x.networks.map(n => esc(n.name)).join(', ') : t('tender.' + x.id + '.sub')}</div></span></button>`).join('')}</div>
    ${panel}<div id="err"></div>
    <div class="pad" style="margin-top:20px"><button class="btn" data-act="confirmPay" ${p.busy || short ? 'disabled' : ''}>${t('pay.confirm')}</button></div></div>`;
}
function payShell(inner, title) {
  if (isDesk()) return `<div class="overlay"><div class="modal" role="dialog" aria-modal="true" aria-label="${title}"><div style="height:44px;display:flex;align-items:center;justify-content:space-between;padding:0 16px"><a href="#/sell">${t('cancel')}</a><b>${title}</b><span style="width:60px"></span></div>${inner}</div></div>`;
  return `<div class="scr">${offlineBar()}<div class="sheetbar"><i></i></div><div class="nav"><a href="#/sell" style="width:70px">${t('cancel')}</a><span class="t">${title}</span><span style="width:70px"></span></div><div class="body">${inner}</div></div>`;
}
VIEWS.pay = async () => {
  if (!S.pay || !cartCount()) { location.hash = '#/sell'; return undefined; }
  if (isDesk()) {
    const base = await VIEWS.sell();
    return base + payShell(payBody(), t('pay.title'));
  }
  if (!S.products.length) await loadProducts();
  return payShell(payBody(), t('pay.title'));
};
function rerenderPay() {
  const m = $('.modal'); const b = m || $('.body');
  if (!b) return;
  const keep = $('#p-cash') && document.activeElement === $('#p-cash');
  if (m) { const head = m.firstElementChild.outerHTML; m.innerHTML = head + payBody(); } else b.innerHTML = payBody();
  if (keep) { const c = $('#p-cash'); c.focus(); c.setSelectionRange(c.value.length, c.value.length); }
}
ACT.setTender = el => { const x = S.cfg.tenders.find(t0 => t0.id === el.dataset.id); S.pay.tender = x.id; S.pay.network = (x.networks[0] || {}).id || null; rerenderPay(); };
ACT.setNetwork = el => { S.pay.network = el.dataset.id; rerenderPay(); };
INPUT['pay.cash'] = v => { S.pay.cash = v; rerenderPay(); };
ACT.confirmPay = async () => {
  const p = S.pay; if (!p || p.busy) return;
  const lines = cartLines();
  const body = {
    lines: lines.map(l => ({ productId: l.p.id, qty: l.qty })), tender: p.tender, tenderRef: p.tender === 'lipa_namba' || p.tender === 'mpesa_till' ? p.network : null,
    idempotencyKey: p.key, cashReceived: p.tender === 'cash' && p.cash ? toMinor(p.cash) : null
  };
  p.busy = true;
  try {
    const r = await api('/shops/' + S.shopId + '/sales', { method: 'POST', body });
    S.lastSale = r.sale; S.cart = {}; S.pay = null;
    location.hash = '#/done';
  } catch (e) {
    p.busy = false;
    if (e instanceof TypeError) {
      // No connection: keep the sale on this device and replay it later with the same idempotency key.
      const total = cartTotal();
      queueSale({ shopId: S.shopId, body });
      S.lastSale = { pending: true, total, vat: vatOf(total), currency: S.cfg.currency.code, tender: p.tender, at: Date.now(), lines: lines.map(l => ({ name: l.p.name, qty: l.qty, unitPrice: l.p.price })) };
      S.cart = {}; S.pay = null;
      location.hash = '#/done';
    } else { showErr(errMsg(e)); rerenderPay(); }
  }
};

/* ---------- Receipt / done ---------- */
function receiptRows(s) {
  return `${s.lines.map(l => `<div class="row"><span class="grow">${esc(l.name)} × ${l.qty}${l.serial ? `<div class="xs sec">${t('act.serial', { serial: l.serial })}</div>` : ''}</span><span class="val">${money(l.unitPrice * l.qty, s.currency)}</span></div>`).join('')}
    <div class="row"><span>${t('tax.included', { name: S.cfg.tax.name, rate: S.cfg.tax.bps / 100 })}</span><span class="val">${money(s.vat, s.currency)}</span></div>
    <div class="row b"><span>${t('total')}</span><span class="val" style="color:var(--label)">${money(s.total, s.currency)}</span></div>`;
}
function doneBody() {
  const s = S.lastSale;
  return `<div style="padding-top:24px"><div class="okmark" style="${s.pending ? 'background:#FF9F0A' : ''}"><svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="${ICON.check}"/></svg></div>
    <div class="bigamt" style="padding-top:12px"><div class="b" style="font-size:22px;line-height:28px">${s.pending ? t('done.pending.title') : t('done.title')}</div><div class="sec sm">${t('tender.' + s.tender)} · ${money(s.total, s.currency)}</div></div></div>
    <div class="sh">${s.number ? t('receipt.no', { n: s.number }) : t('receipt')}</div><div class="grp">${receiptRows(s)}</div>
    ${s.change ? `<div class="grp" style="margin-top:12px"><div class="row"><span>${t('pay.change')}</span><span class="val green b">${money(s.change, s.currency)}</span></div></div>` : ''}
    <div class="grp" style="margin-top:12px"><div class="row">${ic(s.pending ? 'phone' : 'shield', 20, 1.8)}<span class="${s.pending ? '' : 'green'}">${s.pending ? t('done.pending') : t('done.synced')}</span></div></div>
    <div class="pad stack" style="margin-top:20px"><button class="btn sec2" data-act="shareReceipt">${ic('share', 18, 1.8)}${t('done.share')}</button><a class="btn" href="#/sell">${t('done.new')}</a></div>`;
}
VIEWS.done = async () => {
  if (!S.lastSale) { location.hash = '#/sell'; return undefined; }
  if (isDesk()) { const base = await VIEWS.sell(); return base + payShell(doneBody(), t('done.title')).replace(`<a href="#/sell">${t('cancel')}</a>`, '<span style="width:60px"></span>'); }
  return `<div class="scr">${offlineBar()}<div class="nav"><span></span><span></span></div><div class="body">${doneBody()}</div></div>`;
};
ACT.shareReceipt = async () => {
  const s = S.lastSale;
  const text = [S.cfg.shop.name, s.number ? t('receipt.no', { n: s.number }) : t('receipt'), fmtDate(s.at) + ' ' + fmtTime(s.at), ''].concat(s.lines.map(l => `${l.name} × ${l.qty}  ${money(l.unitPrice * l.qty, s.currency)}`)).concat(['', `${t('total')}: ${money(s.total, s.currency)}`]).join('\n').replace(/&amp;/g, '&');
  try { if (navigator.share) await navigator.share({ text }); else { await navigator.clipboard.writeText(text); toast((t('done.copied'))); } }
  catch (e) { toast((t('done.copied'))); }
};
