/* One continuous, paced recording of the web app: onboarding, stocking the shelf, selling for cash.
 *   node journey.js        needs the server on BASE. Captures real screen frames with their own timestamps (CDP screencast),
 *                          so captions line up with the screen exactly. Writes out/journey/ then run compose-journey.js. */
const { chromium } = require(process.env.PLAYWRIGHT_PATH || '/opt/node-tools/node_modules/playwright');
const fs = require('fs'), path = require('path');
const BASE = process.env.BASE || 'http://localhost:8080';
const OUT = path.join(__dirname, 'out', 'journey'); fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(path.join(OUT, 'frames'), { recursive: true });
const ZOOM = 1.25, W = 1920, H = 1080;
const sleep = ms => new Promise(r => setTimeout(r, ms));

// The pointer and click ripple live in the page. Mouse events report real pixels but the page is zoomed, so positions are divided by the zoom.
const OVERLAY = `(() => {
  const Z = ${ZOOM};
  const css = document.createElement('style');
  css.textContent = '#__cur{position:fixed;left:0;top:0;width:26px;height:26px;z-index:2147483647;pointer-events:none;filter:drop-shadow(0 2px 3px rgba(0,0,0,.4));transition:transform .12s cubic-bezier(.2,.9,.3,1.2)}'
   + '#__cur.down{transform:scale(.8)}'
   + '.__rip{position:fixed;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;border:3px solid rgba(0,113,227,.8);background:rgba(0,113,227,.2);z-index:2147483646;pointer-events:none;animation:__rip .65s cubic-bezier(.2,.7,.3,1) forwards}'
   + '@keyframes __rip{to{transform:scale(4.4);opacity:0}}';
  const mount = () => {
    document.head.appendChild(css);
    const d = document.createElement('div'); d.id = '__cur';
    d.innerHTML = '<svg width="26" height="26" viewBox="0 0 24 24"><path d="M4 2l15 9-6.5 1.6L9.4 19z" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    document.documentElement.appendChild(d);
    const at = e => { d.style.left = (e.clientX / Z - 3) + 'px'; d.style.top = (e.clientY / Z - 2) + 'px'; };
    addEventListener('mousemove', at, true);
    addEventListener('mousedown', e => { at(e); d.classList.add('down'); const r = document.createElement('div'); r.className = '__rip'; r.style.left = e.clientX / Z + 'px'; r.style.top = e.clientY / Z + 'px'; document.documentElement.appendChild(r); setTimeout(() => r.remove(), 750); }, true);
    addEventListener('mouseup', () => d.classList.remove('down'), true);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
  const z = () => { if (document.documentElement) document.documentElement.style.zoom = '${ZOOM}'; }; z(); document.addEventListener('DOMContentLoaded', z);
})();`;

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1, locale: 'en-US', timezoneId: 'Africa/Dar_es_Salaam' });
  await ctx.addInitScript(OVERLAY);
  await ctx.addInitScript(() => { try { localStorage.setItem('device', 'Mac app'); localStorage.setItem('lang', 'en'); } catch (e) { } });
  const p = await ctx.newPage();

  // Screen capture with the browser's own frame timestamps.
  const cdp = await ctx.newCDPSession(p);
  const frames = []; let writing = Promise.resolve();
  cdp.on('Page.screencastFrame', ev => {
    const i = frames.length; const file = `frames/${String(i).padStart(6, '0')}.jpg`;
    frames.push({ file, ts: ev.metadata.timestamp });
    const buf = Buffer.from(ev.data, 'base64');
    writing = writing.then(() => fs.promises.writeFile(path.join(OUT, file), buf));
    cdp.send('Page.screencastFrameAck', { sessionId: ev.sessionId }).catch(() => { });
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: W, maxHeight: H, everyNthFrame: 1 });

  const marks = []; const wall = () => Date.now() / 1000;
  const chapter = (n, title, sub) => marks.push({ kind: 'chapter', at: wall(), n, title, sub });
  const say = txt => marks.push({ kind: 'cap', at: wall(), txt });
  const errors = []; p.on('pageerror', e => errors.push(e.message));
  const body = () => p.evaluate(() => document.body.innerText);
  const waitText = async (re, ms = 12000) => { const t = Date.now(); for (;;) { if (new RegExp(re.source, 'i').test(await body())) return; if (Date.now() - t > ms) { await p.screenshot({ path: path.join(OUT, 'fail.png') }); throw new Error('timeout waiting for ' + re + '\n' + (await body()).slice(0, 400)); } await sleep(100); } };

  let mx = 160, my = 160;
  const glide = async (x, y, ms = 750) => {
    const sx = mx, sy = my, dx = x - sx, dy = y - sy, dist = Math.hypot(dx, dy) || 1, bow = Math.min(70, dist * 0.09) * (dx >= 0 ? -1 : 1);
    const n = Math.max(10, Math.round(ms / 16));
    for (let i = 1; i <= n; i++) {
      const t = i / n, e = t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2, arc = Math.sin(Math.PI * e) * bow;
      mx = sx + dx * e + (-dy / dist) * arc; my = sy + dy * e + (dx / dist) * arc;
      await p.mouse.move(mx, my); await sleep(8);
    }
    mx = x; my = y; await p.mouse.move(x, y);
  };
  const pointAt = async sel => {
    const loc = p.locator(sel).first(); await loc.waitFor({ state: 'visible', timeout: 12000 });
    await loc.scrollIntoViewIfNeeded().catch(() => { }); await sleep(150);
    const bx = await loc.boundingBox(); if (!bx) throw new Error('no box ' + sel);
    return { loc, x: bx.x + bx.width * (bx.width > 200 ? 0.78 : 0.5), y: bx.y + Math.min(bx.height / 2, 30) };
  };
  const click = async (sel, { ms = 750, after = 600 } = {}) => {
    const { loc, x, y } = await pointAt(sel); await glide(x, y, ms); await sleep(160);
    await p.mouse.down(); await sleep(90); await p.mouse.up(); await sleep(after); return loc;
  };
  const type = async (sel, text, delay = 62) => {
    await click(sel, { ms: 600, after: 160 });
    await p.locator(sel).first().fill('');
    for (const ch of text) { await p.keyboard.type(ch); await sleep(delay + (ch === ' ' ? 40 : Math.round(Math.random() * 28))); }
    await sleep(280);
  };
  const choose = async (sel, value) => { const { loc, x, y } = await pointAt(sel); await glide(x, y, 650); await sleep(220); await loc.selectOption(value); await sleep(700); };
  const scrollTo = async y => { await p.evaluate(yy => document.querySelectorAll('*').forEach(e => { if (e.scrollHeight > e.clientHeight + 10 && getComputedStyle(e).overflowY !== 'visible') e.scrollTo({ top: yy, behavior: 'smooth' }); }), y); await sleep(1000); };

  await p.goto(BASE + '/#/welcome'); await waitText(/Welcome to/); await sleep(700);
  const T0 = wall();

  /* ---- 1. Onboarding ---- */
  chapter(1, 'Get started', 'Free for 3 months, no card');
  say('Welcome to Emt Shop. The whole platform is free for 3 months.'); await sleep(3200);
  await click('a[href="#/signup"]'); await waitText(/Create your account/); await sleep(300);
  say('Create your account with a name, an email and a password');
  const email = `neema-${Date.now().toString(36)}@example.com`;
  await type('#f-name', 'Neema Mushi'); await type('#f-email', email); await type('#f-pass', 'password123', 50);
  await click('[data-act=doSignup]'); await waitText(/What do you sell\?/); await sleep(700);

  chapter(2, 'Set up your shop', 'A name, a type, a country');
  say('Give your shop a name'); await sleep(500);
  await type('#s-name', 'Mama Neema Stationery');
  await click('[data-act=setType][data-id=retail]', { ms: 700, after: 500 });
  say('Choose what you sell: stationery and retail'); await sleep(1700);
  await choose('#s-country', 'TZ');
  say('Tanzania sets the currency (TSh), VAT and Lipa Namba for you'); await sleep(900);
  await type('#s-till', '5123 4567'); await sleep(900);
  await scrollTo(700);
  await click('[data-act=toggleCash]', { ms: 700, after: 600 });
  say('This shop takes cash only: one switch hides mobile money and card at the till'); await sleep(2600);
  await click('[data-act=toggleDemo]', { ms: 500, after: 600 });
  say('Start with an empty shelf. We will add the real stock next.'); await sleep(1800);
  await click('[data-act=createShop]', { ms: 700, after: 400 }); await waitText(/Add your first product/); await sleep(900);

  /* ---- 2. Add stock ---- */
  chapter(3, 'Add your stock', 'Name, price, how many you have');
  say('The shelf is empty. Add what you sell.'); await sleep(2800);
  await click('[data-act=firstProduct]', { ms: 800, after: 900 }); await waitText(/Add Product/); await sleep(400);
  say('Name, category, price in shillings and how many you have');
  const stock = [['Exercise book 96 pages', 'Books', '1500', '120'], ['Ballpoint pen blue', 'Writing', '400', '300'], ['HB pencil', 'Writing', '300', '250'], ['A4 paper ream', 'Paper', '14000', '40'],
    ['Calculator scientific', 'Office', '28000', '12'], ['Stapler', 'Office', '5500', '18'], ['Glue stick', 'Tools', '1200', '60'], ['Plastic folder', 'Filing', '800', '90']];
  for (let i = 0; i < stock.length; i++) {
    const [n, c, pr, st] = stock[i]; const fast = i >= 3;
    if (i) await click('[data-act=newProduct]', { ms: 600, after: 500 });
    if (i === 3) say('Faster now: each product is saved the moment you press Save');
    await type('#pf-name', n, fast ? 30 : 58); await type('#pf-cat', c, fast ? 26 : 50); await type('#pf-price', pr, fast ? 36 : 70); await type('#pf-stock', st, fast ? 36 : 70);
    await click('[data-act=saveProduct]', { ms: 650, after: 900 });
    await waitText(new RegExp(`${i + 1} items?`), 6000);
  }
  say('Eight products on the shelf, each with its price and stock'); await sleep(3600);

  /* ---- 3. Sell ---- */
  await click('a[href="#/sell"]', { ms: 800, after: 800 }); await waitText(/Current Order/); await sleep(500);
  chapter(4, 'Sell for cash', 'Tap, charge, done');
  say('Tap products to build the order'); await sleep(800);
  const tap = async (name, n = 1) => { for (let i = 0; i < n; i++) await click(`.tile:has-text("${name}")`, { ms: i ? 380 : 800, after: 420 }); };
  await tap('Ballpoint pen blue', 3); await tap('Exercise book 96 pages', 2); await tap('A4 paper ream', 1);
  say('The order, VAT and total update as you tap'); await sleep(2800);
  await click('[data-act=checkout]', { ms: 800, after: 700 }); await waitText(/Confirm Payment/); await sleep(300);
  say('Cash is the only way to pay at this shop'); await sleep(2200);
  await type('#p-cash', '25000', 90);
  say('Type what the customer hands over: the change is worked out for you'); await sleep(2800);
  await click('[data-act=confirmPay]', { ms: 800, after: 300 }); await waitText(/Payment Complete/); await sleep(500);
  say('Sale recorded: stock goes down and a receipt number is issued'); await sleep(4600);
  await click('a.btn[href="#/sell"]', { ms: 800, after: 800 }); await waitText(/Current Order/);
  say('Next customer'); await sleep(700);
  await tap('Calculator scientific', 1); await tap('Stapler', 1); await tap('Glue stick', 2);
  await click('[data-act=checkout]', { ms: 800, after: 700 }); await waitText(/Confirm Payment/);
  await type('#p-cash', '40000', 90); await sleep(1400);
  await click('[data-act=confirmPay]', { ms: 800, after: 300 }); await waitText(/Payment Complete/); await sleep(500);
  say('Another sale, another receipt. Nothing to reconcile at the end of the day.'); await sleep(3800);
  await click('a.btn[href="#/sell"]', { ms: 800, after: 800 }); await waitText(/Current Order/);

  /* ---- 4. See the business ---- */
  await click('a[href="#/history"]', { ms: 800, after: 600 }); await waitText(/Receipt #/); await sleep(400);
  chapter(5, 'See your business', 'Receipts, stock and live activity');
  say('Every sale is a receipt'); await sleep(2200);
  await click('a[href^="#/receipt/"]', { ms: 700, after: 600 }); await waitText(/VAT/);
  say('Open any receipt: the items, the VAT and who sold it'); await sleep(3600);
  if (await p.locator('.modal a[href="#/history"]').count()) await click('.modal a[href="#/history"]', { ms: 500, after: 700 }); else { await p.keyboard.press('Escape'); await sleep(600); }
  await click('a[href="#/products"]', { ms: 800, after: 600 }); await waitText(/In stock/);
  say('Stock went down by exactly what was sold'); await sleep(3800);
  await click('a[href="#/shops"]', { ms: 800, after: 600 }); await waitText(/Live Activity/); await sleep(500);
  say("The dashboard shows today's sales, what to do next, and who sold what"); await sleep(5200);
  say('That is the whole journey: add stock, sell, see how you are doing'); await sleep(3600);
  const END = wall();
  await cdp.send('Page.stopScreencast'); await writing; await ctx.close(); await b.close();
  fs.writeFileSync(path.join(OUT, 'timeline.json'), JSON.stringify({ marks, T0, END, frames, errors }, null, 0));
  console.log('recorded', (END - T0).toFixed(1) + 's,', frames.length, 'frames, errors:', errors.length ? errors : 'none');
})().catch(e => { console.error(e); process.exit(1); });
