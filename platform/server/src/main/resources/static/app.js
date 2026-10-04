'use strict';
/* Boot and event delegation. */
document.addEventListener('click', e => {
  const el = e.target.closest('[data-act]');
  if (!el || el.disabled) return;
  const fn = ACT[el.dataset.act];
  if (fn) { e.preventDefault(); fn(el, e); }
});
document.addEventListener('input', e => {
  const k = e.target.dataset && e.target.dataset.input;
  if (k && INPUT[k]) INPUT[k](e.target.value);
});
document.addEventListener('change', e => {
  const k = e.target.dataset && e.target.dataset.change;
  if (k && ACT[k]) ACT[k](e.target);
});
document.addEventListener('keydown', e => {
  if (e.key !== 'Enter' || e.target.tagName !== 'INPUT') return;
  const c = e.target.closest('[data-enter]');
  if (c && ACT[c.dataset.enter]) { e.preventDefault(); ACT[c.dataset.enter](); }
});
if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => { /* optional */ });
if (!location.hash) location.hash = '#/welcome';
else onHash();
