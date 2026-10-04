/* Service worker: network-first for the app shell so updates arrive immediately, cache fallback so the app opens offline. */
const CACHE = 'emtshop-shell-v2';
const SHELL = ['/', '/index.html', '/styles.css', '/core.js', '/views-a.js', '/views-b.js', '/views-c.js', '/app.js', '/icon.svg', '/manifest.webmanifest',
  '/fonts/inter-latin-wght-normal.woff2', '/fonts/inter-latin-ext-wght-normal.woff2'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin || u.pathname.startsWith('/api') || u.pathname === '/ws') return;
  e.respondWith(fetch(e.request).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return res;
  }).catch(() => caches.match(e.request).then(r => r || caches.match('/index.html'))));
});
