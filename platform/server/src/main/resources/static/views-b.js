'use strict';
/* Views, part 2: products, insights, all-shops overview and live feed, team, float, history, account. */

const tz = () => (S.cfg && S.cfg.timeZone) || undefined;
const dtf = (opts, ms) => new Intl.DateTimeFormat(S.locale, Object.assign({ timeZone: tz() }, opts)).format(ms);
const feedRow = a => `<div class="row" style="align-items:flex-start;padding-top:10px;padding-bottom:10px"><div class="avatar" style="background:${hue(a.userName)}">${initial(a.userName)}</div><div class="grow"><div style="font-size:15px;line-height:20px">${esc(activityText(a))}</div><div class="xs sec">${esc(a.shopName)} · ${esc(a.device)} · ${ago(a.at)}</div></div></div>`;
const confirmTap = (el, label) => {
  if (el.dataset.armed) return true;
  el.dataset.armed = '1'; el.textContent = label;
  setTimeout(() => { if (el.isConnected) { delete el.dataset.armed; el.textContent = el.dataset.label; } }, 4000);
  return false;
};

/* ---------- Products ---------- */
function productRowsPhone() {
  return filtered().map(p => {
    const inner = `<div class="thumb" style="background:${hue(p.name)}">${initial(p.name)}</div><div class="grow"><div>${esc(p.name)}</div><div class="sm">${stockLine(p)} · ${esc(p.category)}</div></div><div class="b">${money(p.price)}</div>${canManage() ? chev : ''}`;
    return canManage() ? `<a class="row thumbs" href="#/product/${p.id}" style="color:inherit">${inner}</a>` : `<div class="row thumbs">${inner}</div>`;
  }).join('');
}
const SORTS = { name: p => p.name.toLowerCase(), category: p => p.category.toLowerCase(), price: p => p.price, stock: p => p.stock, status: p => p.stock - p.lowAt };
function sortedProducts() {
  const f = SORTS[S.sort.key], d = S.sort.dir;
  return [...filtered()].sort((x, y) => (f(x) > f(y) ? 1 : f(x) < f(y) ? -1 : 0) * d);
}
const COLS = 'grid-template-columns:24px 2.2fr 1.3fr 1.2fr .8fr 1fr';
function productTable() {
  const rows = sortedProducts();
  const allOn = rows.length && rows.every(p => S.sel.has(p.id));
  const th = (k, label) => `<button class="th-b ${S.sort.key === k ? 'on' : ''}" data-act="sortBy" data-id="${k}" aria-sort="${S.sort.key === k ? (S.sort.dir > 0 ? 'ascending' : 'descending') : 'none'}">${label}${S.sort.key === k ? (S.sort.dir > 0 ? ' ▲' : ' ▼') : ''}</button>`;
  return `<div class="tbl" role="table"><div class="tr th" role="row" style="${COLS}"><input type="checkbox" data-act="toggleAll" aria-label="${t('col.select')}" ${allOn ? 'checked' : ''}>${th('name', t('col.name'))}${th('category', t('col.category'))}${th('price', t('col.price'))}${th('stock', t('col.stock'))}${th('status', t('col.status'))}</div>
    ${rows.map(p => `<div class="tr ${S.selProduct === p.id ? 'sel' : ''}" role="row" tabindex="0" style="${COLS}" data-act="selProduct" data-id="${p.id}"><input type="checkbox" data-act="toggleSel" data-id="${p.id}" aria-label="${t('col.select')} ${esc(p.name)}" ${S.sel.has(p.id) ? 'checked' : ''}><span class="b">${esc(p.name)}</span><span class="sec">${esc(p.category)}</span><span>${money(p.price)}</span><span>${p.stock}</span><span class="${p.stock <= p.lowAt ? (S.selProduct === p.id ? 'b' : 'red b') : (S.selProduct === p.id ? '' : 'green')}">${p.stock <= p.lowAt ? t('stock.low') : t('stock.ok')}</span></div>`).join('')}</div>`;
}
function bulkBar() {
  if (!S.sel.size || !canManage()) return '';
  return `<div class="bulk" role="region" aria-label="${tn('bulk.selected', S.sel.size)}"><b>${tn('bulk.selected', S.sel.size)}</b>
    <label>${t('bulk.price')} <input id="bk-pct" inputmode="decimal" placeholder="+5"></label><button class="p" data-act="bulkPrice">${t('bulk.apply')}</button>
    <label>${t('bulk.stock')} <input id="bk-stock" inputmode="numeric" placeholder="+10"></label><button class="p" data-act="bulkStock">${t('bulk.apply')}</button>
    <button class="d" data-act="bulkDelete" data-label="${t('bulk.delete')}">${t('bulk.delete')}</button><button data-act="clearSel">${t('bulk.clear')}</button></div>`;
}
function productForm(p) {
  const isNew = !p.id;
  const cats = (S.cfg.categories || []).map(c => `<option value="${esc(c)}"></option>`).join('');
  return `<div data-enter="saveProduct" ${isNew ? '' : `data-pid="${p.id}"`}>
    ${isNew ? '' : `<div style="display:flex;justify-content:center;padding:6px 0 4px"><div class="thumb" style="background:${hue(p.name)};width:72px;height:72px;font-size:30px;border-radius:16px">${initial(p.name)}</div></div>`}
    <div class="sh">${t('product.details')}</div>
    <div class="grp">
      <label class="row"><span>${t('col.name')}</span><input id="pf-name" value="${esc(p.name || '')}" autocapitalize="words" placeholder="${t('product.name.ph')}"></label>
      <label class="row"><span>${t('col.category')}</span><input id="pf-cat" list="cats" value="${esc(p.category || '')}"><datalist id="cats">${cats}</datalist></label>
      <label class="row"><span>${t('col.price')} (${S.cfg.currency.code})</span><input id="pf-price" inputmode="decimal" value="${p.price != null ? fromMinor(p.price) : ''}" placeholder="0"></label>
      <label class="row"><span>${t('col.stock')}</span><input id="pf-stock" inputmode="numeric" value="${p.stock != null ? p.stock : ''}" placeholder="0"></label>
      <label class="row"><span>${t('col.barcode')}</span><input id="pf-bar" inputmode="numeric" value="${esc(p.barcode || '')}" placeholder="${t('product.barcode.ph')}"></label>
    </div>
    <div id="avail"></div><div id="err"></div>
    <div class="stack" style="margin-top:20px"><button class="btn" data-act="saveProduct">${t('save')}</button>
      ${isNew ? '' : `<button class="btn destructive" data-act="deleteProduct" data-id="${p.id}" data-label="${t('product.delete')}">${t('product.delete')}</button>`}</div></div>`;
}
VIEWS.products = async () => {
  if (isAgent()) { location.hash = '#/float'; return undefined; }
  await loadProducts();
  const search = `<div class="search">${ic('search', 16, 2.2)}<input id="q" data-input="search" value="${esc(S.search)}" placeholder="${t('products.search')}" aria-label="${t('products.search')}" autocomplete="off"></div>`;
  if (isDesk()) {
    const sel = S.selProduct === 'new' ? {} : S.products.find(p => p.id === S.selProduct);
    if (sel && sel.id) S.after = () => loadAvail(sel.id);
    return desk({
      active: 'products', title: t('nav.products'), sub: tn('products.count', S.products.length) + ' · ' + tn('products.low', S.products.filter(p => p.stock <= p.lowAt).length),
      tools: search.replace('class="search"', 'class="search" style="width:220px"') + (canManage() ? `<button class="tbtn" data-act="newProduct">${ic('plus', 14, 2.4)}${t('product.add')}</button>` : ''),
      body: `${catChips()}${bulkBar()}<div id="list">${productTable()}</div>`,
      insp: sel ? `<div class="b" style="font-size:15px;margin-bottom:4px">${sel.id ? esc(sel.name) : t('product.add')}</div>${canManage() ? productForm(sel) : ''}` : `<p class="sec sm">${t('products.select')}</p>`
    });
  }
  return phone({
    active: 'products', title: t('nav.products'),
    right: canManage() ? `<a href="#/product/new" aria-label="${t('product.add')}">${ic('plus', 24, 2)}</a>` : '',
    body: `${search}${catChips()}<div class="grp" id="list">${productRowsPhone()}</div>`
  });
};
function refreshProducts() {
  const l = $('#list'); if (!l) return;
  l.innerHTML = isDesk() ? productTable() : productRowsPhone();
}
ACT.selProduct = el => { S.selProduct = el.dataset.id; render(true); };
ACT.sortBy = el => { const k = el.dataset.id; S.sort = { key: k, dir: S.sort.key === k ? -S.sort.dir : 1 }; render(true); };
ACT.toggleSel = el => { if (S.sel.has(el.dataset.id)) S.sel.delete(el.dataset.id); else S.sel.add(el.dataset.id); render(true); };
ACT.toggleAll = el => { const rows = sortedProducts(); if (el.checked) rows.forEach(p => S.sel.add(p.id)); else rows.forEach(p => S.sel.delete(p.id)); render(true); };
ACT.clearSel = () => { S.sel.clear(); render(true); };
const putProduct = (p, patch) => api('/products/' + p.id, { method: 'PUT', body: Object.assign({ name: p.name, category: p.category, price: p.price, stock: p.stock, barcode: p.barcode }, patch) });
ACT.bulkPrice = async () => {
  const pct = parseFloat(val('bk-pct').replace(/[^0-9.\-]/g, ''));
  if (!pct) return showErr(t('error.INVALID_AMOUNT'));
  try {
    const list = S.products.filter(p => S.sel.has(p.id));
    for (const p of list) await putProduct(p, { price: Math.max(0, Math.round(p.price * (1 + pct / 100))) });
    toast(tn('bulk.done', list.length)); S.sel.clear(); render(true);
  } catch (e) { showErr(errMsg(e)); }
};
ACT.bulkStock = async () => {
  const d = parseInt(val('bk-stock'), 10);
  if (!d) return showErr(t('error.INVALID_AMOUNT'));
  try {
    const list = S.products.filter(p => S.sel.has(p.id));
    for (const p of list) await putProduct(p, { stock: Math.max(0, p.stock + d) });
    toast(tn('bulk.done', list.length)); S.sel.clear(); render(true);
  } catch (e) { showErr(errMsg(e)); }
};
ACT.bulkDelete = async el => {
  if (!confirmTap(el, t('bulk.delete.confirm'))) return;
  try {
    const ids = [...S.sel];
    for (const id of ids) await api('/products/' + id, { method: 'DELETE' });
    toast(tn('bulk.deleted', ids.length)); S.sel.clear(); S.selProduct = null; render(true);
  } catch (e) { showErr(errMsg(e)); }
};
ACT.newProduct = () => { S.selProduct = 'new'; render(true); };
VIEWS.product = async params => {
  const id = params[0];
  if (!canManage()) { location.hash = '#/products'; return undefined; }
  if (isDesk()) { S.selProduct = id; location.hash = '#/products'; return undefined; }
  if (!S.products.length) await loadProducts();
  const p = id === 'new' ? {} : S.products.find(x => x.id === id);
  if (!p) { location.hash = '#/products'; return undefined; }
  if (p.id) S.after = () => loadAvail(p.id);
  return `<div class="scr">${offlineBar()}<div class="sheetbar"><i></i></div><div class="nav"><a href="#/products">${t('cancel')}</a><span class="t">${p.id ? t('product.edit') : t('product.add')}</span><button data-act="saveProduct" class="b">${t('done')}</button></div><div class="body">${productForm(p)}</div></div>`;
};
ACT.saveProduct = async () => {
  const form = $('[data-pid]'); const pid = form ? form.dataset.pid : null;
  const body = { name: val('pf-name'), category: val('pf-cat'), price: toMinor(val('pf-price')), stock: parseInt(val('pf-stock') || '0', 10) || 0, barcode: val('pf-bar') };
  try {
    const r = pid ? await api('/products/' + pid, { method: 'PUT', body }) : await api('/shops/' + S.shopId + '/products', { method: 'POST', body });
    toast((t('product.saved', { name: body.name })));
    if (isDesk()) { S.selProduct = r.product.id; render(true); } else location.hash = '#/products';
  } catch (e) { showErr(errMsg(e)); }
};
ACT.deleteProduct = async el => {
  if (!confirmTap(el, t('product.delete.confirm'))) return;
  try { await api('/products/' + el.dataset.id, { method: 'DELETE' }); S.selProduct = null; toast((t('product.deleted'))); if (isDesk()) render(true); else location.hash = '#/products'; }
  catch (e) { showErr(errMsg(e)); }
};
async function loadAvail(id) {
  const box = $('#avail'); if (!box) return;
  try {
    const r = await api('/products/' + id + '/availability');
    if (r.shops.length < 2) return;
    box.innerHTML = `<div class="sh">${t('product.available')}</div><div class="grp">${r.shops.map(s => {
      const same = s.currency === S.cfg.currency.code;
      return `<button class="row" ${same ? `data-act="toggleAvail" data-id="${id}" data-shop="${s.shopId}" data-on="${s.available ? 1 : 0}"` : 'disabled'} role="switch" aria-checked="${s.available}"><span class="grow"><div>${esc(s.shopName)}</div><div class="sm sec">${s.available ? money(s.price, s.currency) + ' · ' + tn('stock.left', s.stock) : (same ? t('product.notsold') : t('product.othercurrency'))}</div></span>${sw(s.available)}</button>`;
    }).join('')}</div><div class="sf">${t('product.available.foot')}</div>`;
  } catch (e) { /* availability is optional */ }
}
ACT.toggleAvail = async el => {
  try { await api('/products/' + el.dataset.id + '/availability', { method: 'PUT', body: { shopId: el.dataset.shop, available: el.dataset.on !== '1' } }); loadAvail(el.dataset.id); }
  catch (e) { showErr(errMsg(e)); }
};

/* ---------- Insights ---------- */
const MIX = { cash: '#0071E3', lipa_namba: '#34C759', mpesa_till: '#34C759', card: '#AF52DE', credit: '#FF9F0A', upi: '#34C759', pix: '#34C759' };
function chartHtml(d) {
  const vals = d.series.map(s => s.value), max = Math.max(...vals, 1), top = vals.indexOf(Math.max(...vals));
  const lab = (s, i) => {
    if (d.range === 'day') return i % 3 === 0 ? dtf({ hour: 'numeric' }, s.t) : '';
    if (d.range === 'week') return dtf({ weekday: 'short' }, s.t);
    if (d.range === 'month') return i % 5 === 0 ? dtf({ day: 'numeric' }, s.t) : '';
    return dtf({ month: 'short' }, s.t);
  };
  return `<div class="chart" role="img" aria-label="${t('insights.chart')}">${[0, 50, 100].map(p => `<div class="gl" style="top:${100 - p}%"><span>${moneyShort(Math.round(max * p / 100), d.currency)}</span></div>`).join('')}
    <div class="bars">${d.series.map((s, i) => `<div class="${i === top && max > 1 ? 'hi' : ''}" style="height:${(s.value / max * 100).toFixed(1)}%" title="${money(s.value, d.currency)}"><span>${lab(s, i)}</span></div>`).join('')}</div></div>`;
}
const delta = (cur, prev) => {
  if (!prev) return cur ? `<span class="green">${t('insights.new')}</span>` : '';
  const p = Math.round((cur - prev) / prev * 100);
  return `<span class="${p >= 0 ? 'green' : 'red'}">${p >= 0 ? '▲' : '▼'} ${Math.abs(p)}%</span>`;
};
VIEWS.insights = async () => {
  if (isAgent()) { location.hash = '#/float'; return undefined; }
  const d = await api('/shops/' + S.shopId + '/insights?range=' + S.range);
  const seg = segHtml([['day', t('range.day')], ['week', t('range.week')], ['month', t('range.month')], ['year', t('range.year')]], S.range, 'setRange');
  const mix = d.paymentMix.length ? `<div class="mix">${d.paymentMix.map(m => `<div style="width:${(m.amount / d.revenue * 100).toFixed(1)}%;background:${MIX[m.tender] || '#8E8E93'}"></div>`).join('')}</div>
    <div class="xs sec" style="display:flex;gap:12px;flex-wrap:wrap;margin-top:8px">${d.paymentMix.map(m => `<span><span style="color:${MIX[m.tender] || '#8E8E93'}">●</span> ${t('tender.' + m.tender)} ${Math.round(m.amount / d.revenue * 100)}%</span>`).join('')}</div>` : `<p class="sec sm">${t('insights.empty')}</p>`;
  const hourText = d.busiestHour != null ? new Intl.DateTimeFormat(S.locale, { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' }).format(Date.UTC(2020, 0, 1, d.busiestHour)) : '';
  const busy = d.busiestHour != null ? `<p class="sm" style="margin-top:8px">${t('insights.busiest', { hour: hourText })}</p>` : '';
  const kpis = [
    [t('kpi.revenue'), money(d.revenue, d.currency), delta(d.revenue, d.previousRevenue)],
    [t('kpi.sales'), String(d.count), delta(d.count, d.previousCount)],
    [t('kpi.average'), money(d.average, d.currency), ''],
    [t('kpi.refunds'), money(d.refunds, d.currency), '']
  ];
  const top = d.topProducts.length ? d.topProducts.map((p, i) => `<div class="row"><span class="sec" style="width:14px">${i + 1}</span><span class="grow">${esc(p.name)}</span><span class="sec sm">${tn('insights.units', p.units)}</span><span class="b" style="min-width:90px;text-align:right">${money(p.revenue, d.currency)}</span></div>`).join('') : `<div class="row sec">${t('insights.empty')}</div>`;
  if (isDesk()) {
    return desk({
      active: 'insights', title: t('nav.insights'), sub: esc(S.cfg.shop.name), tools: `<div style="width:300px">${seg}</div>`,
      body: `<div class="cards4">${kpis.map(k => `<div class="card"><div class="cap">${k[0]}</div><div class="num">${k[1]}</div><div>${k[2]}</div></div>`).join('')}</div>
        <div style="display:flex;gap:14px;margin-top:14px;align-items:flex-start"><div class="card" style="flex:1.7"><div class="cap">${t('insights.revenue')}</div>${chartHtml(d)}${busy}</div>
        <div style="flex:1;display:flex;flex-direction:column;gap:14px"><div class="card" style="padding:12px 0 0"><div class="cap" style="padding:0 16px 6px">${t('insights.top')}</div><div class="grp" style="background:transparent">${top}</div></div><div class="card"><div class="cap">${t('insights.payments')}</div>${mix}</div></div></div>`
    });
  }
  return phone({
    active: 'insights', title: t('nav.insights'),
    body: `${seg}<div class="grp" style="margin-top:14px;padding:14px 16px 8px"><div class="sm sec">${t('kpi.revenue')}</div><div style="font-size:34px;line-height:40px;font-weight:700;letter-spacing:.3px">${money(d.revenue, d.currency)} <span class="sm">${delta(d.revenue, d.previousRevenue)}</span></div>${chartHtml(d)}${busy}</div>
      <div class="grp" style="margin-top:12px"><div class="row"><span>${t('kpi.sales')}</span><span class="val">${d.count} ${delta(d.count, d.previousCount)}</span></div><div class="row"><span>${t('kpi.average')}</span><span class="val">${money(d.average, d.currency)}</span></div><div class="row"><span>${t('kpi.refunds')}</span><span class="val">${money(d.refunds, d.currency)}</span></div></div>
      <div class="sh">${t('insights.top')}</div><div class="grp">${top}</div>
      <div class="sh">${t('insights.payments')}</div><div class="grp" style="padding:14px 16px">${mix}</div>
      <div class="sh"></div><div class="grp"><a class="row" href="#/history" style="color:inherit">${ic('history', 22, 1.7)}<span class="grow">${t('nav.receipts')}</span>${chev}</a><a class="row" href="#/payments" style="color:inherit">${ic('payments', 22, 1.7)}<span class="grow">${t('nav.payments')}</span>${chev}</a><a class="row" href="#/assistant" style="color:inherit"><span class="tint">${ic('sparkle', 22, 1.7)}</span><span class="grow">${t('assistant.ask.row')}</span>${chev}</a></div>`
  });
};
ACT.setRange = el => { S.range = el.dataset.id; render(true); };

/* ---------- All shops: overview and live feed ---------- */
function spark(vals) {
  const max = Math.max(...vals, 1), w = 200, h = 34;
  const pts = vals.map((v, i) => `${(i / Math.max(vals.length - 1, 1) * w).toFixed(1)},${(h - 3 - v / max * (h - 6)).toFixed(1)}`).join(' ');
  return `<svg width="100%" height="34" viewBox="0 0 200 34" preserveAspectRatio="none" aria-hidden="true"><polyline points="${pts}" fill="none" stroke="var(--tint)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg>`;
}
function shopAlerts(s) {
  const out = [];
  if (s.lowStock) out.push(`<span class="red b">${tn('alert.lowstock', s.lowStock)}</span>`);
  if (s.lowFloat && s.lowFloat.length) out.push(`<span class="red b">${t('alert.lowfloat', { names: s.lowFloat.map(netNameFor(s)).join(', ') })}</span>`);
  return out.length ? out.join(' · ') : `<span class="green b">${t('alert.clear')}</span>`;
}
const netNameFor = () => id => (id === 'cash' ? t('float.cash') : ({ mpesa: 'M-Pesa', mixx: 'Mixx by Yas', airtel: 'Airtel Money', halopesa: 'HaloPesa' }[id] || id));
const ACTION_ICON = { topup: 'float', restock: 'products', limit: 'shield', trial: 'account', trial_over: 'account', payments: 'payments' };
function actionCard(a) {
  const nets = (a.networks || []).map(netNameFor()).join(', ');
  const c = {
    topup: [t('action.topup.title', { shop: a.shopName }), t('action.topup.d', { networks: nets }), t('action.topup.cta'), '#/float'],
    restock: [tn('action.restock.title', a.count, { shop: a.shopName }), t('action.restock.d', { items: (a.items || []).map(i => (i.daysLeft != null ? i.name + ' (' + t('unit.days', { n: i.daysLeft }) + ')' : i.name)).join(', ') }), t('action.restock.cta'), '#/products'],
    payments: [tn('action.payments.title', a.count), t('action.payments.d'), t('action.payments.cta'), '#/payments'],
    trial_over: [t('action.trial_over.title'), t('action.trial_over.d'), t('action.trial_over.cta'), '#/plans'],
    limit: [t('action.limit.title'), t('action.limit.d', { shop: a.shopName, used: a.used, max: a.max }), t('action.limit.cta'), '#/plans'],
    trial: [tn('action.trial.title', a.days), t('action.trial.d'), t('action.trial.cta'), '#/plans']
  }[a.kind];
  return `<button class="act ${['topup', 'restock', 'payments', 'trial_over'].includes(a.kind) ? 'warn' : ''}" data-act="doAction" data-shop="${a.shopId || ''}" data-route="${c[3]}"><span class="act-ic">${ic(ACTION_ICON[a.kind], 20, 1.8)}</span><span class="grow"><b>${c[0]}</b><span>${c[1]}</span></span><span class="act-cta">${c[2]}</span></button>`;
}
ACT.doAction = async el => {
  const id = el.dataset.shop;
  if (id && id !== S.shopId) { S.shopId = id; ls.set('shopId', id); S.cart = {}; S.cat = ''; S.sel.clear(); await loadCfg(); await loadStrings(); }
  location.hash = el.dataset.route;
};
ACT.toggleSwitch = () => { S.menuOpen = !S.menuOpen; render(true); };
ACT.setDashFilter = el => { S.dashFilter = el.dataset.id; render(true); };
VIEWS.shops = async () => {
  const [ov, fd] = await Promise.all([api('/overview'), api('/activity?limit=30')]);
  S.feed = fd.activity; S.actions = ov.actions;
  let insight = '';
  if (S.cfg && !isAgent()) {
    try {
      const f = await api('/shops/' + S.shopId + '/forecast');
      const v = f.versusTypical;
      if (v) {
        const wd = new Intl.DateTimeFormat(S.locale, { weekday: 'long', timeZone: tz() }).format(Date.now());
        insight = `<a class="act" href="#/assistant" style="margin-bottom:14px;color:inherit"><span class="act-ic">${ic('sparkle', 20, 1.8)}</span><span class="grow"><b>${t('insight.title')}</b><span>${t(v.percent >= 0 ? 'ai.typical.up' : 'ai.typical.down', { pct: Math.abs(v.percent), weekday: wd })}</span></span><span class="act-cta">${t('assistant.ask.row')}</span></a>`;
      }
    } catch (e) { /* the insight is optional */ }
  }
  const agents = ov.shops.filter(s => s.type === 'mobile_money').length, stores = ov.shops.length - agents;
  const filter = agents && stores ? S.dashFilter : 'all';
  const shown = ov.shops.filter(s => filter === 'all' || (filter === 'agent') === (s.type === 'mobile_money'));
  const chips = agents && stores ? chipsHtml([['all', t('chip.all')], ['store', t('chip.stores')], ['agent', t('chip.agents')]], filter, 'setDashFilter') : '';
  const totals = ov.totals.map(x => `<div class="grow"><div class="xs sec">${t('dash.today')} · ${x.currency}</div><div style="font-size:26px;line-height:32px;font-weight:700">${money(x.today, x.currency)}</div><div class="xs">${delta(x.today, x.yesterday)}</div></div>`).join('');
  const metric = (label, v) => `<div>${label}<b>${v}</b></div>`;
  const metricsOf = s => (s.floatTotal != null
    ? metric(t('metric.float'), moneyShort(s.floatTotal, s.currency)) + metric(t('metric.lowfloat'), s.lowFloat.length) + metric(t('metric.online'), s.online)
    : metric(t('metric.sales'), s.todayCount) + metric(t('metric.avg'), s.todayCount ? moneyShort(Math.round(s.todayRevenue / s.todayCount), s.currency) : '—') + metric(t('metric.low'), s.lowStock) + metric(t('metric.online'), s.online));
  const cardHtml = s => `<button class="card" data-act="openShop" data-id="${s.id}" style="text-align:left;width:100%"><div style="display:flex;justify-content:space-between;align-items:baseline"><b style="font-size:15px">${esc(s.name)}</b><span class="sec">${t('type.' + s.type)}</span></div>
    <div style="font-size:24px;line-height:30px;font-weight:700">${s.floatTotal != null ? money(s.floatTotal, s.currency) : money(s.todayRevenue, s.currency)}</div>${spark(s.spark)}<div>${shopAlerts(s)}</div><div class="metrics">${metricsOf(s)}</div></button>`;
  const rowHtml = s => `<button class="row" data-act="openShop" data-id="${s.id}"><span class="dot ${s.online ? '' : 'off'}"></span><span class="grow"><div>${esc(s.name)}</div><div class="sm sec">${t('type.' + s.type)} · ${tn('shops.online', s.online)}</div><div class="xs">${shopAlerts(s)}</div></span><span class="right"><div class="b">${s.floatTotal != null ? money(s.floatTotal, s.currency) : money(s.todayRevenue, s.currency)}</div></span>${chev}</button>`;
  const feed = S.feed.map(feedRow).join('') || `<div class="row sec">${t('feed.empty')}</div>`;
  const actions = ov.actions.length ? ov.actions.map(actionCard).join('') : '';
  if (isDesk()) {
    return desk({
      active: 'shops', title: t('nav.overview'), sub: `<span class="green">● ${t('live')}</span> · ${tn('shops.count', ov.shops.length)}`,
      tools: `<button class="tbtn" data-act="addShop">${ic('plus', 14, 2.4)}${t('shops.add')}</button>`,
      body: `<div class="card" style="flex-direction:row;gap:24px;margin-bottom:14px">${totals}</div>${insight}
        <div class="sectitle">${t('dash.actions')}</div>${actions ? `<div class="acts">${actions}</div>` : `<p class="sec sm" style="margin-bottom:14px">${t('dash.none')}</p>`}
        <div class="sectitle">${t('dash.shops')}</div>${chips}<div class="cards2">${shown.map(cardHtml).join('')}</div>`,
      insp: `<div class="b" style="font-size:15px;margin-bottom:6px">${t('feed.title')}</div><div id="feed" class="grp" style="background:transparent">${feed}</div>`
    });
  }
  return phone({
    active: 'shops', title: t('nav.shops'), right: `<button data-act="addShop" aria-label="${t('shops.add')}">${ic('plus', 24, 2)}</button>`,
    body: `<div class="grp" style="padding:14px 16px;display:flex;gap:16px">${totals}</div>
      <div class="grp" style="margin-top:12px"><a class="row" href="#/assistant" style="color:inherit"><span class="tint">${ic('sparkle', 22, 1.7)}</span><span class="grow">${t('assistant.ask.row')}</span>${chev}</a></div>
      ${actions ? `<div class="sh">${t('dash.actions')}</div><div class="acts" style="padding:0 16px;grid-template-columns:1fr">${actions}</div>` : ''}
      <div class="sh">${t('nav.shops')}</div>${chips}<div class="grp">${shown.map(rowHtml).join('')}</div>
      <div class="sh" style="display:flex;justify-content:space-between"><span>${t('feed.title')}</span><span class="green">● ${t('live')}</span></div><div class="grp" id="feed">${feed}</div>
      <div class="sh"></div><div class="grp"><a class="row" href="#/team" style="color:inherit">${ic('team', 22, 1.7)}<span class="grow">${t('nav.team')}</span>${chev}</a></div>`
  });
};
ACT.addShop = () => { S.setup = null; location.hash = '#/setup'; };
ACT.openShop = async el => { await switchShop(el.dataset.id); };
ACT.switchShop = async el => { await switchShop(el.dataset.id); };
async function switchShop(id) {
  S.shopId = id; ls.set('shopId', id); S.cart = {}; S.search = ''; S.selProduct = null; S.cat = ''; S.sel.clear(); S.menuOpen = false;
  await loadCfg(); await loadStrings();
  location.hash = homeRoute();
  if (location.hash === homeRoute()) render();
}

/* ---------- Team and audit ---------- */
const AUDIT = 'price_change,void,stock_adjust,float_adjust,product_removed,member_added';
VIEWS.team = async () => {
  if (!S.shopId) { location.hash = '#/setup'; return undefined; }
  const [mem, aud] = await Promise.all([api('/shops/' + S.shopId + '/members'), api('/activity?shopId=' + S.shopId + '&kinds=' + AUDIT + '&limit=20')]);
  const isOwner = myRole() === 'owner';
  const last = m => (m.last ? `${t('kind.' + m.last.kind)} · ${esc(m.last.device)} · ${ago(m.last.at)}` : t('team.noactivity'));
  const memRows = mem.members.map(m => `<div class="row"><div class="avatar" style="background:${hue(m.name)}">${initial(m.name)}</div><div class="grow"><div class="b">${esc(m.name)} <span class="sec" style="font-weight:400">· ${t('role.' + m.role)}</span></div><div class="sm sec">${last(m)}</div></div><span class="dot ${m.online ? '' : 'off'}" role="img" aria-label="${m.online ? t('online') : t('offline')}"></span></div>`).join('');
  const audRows = aud.activity.map(feedRow).join('') || `<div class="row sec">${t('feed.empty')}</div>`;
  const invite = isOwner ? `<div class="sh">${t('team.invite')}</div><div class="grp" data-enter="invite">
      <label class="row"><span>${t('field.name')}</span><input id="i-name" autocapitalize="words"></label>
      <label class="row"><span>${t('field.email')}</span><input id="i-email" type="email" inputmode="email"></label>
      <label class="row"><span>${t('field.password')}</span><input id="i-pass" type="password" autocomplete="new-password" placeholder="${t('field.password.hint')}"></label>
      <label class="row"><span>${t('field.role')}</span><select id="i-role"><option value="cashier">${t('role.cashier')}</option><option value="manager">${t('role.manager')}</option></select></label></div>
      <div id="err"></div><div class="pad" style="margin-top:14px"><button class="btn" data-act="invite">${t('team.invite.cta')}</button></div><div class="sf">${t('team.invite.foot')}</div>` : '';
  const body = `<div class="sh">${t('team.members')}</div><div class="grp">${memRows}</div>${invite}<div class="sh">${t('team.audit')}</div><div class="grp">${audRows}</div>`;
  if (isDesk()) return desk({ active: 'team', title: t('nav.team'), sub: `${esc(S.cfg.shop.name)} · ${tn('team.count', mem.members.length)}`, body: `<div style="max-width:720px">${body}</div>` });
  return phone({ active: 'shops', title: t('nav.team'), left: backLink('#/shops', t('nav.shops')), body });
};
ACT.invite = async () => {
  try {
    await api('/shops/' + S.shopId + '/members', { method: 'POST', body: { name: val('i-name'), email: val('i-email'), password: val('i-pass'), role: val('i-role') } });
    toast((t('team.invited'))); render(true);
  } catch (e) { showErr(errMsg(e)); }
};

/* ---------- Mobile money float ---------- */
VIEWS.float = async () => {
  if (!isAgent()) { location.hash = '#/sell'; return undefined; }
  const f = await api('/shops/' + S.shopId + '/float');
  const kind = S.floatKind = S.floatKind || 'cash_out';
  const nets = S.cfg.networks;
  const acc = f.accounts.map(a => {
    const pct = a.lowAt > 0 ? Math.min(100, Math.round(a.balance / (a.lowAt * 3) * 100)) : Math.min(100, Math.round(a.balance / Math.max(f.total, 1) * 200));
    return `<div class="row"><div class="grow"><div style="display:flex;justify-content:space-between"><span>${a.network === 'cash' ? t('float.cash') : esc(a.name)}</span><span class="b ${a.low ? 'red' : ''}">${money(a.balance, f.currency)}${a.low ? ' · ' + t('float.low') : ''}</span></div><div class="gauge ${a.low ? 'low' : ''}"><i style="width:${pct}%"></i></div></div></div>`;
  }).join('');
  const recent = f.recent.map(r => `<div class="row"><div class="grow"><div style="font-size:15px">${t('float.kind.' + r.kind)} · ${esc(netName(r.network))}</div><div class="xs sec">${esc(r.userName)} · ${ago(r.at)}</div></div><span class="${r.kind === 'cash_out' ? '' : 'sec'} b">${money(r.amount, f.currency)}</span></div>`).join('') || `<div class="row sec">${t('feed.empty')}</div>`;
  const form = `<div class="sh">${t('float.new')}</div>${segHtml([['cash_in', t('float.kind.cash_in')], ['cash_out', t('float.kind.cash_out')], ['airtime', t('float.kind.airtime')]], kind, 'setFloatKind')}
    <div class="grp" style="margin-top:12px" data-enter="floatTx"><label class="row"><span>${t('float.network')}</span><select id="fl-net">${nets.map(n => `<option value="${n.id}">${esc(n.name)}</option>`).join('')}</select></label>
    <label class="row"><span>${t('field.amount')} (${f.currency})</span><input id="fl-amt" inputmode="decimal" placeholder="0"></label></div>
    <div id="err"></div><div class="pad" style="margin-top:14px"><button class="btn" data-act="floatTx">${t('float.record')}</button></div>`;
  const adjust = canManage() ? `<div class="sh">${t('float.adjust')}</div><div class="grp" data-enter="floatAdjust"><label class="row"><span>${t('float.network')}</span><select id="fa-net"><option value="cash">${t('float.cash')}</option>${nets.map(n => `<option value="${n.id}">${esc(n.name)}</option>`).join('')}</select></label>
    <label class="row"><span>${t('float.delta')}</span><input id="fa-amt" inputmode="decimal" placeholder="+0"></label></div><div class="pad" style="margin-top:14px"><button class="btn sec2" data-act="floatAdjust">${t('float.adjust.cta')}</button></div><div class="sf">${t('float.adjust.foot')}</div>` : '';
  const totalCard = `<div class="grp" style="padding:14px 16px"><div class="sm sec">${t('float.total')}</div><div style="font-size:34px;line-height:40px;font-weight:700;letter-spacing:.3px">${money(f.total, f.currency)}</div><div class="sm sec">${tn('float.today', f.todayCount)} · ${t('float.commission', { amount: money(f.todayCommission, f.currency) })}</div></div>`;
  if (isDesk()) {
    return desk({
      active: 'float', title: t('nav.float'), sub: esc(S.cfg.shop.name),
      body: `<div style="display:grid;grid-template-columns:1.2fr 1fr;gap:20px;max-width:1000px"><div>${totalCard}<div class="sh">${t('float.byNetwork')}</div><div class="grp">${acc}</div><div class="sh">${t('float.recent')}</div><div class="grp">${recent}</div></div><div>${form}${adjust}</div></div>`
    });
  }
  return phone({
    active: 'float', title: t('nav.float'), left: `<a href="#/shops" class="b">${esc(S.cfg.shop.name)}</a>`,
    body: `${totalCard}${form}<div class="sh">${t('float.byNetwork')}</div><div class="grp">${acc}</div><div class="sh">${t('float.recent')}</div><div class="grp">${recent}</div>${adjust}`
  });
};
ACT.setFloatKind = el => { S.floatKind = el.dataset.id; render(true); };
ACT.floatTx = async () => {
  try {
    await api('/shops/' + S.shopId + '/float/tx', { method: 'POST', body: { network: val('fl-net'), kind: S.floatKind, amount: toMinor(val('fl-amt')) } });
    toast((t('float.recorded'))); render(true);
  } catch (e) { showErr(errMsg(e)); }
};
ACT.floatAdjust = async () => {
  try {
    await api('/shops/' + S.shopId + '/float/adjust', { method: 'POST', body: { network: val('fa-net'), delta: toMinor(val('fa-amt')) } });
    toast((t('float.adjusted'))); render(true);
  } catch (e) { showErr(errMsg(e)); }
};

/* ---------- History and receipts ---------- */
VIEWS.history = async () => {
  if (isAgent()) {
    const f = await api('/shops/' + S.shopId + '/float');
    const rows = f.recent.map(r => `<div class="row"><div class="grow"><div>${t('float.kind.' + r.kind)} · ${esc(netName(r.network))}</div><div class="xs sec">${esc(r.userName)} · ${fmtTime(r.at)} · ${ago(r.at)}</div></div><span class="b">${money(r.amount, f.currency)}</span></div>`).join('') || `<div class="row sec">${t('feed.empty')}</div>`;
    return page({ active: 'history', title: t('nav.history'), body: `<div class="grp" style="${isDesk() ? 'max-width:640px' : ''}">${rows}</div>` });
  }
  const r = await api('/shops/' + S.shopId + '/sales?limit=50');
  const row = s => `<a class="row" href="#/receipt/${s.id}" style="color:inherit"><div class="grow"><div>${t('receipt.no', { n: s.number })} ${s.status === 'void' ? `<span class="red sm b">${t('receipt.void')}</span>` : ''}</div><div class="xs sec">${esc(s.cashier)} · ${t('tender.' + s.tender)} · ${fmtTime(s.at)} · ${ago(s.at)}</div></div><span class="b" style="${s.status === 'void' ? 'text-decoration:line-through' : ''}">${money(s.total, s.currency)}</span>${chev}</a>`;
  const rows = r.sales.map(row).join('') || `<div class="row sec">${t('feed.empty')}</div>`;
  if (isDesk()) return desk({ active: 'history', title: t('nav.receipts'), sub: esc(S.cfg.shop.name), body: `<div class="grp" style="max-width:720px">${rows}</div>` });
  return phone({ active: 'insights', title: t('nav.receipts'), left: backLink('#/insights', t('nav.insights')), body: `<div class="grp">${rows}</div>` });
};
VIEWS.receipt = async params => {
  const r = await api('/sales/' + params[0]); const s = r.sale;
  const body = `<div class="sh">${s.status === 'void' ? t('receipt.void') : t('receipt.no', { n: s.number })}</div><div class="grp">${receiptRows(s)}</div>
    <div class="grp" style="margin-top:12px"><div class="row"><span>${t('receipt.cashier')}</span><span class="val">${esc(s.cashier)}</span></div><div class="row"><span>${t('receipt.time')}</span><span class="val">${fmtDate(s.at)} ${fmtTime(s.at)}</span></div><div class="row"><span>${t('pay.with')}</span><span class="val">${t('tender.' + s.tender)}</span></div></div>
    <div id="err"></div>${canManage() && s.status === 'completed' ? `<div class="pad" style="margin-top:20px"><button class="btn destructive" data-act="voidSale" data-id="${s.id}" data-label="${t('receipt.void.cta')}">${t('receipt.void.cta')}</button></div><div class="sf">${t('receipt.void.foot')}</div>` : ''}`;
  if (isDesk()) {
    const base = await VIEWS.history();
    return base + `<div class="overlay"><div class="modal" role="dialog" aria-modal="true"><div style="height:44px;display:flex;align-items:center;justify-content:space-between;padding:0 16px"><span style="width:60px"></span><b>${t('receipt')}</b><a href="#/history">${t('done')}</a></div>${body}</div></div>`;
  }
  return `<div class="scr">${offlineBar()}<div class="nav">${backLink('#/history', t('nav.receipts'))}<span></span></div><div class="body">${body}</div></div>`;
};
ACT.voidSale = async el => {
  if (!confirmTap(el, t('receipt.void.confirm'))) return;
  try { await api('/sales/' + el.dataset.id + '/void', { method: 'POST' }); toast((t('receipt.voided'))); render(true); }
  catch (e) { showErr(errMsg(e)); }
};

/* ---------- Account: subscription, language, shop settings ---------- */
VIEWS.account = async () => {
  await api('/me').then(me => { S.sub = me.subscription; });
  if (S.shopId) await loadCfg();
  const sub = S.sub;
  const date = sub ? fmtDate(sub.free ? sub.trialEndsAt : sub.renewsAt) : '';
  const statusText = !sub ? t('account.staff') : sub.free ? t('sub.free', { date }) : t('sub.' + sub.status, { date });
  const freeCard = sub && sub.free ? `<div class="sh">${t('account.subscription')}</div><div class="grp">
      <div class="row" style="align-items:flex-start"><span class="tint" style="padding-top:2px">${ic('sparkle', 22, 1.7)}</span><span class="grow"><div class="b">${t('account.free')}</div><div class="sm green b">${t('account.free.until', { date, n: sub.freeDaysLeft })}</div><div class="sm sec" style="margin-top:4px">${t('account.free.d')}</div></span></div>
      ${sub.status === 'active' ? `<div class="row"><span>${t('account.plan.chosen', { plan: t('plan.' + sub.plan) })}</span></div>` : ''}
      ${sub.plansOpen ? `<a class="row" href="#/plans" style="color:inherit"><span class="tint grow">${t('plans.choose')}</span>${chev}</a>` : ''}</div>
      <div class="sf">${t('account.pay.later')}</div>` : '';
  const subGroup = !sub ? `<div class="sh">${t('account.subscription')}</div><div class="grp"><div class="row sec">${statusText}</div></div>` : (sub.free ? freeCard : `<div class="sh">${t('account.subscription')}</div><div class="grp">
      <div class="row"><span>${t('account.plan')}</span><span class="val b" style="color:var(--label)">${t('plan.' + sub.plan)} · ${t('plans.' + sub.period)}</span></div>
      <div class="row"><span>${t('account.status')}</span><span class="val ${sub.active ? 'green' : 'red'}">${statusText}</span></div>
      <div class="row"><span>${t('account.billedvia')}</span><span class="val">${t('channel.' + sub.channel)}</span></div>
      <a class="row" href="#/plans" style="color:inherit"><span class="tint grow">${t('account.change')}</span>${chev}</a>
      ${sub.status !== 'canceled' ? `<button class="row" data-act="cancelSub" data-label="${t('account.cancel')}"><span class="red grow">${t('account.cancel')}</span></button>` : ''}</div>
      <div class="sf">${t('account.sub.foot')}</div>`);
  const shopGroup = S.cfg && canManage() ? `<div class="sh">${t('account.shop')}</div><div class="grp" data-enter="saveShop"><label class="row"><span>${t('field.name')}</span><input id="a-name" value="${esc(S.cfg.shop.name)}"></label>
      ${['TZ', 'KE'].includes(S.cfg.shop.country) ? `<label class="row"><span>${t(S.cfg.shop.country === 'TZ' ? 'field.lipa' : 'field.till')}</span><input id="a-till" value="${esc(S.cfg.shop.till || '')}" inputmode="numeric"></label>` : ''}</div>
      <div id="err"></div><div class="pad" style="margin-top:12px"><button class="btn sec2" data-act="saveShop">${t('save')}</button></div>` : '';
  const ai = S.cfg ? S.cfg.ai : null;
  const aiGroup = ai ? `<div class="sh">${t('account.ai')}</div><div class="grp"><button class="row" data-act="toggleAi" role="switch" aria-checked="${ai.external}" ${!ai.available || myRole() !== 'owner' ? 'disabled' : ''}><span class="grow"><div>${t('account.ai.toggle')}</div><div class="sm sec">${!ai.available ? t('assistant.cloud.na') : myRole() !== 'owner' ? t('assistant.cloud.owner') : t('assistant.cloud.d')}</div></span>${sw(ai.external)}</button></div>` : '';
  const body = `<div class="grp"><div class="row"><div class="avatar" style="background:${hue(S.user.name)}">${initial(S.user.name)}</div><div class="grow"><div class="b">${esc(S.user.name)}</div><div class="sm sec">${esc(S.user.email)}</div></div></div></div>
    ${subGroup}${shopGroup}${aiGroup}
    <div class="sh">${t('account.language')}</div><div class="grp"><label class="row"><span>${t('field.language')}</span><select id="a-lang" data-change="pickLang">${Object.entries(LANGS).map(([k, v]) => `<option value="${k}" ${k === S.lang ? 'selected' : ''}>${v}</option>`).join('')}</select></label></div><div class="sf">${t('account.language.foot')}</div>
    <div class="grp" style="margin-top:22px"><button class="row" data-act="signOut"><span class="red grow" style="text-align:center">${t('account.signout')}</span></button></div>`;
  if (isDesk()) return desk({ active: 'account', title: t('nav.account'), body: `<div style="max-width:560px">${body}</div>` });
  return phone({ active: 'account', title: t('nav.account'), body });
};
ACT.toggleAi = async () => {
  try { S.cfg = await api('/shops/' + S.shopId, { method: 'PUT', body: { aiExternal: !S.cfg.ai.external } }); render(true); }
  catch (e) { showErr(errMsg(e)); }
};
ACT.pickLang = async el => { S.lang = el.value; ls.set('lang', S.lang); await loadStrings(); render(true); };
ACT.cancelSub = async el => {
  if (!confirmTap(el, t('account.cancel.confirm'))) return;
  try { const r = await api('/billing/cancel', { method: 'POST' }); S.sub = r.subscription; toast((t('account.canceled'))); render(true); }
  catch (e) { showErr(errMsg(e)); }
};
ACT.saveShop = async () => {
  try {
    const body = { name: val('a-name') }; if ($('#a-till')) body.till = val('a-till');
    S.cfg = await api('/shops/' + S.shopId, { method: 'PUT', body });
    const s = S.shops.find(x => x.id === S.shopId); if (s) s.name = S.cfg.shop.name;
    toast((t('saved'))); render(true);
  } catch (e) { showErr(errMsg(e)); }
};
ACT.signOut = async () => {
  try { await api('/auth/logout', { method: 'POST' }); } catch (e) { /* offline sign out still clears the device */ }
  signOutLocal(); location.hash = '#/welcome';
};
VIEWS.notfound = VIEWS.welcome;
