/* Fails if the client uses a string key the server catalogs do not define, or if Kiswahili misses a key English has. */
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..', 'server', 'src', 'main', 'resources');
const en = JSON.parse(fs.readFileSync(path.join(root, 'i18n', 'en.json'), 'utf8'));
const sw = JSON.parse(fs.readFileSync(path.join(root, 'i18n', 'sw.json'), 'utf8'));
const src = fs.readdirSync(path.join(root, 'static')).filter(f => f.endsWith('.js') && f !== 'sw.js').map(f => fs.readFileSync(path.join(root, 'static', f), 'utf8')).join('\n');
const missing = new Set();
for (const m of src.matchAll(/\bt\('([^']+)'\s*[,)]/g)) if (!(m[1] in en)) missing.add(m[1]);
for (const m of src.matchAll(/\btn\('([^']+)'/g)) if (!((m[1] + '.other') in en)) missing.add(m[1] + '.other');
const dyn = { 'tender.': ['cash', 'lipa_namba', 'mpesa_till', 'card', 'credit', 'upi', 'pix'], 'type.': ['retail', 'grocery', 'mobile_money', 'phones', 'restaurant'], 'plan.': ['starter', 'business', 'multi'], 'role.': ['owner', 'cashier', 'manager'], 'sub.': ['trialing', 'active', 'canceled'], 'channel.': ['web', 'appstore', 'play'], 'float.kind.': ['cash_in', 'cash_out', 'airtime'], 'kind.': ['sale', 'void', 'price_change', 'stock_adjust', 'product_added', 'product_removed', 'member_added', 'shop_created', 'float_tx', 'float_adjust'] };
for (const [p, ks] of Object.entries(dyn)) for (const k of ks) if (!((p + k) in en)) missing.add(p + k);
const gap = Object.keys(en).filter(k => !(k in sw));
const extra = Object.keys(sw).filter(k => !(k in en));
console.log(`keys: en=${Object.keys(en).length} sw=${Object.keys(sw).length}`);
if (missing.size || gap.length || extra.length) { console.log('missing in en:', [...missing], 'missing in sw:', gap, 'extra in sw:', extra); process.exit(1); }
console.log('i18n OK: every key used by the client exists in English and Kiswahili');
