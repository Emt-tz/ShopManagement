/* One continuous, paced recording of the web app: onboarding, stocking the shelf, selling for cash.
 *   node journey.js      needs the server on BASE (sandbox on or off, nothing is simulated here). Writes out/journey.mp4 */
const { chromium } = require(process.env.PLAYWRIGHT_PATH || '/opt/node-tools/node_modules/playwright');
const fs = require('fs'), path = require('path');
const { execFileSync } = require('child_process');
const BASE = process.env.BASE || 'http://localhost:8080';
const OUT = path.join(__dirname, 'out', 'journey'); fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
const ZOOM = 1.25, W = 1920, H = 1080;
const sleep = ms => new Promise(r => setTimeout(r, ms));

const OVERLAY = `(() => {
  const css = document.createElement('style');
  css.textContent = '#__cur{position:fixed;left:0;top:0;width:26px;height:26px;margin:-4px 0 0 -4px;z-index:2147483647;pointer-events:none;filter:drop-shadow(0 2px 3px rgba(0,0,0,.35));transition:transform .12s cubic-bezier(.2,.9,.3,1.2)}'
   + '#__cur.down{transform:scale(.82)}'
   + '.__rip{position:fixed;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;border:3px solid rgba(0,113,227,.75);background:rgba(0,113,227,.18);z-index:2147483646;pointer-events:none;animation:__rip .6s cubic-bezier(.2,.7,.3,1) forwards}'
   + '@keyframes __rip{to{transform:scale(4.2);opacity:0}}';
  const mount = () => {
    document.head.appendChild(css);
    const d = document.createElement('div'); d.id = '__cur';
    d.innerHTML = '<svg width="26" height="26" viewBox="0 0 24 24"><path d="M4 2l15 9-6.5 1.6L9.4 19z" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    document.documentElement.appendChild(d);
    addEventListener('mousemove', e => { d.style.left = e.clientX + 'px'; d.style.top = e.clientY + 'px'; }, true);
    addEventListener('mousedown', e => { d.classList.add('down'); const r = document.createElement('div'); r.className = '__rip'; r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px'; document.documentElement.appendChild(r); setTimeout(() => r.remove(), 700); }, true);
    addEventListener('mouseup', () => d.classList.remove('down'), true);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
  const z = () => { if (document.documentElement) document.documentElement.style.zoom = '${ZOOM}'; }; z(); document.addEventListener('DOMContentLoaded', z);
})();`;

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1, locale: 'en-US', timezoneId: 'Africa/Dar_es_Salaam', recordVideo: { dir: OUT, size: { width: W, height: H } } });
  await ctx.addInitScript(OVERLAY);
  await ctx.addInitScript(() => { try { localStorage.setItem('device', 'Mac app'); localStorage.setItem('lang', 'en'); } catch (e) { } });
  const p = await ctx.newPage(); const created = Date.now();
  const marks = []; let T0 = 0;
  const now = () => Date.now() - T0;
  const chapter = (n, title, sub) => marks.push({ kind: 'chapter', at: now(), n, title, sub });
  const say = txt => marks.push({ kind: 'cap', at: now(), txt });
  const errors = []; p.on('pageerror', e => errors.push(e.message));
  const body = () => p.evaluate(() => document.body.innerText);
  const waitText = async (re, ms = 10000) => { const t = Date.now(); for (;;) { if (new RegExp(re.source, 'i').test(await body())) return; if (Date.now() - t > ms) { await p.screenshot({ path: path.join(OUT, 'fail.png') }); throw new Error('timeout waiting for ' + re + '\n' + (await body()).slice(0, 400)); } await sleep(100); } };

  let mx = 120, my = 120;
  // Eased, slightly curved pointer travel (ease-in-out, 60 frames a second).
  const glide = async (x, y, ms = 750) => {
    const sx = mx, sy = my, dx = x - sx, dy = y - sy, dist = Math.hypot(dx, dy), bow = Math.min(60, dist * 0.08) * (dx >= 0 ? -1 : 1);
    const n = Math.max(8, Math.round(ms / 16));
    for (let i = 1; i <= n; i++) {
      const t = i / n, e = t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2, arc = Math.sin(Math.PI * e) * bow;
      mx = sx + dx * e + (-dy / (dist || 1)) * arc; my = sy + dy * e + (dx / (dist || 1)) * arc;
      await p.mouse.move(mx, my); await sleep(10);
    }
    mx = x; my = y; await p.mouse.move(x, y);
  };
  const pointAt = async sel => {
    const loc = p.locator(sel).first(); await loc.waitFor({ state: 'visible', timeout: 10000 });
    await loc.scrollIntoViewIfNeeded().catch(() => { }); await sleep(120);
    const bx = await loc.boundingBox(); if (!bx) throw new Error('no box ' + sel);
    return { loc, x: bx.x + bx.width / 2 + (bx.width > 80 ? Math.min(12, bx.width * .08) : 0), y: bx.y + Math.min(bx.height / 2, 28) };
  };
  const click = async (sel, { ms = 750, after = 600 } = {}) => {
    const { loc, x, y } = await pointAt(sel); await glide(x, y, ms); await sleep(140);
    await p.mouse.down(); await sleep(80); await p.mouse.up(); await sleep(after); return loc;
  };
  const type = async (sel, text, delay = 62) => {
    await click(sel, { ms: 600, after: 160 });
    const loc = p.locator(sel).first(); await loc.fill('');
    for (const ch of text) { await p.keyboard.type(ch); await sleep(delay + (ch === ' ' ? 40 : Math.round(Math.random() * 28))); }
    await sleep(260);
  };
  const choose = async (sel, value) => { const { loc, x, y } = await pointAt(sel); await glide(x, y, 650); await sleep(200); await loc.selectOption(value); await sleep(600); };
  const scrollTo = async y => { await p.evaluate(yy => document.querySelectorAll('*').forEach(e => { if (e.scrollHeight > e.clientHeight + 10 && getComputedStyle(e).overflowY !== 'visible') e.scrollTo({ top: yy, behavior: 'smooth' }); }), y); await sleep(900); };

  await p.goto(BASE + '/#/welcome'); await waitText(/Welcome to/); T0 = Date.now();
  const lead = (T0 - created) / 1000;

  /* ---- 1. Onboarding ---- */
  chapter(1, 'Get started', 'Free for 3 months, no card');
  say('Welcome to Emt Shop. Everything is free for 3 months.'); await sleep(2600);
  await click('a[href="#/signup"]'); await waitText(/Create your account/);
  say('Create your account'); await sleep(500);
  const email = `neema-${Date.now().toString(36)}@example.com`;
  await type('#f-name', 'Neema Mushi'); await type('#f-email', email); await type('#f-pass', 'password123', 50);
  await click('[data-act=doSignup]'); await waitText(/What do you sell\?/);

  chapter(2, 'Set up your shop', 'A name, a type, a country');
  say('Name your shop'); await sleep(400);
  await type('#s-name', 'Mama Neema Stationery');
  say('Pick what you sell: stationery and retail'); await sleep(1200);
  await choose('#s-country', 'TZ'); await sleep(300);
  say('Tanzania sets TZS, VAT and Lipa Namba automatically');
  await type('#s-till', '5123 4567'); await sleep(900);
  await scrollTo(600);
  say('This client takes cash only. One switch hides everything else.');
  await click('[data-act=toggleCash]', { ms: 700, after: 1500 });
  await click('[data-act=toggleDemo]', { ms: 500, after: 1300 });   // start empty: add real stock next
  await click('[data-act=createShop]', { ms: 700, after: 400 }); await waitText(/Add your first product|is ready/); await sleep(2600);

  /* ---- 2. Add stock ---- */
  chapter(3, 'Add your stock', 'Name, price, how many you have');
  say('The shelf is empty. Add what you sell.'); await sleep(900);
  await click('[data-act=firstProduct]', { ms: 800, after: 900 }); await waitText(/Add Product|Details/);
  const stock = [['Exercise book 96 pages', 'Books', '1500', '120'], ['Ballpoint pen blue', 'Writing', '400', '300'], ['HB pencil', 'Writing', '300', '250'], ['A4 paper ream', 'Paper', '14000', '40'],
    ['Calculator scientific', 'Office', '28000', '12'], ['Stapler', 'Office', '5500', '18'], ['Glue stick', 'Tools', '1200', '60'], ['Plastic folder', 'Filing', '800', '90']];
  for (let i = 0; i < stock.length; i++) {
    const [n, c, pr, st] = stock[i]; const fast = i >= 3;
    if (i) { await click('[data-act=newProduct]', { ms: 600, after: 500 }); }
    if (i === 0) say('Name, category, price in shillings, and stock on hand');
    if (i === 3) say('Faster now: every product is saved the moment you press Save');
    await type('#pf-name', n, fast ? 30 : 58); await type('#pf-cat', c, fast ? 26 : 50); await type('#pf-price', pr, fast ? 36 : 70); await type('#pf-stock', st, fast ? 36 : 70);
    await click('[data-act=saveProduct]', { ms: 650, after: 1100 }); await waitText(new RegExp(n.split(' ')[0] + '.*saved|saved', 'i'), 6000).catch(() => { });
  }
  say('Eight products on the shelf. Low stock is flagged automatically.'); await sleep(2800);

  /* ---- 3. Sell ---- */
  chapter(4, 'Sell for cash', 'Tap, charge, done');
  await click('a[href="#/sell"]', { ms: 800, after: 900 }); await waitText(/Current Order/);
  say('Tap products to build the order'); await sleep(900);
  const tap = async (name, n = 1) => { for (let i = 0; i < n; i++) await click(`.tile:has-text("${name}")`, { ms: i ? 380 : 800, after: 380 }); };
  await tap('Ballpoint pen blue', 3); await tap('Exercise book 96 pages', 2); await tap('A4 paper ream', 1);
  say('The order, VAT and total update as you tap'); await sleep(2400);
  await click('[data-act=checkout]', { ms: 800, after: 900 }); await waitText(/Cash/);
  say('Cash is the only way to pay at this shop'); await sleep(1800);
  await type('#p-cash', '25000', 90); say('Enter what the customer hands over: change is worked out for you'); await sleep(2400);
  await click('[data-act=confirmPay]', { ms: 800, after: 500 }); await waitText(/Payment Complete/);
  say('Sale recorded. Stock goes down. A receipt number is issued.'); await sleep(4200);
  await click('a.btn[href="#/sell"]', { ms: 800, after: 900 });

  say('Second customer'); await sleep(700);
  await tap('Calculator scientific', 1); await tap('Stapler', 1); await tap('Glue stick', 2);
  await click('[data-act=checkout]', { ms: 800, after: 700 }); await waitText(/Cash/);
  await type('#p-cash', '40000', 90); await sleep(1400);
  await click('[data-act=confirmPay]', { ms: 800, after: 500 }); await waitText(/Payment Complete/); await sleep(3400);
  await click('a.btn[href="#/sell"]', { ms: 800, after: 900 });

  /* ---- 4. See the business ---- */
  chapter(5, 'See your business', 'Receipts, stock and live activity');
  say('Every sale is a receipt'); await click('a[href="#/history"]', { ms: 800, after: 1500 }); await waitText(/Receipt #/);
  await click('a[href^="#/receipt/"]', { ms: 700, after: 2800 });
  await p.keyboard.press('Escape'); await sleep(300); if (/Void Sale/.test(await body())) { const c = p.locator('.modal a[href="#/history"]'); if (await c.count()) await click('.modal a[href="#/history"]', { ms: 500, after: 700 }); }
  say('Stock updated live'); await click('a[href="#/products"]', { ms: 800, after: 2800 });
  say('Dashboard: today, recommended actions and who sold what'); await click('a[href="#/shops"]', { ms: 800, after: 4200 });
  say('That is the whole journey. Add stock, sell, see how you are doing.'); await sleep(3200);
  const total = now();
  const vpath = await p.video().path(); await ctx.close(); await b.close();
  fs.writeFileSync(path.join(OUT, 'timeline.json'), JSON.stringify({ marks, total, lead, video: vpath, errors }, null, 1));
  console.log('recorded', (total / 1000).toFixed(1) + 's', 'errors:', errors.length ? errors : 'none');
})().catch(e => { console.error(e); process.exit(1); });
