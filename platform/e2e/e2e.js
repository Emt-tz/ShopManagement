/* End-to-end test and demo recorder for Emt Shop.
 *   node e2e.js            runs the whole product through a real browser against a running server, with assertions
 *   DEMO=1 node e2e.js     same flows, paced for viewing, recorded to ./out/video/*.webm
 * Needs the server on BASE (default http://localhost:8080) with an empty database. */
const { chromium } = require(process.env.PLAYWRIGHT_PATH || '/opt/node-tools/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const BASE = process.env.BASE || 'http://localhost:8080';
const DEMO = !!process.env.DEMO;
const OUT = path.join(__dirname, 'out');
const SHOTS = path.join(OUT, 'shots');
fs.mkdirSync(SHOTS, { recursive: true });
const stamp = Date.now().toString(36);
const OWNER = { name: 'Emmanuel', email: `emmanuel-${stamp}@example.com`, pass: 'password123' };
const STAFF = { name: 'Asha', email: `asha-${stamp}@example.com`, pass: 'password123' };

// Section headings are upper-cased by CSS and innerText returns them upper-cased, so text matching is case-insensitive.
const _test = RegExp.prototype.test;
RegExp.prototype.test = function (str) { return _test.call(this.flags.includes('i') ? this : new RegExp(this.source, this.flags + 'i'), str); };

let passed = 0;
let T0 = Date.now();
const steps = [];
const beat = ms => new Promise(r => setTimeout(r, DEMO ? ms : Math.min(ms, 60)));
function ok(cond, msg) { if (!cond) throw new Error('ASSERT FAILED: ' + msg); }
async function step(name, fn) {
  const t0 = Date.now();
  const start = Date.now() - T0;
  try { await fn(); passed++; steps.push({ name, ok: true, start, end: Date.now() - T0 }); console.log(`  ✓ ${name} (${Date.now() - t0} ms)`); }
  catch (e) { steps.push({ name, ok: false, err: e.message }); console.log(`  ✗ ${name}\n    ${e.message.split('\n')[0]}`); throw e; }
}
const body = p => p.evaluate(() => document.body.innerText.replace(/ /g, ' '));
async function waitText(p, re, timeout = 8000) {
  const t0 = Date.now();
  for (;;) {
    const t = await body(p);
    if (re.test(t)) return t;
    if (Date.now() - t0 > timeout) throw new Error(`Timed out waiting for ${re} on ${p.url()}\n--- page text ---\n${t.slice(0, 600)}`);
    await p.waitForTimeout(100);
  }
}
async function shot(p, name) { await p.screenshot({ path: path.join(SHOTS, name + '.png') }); }
async function tap(p, sel, opts) {
  const loc = p.locator(sel).first();
  if (DEMO) {
    await loc.scrollIntoViewIfNeeded().catch(() => {});
    const box = await loc.boundingBox().catch(() => null);
    if (box) await p.mouse.move(box.x + box.width / 2, box.y + Math.min(box.height / 2, 24), { steps: 14 });
    await p.waitForTimeout(160);
  }
  await loc.click(opts); await beat(450);
}
async function fill(p, sel, v) {
  const loc = p.locator(sel);
  if (DEMO && v.length <= 30) { await loc.click(); await loc.fill(''); await loc.pressSequentially(v, { delay: 45 }); await beat(250); }
  else { await loc.fill(v); await beat(120); }
}
const CURSOR = `(() => { const d = document.createElement('div'); d.id = '__cur';
  d.style.cssText = 'position:fixed;left:0;top:0;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:rgba(0,0,0,.28);border:2px solid #fff;box-shadow:0 1px 6px rgba(0,0,0,.4);z-index:2147483647;pointer-events:none;transition:transform .08s';
  const add = () => document.documentElement.appendChild(d);
  if (document.documentElement) add(); else document.addEventListener('DOMContentLoaded', add);
  addEventListener('mousemove', e => { d.style.left = e.clientX + 'px'; d.style.top = e.clientY + 'px'; }, true);
  addEventListener('mousedown', () => { d.style.transform = 'scale(.7)'; }, true);
  addEventListener('mouseup', () => { d.style.transform = 'scale(1)'; }, true); })();`;

async function ctx(browser, { w, h, device, label, scale, zoom }) {
  // Demo recording: phones render at 1.3x via CSS zoom so the video is crisp; layout stays 390 wide.
  const z = DEMO && zoom ? zoom : 1;
  const opts = { viewport: { width: Math.round(w * z), height: Math.round(h * z) }, deviceScaleFactor: DEMO ? 1 : (scale || 1), locale: 'en-US', timezoneId: 'Africa/Dar_es_Salaam' };
  if (DEMO) opts.recordVideo = { dir: path.join(OUT, 'video', label), size: { width: opts.viewport.width, height: opts.viewport.height } };
  const c = await browser.newContext(opts);
  await c.addInitScript(d => { try { localStorage.setItem('device', d); } catch (e) { /* ignore */ } }, device);
  if (DEMO) await c.addInitScript(CURSOR);
  if (z !== 1) await c.addInitScript(zz => { const f = () => { if (document.documentElement) document.documentElement.style.zoom = String(zz); }; f(); document.addEventListener('DOMContentLoaded', f); }, z);
  const p = await c.newPage();
  p.createdAt = Date.now();
  p.errors = [];
  p.on('pageerror', e => p.errors.push('pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|ERR_INTERNET_DISCONNECTED/.test(m.text())) p.errors.push('console: ' + m.text()); });
  return { c, p };
}
const api = async (token, method, url, data) => {
  const r = await fetch(BASE + '/api' + url, { method, headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token }, body: data ? JSON.stringify(data) : undefined });
  return { status: r.status, json: await r.json().catch(() => ({})) };
};
const tokenOf = p => p.evaluate(() => localStorage.getItem('token'));
const addItems = async (p, items, desktop) => {
  for (const [name, n] of items) {
    for (let i = 0; i < n; i++) {
      const sel = desktop ? `.tile:has-text("${name}")` : `.row:has-text("${name}") [data-act=inc]`;
      await tap(p, sel);
    }
  }
};

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const phone = await ctx(browser, { w: 390, h: 844, device: 'iPhone 15', label: 'phone', scale: 2, zoom: 1.3 });
  const created = {};
  const desk = await ctx(browser, { w: 1280, h: 800, device: 'Mac app', label: 'desktop' });
  created.desktop = desk.p.createdAt;
  const staff = await ctx(browser, { w: 390, h: 844, device: 'iPhone 14', label: 'staff', scale: 2, zoom: 1.3 });
  created.staff = staff.p.createdAt;
  const P = phone.p, D = desk.p, S2 = staff.p;
  created.phone = P.createdAt;
  T0 = Date.now();
  await S2.goto(BASE + '/#/welcome'); await D.goto(BASE + '/#/welcome');
  let token, base = 0, shopId, outboxEmpty;

  console.log(`Emt Shop end-to-end ${DEMO ? '(demo recording)' : ''} against ${BASE}`);
  try {
    /* ---------- Flow 1: get started and subscribe (phone) ---------- */
    await step('1.1 Welcome screen explains the product', async () => {
      await P.goto(BASE + '/'); await waitText(P, /Welcome to\s+Emt Shop/);
      const t = await body(P); ok(/Sell anywhere/.test(t) && /Lipa Namba/.test(t), 'feature list'); await shot(P, '01-welcome'); await beat(1800);
    });
    await step('1.2 Create an account', async () => {
      await tap(P, 'a[href="#/signup"]'); await waitText(P, /Create your account/);
      await fill(P, '#f-name', OWNER.name); await fill(P, '#f-email', OWNER.email); await fill(P, '#f-pass', OWNER.pass);
      await shot(P, '02-signup'); await tap(P, '[data-act=doSignup]'); await waitText(P, /Choose your plan/);
    });
    await step('1.3 Pick a plan and start the free trial', async () => {
      await P.locator('#pl-country').selectOption('TZ'); await beat(400);
      await tap(P, '[data-act=setPeriod][data-id=yearly]'); await tap(P, '[data-act=setPeriod][data-id=monthly]');
      await tap(P, '[data-act=selPlan][data-id=business]'); const t = await body(P);
      ok(/(?:TZS|TSh)\s*49,900/.test(t), 'Business price in TZS'); await shot(P, '03-plans'); await beat(1200);
      await tap(P, '[data-act=subscribe]'); await waitText(P, /What do you sell\?/);
    });
    await step('1.4 Set up the shop with sample data', async () => {
      await fill(P, '#s-name', 'Mikocheni Stationery'); await tap(P, '[data-act=setType][data-id=retail]');
      await fill(P, '#s-till', '5123 4567'); await shot(P, '04-setup'); await beat(900);
      await tap(P, '[data-act=createShop]'); await waitText(P, /Rice 5 kg/); await shot(P, '05-sell-phone');
    });

    /* ---------- Flow 2: ring up a sale (phone) ---------- */
    await step('2.1 Add items and review the order', async () => {
      await addItems(P, [['Rice 5 kg', 2], ['Cooking oil 1 L', 1], ['Soap bar', 1]], false);
      const t = await waitText(P, /Review Order · 4 items/); ok(/(?:TZS|TSh)\s*46,000/.test(t), 'cart total TZS 46,000'); await shot(P, '06-cart'); await beat(900);
    });
    await step('2.2 Pay with Lipa Namba (M-Pesa)', async () => {
      await tap(P, '.cartbar'); await waitText(P, /Pay with/);
      await tap(P, '[data-act=setTender][data-id=lipa_namba]'); await tap(P, '[data-act=setNetwork][data-id=mpesa]');
      const t = await body(P); ok(/5123 4567/.test(t) && /Waiting for the customer/.test(t), 'till number and waiting state'); await shot(P, '07-pay'); await beat(1200);
      await tap(P, '[data-act=confirmPay]'); const d = await waitText(P, /Payment Complete/);
      base = parseInt(/Receipt #(\d+)/i.exec(d)[1], 10); ok(base >= 1 && /(?:TZS|TSh)\s*7,017/.test(d), 'receipt number and VAT 7,017'); await shot(P, '08-done'); await beat(1500);
    });
    token = await tokenOf(P);
    await step('2.3 Server recorded the sale and decremented stock', async () => {
      const shops = (await api(token, 'GET', '/shops')).json.shops; const id = shops[0].id; shopId = id;
      const prods = (await api(token, 'GET', `/shops/${id}/products`)).json.products;
      ok(prods.find(p => p.name === 'Rice 5 kg').stock === 22, 'rice 24 -> 22');
      const sales = (await api(token, 'GET', `/shops/${id}/sales`)).json.sales; ok(sales[0].total === 46000 && sales[0].tender === 'lipa_namba' && sales[0].tenderRef === 'mpesa' && sales[0].number === base, 'latest sale is the 46,000 M-Pesa sale');
    });
    await tap(P, '[data-act=newSale], a[href="#/sell"]');

    /* ---------- Desktop: live monitoring ---------- */
    await step('3.1 Sign in on the desktop app and see the shop live', async () => {
      await D.goto(BASE + '/#/welcome'); await waitText(D, /Welcome to/);
      await tap(D, 'a[href="#/login"]'); await fill(D, '#f-email', OWNER.email); await fill(D, '#f-pass', OWNER.pass);
      await tap(D, '[data-act=doLogin]'); await waitText(D, /Register/); await shot(D, '09-desktop-sell');
      await tap(D, 'a[href="#/shops"]'); const t = await waitText(D, /Live Activity/);
      ok(/Emmanuel sold 4 items for (?:TZS|TSh) 46,000/.test(t), 'feed shows the phone sale with who sold it'); ok(/iPhone 15/.test(t), 'feed shows the device'); await shot(D, '10-desktop-overview'); await beat(1800);
    });
    await step('3.2 A new sale on the phone appears on the desktop in real time', async () => {
      await P.goto(BASE + '/#/sell'); await waitText(P, /Rice 5 kg/);
      await addItems(P, [['Bread', 1], ['Sugar 1 kg', 2]], false);
      await tap(P, '.cartbar'); await tap(P, '[data-act=setTender][data-id=cash]'); await fill(P, '#p-cash', '10000');
      await tap(P, '[data-act=confirmPay]'); await waitText(P, /Payment Complete/);
      await waitText(D, /Emmanuel sold 3 items for (?:TZS|TSh) 8,200/, 6000); await shot(D, '11-desktop-live'); await beat(1500);
    });

    /* ---------- Flow 3: manage products (desktop) ---------- */
    await step('4.1 Change a price on the desktop; it is audited', async () => {
      await tap(D, 'a[href="#/products"]'); await waitText(D, /Notebook A4/);
      await tap(D, '.tr:has-text("Notebook A4")'); await waitText(D, /Details/);
      await fill(D, '#pf-price', '2000'); await shot(D, '12-products-desktop'); await tap(D, '[data-act=saveProduct]');
      await waitText(D, /Notebook A4 saved/); await beat(900);
      const prods = (await api(token, 'GET', `/shops/${(await api(token, 'GET', '/shops')).json.shops[0].id}/products`)).json.products;
      ok(prods.find(p => p.name === 'Notebook A4').price === 2000, 'price saved');
    });
    await step('4.2 Add a new product on the phone', async () => {
      await P.goto(BASE + '/#/products'); await waitText(P, /Notebook A4/); await tap(P, 'a[aria-label="Add Product"]');
      await waitText(P, /Add Product/); await fill(P, '#pf-name', 'Stapler'); await fill(P, '#pf-cat', 'Stationery');
      await fill(P, '#pf-price', '4500'); await fill(P, '#pf-stock', '15'); await shot(P, '13-product-new'); await tap(P, '[data-act=saveProduct]');
      await waitText(P, /Stapler/);
    });

    /* ---------- Flow 4: insights ---------- */
    await step('5.1 Insights show revenue, top products and payment mix', async () => {
      await tap(D, 'a[href="#/insights"]'); const t = await waitText(D, /Top products/);
      ok(/Revenue/.test(t) && /Payment methods/.test(t) && /Lipa Namba/.test(t) && /Cash/.test(t), 'insights content'); ok(/Busiest hour/.test(t), 'busiest hour');
      await tap(D, '[data-act=setRange][data-id=month]'); await beat(500); await tap(D, '[data-act=setRange][data-id=week]'); await beat(800); await shot(D, '14-insights-desktop');
      await P.goto(BASE + '/#/insights'); await waitText(P, /Top products/); await shot(P, '15-insights-phone'); await beat(1200);
    });

    /* ---------- Flow 5: team and devices ---------- */
    await step('6.1 Owner invites a cashier', async () => {
      await tap(D, 'a[href="#/team"]'); await waitText(D, /Invite a team member/);
      await fill(D, '#i-name', STAFF.name); await fill(D, '#i-email', STAFF.email); await fill(D, '#i-pass', STAFF.pass);
      await tap(D, '[data-act=invite]'); await waitText(D, /Team member added/); await beat(600);
    });
    await step('6.2 The cashier signs in on another iPhone and sells', async () => {
      await S2.goto(BASE + '/#/login'); await fill(S2, '#f-email', STAFF.email); await fill(S2, '#f-pass', STAFF.pass);
      await tap(S2, '[data-act=doLogin]'); await waitText(S2, /Rice 5 kg/);
      ok(!(await S2.locator('a[aria-label="Add Product"]').count()), 'cashier has no add-product button');
      await addItems(S2, [['Soap bar', 2]], false); await tap(S2, '.cartbar'); await tap(S2, '[data-act=confirmPay]'); await waitText(S2, /Payment Complete/);
      await waitText(D, /Asha sold 2 items/, 6000); await beat(800);
    });
    await step('6.3 Team screen shows who did what, on which device', async () => {
      await D.reload(); await waitText(D, /Team and devices/);
      const t = await waitText(D, /Made a sale · iPhone 14/);
      ok(/changed the price of Notebook A4/.test(t), 'audit shows the price change'); ok(/Mac app/.test(t), 'audit shows the Mac app device'); await shot(D, '16-team-desktop'); await beat(2000);
    });

    /* ---------- Flow 6: receipts and void ---------- */
    await step('7.1 Void a sale from the receipt list', async () => {
      await tap(D, 'a[href="#/history"]'); await waitText(D, new RegExp('Receipt #' + (base + 2))); await tap(D, 'a[href^="#/receipt/"]');
      await waitText(D, /Void Sale/); await shot(D, '17-receipt'); await tap(D, '[data-act=voidSale]'); await tap(D, '[data-act=voidSale]');
      await waitText(D, /Sale voided/); await beat(800); await tap(D, '.modal a[href="#/history"]');
      const prods = (await api(token, 'GET', `/shops/${shopId}/products`)).json.products;
      ok(prods.find(p => p.name === 'Soap bar').stock === 59, 'void restocked the soap (60-1-2+2)'); // sold 1 + 2, voided the latest (2)
    });

    /* ---------- Flow 7: offline sale ---------- */
    let before = 0;
    await step('8.1 Selling offline saves the sale on the device', async () => {
      await P.goto(BASE + '/#/sell'); await waitText(P, /Rice 5 kg/);
      before = (await api(token, 'GET', `/shops/${shopId}/sales?limit=200`)).json.sales.length;
      await phone.c.setOffline(true); await beat(300);
      await addItems(P, [['Salt 500 g', 1]], false); await tap(P, '.cartbar'); await tap(P, '[data-act=confirmPay]');
      const t = await waitText(P, /Saved on this device/); ok(/send when you are back online/.test(t), 'offline notice'); await shot(P, '18-offline-sale'); await beat(1800);
      ok((await api(token, 'GET', `/shops/${shopId}/sales?limit=200`)).json.sales.length === before, 'server has not seen it yet');
    });
    await step('8.2 Reloading the app while offline still opens it, with the catalogue', async () => {
      await P.reload(); const t = await waitText(P, /Rice 5 kg/, 10000);
      ok(await P.evaluate(() => document.body.classList.contains('is-offline')), 'offline banner state'); await shot(P, '18b-offline-reload'); await beat(1800);
    });
    await step('8.3 Back online: the queued sale reaches the server exactly once', async () => {
      await phone.c.setOffline(false);
      let n = 0; for (let i = 0; i < 40; i++) { n = (await api(token, 'GET', `/shops/${shopId}/sales?limit=200`)).json.sales.length; if (n >= before + 1) break; await P.waitForTimeout(500); }
      await P.waitForTimeout(1500);
      n = (await api(token, 'GET', `/shops/${shopId}/sales?limit=200`)).json.sales.length;
      ok(n === before + 1, 'queued sale reached the server exactly once (sales ' + before + ' -> ' + n + ')');
      ok(outboxEmpty = await P.evaluate(() => (localStorage.getItem('outbox') || '[]') === '[]'), 'outbox drained');
    });

    /* ---------- Flow 8: language ---------- */
    await step('9.1 Switch the whole app to Kiswahili (server catalog)', async () => {
      await P.goto(BASE + '/#/account'); await waitText(P, /Subscription/);
      await P.locator('#a-lang').selectOption('sw'); const t = await waitText(P, /Usajili/);
      ok(/Akaunti/.test(t), 'Swahili account title'); await shot(P, '19-account-sw');
      await P.goto(BASE + '/#/sell'); const s = await waitText(P, /Zimebaki/); ok(/Zimebaki/.test(s) && /Bidhaa/.test(s), 'Swahili sell screen'); ok(/TSh/.test(s), 'currency formatted by CLDR as TSh'); await shot(P, '20-sell-sw'); await beat(1800);
      await P.goto(BASE + '/#/account'); await P.locator('#a-lang').selectOption('en'); await waitText(P, /Subscription/);
    });

    /* ---------- Flow 9: second shop (mobile money agent) ---------- */
    await step('10.1 Plan limit: Business includes one shop', async () => {
      await tap(D, 'a[href="#/shops"]'); await tap(D, '[data-act=addShop]'); await waitText(D, /What do you sell\?/);
      await fill(D, '#s-name', 'Kariakoo Mobile Money'); await tap(D, '[data-act=setType][data-id=mobile_money]'); await tap(D, '[data-act=createShop]');
      const t = await waitText(D, /includes one shop/); ok(/Upgrade/.test(t), 'upgrade hint'); await shot(D, '21-plan-limit'); await beat(1500);
    });
    await step('10.2 Upgrade to Multi-shop', async () => {
      await D.goto(BASE + '/#/plans'); await waitText(D, /Choose your plan/);
      await tap(D, '[data-act=selPlan][data-id=multi]'); await tap(D, '[data-act=subscribe]'); await waitText(D, /Subscription/);
      const t = await body(D); ok(/Multi-shop/.test(t), 'plan switched'); await shot(D, '22-account-multi'); await beat(900);
    });
    await step('10.3 Create the mobile money shop and manage float', async () => {
      await D.goto(BASE + '/#/setup'); await waitText(D, /What do you sell\?/);
      await fill(D, '#s-name', 'Kariakoo Mobile Money'); await tap(D, '[data-act=setType][data-id=mobile_money]'); await tap(D, '[data-act=createShop]');
      await waitText(D, /Float by network/); await shot(D, '23-float-desktop');
      const t = await body(D); ok(/Airtel Money/.test(t) && /Low/.test(t), 'airtel flagged low');
      await D.locator('#fl-net').selectOption('mpesa'); await fill(D, '#fl-amt', '200000'); await tap(D, '[data-act=floatTx]'); await waitText(D, /Transaction recorded/);
      await beat(900); await shot(D, '24-float-after');
      const t2 = await waitText(D, /Cash Out · M-Pesa/); ok(/Commission today/.test(t2), 'commission shown');
    });
    await step('10.4 Overview shows both shops with alerts', async () => {
      await tap(D, 'a[href="#/shops"]'); const t = await waitText(D, /Kariakoo Mobile Money/);
      ok(/Mikocheni Stationery/.test(t) && /float is low/.test(t), 'both shops and the float alert'); await shot(D, '25-overview-two-shops'); await beat(2200);
    });
    await step('10.5 Mobile money on the phone', async () => {
      await P.goto(BASE + '/#/shops'); await waitText(P, /Kariakoo Mobile Money/);
      await tap(P, '.row:has-text("Kariakoo Mobile Money")'); await waitText(P, /Float by network/); await shot(P, '26-float-phone'); await beat(1800);
    });

    /* ---------- Flow 10: subscription management ---------- */
    await step('11.1 Cancel the subscription: access stays until the period ends', async () => {
      await tap(D, 'a[href="#/account"]'); await waitText(D, /Cancel Subscription/);
      await tap(D, '[data-act=cancelSub]'); await tap(D, '[data-act=cancelSub]'); const t = await waitText(D, /Ends /);
      ok(/Subscription canceled/.test(t) || /Ends/.test(t), 'canceled status'); await shot(D, '27-canceled'); await beat(1500);
      const me = (await api(token, 'GET', '/me')).json; ok(me.subscription.status === 'canceled' && me.subscription.active, 'still active until renewal date');
    });
    await step('11.2 Sign out and back in', async () => {
      await tap(D, '[data-act=signOut]'); await waitText(D, /Welcome to/);
      await tap(D, 'a[href="#/login"]'); await fill(D, '#f-email', OWNER.email); await fill(D, '#f-pass', 'wrong-password'); await tap(D, '[data-act=doLogin]');
      await waitText(D, /incorrect/); await fill(D, '#f-pass', OWNER.pass); await tap(D, '[data-act=doLogin]'); await waitText(D, /Register|Float/);
    });

    /* ---------- Client health ---------- */
    await step('12.1 No JavaScript errors in any browser context', async () => {
      const all = [...P.errors, ...D.errors, ...S2.errors]; ok(all.length === 0, all.join(' | '));
    });
  } catch (e) {
    console.log('\nFAILED: ' + e.message);
    await shot(P, 'fail-phone').catch(() => {}); await shot(D, 'fail-desktop').catch(() => {});
    process.exitCode = 1;
  } finally {
    const vids = DEMO ? { phone: P.video(), desktop: D.video(), staff: S2.video() } : {};
    await phone.c.close(); await desk.c.close(); await staff.c.close();
    if (DEMO) { for (const k of Object.keys(vids)) vids[k] = await vids[k].path(); fs.writeFileSync(path.join(OUT, 'timeline.json'), JSON.stringify({ created, t0: T0, videos: vids, steps }, null, 1)); }
    await browser.close();
    console.log(`\n${passed} steps passed${process.exitCode ? ', 1 failed' : ''}`);
    fs.writeFileSync(path.join(OUT, 'results.json'), JSON.stringify(steps, null, 1));
  }
})();
