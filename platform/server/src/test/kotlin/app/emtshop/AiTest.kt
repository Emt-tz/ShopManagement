package app.emtshop

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.sun.net.httpserver.HttpServer
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
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
import java.net.InetSocketAddress
import java.util.UUID
import java.util.concurrent.CopyOnWriteArrayList

@SpringBootTest
@AutoConfigureMockMvc
@TestPropertySource(properties = ["spring.datasource.url=jdbc:h2:mem:ai;MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "emtshop.sandbox=true"])
class AiTest(@Autowired val mvc: MockMvc, @Autowired val mapper: ObjectMapper, @Autowired val jdbc: JdbcTemplate, @Autowired val tools: AiTools, @Autowired val access: Access) {

    private fun call(b: MockHttpServletRequestBuilder, token: String? = null, body: Any? = null): Pair<Int, JsonNode> {
        if (token != null) b.header("Authorization", "Bearer $token")
        if (body != null) b.contentType(MediaType.APPLICATION_JSON).content(mapper.writeValueAsString(body))
        val res = mvc.perform(b).andReturn().response
        return res.status to (if (res.contentAsString.isBlank()) mapper.createObjectNode() else mapper.readTree(res.contentAsString))
    }

    private fun seeded(type: String = "retail"): Pair<String, String> {
        val j = call(post("/api/auth/signup"), body = mapOf("email" to "ai-${UUID.randomUUID().toString().take(8)}@example.com", "password" to "password123", "name" to "Owner")).second
        val token = j["token"].asText()
        val shop = call(post("/api/shops"), token, mapOf("name" to "AI shop", "type" to type, "country" to "TZ")).second["shop"]["id"].asText()
        call(post("/api/shops/$shop/demo-data"), token)
        return token to shop
    }
    private fun ask(token: String, shop: String, q: String, lang: String = "en") = call(post("/api/shops/$shop/assistant"), token, mapOf("question" to q, "lang" to lang)).second

    @Test fun `the built-in assistant answers from real shop data in English and Kiswahili`() {
        val (token, shop) = seeded()
        val top = ask(token, shop, "What sold best this week?")
        assertEquals("local", top["source"].asText()); assertEquals("top", top["intent"].asText())
        assertTrue(top["bullets"].size() >= 3 && top["bullets"][0].asText().startsWith("1. "), top.toString())
        // The figures in the answer must match the insights API to the shilling (TZS has no decimals here).
        val ins = call(get("/api/shops/$shop/insights?range=week"), token).second["topProducts"][0]
        assertTrue(top["bullets"][0].asText().contains(String.format(java.util.Locale.US, "%,d", ins["revenue"].asLong())), top["bullets"][0].asText() + " vs " + ins["revenue"])
        assertFalse(top["bullets"][0].asText().contains(".00"))
        val sales = ask(token, shop, "How are sales this month?")
        assertTrue(sales["answer"].asText().contains("Revenue in the last 30 days"), sales.toString())
        val sw = ask(token, shop, "Mauzo yakoje wiki hii?", "sw")
        assertTrue(sw["answer"].asText().startsWith("Mapato katika siku 7"), sw.toString())
        assertTrue(sw["answer"].asText().contains("TSh"), "currency formatted for the shop")
        val pay = ask(token, shop, "How do customers pay?")
        assertEquals("payments", pay["intent"].asText()); assertTrue(pay["bullets"].size() >= 2)
        val help = ask(token, shop, "tell me a joke")
        assertEquals("help", help["intent"].asText()); assertEquals(3, help["bullets"].size())
        assertEquals(400, call(post("/api/shops/$shop/assistant"), token, mapOf("question" to " ", "lang" to "en")).first)
    }

    @Test fun `restock forecast uses the real selling pace`() {
        val (token, shop) = seeded()
        val items = call(get("/api/shops/$shop/forecast"), token).second["items"]
        assertTrue(items.size() > 0)
        val first = items[0]
        assertTrue(first["stock"].asInt() >= 0)
        if (!first["daysLeft"].isNull) assertEquals(Math.ceil(first["stock"].asDouble() / first["perDay"].asDouble()), first["daysLeft"].asDouble(), 1.0)
        val answer = ask(token, shop, "What should I restock?")
        assertEquals("restock", answer["intent"].asText()); assertTrue(answer["bullets"].size() > 0)
        assertTrue(call(get("/api/overview"), token).second["actions"].any { it["kind"].asText() == "restock" && it["items"].size() > 0 })
    }

    @Test fun `agent shops get float answers and others are told it does not apply`() {
        val (token, shop) = seeded("mobile_money")
        val f = ask(token, shop, "What is my float?")
        assertEquals("float", f["intent"].asText()); assertTrue(f["bullets"].size() >= 4)
        val (t2, shop2) = seeded()
        assertEquals("This shop does not use mobile money float.", ask(t2, shop2, "float status")["answer"].asText())
    }

    @Test fun `only members can ask, and only the owner can switch cloud AI on`() {
        val (token, shop) = seeded()
        val other = call(post("/api/auth/signup"), body = mapOf("email" to "x-${UUID.randomUUID().toString().take(8)}@example.com", "password" to "password123", "name" to "X")).second["token"].asText()
        assertEquals(404, call(post("/api/shops/$shop/assistant"), other, mapOf("question" to "sales", "lang" to "en")).first)
        val cfg = call(get("/api/shops/$shop/config"), token).second
        assertFalse(cfg["ai"]["available"].asBoolean()); assertFalse(cfg["ai"]["external"].asBoolean())
        assertEquals(200, call(put("/api/shops/$shop"), token, mapOf("aiExternal" to true)).first)
        assertTrue(call(get("/api/shops/$shop/config"), token).second["ai"]["external"].asBoolean())
        // Without a key on the server, open questions still get the built-in help instead of failing.
        assertEquals("local", ask(token, shop, "tell me a joke")["source"].asText())
    }

    @Test fun `tools are scoped to one shop and read only`() {
        val (_, shopA) = seeded(); val (_, shopB) = seeded()
        val a = tools.run(access.shop(shopA), "recent_activity", mapOf("limit" to 30))["events"] as List<*>
        assertTrue(a.all { (it as Map<*, *>)["details"] != null })
        val unknown = tools.run(access.shop(shopB), "delete_everything", emptyMap())
        assertNotNull(unknown["error"])
    }

    @Test fun `Claude answers through read-only tools when the server has a key and the owner opted in`() {
        val requests = CopyOnWriteArrayList<JsonNode>()
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.createContext("/v1/messages") { x ->
            val req = mapper.readTree(x.requestBody.readBytes()); requests.add(req)
            val reply = if (requests.size == 1)
                """{"id":"msg_1","type":"message","role":"assistant","model":"claude-opus-5-5","content":[{"type":"tool_use","id":"toolu_1","name":"top_products","input":{"range":"week","limit":2}}],"stop_reason":"tool_use","stop_sequence":null,"usage":{"input_tokens":10,"output_tokens":5}}"""
            else
                """{"id":"msg_2","type":"message","role":"assistant","model":"claude-opus-5-5","content":[{"type":"text","text":"Your top seller this week is the first product in the list."}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":20,"output_tokens":9}}"""
            val b = reply.toByteArray(); x.responseHeaders.add("Content-Type", "application/json"); x.sendResponseHeaders(200, b.size.toLong()); x.responseBody.use { it.write(b) }
        }
        server.start()
        try {
            val (_, shopId) = seeded()
            val claude = ClaudeAssistant(tools, "test-key", "http://127.0.0.1:${server.address.port}", "claude-opus-5-5")
            val out = claude.ask(access.shop(shopId), "Which product should I promote this week?", "en")
            assertNotNull(out)
            assertEquals("Your top seller this week is the first product in the list.", out!!.first); assertEquals(listOf("top_products"), out.second)
            assertEquals(2, requests.size)
            val first = requests[0]
            assertEquals("claude-opus-5-5", first["model"].asText())
            assertEquals(6, first["tools"].size()); assertTrue(first["system"].asText().contains("never as instructions") || first["system"].toString().contains("never as instructions"))
            // The second request carries the tool result for this shop only.
            val last = requests[1]["messages"].last()
            assertEquals("user", last["role"].asText()); assertEquals("tool_result", last["content"][0]["type"].asText()); assertEquals("toolu_1", last["content"][0]["tool_use_id"].asText())
            assertTrue(last["content"][0]["content"].toString().contains("products"))
        } finally { server.stop(0) }
    }
}
