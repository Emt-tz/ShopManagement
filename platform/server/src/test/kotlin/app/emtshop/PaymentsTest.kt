package app.emtshop

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
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
import java.util.UUID

@SpringBootTest
@AutoConfigureMockMvc
@TestPropertySource(properties = ["spring.datasource.url=jdbc:h2:mem:pay;MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "emtshop.sandbox=true"])
class PaymentsTest(@Autowired val mvc: MockMvc, @Autowired val mapper: ObjectMapper, @Autowired val jdbc: JdbcTemplate, @Autowired val payments: PaymentService) {

    private fun call(b: MockHttpServletRequestBuilder, token: String? = null, body: Any? = null): Pair<Int, JsonNode> {
        if (token != null) b.header("Authorization", "Bearer $token")
        if (body != null) b.contentType(MediaType.APPLICATION_JSON).content(if (body is String) body else mapper.writeValueAsString(body))
        val res = mvc.perform(b).andReturn().response
        return res.status to (if (res.contentAsString.isBlank()) mapper.createObjectNode() else mapper.readTree(res.contentAsString))
    }

    private class Ctx(val token: String, val shopId: String, val rice: String, val oil: String)

    private fun setup(stock: Int = 10): Ctx {
        val (s, j) = call(post("/api/auth/signup"), body = mapOf("email" to "p-${UUID.randomUUID().toString().take(8)}@example.com", "password" to "password123", "name" to "Owner"))
        assertEquals(201, s)
        val token = j["token"].asText()
        val shop = call(post("/api/shops"), token, mapOf("name" to "Pay shop", "type" to "retail", "country" to "TZ", "till" to "5123 4567")).second["shop"]["id"].asText()
        val rice = call(post("/api/shops/$shop/products"), token, mapOf("name" to "Rice", "price" to 18000, "stock" to stock)).second["product"]["id"].asText()
        val oil = call(post("/api/shops/$shop/products"), token, mapOf("name" to "Oil", "price" to 7500, "stock" to stock)).second["product"]["id"].asText()
        return Ctx(token, shop, rice, oil)
    }

    private fun cart(c: Ctx, riceQty: Int = 2, oilQty: Int = 1) = listOf(mapOf("productId" to c.rice, "qty" to riceQty), mapOf("productId" to c.oil, "qty" to oilQty))
    private fun request(c: Ctx, lines: List<Map<String, Any>> = cart(c)): JsonNode {
        val (s, j) = call(post("/api/shops/${c.shopId}/payments"), c.token, mapOf("lines" to lines, "network" to "mpesa", "phone" to "0712 345 678"))
        assertEquals(201, s, j.toString())
        return j["payment"]
    }
    private fun approve(c: Ctx, id: String, amount: Long? = null) = call(post("/api/dev/payments/$id/approve"), c.token, if (amount != null) mapOf("amount" to amount) else mapOf<String, Any>()).second["payment"]
    private fun sale(c: Ctx, paymentId: String?, key: String = UUID.randomUUID().toString(), lines: List<Map<String, Any>> = cart(c)) =
        call(post("/api/shops/${c.shopId}/sales"), c.token, mapOf("lines" to lines, "tender" to "lipa_namba", "tenderRef" to "mpesa", "idempotencyKey" to key, "paymentId" to paymentId))
    private fun stock(c: Ctx, id: String) = call(get("/api/shops/${c.shopId}/products"), c.token).second["products"].first { it["id"].asText() == id }["stock"].asInt()

    @Test fun `a paid request becomes exactly one sale and the amounts agree`() {
        val c = setup()
        val p = request(c)
        assertEquals("pending", p["status"].asText()); assertEquals(43500, p["amount"].asLong()); assertTrue(p["phone"].asText().endsWith("678") && !p["phone"].asText().contains("0712"))
        val ok = approve(c, p["id"].asText())
        assertEquals("succeeded", ok["status"].asText()); assertTrue(ok["receipt"].asText().startsWith("SIM"))
        val (s1, s) = sale(c, p["id"].asText())
        assertEquals(201, s1, s.toString()); assertEquals(43500, s["sale"]["total"].asLong())
        assertEquals(8, stock(c, c.rice))
        // The same payment can never become a second sale, whatever idempotency key the client uses.
        val (_, again) = sale(c, p["id"].asText())
        assertTrue(again["sale"]["duplicate"].asBoolean()); assertEquals(s["sale"]["id"].asText(), again["sale"]["id"].asText())
        assertEquals(8, stock(c, c.rice))
        val day = call(get("/api/shops/${c.shopId}/reconciliation"), c.token).second
        val today = day["days"][0]
        assertEquals(43500, today["confirmed"].asLong()); assertEquals(43500, today["matched"].asLong()); assertEquals(0, today["unmatched"].asLong()); assertEquals(0, day["needsAttention"].size())
    }

    @Test fun `mobile money sales cannot be recorded without a confirmed payment`() {
        val c = setup()
        val (s, e) = sale(c, null)
        assertEquals(400, s); assertEquals("PAYMENT_REQUIRED", e["error"]["code"].asText())
        val p = request(c)
        val (s2, e2) = sale(c, p["id"].asText())                                    // still pending
        assertEquals(409, s2); assertEquals("NOT_PAID", e2["error"]["code"].asText())
        val declined = call(post("/api/dev/payments/${p["id"].asText()}/decline"), c.token).second["payment"]
        assertEquals("failed", declined["status"].asText())
        assertEquals(409, sale(c, p["id"].asText()).first)
        assertEquals(10, stock(c, c.rice))
        // A different cart than the one that was paid for is refused.
        val q = request(c); approve(c, q["id"].asText())
        val (s3, e3) = sale(c, q["id"].asText(), lines = cart(c, riceQty = 3))
        assertEquals(409, s3); assertEquals("AMOUNT_MISMATCH", e3["error"]["code"].asText())
    }

    @Test fun `repeated and conflicting callbacks never double count`() {
        val c = setup()
        val p = request(c); val id = p["id"].asText()
        val first = approve(c, id); val second = approve(c, id)
        assertEquals(first["receipt"].asText(), second["receipt"].asText())
        assertEquals(1, jdbc.queryForObject("select count(*) from payment_intents where id=? and status='succeeded'", Long::class.java, id)!!.toInt())
        val token = jdbc.queryForObject("select callback_token from payment_intents where id=?", String::class.java, id)!!
        val ref = jdbc.queryForObject("select provider_ref from payment_intents where id=?", String::class.java, id)!!
        call(post("/api/payments/callback/simulator/$token"), body = """{"providerRef":"$ref","state":"succeeded","receipt":"OTHER999","amount":43500}""")
        assertEquals(first["receipt"].asText(), call(get("/api/payments/$id"), c.token).second["payment"]["receipt"].asText())
        assertTrue(jdbc.queryForObject("select count(*) from payment_events where intent_id=? and kind='conflict'", Long::class.java, id)!! >= 1)
    }

    @Test fun `a wrong amount is held for a person, not accepted`() {
        val c = setup()
        val p = request(c); val id = p["id"].asText()
        assertEquals("mismatch", approve(c, id, amount = 40000)["status"].asText())
        assertEquals(409, sale(c, id).first)
        val rec = call(get("/api/shops/${c.shopId}/reconciliation"), c.token).second
        assertEquals("mismatch", rec["needsAttention"][0]["issue"].asText())
        assertTrue(call(get("/api/overview"), c.token).second["actions"].any { it["kind"].asText() == "payments" })
        call(post("/api/payments/$id/resolve"), c.token, mapOf("action" to "acknowledge"))
        assertEquals(0, call(get("/api/shops/${c.shopId}/reconciliation"), c.token).second["needsAttention"].size())
    }

    @Test fun `money that arrives after the request expired is still honoured`() {
        val c = setup()
        val id = request(c)["id"].asText()
        jdbc.update("update payment_intents set status='expired' where id=?", id)
        val late = approve(c, id)
        assertEquals("succeeded", late["status"].asText()); assertTrue(late["late"].asBoolean())
    }

    @Test fun `the server finishes the sale when the cashier's phone never does, even if stock ran out`() {
        val c = setup(stock = 5)
        val id = request(c, cart(c, riceQty = 3, oilQty = 1))["id"].asText()
        approve(c, id)
        jdbc.update("update products set stock=0 where id=?", c.rice)             // someone else sold the last bags meanwhile
        jdbc.update("update payment_intents set updated_at=updated_at-60000 where id=?", id)
        payments.sweep()
        val pay = call(get("/api/payments/$id"), c.token).second["payment"]
        assertNotNull(pay["saleId"]); assertFalse(pay["saleId"].isNull)
        assertEquals(0, stock(c, c.rice)); assertEquals(4, stock(c, c.oil))
        val sales = call(get("/api/shops/${c.shopId}/sales"), c.token).second["sales"]
        assertEquals(1, sales.size()); assertEquals(3 * 18000 + 7500L, sales[0]["total"].asLong())
        assertEquals(0, call(get("/api/shops/${c.shopId}/reconciliation"), c.token).second["needsAttention"].size())
    }

    @Test fun `unknown callbacks are stored, voiding a paid sale raises a refund task, outsiders cannot see payments`() {
        val c = setup()
        val (st, body) = call(post("/api/payments/callback/simulator/not-a-real-token"), body = """{"providerRef":"x","state":"succeeded","receipt":"Z1","amount":100}""")
        assertEquals(200, st); assertEquals(0, body["ResultCode"].asInt())
        assertEquals(1, call(get("/api/shops/${c.shopId}/reconciliation"), c.token).second["unmatchedMessages"].asInt())
        val id = request(c)["id"].asText(); approve(c, id)
        val saleId = sale(c, id).second["sale"]["id"].asText()
        assertEquals(200, call(post("/api/sales/$saleId/void"), c.token).first)
        val issue = call(get("/api/shops/${c.shopId}/reconciliation"), c.token).second["needsAttention"][0]
        assertEquals("refund_due", issue["issue"].asText())
        val (_, o) = call(post("/api/auth/signup"), body = mapOf("email" to "o-${UUID.randomUUID().toString().take(8)}@example.com", "password" to "password123", "name" to "Other"))
        assertEquals(404, call(get("/api/payments/$id"), o["token"].asText()).first)
    }

    @Test fun `live networks are advertised in the shop config and phones are normalised`() {
        val c = setup()
        val cfg = call(get("/api/shops/${c.shopId}/config"), c.token).second
        assertTrue(cfg["tenders"].first { it["id"].asText() == "lipa_namba" }["networks"].all { it["live"].asBoolean() })
        assertEquals("255712345678", payments.normalizePhone("TZ", "0712 345 678"))
        assertEquals("254712345678", payments.normalizePhone("KE", "+254 712 345 678"))
        assertEquals(400, call(post("/api/shops/${c.shopId}/payments"), c.token, mapOf("lines" to cart(c), "network" to "mpesa", "phone" to "12")).first)
    }
}
