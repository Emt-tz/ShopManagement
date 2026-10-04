/* Month-in-the-life showcase: a stationery shop (standard catalogue, ~1000 customers over 30 days, 3 staff on different devices)
 * and a mobile money agent counter, seeded through the real API, then browsed in a real browser and recorded.
 *   node month.js        needs the server on BASE with EMTSHOP_SANDBOX=true; writes out/month.mp4 */
const { chromium } = require(process.env.PLAYWRIGHT_PATH || '/opt/node-tools/node_modules/playwright');
const fs = require('fs'), path = require('path');
const { execFileSync } = require('child_process');
const BASE = process.env.BASE || 'http://localhost:8080';
const OUT = path.join(__dirname, 'out', 'month'); fs.mkdirSync(OUT, { recursive: true });
const stamp = Date.now().toString(36);
const api = async (tok, method, url, data, hdr = {}) => {
  const r = await fetch(BASE + '/api' + url, { method, headers: { 'Content-Type': 'application/json', ...(tok ? { Authorization: 'Bearer ' + tok } : {}), ...hdr }, body: data ? JSON.stringify(data) : undefined });
  const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(`${method} ${url} ${r.status} ${JSON.stringify(j)}`); return j;
};
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const email = `neema-${stamp}@example.com`;
  const { token } = await api(null, 'POST', '/auth/signup', { name: 'Neema Mushi', email, password: 'password123' });
  const st = (await api(token, 'POST', '/shops', { name: 'Neema Stationery', type: 'retail', country: 'TZ' })).shop;
  const ag = (await api(token, 'POST', '/shops', { name: 'Neema Pesa Agent', type: 'mobile_money', country: 'TZ' })).shop;
  for (const [n, role] of [['Asha', 'cashier'], ['Baraka', 'cashier'], ['Zawadi', 'manager']]) {
    for (const s of [st, ag]) await api(token, 'POST', `/shops/${s.id}/members`, { name: n, email: `${n.toLowerCase()}-${stamp}-${s.type}@example.com`, password: 'password123', role }).catch(e => console.log('invite', e.message));
  }
  const r1 = await api(token, 'POST', `/shops/${st.id}/demo-month`); const r2 = await api(token, 'POST', `/shops/${ag.id}/demo-month`);
  console.log('stationery', r1, '\nagent', r2);
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const mk = async (w, h, label, shopId, zoom) => {
    const z = zoom || 1;
    const c = await b.newContext({ viewport: { width: Math.round(w * z), height: Math.round(h * z) }, locale: 'en-US', timezoneId: 'Africa/Dar_es_Salaam', recordVideo: { dir: path.join(OUT, label), size: { width: Math.round(w * z), height: Math.round(h * z) } } });
    await c.addInitScript(([t, s, zz]) => { try { localStorage.setItem('token', t); localStorage.setItem('shopId', s); localStorage.setItem('lang', 'en'); } catch (e) { } const f = () => { if (zz !== 1 && document.documentElement) document.documentElement.style.zoom = String(zz); }; f(); document.addEventListener('DOMContentLoaded', f); }, [token, shopId, z]);
    const p = await c.newPage(); p.created = Date.now(); return { c, p };
  };
  const D = await mk(1280, 800, 'desktop', st.id), P = await mk(390, 844, 'phone', ag.id, 1.3);
  const t0 = Date.now(); const caps = [];
  const cap = (txt) => caps.push({ at: Date.now() - t0, txt });
  const go = async (pg, hash, ms) => { await pg.goto(BASE + '/#' + hash); await pg.reload(); await sleep(ms); };
  cap('Stationery shop · standard catalogue of 56 items, prefilled'); await go(D.p, '/products', 5000);
  await go(P.p, '/float', 100);
  cap('Dashboard · the whole month, ~1000 customers'); await go(D.p, '/shops', 5500);
  cap('Insights · revenue, tenders, top products, busiest hours'); await go(D.p, '/insights', 3000);
  await D.p.getByText(/month/i).first().click().catch(() => {}); await sleep(5000);
  cap('Agent counter · float balances per network, one month of cash in / out / airtime'); await go(P.p, '/float', 7000);
  cap('Sales history · every receipt with staff and device'); await go(P.p, '/history', 100); await go(D.p, '/history', 6000);
  cap('Team · who is online and what they did last'); await go(D.p, '/team', 5000);
  cap('Ask the assistant, answered from the shop's own data'); await go(D.p, '/assistant', 2500);
  const inp = D.p.locator('#q-ask');
  await inp.pressSequentially('What sold best this week?', { delay: 50 }); await inp.press('Enter'); await sleep(5000);
  cap('Done'); await sleep(1500);
  const total = Date.now() - t0;
  const dv = await D.p.video().path(), pv = await P.p.video().path();
  await D.c.close(); await P.c.close(); await b.close();
  const lead = (t0 - D.p.created) / 1000; const offP = (P.p.created - D.p.created) / 1000, t = (D.p.created - D.p.created);
  const esc = s => s.replace(/[\\:']/g, m => '\\' + m).replace(/,/g, '\\,');
  const dt = ms => { const s = ms / 1000; return `0:${String(Math.floor(s / 60)).padStart(2, '0')}:${(s % 60).toFixed(2).padStart(5, '0')}`; };
  const ass = ['[Script Info]', 'ScriptType: v4.00+', 'PlayResX: 1920', 'PlayResY: 1080', '[V4+ Styles]',
    'Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding',
    'Style: Cap,DejaVu Sans,40,&H00FFFFFF,&H000000FF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,3,10,0,2,40,40,30,1', '[Events]',
    'Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text',
    ...caps.map((c, i) => `Dialogue: 0,${dt(c.at + lead * 1000)},${dt((caps[i + 1] ? caps[i + 1].at : total) + lead * 1000)},Cap,,0,0,0,,${c.txt.replace(/[{}\\]/g, '')}`)].join('\n');
  fs.writeFileSync(path.join(OUT, 'cap.ass'), ass);
  const dur = Math.ceil(total / 1000) + 2;
  const f = [`color=c=0x0d0d10:s=1920x1080:r=25:d=${dur}[bg]`, `[0:v]fps=25,scale=1280:800[d]`, `[1:v]fps=25,scale=420:910[p]`,
    `[bg][d]overlay=40:60:eof_action=pass[o1]`, `[o1][p]overlay=1400:60:eof_action=pass[o2]`, `[o2]ass=${path.join(OUT, 'cap.ass')}:fontsdir=/usr/share/fonts/truetype/dejavu[v]`].join(';');
  execFileSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-i', dv, '-itsoffset', String(Math.max(0, offP)), '-i', pv, '-filter_complex', f, '-map', '[v]', '-t', String(dur), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path.join(OUT, '..', 'month.mp4')], { stdio: 'inherit' });
  console.log('wrote out/month.mp4');
})().catch(e => { console.error(e); process.exit(1); });
