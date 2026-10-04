# Emt Shop platform

One JVM backend and one Apple-style client that runs as a phone app, a desktop app and a web app.

```
platform/
  server/   Kotlin + Spring Boot 3 on Java 21 (virtual threads). REST, WebSocket, Caffeine cache, JDBC.
    src/main/resources/static/   the web client (no build step): phone layout < 900 px, desktop layout >= 900 px
    src/main/resources/i18n/     server-driven string catalogs (en, sw)
  e2e/      Playwright end-to-end suite and the demo recorder
```

## Run

```bash
cd platform/server
./gradlew bootRun            # http://localhost:8080  (embedded H2 file database in ./data)
EMTSHOP_SANDBOX=true ./gradlew bootRun   # also enables the simulated mobile money network and /api/dev helpers
```

Production: set `SPRING_DATASOURCE_URL=jdbc:postgresql://host/emtshop` (plus user and password) and leave `EMTSHOP_SANDBOX` unset.

## Test

```bash
cd platform/server && ./gradlew test                  # 28 API tests
cd platform/e2e
node check-i18n.js                                     # every string key used by the client exists in English and Kiswahili
# start the server with EMTSHOP_SANDBOX=true, then:
BASE=http://localhost:8080 node e2e.js                 # 38 browser steps across 3 browsers (needs a running server)
DEMO=1 node e2e.js && node compose.js                  # records out/demo.mp4
```

## Free for 90 days, payment later

Every new account gets the **whole platform for 90 days** (the Multi-shop feature set), with no plan screen and no payment screen.
Plans and payment appear only in the **last 14 days**: the dashboard shows a reminder, the plans page opens, and billing for the
chosen plan starts when the free period ends, never earlier. After that there is a 7-day grace period before selling is blocked.
Staff accounts never see billing; they use the owner's plan.

| Where | What |
|---|---|
| `Billing.kt` | `TRIAL_DAYS`, `PLANS_OPEN_DAYS`, `GRACE_DAYS`, entitlement rules |
| `Dev.kt` | sandbox-only clock shift so tests can reach day 80 without waiting |

## Mobile money: real payments, matched to sales

The cashier asks for the money on the customer's phone; the sale is only recorded when the network confirms it.

1. `POST /shops/{id}/payments` prices the cart on the server, stores a **payment intent** and sends the push to the customer's phone.
2. The network calls our **webhook** (`/api/payments/callback/{provider}/{token}`). A background sweep also **asks the network**
   about any request that has no answer after 15 s, so a lost webhook does not lose a payment.
3. A confirmed payment becomes a **sale** exactly once. If the cashier's phone died, the server creates the sale itself after 20 s.
4. `GET /shops/{id}/reconciliation` shows, per day, what the networks confirmed, what became sales, and everything that needs a person.

Safeguards, all covered by tests (`PaymentsTest`): a sale paid by mobile money without a confirmed payment is refused;
one payment can become one sale; a wrong amount is held, not accepted; duplicate or conflicting callbacks are ignored and logged;
money that arrives after the request expired is still honoured; unknown callbacks are stored, not dropped; every provider message
is kept (`payment_events`); voiding a paid sale raises a refund task.

### Going live

| Network | Status |
|---|---|
| M-Pesa Kenya (Safaricom Daraja, STK push) | Implemented in `DarajaProvider` and checked against a local stand-in that follows Safaricom's documented request and callback shapes. **Not yet run against Safaricom.** Needs your merchant credentials. |
| M-Pesa Tanzania (Vodacom), Mixx by Yas, Airtel Money, HaloPesa | **Not implemented.** Each needs merchant onboarding and its own adapter, or a single aggregator that covers them. Until then these networks run in manual-confirm mode (the cashier confirms by hand) and are marked as not live in the shop config. |

To go live with Daraja, set these on the server, and make `EMTSHOP_PUBLIC_URL` a public HTTPS address that Safaricom can reach:

```
DARAJA_CONSUMER_KEY  DARAJA_CONSUMER_SECRET  DARAJA_SHORTCODE  DARAJA_PASSKEY
DARAJA_BASE_URL=https://api.safaricom.co.ke   DARAJA_TILL_TYPE=paybill|till
EMTSHOP_PUBLIC_URL=https://your-domain
```

Test with Safaricom's sandbox first (`https://sandbox.safaricom.co.ke`, the default). To add a network, implement
`MobileMoneyProvider` (`request`, `query`, `parseCallback`) and route it in `PaymentRouter`.

What this does and does not guarantee: it removes the common ways money gets lost inside the app (unrecorded payments, double
counting, lost webhooks, crashes between payment and sale). It cannot guarantee that the networks settle correctly, and refunds to
customers still have to be sent from the merchant account; the app only raises the task.

## AI

* **Built-in assistant** (always on, no data leaves the server): answers questions about sales, best sellers, what to restock,
  payment mix, float and team activity, in English or Kiswahili, from the shop's own numbers. `LocalAssistant`.
* **Restock forecast**: days of stock left at the real selling pace, with a suggested order. Feeds the dashboard and the assistant.
* **Typical-day insight**: today compared with the same weekday and time over the previous four weeks.
* **Claude for open questions** (optional): set `ANTHROPIC_API_KEY` (and optionally `EMTSHOP_AI_MODEL`, default `claude-opus-5-5`;
  `claude-sonnet-5-5` or `claude-haiku-4-5` cost less) **and** the owner switches it on in Account. Claude only calls six
  read-only tools scoped to that one shop, cannot change anything, and its answers are marked as coming from Claude.
  Questions and the figures the tools return are sent to Anthropic, which is why it is opt-in per shop. A 40-question hourly
  limit per user bounds cost.

## What is built

| Area | Where |
|---|---|
| Accounts, sessions | `Core.kt` |
| Free period, plans, limits, cancel keeps access | `Billing.kt` |
| Region config (currency, VAT, tenders, networks, time zone) | `Config.kt` |
| Shops of different types per owner, roles, staff | `Shops.kt` |
| Products, per-shop availability, audit | `Products.kt` |
| Sales: idempotent, VAT, stock, receipts, void | `Sales.kt` |
| Mobile money providers, intents, reconciliation | `Payments.kt` |
| Insights and recommended actions | `Insights.kt` |
| Assistant, forecast, Claude tools | `Ai.kt` |
| Mobile money float and commission | `Float.kt` |
| Live activity over WebSocket | `Realtime.kt` |
| Offline sales queue, service worker | `static/core.js`, `static/sw.js` |

## Not built yet

Native iOS (SwiftUI), Android (Compose) and a Compose desktop app. They need Xcode and the Android SDK, which are not in this
environment. They would call the same REST and WebSocket API; the web client is the reference for behaviour and layout.

Also not built: Stripe, StoreKit and Play receipt verification for the subscription itself (a plan is recorded with its channel
but nothing is charged), mobile money for Tanzanian networks (above), card payments, and multi-node realtime fan-out
(use Redis pub/sub or Kafka to run more than one instance).

## Month-in-the-life showcase

`POST /api/shops/{id}/demo-month` (owner only) replaces a shop's data with 30 days of trading: a retail shop gets a 56-item standard
stationery catalogue and about 1000 customers (term-start and month-end surges, quieter Sundays, cash / Lipa Namba / card mix, 3 staff
on different devices, restocks, a few voids); a mobile money shop gets about 1000 cash in / cash out / airtime transactions with daily float
top-ups. Seed sales are written directly, not through live payments, so no provider is contacted.
`node e2e/month.js` (server with `EMTSHOP_SANDBOX=true`) seeds both shops and records `e2e/out/month.mp4`.
