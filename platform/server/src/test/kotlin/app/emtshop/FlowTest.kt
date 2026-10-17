package app.emtshop

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.http.MediaType
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.test.context.TestPropertySource
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put
import java.util.UUID

@SpringBootTest
@AutoConfigureMockMvc
@TestPropertySource(properties = ["spring.datasource.url=jdbc:h2:mem:flow;MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "emtshop.sandbox=true"])
class FlowTest(@Autowired val mvc: MockMvc, @Autowired val mapper: ObjectMapper, @Autowired val jdbc: JdbcTemplate) {

    private fun call(b: MockHttpServletRequestBuilder, token: String? = null, body: Any? = null, device: String = "Web"): Pair<Int, JsonNode> {
        b.header("X-Device", device)
        if (token != null) b.header("Authorization", "Bearer $token")
        if (body != null) b.contentType(MediaType.APPLICATION_JSON).content(mapper.writeValueAsString(body))
        val res = mvc.perform(b).andReturn().response
        val text = res.contentAsString
        return res.status to (if (text.isBlank()) mapper.createObjectNode() else mapper.readTree(text))
    }

    private fun signup(prefix: String = "owner"): Pair<String, String> {
        val email = "$prefix-${UUID.randomUUID().toString().take(8)}@example.com"
        val (status, json) = call(post("/api/auth/signup"), body = mapOf("email" to email, "password" to "password123", "name" to prefix.replaceFirstChar { it.uppercase() }))
        assertEquals(201, status)
        return json["token"].asText() to email
    }

    /** Move this account's clock forward by shifting its free period and renewal dates back. */
    private fun fastForward(token: String, days: Long) {
        val id = call(get("/api/me"), token).second["user"]["id"].asText()
        val ms = days * 86_400_000L
        jdbc.update("update subscriptions set trial_ends_at=trial_ends_at-?, renews_at=renews_at-? where user_id=?", ms, ms, id)
    }

    private fun shop(token: String, type: String = "retail", country: String = "TZ"): String {
        val (s, j) = call(post("/api/shops"), token, mapOf("name" to "Test $type", "type" to type, "country" to country, "till" to "5123 4567"))
        assertEquals(201, s, j.toString())
        return j["shop"]["id"].asText()
    }

    @Test fun `auth rejects bad credentials and protects routes`() {
        assertEquals(401, call(get("/api/me")).first)
        val (token, email) = signup()
        assertEquals(200, call(get("/api/me"), token).first)
        assertEquals(401, call(post("/api/auth/login"), body = mapOf("email" to email, "password" to "wrong-password")).first)
        assertEquals(200, call(post("/api/auth/login"), body = mapOf("email" to email, "password" to "password123")).first)
        assertEquals(409, call(post("/api/auth/signup"), body = mapOf("email" to email, "password" to "password123", "name" to "X")).first)
        assertEquals(400, call(post("/api/auth/signup"), body = mapOf("email" to "nope", "password" to "password123", "name" to "X")).first)
    }

    @Test fun `new accounts get the whole platform free for 90 days and plans open late`() {
        val (_, tz) = call(get("/api/billing/plans?country=TZ"))
        assertEquals("TZS", tz["currency"].asText())
        assertEquals(49900, tz["plans"][1]["monthly"].asLong())
        assertEquals(49900L * 12 * 80 / 100, tz["plans"][1]["yearly"].asLong())
        assertEquals(90, tz["trialDays"].asInt())
        val (token, _) = signup()
        val sub = call(get("/api/billing/subscription"), token).second["subscription"]
        assertEquals("trialing", sub["status"].asText()); assertTrue(sub["free"].asBoolean()); assertFalse(sub["plansOpen"].asBoolean())
        assertTrue(sub["freeDaysLeft"].asLong() in 89..90)
        assertEquals(null, sub["limits"]["shops"].let { if (it.isNull) null else it.asInt() }, "free period is unlimited")
        shop(token)                       // no plan needed to start
        val (early, err) = call(post("/api/billing/subscribe"), token, mapOf("plan" to "business"))
        assertEquals(409, early); assertEquals("PLANS_NOT_OPEN", err["error"]["code"].asText())
        fastForward(token, 80)            // last two weeks: payments now show up
        val open = call(post("/api/billing/subscribe"), token, mapOf("plan" to "business", "period" to "monthly", "channel" to "appstore"))
        assertEquals(200, open.first)
        val after = open.second["subscription"]
        assertEquals("business", after["plan"].asText()); assertTrue(after["free"].asBoolean(), "still free until day 90")
        assertTrue(after["renewsAt"].asLong() > after["trialEndsAt"].asLong(), "billing starts after the free period")
    }

    @Test fun `full retail flow sells, decrements stock, computes VAT and reports it`() {
        val (token, _) = signup()
        val shopId = shop(token)
        val cfg = call(get("/api/shops/$shopId/config"), token).second
        assertEquals("sw-TZ", cfg["locale"].asText())
        assertEquals("TZS", cfg["currency"]["code"].asText())
        assertEquals(listOf("cash", "lipa_namba", "card", "credit"), cfg["tenders"].map { it["id"].asText() })
        assertEquals(4, cfg["tenders"][1]["networks"].size())

        val rice = call(post("/api/shops/$shopId/products"), token, mapOf("name" to "Rice 5 kg", "category" to "Food", "price" to 18000, "stock" to 5)).second["product"]["id"].asText()
        val oil = call(post("/api/shops/$shopId/products"), token, mapOf("name" to "Oil", "category" to "Food", "price" to 7500, "stock" to 12)).second["product"]["id"].asText()

        val key = UUID.randomUUID().toString()
        val body = mapOf("lines" to listOf(mapOf("productId" to rice, "qty" to 2), mapOf("productId" to oil, "qty" to 1)), "tender" to "card", "idempotencyKey" to key)
        val (s1, sale) = call(post("/api/shops/$shopId/sales"), token, body)
        assertEquals(201, s1, sale.toString())
        assertEquals(43500, sale["sale"]["total"].asLong())
        assertEquals((43500L * 1800 + 11800 / 2) / 11800, sale["sale"]["vat"].asLong())
        assertEquals(1, sale["sale"]["number"].asInt())
        // Retrying with the same key must not sell twice.
        val (_, again) = call(post("/api/shops/$shopId/sales"), token, body)
        assertTrue(again["sale"]["duplicate"].asBoolean())
        val products = call(get("/api/shops/$shopId/products"), token).second["products"]
        assertEquals(3, products.first { it["id"].asText() == rice }["stock"].asInt())
        // Out of stock is refused and leaves stock unchanged.
        val (s2, err) = call(post("/api/shops/$shopId/sales"), token, mapOf("lines" to listOf(mapOf("productId" to rice, "qty" to 9)), "tender" to "cash", "idempotencyKey" to "k2"))
        assertEquals(409, s2); assertEquals("OUT_OF_STOCK", err["error"]["code"].asText())
        assertEquals(400, call(post("/api/shops/$shopId/sales"), token, mapOf("lines" to listOf(mapOf("productId" to oil, "qty" to 1)), "tender" to "upi", "idempotencyKey" to "k3")).first)
        // Cash change
        val (_, cash) = call(post("/api/shops/$shopId/sales"), token, mapOf("lines" to listOf(mapOf("productId" to oil, "qty" to 1)), "tender" to "cash", "cashReceived" to 10000, "idempotencyKey" to "k4"))
        assertEquals(2500, cash["sale"]["change"].asLong())

        val ins = call(get("/api/shops/$shopId/insights?range=day"), token).second
        assertEquals(51000, ins["revenue"].asLong())
        assertEquals(2, ins["count"].asInt())
        assertEquals("Rice 5 kg", ins["topProducts"][0]["name"].asText())
        assertEquals(24, ins["series"].size())

        // Void restocks and shows in refunds
        val saleId = sale["sale"]["id"].asText()
        assertEquals(200, call(post("/api/sales/$saleId/void"), token).first)
        assertEquals(409, call(post("/api/sales/$saleId/void"), token).first)
        assertEquals(5, call(get("/api/shops/$shopId/products"), token).second["products"].first { it["id"].asText() == rice }["stock"].asInt())
        assertEquals(43500, call(get("/api/shops/$shopId/insights?range=day"), token).second["refunds"].asLong())

        val feed = call(get("/api/activity?shopId=$shopId"), token).second["activity"].map { it["kind"].asText() }
        assertTrue(feed.containsAll(listOf("shop_created", "product_added", "sale", "void")), feed.toString())
    }

    @Test fun `plan limits apply only after the free period`() {
        val (token, _) = signup()
        val shopId = shop(token)
        // Free period: everything is unlocked, including a second shop and staff.
        assertEquals(201, call(post("/api/shops"), token, mapOf("name" to "Second", "type" to "retail", "country" to "TZ")).first)
        fastForward(token, 80)
        call(post("/api/billing/subscribe"), token, mapOf("plan" to "starter"))
        fastForward(token, 12)           // free period is over, starter is now in force
        val (s, e) = call(post("/api/shops"), token, mapOf("name" to "Third", "type" to "retail", "country" to "TZ"))
        assertEquals(402, s); assertEquals("PLAN_LIMIT_SHOPS", e["error"]["code"].asText())
        val (s2, e2) = call(post("/api/shops/$shopId/members"), token, mapOf("name" to "Asha", "email" to "a-${UUID.randomUUID()}@example.com", "password" to "password123", "role" to "cashier"))
        assertEquals(402, s2); assertEquals("PLAN_LIMIT_STAFF", e2["error"]["code"].asText())
        call(post("/api/billing/subscribe"), token, mapOf("plan" to "multi"))
        assertEquals(201, call(post("/api/shops"), token, mapOf("name" to "Third", "type" to "phones", "country" to "KE")).first)
        assertEquals(201, call(post("/api/shops/$shopId/members"), token, mapOf("name" to "Asha", "email" to "b-${UUID.randomUUID()}@example.com", "password" to "password123", "role" to "manager")).first)
    }

    @Test fun `expired subscriptions block selling and cancel keeps access until the period ends`() {
        val (token, _) = signup()
        val me = call(get("/api/me"), token).second["user"]["id"].asText()
        val shopId = shop(token)
        val p = call(post("/api/shops/$shopId/products"), token, mapOf("name" to "Pen", "price" to 500, "stock" to 10)).second["product"]["id"].asText()
        fastForward(token, 80)
        call(post("/api/billing/subscribe"), token, mapOf("plan" to "business"))
        val canceled = call(post("/api/billing/cancel"), token).second["subscription"]
        assertEquals("canceled", canceled["status"].asText()); assertTrue(canceled["active"].asBoolean())
        jdbc.update("update subscriptions set renews_at=? where user_id=?", now() - 8 * 86_400_000L, me)   // past the 7-day grace
        val (s, e) = call(post("/api/shops/$shopId/sales"), token, mapOf("lines" to listOf(mapOf("productId" to p, "qty" to 1)), "tender" to "cash", "idempotencyKey" to "x"))
        assertEquals(402, s); assertEquals("SUBSCRIPTION_EXPIRED", e["error"]["code"].asText())
    }

    @Test fun `roles and tenancy are enforced`() {
        val (owner, _) = signup("owner")
        val shopId = shop(owner)
        val staffEmail = "staff-${UUID.randomUUID().toString().take(8)}@example.com"
        assertEquals(201, call(post("/api/shops/$shopId/members"), owner, mapOf("name" to "Asha", "email" to staffEmail, "password" to "password123", "role" to "cashier")).first)
        val cashier = call(post("/api/auth/login"), body = mapOf("email" to staffEmail, "password" to "password123")).second["token"].asText()
        val p = call(post("/api/shops/$shopId/products"), owner, mapOf("name" to "Pen", "price" to 500, "stock" to 10)).second["product"]["id"].asText()
        // Cashier can sell (the owner's plan applies) but cannot edit prices or products.
        assertEquals(201, call(post("/api/shops/$shopId/sales"), cashier, mapOf("lines" to listOf(mapOf("productId" to p, "qty" to 1)), "tender" to "cash", "idempotencyKey" to "c1"), "iPhone 14").first)
        assertEquals(403, call(put("/api/products/$p"), cashier, mapOf("name" to "Pen", "price" to 100, "stock" to 10)).first)
        assertEquals(403, call(post("/api/shops/$shopId/members"), cashier, mapOf("name" to "X", "email" to "x@example.com", "password" to "password123")).first)
        // A stranger cannot see the shop at all.
        val (stranger, _) = signup("stranger")
        assertEquals(404, call(get("/api/shops/$shopId/products"), stranger).first)
        // Team list shows who did what, on which device.
        val team = call(get("/api/shops/$shopId/members"), owner).second["members"]
        val asha = team.first { it["name"].asText() == "Asha" }
        assertEquals("sale", asha["last"]["kind"].asText())
        assertEquals("iPhone 14", asha["last"]["device"].asText())
        // Price change is audited.
        assertEquals(200, call(put("/api/products/$p"), owner, mapOf("name" to "Pen", "price" to 600, "stock" to 9), "Mac app").first)
        val audit = call(get("/api/activity?shopId=$shopId&kinds=price_change"), owner).second["activity"]
        assertEquals(1, audit.size()); assertEquals(600, audit[0]["data"]["to"].asLong())
    }

    @Test fun `mobile money agents manage float with commission and low alerts`() {
        val (token, _) = signup()
        val shopId = shop(token, "mobile_money")
        call(post("/api/shops/$shopId/float/adjust"), token, mapOf("network" to "cash", "delta" to 1_000_000))
        call(post("/api/shops/$shopId/float/adjust"), token, mapOf("network" to "mpesa", "delta" to 2_000_000))
        val (s, f) = call(post("/api/shops/$shopId/float/tx"), token, mapOf("network" to "mpesa", "kind" to "cash_out", "amount" to 200_000))
        assertEquals(201, s)
        assertEquals(2_200_000, f["accounts"].first { it["network"].asText() == "mpesa" }["balance"].asLong())
        assertEquals(800_000, f["accounts"].first { it["network"].asText() == "cash" }["balance"].asLong())
        assertEquals(1600, f["todayCommission"].asLong())
        assertEquals(409, call(post("/api/shops/$shopId/float/tx"), token, mapOf("network" to "mpesa", "kind" to "cash_out", "amount" to 5_000_000)).first)
        val after = call(post("/api/shops/$shopId/float/tx"), token, mapOf("network" to "airtel", "kind" to "cash_in", "amount" to 1000))
        assertEquals(409, after.first)
        val ov = call(get("/api/overview"), token).second["shops"].first { it["id"].asText() == shopId }
        assertTrue(ov["lowFloat"].size() >= 1)
        assertEquals(3_000_000L, ov["floatTotal"].asLong())
    }

    @Test fun `demo data, overview and multi-currency totals`() {
        val (token, _) = signup()
        val a = shop(token, "retail", "TZ"); val b = shop(token, "retail", "KE")
        call(post("/api/shops/$a/demo-data"), token); call(post("/api/shops/$b/demo-data"), token)
        val week = call(get("/api/shops/$a/insights?range=week"), token).second
        assertTrue(week["revenue"].asLong() > 0); assertEquals(7, week["series"].size()); assertTrue(week["paymentMix"].size() >= 2)
        assertTrue(week["busiestHour"].asInt() in 0..23)
        val ov = call(get("/api/overview"), token).second
        assertEquals(2, ov["shops"].size()); assertEquals(setOf("TZS", "KES"), ov["totals"].map { it["currency"].asText() }.toSet())
        // Recommended actions: the demo catalogue has low-stock items, and a new plan is still on trial.
        val kinds = call(get("/api/overview"), token).second["actions"].map { it["kind"].asText() }
        assertTrue("restock" in kinds && "trial" !in kinds, kinds.toString())   // payments are not mentioned in the first 76 days
        fastForward(token, 80)
        assertTrue("trial" in call(get("/api/overview"), token).second["actions"].map { it["kind"].asText() })
        assertEquals(2, call(get("/api/me"), token).second["shops"][0]["members"].asInt() + 1)
        // Product availability across shops with the same currency is rejected; other currency copies are not allowed.
        val rice = call(get("/api/shops/$a/products"), token).second["products"][0]["id"].asText()
        assertEquals(400, call(put("/api/products/$rice/availability"), token, mapOf("shopId" to b, "available" to true)).first)
        val c = shop(token, "retail", "TZ")
        val av = call(put("/api/products/$rice/availability"), token, mapOf("shopId" to c, "available" to true)).second
        assertTrue(av["shops"].first { it["shopId"].asText() == c }["available"].asBoolean())
        val off = call(put("/api/products/$rice/availability"), token, mapOf("shopId" to c, "available" to false)).second
        assertFalse(off["shops"].first { it["shopId"].asText() == c }["available"].asBoolean())
    }

    @Test fun `i18n catalogs fall back to english and regions are listed`() {
        val sw = call(get("/api/i18n/sw-TZ")).second["strings"]
        val en = call(get("/api/i18n/en")).second["strings"]
        assertEquals("Taslimu", sw["tender.cash"].asText())
        assertEquals("Cash", en["tender.cash"].asText())
        assertEquals("Cash", call(get("/api/i18n/fr-FR")).second["strings"]["tender.cash"].asText())
        en.fieldNames().forEach { assertTrue(sw.has(it), "missing Swahili key $it") }
        assertEquals(5, call(get("/api/regions")).second["regions"].size())
    }
}
