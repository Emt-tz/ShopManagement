package app.emtshop

import com.fasterxml.jackson.databind.ObjectMapper
import com.sun.net.httpserver.HttpExchange
import com.sun.net.httpserver.HttpServer
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import java.net.InetSocketAddress
import java.util.Base64

/** Checks our Daraja adapter against a local stand-in that follows Safaricom's documented request and response shapes. */
class DarajaTest {
    private val mapper = ObjectMapper()
    private lateinit var server: HttpServer
    private var tokenCalls = 0
    private var lastAuth: String? = null
    private var lastPush: String? = null
    private var lastPushAuth: String? = null
    private var queryResponse: Pair<Int, String> = 200 to "{}"

    private fun reply(x: HttpExchange, code: Int, body: String) {
        val b = body.toByteArray(); x.responseHeaders.add("Content-Type", "application/json"); x.sendResponseHeaders(code, b.size.toLong()); x.responseBody.use { it.write(b) }
    }

    @BeforeEach fun start() {
        server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.createContext("/oauth/v1/generate") { x -> tokenCalls++; lastAuth = x.requestHeaders.getFirst("Authorization"); reply(x, 200, """{"access_token":"tok123","expires_in":"3599"}""") }
        server.createContext("/mpesa/stkpush/v1/processrequest") { x ->
            lastPushAuth = x.requestHeaders.getFirst("Authorization"); lastPush = x.requestBody.readBytes().decodeToString()
            reply(x, 200, """{"MerchantRequestID":"29115-34620561-1","CheckoutRequestID":"ws_CO_191220191020363925","ResponseCode":"0","ResponseDescription":"Success. Request accepted for processing","CustomerMessage":"Success. Request accepted for processing"}""")
        }
        server.createContext("/mpesa/stkpushquery/v1/query") { x -> reply(x, queryResponse.first, queryResponse.second) }
        server.start()
    }
    @AfterEach fun stop() { server.stop(0) }

    private fun provider() = DarajaProvider(mapper, "key", "secret", "174379", "PASSKEY", "http://127.0.0.1:${server.address.port}", "paybill")
    private fun push(p: DarajaProvider, amount: Long = 15000) =
        p.request(PushRequest("i1", amount, "KES", "254712345678", "mpesa", "EMT12345678901234", "Emt Shop purchase", "https://example.com/cb/xyz", null))

    @Test fun `push request follows the documented Daraja contract`() {
        val p = provider()
        assertTrue(p.configured)
        val res = push(p)
        assertEquals("ws_CO_191220191020363925", res.providerRef)
        assertEquals("Basic " + Base64.getEncoder().encodeToString("key:secret".toByteArray()), lastAuth)
        assertEquals("Bearer tok123", lastPushAuth)
        val j = mapper.readTree(lastPush)
        assertEquals("174379", j["BusinessShortCode"].asText())
        assertEquals(Base64.getEncoder().encodeToString(("174379" + "PASSKEY" + j["Timestamp"].asText()).toByteArray()), j["Password"].asText())
        assertEquals(14, j["Timestamp"].asText().length)
        assertEquals("CustomerPayBillOnline", j["TransactionType"].asText())
        assertEquals(150, j["Amount"].asInt())                         // minor units 15000 = KSh 150
        assertEquals("254712345678", j["PartyA"].asText()); assertEquals("254712345678", j["PhoneNumber"].asText()); assertEquals("174379", j["PartyB"].asText())
        assertEquals("https://example.com/cb/xyz", j["CallBackURL"].asText())
        assertTrue(j["AccountReference"].asText().length <= 12 && j["TransactionDesc"].asText().length <= 13)
        push(p); assertEquals(1, tokenCalls, "the access token is cached")
    }

    @Test fun `till shops use buy goods and cents are refused`() {
        val p = DarajaProvider(mapper, "key", "secret", "600000", "PASSKEY", "http://127.0.0.1:${server.address.port}", "till")
        p.request(PushRequest("i2", 5000, "KES", "254712345678", "mpesa", "ref", "d", "https://example.com/cb", "987654"))
        val j = mapper.readTree(lastPush)
        assertEquals("CustomerBuyGoodsOnline", j["TransactionType"].asText()); assertEquals("987654", j["PartyB"].asText())
        assertThrows(ProviderException::class.java) { push(p, amount = 15050) }
    }

    @Test fun `status query maps results and treats the processing error as pending`() {
        val p = provider()
        queryResponse = 200 to """{"ResponseCode":"0","ResponseDescription":"ok","MerchantRequestID":"m","CheckoutRequestID":"c","ResultCode":"0","ResultDesc":"The service request is processed successfully."}"""
        assertEquals("succeeded", p.query("c").state)
        queryResponse = 200 to """{"ResponseCode":"0","ResultCode":"1032","ResultDesc":"Request cancelled by user"}"""
        assertEquals("failed", p.query("c").state)
        queryResponse = 500 to """{"requestId":"r","errorCode":"500.001.1001","errorMessage":"The transaction is being processed"}"""
        assertEquals("pending", p.query("c").state)
        queryResponse = 500 to """{"errorCode":"500.003.1001","errorMessage":"Internal"}"""
        assertThrows(ProviderException::class.java) { p.query("c") }
    }

    @Test fun `callbacks are parsed into receipt and amount`() {
        val p = provider()
        val ok = p.parseCallback("""{"Body":{"stkCallback":{"MerchantRequestID":"29115-34620561-1","CheckoutRequestID":"ws_CO_191220191020363925","ResultCode":0,"ResultDesc":"The service request is processed successfully.","CallbackMetadata":{"Item":[{"Name":"Amount","Value":1.00},{"Name":"MpesaReceiptNumber","Value":"NLJ7RT61SV"},{"Name":"TransactionDate","Value":20191219102115},{"Name":"PhoneNumber","Value":254708374149}]}}}}""")!!
        assertEquals("succeeded", ok.state); assertEquals("NLJ7RT61SV", ok.receipt); assertEquals(100, ok.amount); assertEquals("ws_CO_191220191020363925", ok.providerRef)
        val cancelled = p.parseCallback("""{"Body":{"stkCallback":{"MerchantRequestID":"m","CheckoutRequestID":"c1","ResultCode":1032,"ResultDesc":"Request cancelled by user"}}}""")!!
        assertEquals("failed", cancelled.state); assertNull(cancelled.receipt)
        assertNull(p.parseCallback("""{"unrelated":true}"""))
        assertNotNull(p.timestamp())
    }

    @Test fun `unconfigured provider reports itself as off`() {
        assertEquals(false, DarajaProvider(mapper, "", "", "", "", "http://x", "paybill").configured)
    }
}
