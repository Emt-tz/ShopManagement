'use strict';
/* Views, part 3: the assistant and the payments reconciliation screen. */

/* ---------- Assistant ---------- */
const chatBubble = m => m.role === 'user'
  ? `<div class="bubble me"><span class="xs sec">${t('assistant.you')}</span><div>${esc(m.text)}</div></div>`
  : `<div class="bubble bot"><span class="tint">${ic('sparkle', 16, 2)}</span><div>${m.pending ? `<span class="sec">${t('assistant.thinking')}</span>` : `<div>${esc(m.text)}</div>${(m.bullets || []).length ? `<ul>${m.bullets.map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : ''}<div class="xs sec" style="margin-top:6px">${t(m.source === 'claude' ? 'assistant.source.claude' : 'assistant.source.local')}</div>`}</div></div>`;
function chatHtml() {
  const sugg = ['ai.help.1', 'ai.help.2', 'ai.help.3', 'assistant.s4', 'assistant.s5'];
  return `<div class="chat" id="chat">${S.chat.length ? S.chat.map(chatBubble).join('') : `<div class="sec" style="padding:8px 4px 12px">${t('ai.help')}</div>`}</div>
    <div class="chips" style="padding:8px 0 4px">${sugg.map(k => `<button class="chip" data-act="askSuggest" data-q="${esc(t(k))}">${t(k)}</button>`).join('')}</div>
    <div class="askbar" data-enter="askNow"><input id="q-ask" placeholder="${t('assistant.ph')}" aria-label="${t('assistant.ph')}" autocomplete="off"><button class="btn" style="width:auto;height:36px;padding:0 16px" data-act="askNow">${t('assistant.send')}</button></div>`;
}
VIEWS.assistant = async () => {
  if (!S.cfg) { location.hash = '#/setup'; return undefined; }
  S.after = () => { const c = $('#chat'); if (c) c.scrollTop = c.scrollHeight; };
  if (isDesk()) return desk({ active: 'assistant', title: t('assistant.title'), sub: esc(S.cfg.shop.name), body: `<div style="max-width:720px">${chatHtml()}</div>` });
  return phone({ active: '', tabs: false, title: t('assistant.title'), left: backLink('#/shops', t('nav.shops')), body: `<div class="pad">${chatHtml()}</div>` });
};
async function ask(q) {
  q = q.trim(); if (!q) return;
  S.chat.push({ role: 'user', text: q });
  const pending = { role: 'bot', pending: true }; S.chat.push(pending);
  render(true);
  try {
    const r = await api('/shops/' + S.shopId + '/assistant', { method: 'POST', body: { question: q, lang: S.lang } });
    Object.assign(pending, { pending: false, text: r.answer, bullets: r.bullets, source: r.source });
  } catch (e) { Object.assign(pending, { pending: false, text: errMsg(e), bullets: [], source: 'local' }); }
  render(true);
}
ACT.askSuggest = el => ask(el.dataset.q);
ACT.askNow = () => { const i = $('#q-ask'); if (i && i.value.trim()) { const q = i.value; i.value = ''; ask(q); } };

/* ---------- Payments: the daily proof that every shilling received is a sale ---------- */
const PAY_PILL = { succeeded: 'green', failed: 'red', expired: 'red', mismatch: 'red', pending: 'sec', created: 'sec' };
VIEWS.payments = async () => {
  if (!S.cfg) { location.hash = '#/setup'; return undefined; }
  const manage = canManage();
  const [list, rec] = await Promise.all([api('/shops/' + S.shopId + '/payments?limit=15'), manage ? api('/shops/' + S.shopId + '/reconciliation?days=7') : Promise.resolve(null)]);
  const cur = S.cfg.currency.code;
  const today = rec ? rec.days[0] : null;
  const kpis = today ? [
    [t('payments.requested'), String(today.requested)],
    [t('payments.confirmed'), money(today.confirmed, cur)],
    [t('payments.matched'), money(today.matched, cur)],
    [t('payments.attention'), String(rec.needsAttention.length)]] : [];
  const issue = p => `<div class="row" style="align-items:flex-start;flex-wrap:wrap"><div class="grow"><div class="b red">${t('payments.issue.' + p.issue)}</div><div class="sm">${money(p.amount, cur)} · ${esc(netName(p.network))} ${p.receipt ? '· ' + esc(p.receipt) : ''} · ${esc(p.phone)}</div><div class="xs sec">${fmtDate(p.createdAt)} ${fmtTime(p.createdAt)}${p.late ? ' · ' + t('payments.late') : ''}</div></div>
    <div style="display:flex;gap:8px">${p.issue === 'unmatched' ? `<button class="chip on" data-act="payComplete" data-id="${p.id}">${t('payments.complete')}</button>` : ''}<button class="chip" data-act="payAck" data-id="${p.id}">${t('payments.ack')}</button></div></div>`;
  const attention = rec ? (rec.needsAttention.length ? `<div class="grp">${rec.needsAttention.map(issue).join('')}</div>` : `<div class="grp"><div class="row green">${ic('check', 20, 2.4)}<span>${t('payments.none')}</span></div></div>`) : '';
  const days = rec ? rec.days.map(d => `<div class="row"><span class="grow">${dtf({ weekday: 'short', day: 'numeric', month: 'short' }, d.day)}</span><span class="sm sec" style="min-width:60px;text-align:right">${d.requested}</span><span style="min-width:110px;text-align:right">${money(d.confirmed, cur)}</span><span class="b ${d.unmatched ? 'red' : 'green'}" style="min-width:110px;text-align:right">${money(d.matched, cur)}</span></div>`).join('') : '';
  const recent = list.payments.length ? list.payments.map(p => `<div class="row"><div class="grow"><div>${money(p.amount, cur)} · ${esc(netName(p.network))}</div><div class="xs sec">${esc(p.phone)} · ${fmtTime(p.createdAt)}${p.receipt ? ' · ' + esc(p.receipt) : ''}</div></div><span class="sm b ${PAY_PILL[p.status]}">${t('payments.status.' + p.status)}</span></div>`).join('') : `<div class="row sec">${t('feed.empty')}</div>`;
  const body = `${rec ? `<div class="${isDesk() ? 'cards4' : ''}" ${isDesk() ? '' : 'style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:0 16px"'}>${kpis.map(k => `<div class="card"><div class="cap">${k[0]}</div><div class="num" style="font-size:${isDesk() ? 22 : 18}px">${k[1]}</div></div>`).join('')}</div>` : ''}
    ${rec ? `<div class="sh">${t('payments.attention')}</div><div id="err"></div>${attention}${rec.unmatchedMessages ? `<div class="sf">${t('payments.unmatched', { n: rec.unmatchedMessages })}</div>` : ''}
    <div class="sh">${t('payments.days')}</div><div class="grp"><div class="row xs sec" style="min-height:28px"><span class="grow"></span><span style="min-width:60px;text-align:right">${t('payments.requested')}</span><span style="min-width:110px;text-align:right">${t('payments.confirmed')}</span><span style="min-width:110px;text-align:right">${t('payments.matched')}</span></div>${days}</div>` : ''}
    <div class="sh">${t('payments.recent')}</div><div class="grp">${recent}</div>`;
  if (isDesk()) return desk({ active: 'payments', title: t('payments.title'), sub: esc(S.cfg.shop.name), body: `<div style="max-width:860px">${body}</div>` });
  return phone({ active: 'insights', title: t('payments.title'), left: backLink('#/insights', t('nav.insights')), body });
};
ACT.payComplete = async el => {
  try { await api('/payments/' + el.dataset.id + '/resolve', { method: 'POST', body: { action: 'complete' } }); toast(t('payments.completed')); render(true); refreshActions(); }
  catch (e) { showErr(errMsg(e)); }
};
ACT.payAck = async el => {
  try { await api('/payments/' + el.dataset.id + '/resolve', { method: 'POST', body: { action: 'acknowledge' } }); toast(t('payments.handled')); render(true); refreshActions(); }
  catch (e) { showErr(errMsg(e)); }
};
