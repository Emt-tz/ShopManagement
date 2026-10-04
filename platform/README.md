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
```

Production: set `SPRING_DATASOURCE_URL=jdbc:postgresql://host/emtshop` (plus user and password). The schema uses portable SQL.

## Test

```bash
cd platform/server && ./gradlew test                  # 9 API tests: auth, billing limits, sales, VAT, void, float, roles, tenancy, i18n
cd platform/e2e
node check-i18n.js                                     # every string key used by the client exists in English and Kiswahili
BASE=http://localhost:8080 node e2e.js                 # 28 browser steps across 3 browsers (needs a running server)
DEMO=1 node e2e.js && node compose.js                  # records out/demo.mp4
```

## What is built

| Area | Where |
|---|---|
| Accounts, sessions | `Core.kt` |
| Plans, free trial, plan limits, cancel keeps access to period end | `Billing.kt` |
| Region config (currency, VAT, tender types, mobile money networks, time zone) | `Config.kt` |
| Shops of different types per owner, roles, staff accounts | `Shops.kt` |
| Products, per-shop availability, price and stock audit | `Products.kt` |
| Sales: idempotent, VAT, stock checks, receipt numbers, void | `Sales.kt` |
| Insights: revenue, previous period, top products, payment mix, busiest hour | `Insights.kt` |
| Mobile money float, commission, low-float alerts | `Float.kt` |
| Live activity over WebSocket | `Realtime.kt` |
| Offline sales queue, service worker | `static/core.js`, `static/sw.js` |

## Not built yet

Native iOS (SwiftUI), Android (Compose) and a Compose desktop app. They need Xcode and the Android SDK, which are not in this
environment. They would call the same REST and WebSocket API; the web client is the reference for behaviour and layout.

Payment providers are stubs: subscriptions are recorded with a `channel` (web, appstore, play) but no receipt is verified with
Stripe, StoreKit or Play. Mobile money payments (Lipa Namba) are confirmed by the cashier; there is no network callback yet.
Realtime fan-out is single node. Use Redis pub/sub or Kafka to run more than one instance.
