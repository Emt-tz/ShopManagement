package app.emtshop

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import org.springframework.beans.factory.annotation.Value
import org.springframework.dao.DuplicateKeyException
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Component
import org.springframework.stereotype.Service
import org.springframework.transaction.support.TransactionTemplate
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestAttribute
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestHeader
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.ResponseStatus
import org.springframework.web.bind.annotation.RestController
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.security.SecureRandom
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Base64
import java.util.concurrent.ConcurrentHashMap

/* ------------------------------------------------------------------------------------------------
 * Mobile money providers. A provider asks the customer's phone to approve a payment (a "push"),
 * can be asked later what happened to it, and turns its own webhook body into a CallbackResult.
 * Adding a country or network means implementing this interface; nothing else changes.
 * ---------------------------------------------------------------------------------------------- */

data class PushRequest(
    val intentId: String, val amount: Long, val currency: String, val phone: String, val network: String,
    val reference: String, val description: String, val callbackUrl: String, val till: String?
)
data class PushResult(val providerRef: String)
data class ProviderStatus(val state: String, val receipt: String?, val amount: Long?, val code: String?, val desc: String?)
data class CallbackResult(val providerRef: String, val state: String, val receipt: String?, val amount: Long?, val code: String?, val desc: String?)
class ProviderException(message: String) : RuntimeException(message)

interface MobileMoneyProvider {
    val id: String
    fun request(req: PushRequest): PushResult
    fun query(providerRef: String): ProviderStatus
    fun parseCallback(body: String): CallbackResult?
}

/** Safaricom Daraja: M-Pesa Express (STK push) for Kenya. Needs the merchant's own credentials. */
@Component
class DarajaProvider(
    val mapper: ObjectMapper,
    @Value("\${emtshop.payments.daraja.consumer-key:}") val consumerKey: String,
    @Value("\${emtshop.payments.daraja.consumer-secret:}") val consumerSecret: String,
    @Value("\${emtshop.payments.daraja.shortcode:}") val shortcode: String,
    @Value("\${emtshop.payments.daraja.passkey:}") val passkey: String,
    @Value("\${emtshop.payments.daraja.base-url:https://sandbox.safaricom.co.ke}") val baseUrl: String,
    @Value("\${emtshop.payments.daraja.till-type:paybill}") val tillType: String
) : MobileMoneyProvider {
    override val id = "daraja"
    val configured get() = consumerKey.isNotBlank() && consumerSecret.isNotBlank() && shortcode.isNotBlank() && passkey.isNotBlank()
    private val http: HttpClient = HttpClient.newHttpClient()
    @Volatile private var token: String? = null
    @Volatile private var tokenExpiry = 0L

    private fun accessToken(): String {
        val cached = token
        if (cached != null && now() < tokenExpiry - 60_000) return cached
        val basic = Base64.getEncoder().encodeToString("$consumerKey:$consumerSecret".toByteArray())
        val res = send(HttpRequest.newBuilder(URI("$baseUrl/oauth/v1/generate?grant_type=client_credentials")).header("Authorization", "Basic $basic").GET().build())
        val json = mapper.readTree(res)
        val t = json.path("access_token").asText("")
        if (t.isBlank()) throw ProviderException("Daraja did not return an access token")
        token = t; tokenExpiry = now() + json.path("expires_in").asText("3599").toLong() * 1000
        return t
    }

    private fun send(req: HttpRequest): String {
        val res = try { http.send(req, HttpResponse.BodyHandlers.ofString()) } catch (e: Exception) { throw ProviderException("Could not reach M-Pesa: ${e.message}") }
        if (res.statusCode() !in 200..299) throw ProviderException("M-Pesa returned HTTP ${res.statusCode()}: ${res.body().take(300)}")
        return res.body()
    }

    fun timestamp(): String = LocalDateTime.now(ZoneId.of("Africa/Nairobi")).format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"))
    fun password(ts: String): String = Base64.getEncoder().encodeToString((shortcode + passkey + ts).toByteArray())

    private fun post(path: String, body: Map<String, Any?>): String =
        send(HttpRequest.newBuilder(URI(baseUrl + path)).header("Authorization", "Bearer " + accessToken()).header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(mapper.writeValueAsString(body))).build())

    override fun request(req: PushRequest): PushResult {
        if (req.amount % 100 != 0L) throw ProviderException("M-Pesa Kenya accepts whole shillings only")
        val ts = timestamp()
        val raw = post("/mpesa/stkpush/v1/processrequest", mapOf(
            "BusinessShortCode" to shortcode, "Password" to password(ts), "Timestamp" to ts,
            "TransactionType" to if (tillType == "till") "CustomerBuyGoodsOnline" else "CustomerPayBillOnline",
            "Amount" to req.amount / 100, "PartyA" to req.phone, "PartyB" to (req.till?.takeIf { it.isNotBlank() } ?: shortcode),
            "PhoneNumber" to req.phone, "CallBackURL" to req.callbackUrl,
            "AccountReference" to req.reference.take(12), "TransactionDesc" to req.description.take(13)
        ))
        val j = mapper.readTree(raw)
        if (j.path("ResponseCode").asText() != "0") throw ProviderException(j.path("ResponseDescription").asText("M-Pesa rejected the request"))
        return PushResult(j.path("CheckoutRequestID").asText())
    }

    override fun query(providerRef: String): ProviderStatus {
        val ts = timestamp()
        val raw = try {
            post("/mpesa/stkpushquery/v1/query", mapOf("BusinessShortCode" to shortcode, "Password" to password(ts), "Timestamp" to ts, "CheckoutRequestID" to providerRef))
        } catch (e: ProviderException) {
            // While the customer is still deciding, Daraja answers with an error body: that means "pending".
            if (e.message?.contains("500.001.1001") == true) return ProviderStatus("pending", null, null, null, null)
            throw e
        }
        val j = mapper.readTree(raw)
        val code = j.path("ResultCode").asText("")
        return when {
            code == "0" -> ProviderStatus("succeeded", null, null, code, j.path("ResultDesc").asText())
            code.isBlank() -> ProviderStatus("pending", null, null, null, null)
            else -> ProviderStatus("failed", null, null, code, j.path("ResultDesc").asText())
        }
    }

    override fun parseCallback(body: String): CallbackResult? {
        val cb = mapper.readTree(body).path("Body").path("stkCallback")
        if (cb.isMissingNode) return null
        val ref = cb.path("CheckoutRequestID").asText("")
        val code = cb.path("ResultCode").asText("")
        if (ref.isBlank() || code.isBlank()) return null
        if (code != "0") return CallbackResult(ref, "failed", null, null, code, cb.path("ResultDesc").asText())
        var amount: Long? = null
        var receipt: String? = null
        for (item in cb.path("CallbackMetadata").path("Item")) when (item.path("Name").asText()) {
            "Amount" -> amount = java.math.BigDecimal(item.path("Value").asText("0")).multiply(java.math.BigDecimal(100)).toLong()
            "MpesaReceiptNumber" -> receipt = item.path("Value").asText()
        }
        return CallbackResult(ref, "succeeded", receipt, amount, code, cb.path("ResultDesc").asText())
    }
}

/** Stands in for a real network in development and tests. A person plays the customer's phone via the sandbox endpoints. */
@Component
class SimulatedProvider(val mapper: ObjectMapper) : MobileMoneyProvider {
    override val id = "simulator"
    private data class Sim(var state: String, var receipt: String?, var amount: Long, var code: String?, var desc: String?)
    private val sims = ConcurrentHashMap<String, Sim>()
    private val rnd = SecureRandom()

    override fun request(req: PushRequest): PushResult {
        val ref = "SIM-" + newId().take(12)
        sims[ref] = Sim("pending", null, req.amount, null, null)
        return PushResult(ref)
    }
    override fun query(providerRef: String): ProviderStatus {
        val s = sims[providerRef] ?: return ProviderStatus("failed", null, null, "404", "Unknown request")
        return ProviderStatus(s.state, s.receipt, s.amount.takeIf { s.state == "succeeded" }, s.code, s.desc)
    }
    override fun parseCallback(body: String): CallbackResult? {
        val j = mapper.readTree(body)
        val ref = j.path("providerRef").asText("")
        if (ref.isBlank()) return null
        return CallbackResult(ref, j.path("state").asText(), j.path("receipt").takeIf { !it.isNull && !it.isMissingNode }?.asText(),
            j.path("amount").takeIf { it.isNumber }?.asLong(), j.path("code").asText(null), j.path("desc").asText(null))
    }
    /** The customer enters their PIN. Returns the callback body the network would POST. */
    fun approve(ref: String, amountOverride: Long? = null): String {
        val s = sims[ref] ?: throw ProviderException("Unknown request")
        s.state = "succeeded"; s.receipt = "SIM" + (1000000 + rnd.nextInt(8999999)); s.code = "0"; s.desc = "Approved"
        return mapper.writeValueAsString(mapOf("providerRef" to ref, "state" to "succeeded", "receipt" to s.receipt, "amount" to (amountOverride ?: s.amount), "code" to "0", "desc" to "Approved"))
    }
    fun decline(ref: String): String {
        val s = sims[ref] ?: throw ProviderException("Unknown request")
        s.state = "failed"; s.code = "1032"; s.desc = "Request cancelled by user"
        return mapper.writeValueAsString(mapOf("providerRef" to ref, "state" to "failed", "code" to "1032", "desc" to s.desc))
    }
}

@Component
class PaymentRouter(val daraja: DarajaProvider, val sim: SimulatedProvider, @Value("\${emtshop.sandbox:false}") val sandbox: Boolean) {
    /** Which provider handles this network in this country. Null means no live integration: the cashier confirms by hand. */
    fun providerFor(country: String, network: String): MobileMoneyProvider? = when {
        country == "KE" && network == "mpesa" && daraja.configured -> daraja
        sandbox -> sim
        else -> null
    }
    fun byId(id: String): MobileMoneyProvider? = when (id) { "daraja" -> daraja; "simulator" -> sim; else -> null }
}

/* ------------------------------------------------------------------------------------------------
 * Payment intents. Every request for money is recorded before it is sent, every provider message is
 * stored, and a payment that succeeds is always turned into a sale (by the client or, failing that, the server).
 * ---------------------------------------------------------------------------------------------- */

data class PaymentReq(val lines: List<SaleLineReq> = emptyList(), val network: String = "", val phone: String = "")
data class ResolveReq(val action: String = "")

val DIAL = mapOf("TZ" to "255", "KE" to "254", "IN" to "91", "BR" to "55", "US" to "1")
const val INTENT_TTL_MS = 3 * 60_000L
val LIVE_TENDERS = setOf("lipa_namba", "mpesa_till")

@Service
class PaymentService(
    val jdbc: JdbcTemplate, val tx: TransactionTemplate, val router: PaymentRouter, val access: Access, val products: ProductService,
    val sales: SalesService, val activity: ActivityService, val hub: Hub, val json: Json, val mapper: ObjectMapper,
    @Value("\${emtshop.public-url:http://localhost:8080}") val publicUrl: String
) {
    private data class Intent(
        val id: String, val shopId: String, val userId: String, val provider: String, val network: String, val phone: String, val amount: Long, val currency: String,
        val linesJson: String, val status: String, val providerRef: String?, val token: String, val receipt: String?, val late: Boolean, val saleId: String?,
        val createdAt: Long, val updatedAt: Long, val expiresAt: Long, val resultDesc: String?, val acked: Boolean
    )
    private val cols = "id,shop_id,user_id,provider,network,phone,amount,currency,lines_json,status,provider_ref,callback_token,receipt,late,sale_id,created_at,updated_at,expires_at,result_desc,acked"
    private val mapperRow = RowMapper<Intent> { r, _ ->
        Intent(r.getString(1), r.getString(2), r.getString(3), r.getString(4), r.getString(5), r.getString(6), r.getLong(7), r.getString(8), r.getString(9), r.getString(10),
            r.getString(11), r.getString(12), r.getString(13), r.getBoolean(14), r.getString(15), r.getLong(16), r.getLong(17), r.getLong(18), r.getString(19), r.getBoolean(20))
    }
    private fun load(id: String, lock: Boolean = false): Intent =
        jdbc.query("select $cols from payment_intents where id=?" + if (lock) " for update" else "", mapperRow, id).firstOrNull() ?: notFound("PAYMENT_NOT_FOUND", "Payment not found")

    fun normalizePhone(country: String, raw: String): String {
        var d = raw.filter { it.isDigit() }
        val dial = DIAL[country] ?: bad("INVALID_PHONE", "Phone numbers are not supported in this country")
        if (d.startsWith("0")) d = dial + d.substring(1)
        if (!d.startsWith(dial)) d = dial + d
        if (d.length !in 11..13) bad("INVALID_PHONE", "Enter the customer's mobile number")
        return d
    }

    private fun view(i: Intent): Map<String, Any?> = mapOf(
        "id" to i.id, "shopId" to i.shopId, "status" to i.status, "amount" to i.amount, "currency" to i.currency, "network" to i.network,
        "phone" to "••• " + i.phone.takeLast(3), "receipt" to i.receipt, "late" to i.late, "saleId" to i.saleId, "acked" to i.acked,
        "message" to i.resultDesc, "createdAt" to i.createdAt, "expiresAt" to i.expiresAt
    )
    fun view(id: String): Map<String, Any?> = view(load(id))
    fun shopOf(id: String): String = load(id).shopId

    fun create(shop: Shop, user: AuthUser, req: PaymentReq, device: String): Map<String, Any?> {
        val region = Regions.get(shop.country)
        if (region.networks.none { it.id == req.network }) bad("INVALID_NETWORK", "Unknown network")
        val provider = router.providerFor(shop.country, req.network) ?: throw ApiException(HttpStatus.SERVICE_UNAVAILABLE, "PAYMENTS_NOT_CONFIGURED", "Live payments are not set up for this network")
        val phone = normalizePhone(shop.country, req.phone)
        val total = sales.price(shop, req.lines)
        if (total <= 0) bad("EMPTY_SALE", "Add at least one item")
        val id = newId()
        val token = newId()
        val t = now()
        jdbc.update(
            "insert into payment_intents(id,shop_id,user_id,provider,network,phone,amount,currency,lines_json,status,callback_token,created_at,updated_at,expires_at) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            id, shop.id, user.id, provider.id, req.network, phone, total, shop.currency, json.write(req.lines), "created", token, t, t, t + INTENT_TTL_MS
        )
        try {
            val res = provider.request(PushRequest(id, total, shop.currency, phone, req.network, "EMT" + id.take(8), "Emt Shop", "$publicUrl/api/payments/callback/${provider.id}/$token", shop.till))
            jdbc.update("update payment_intents set status='pending',provider_ref=?,updated_at=? where id=?", res.providerRef, now(), id)
            event(id, provider.id, "pushed", mapOf("providerRef" to res.providerRef, "amount" to total))
        } catch (e: ProviderException) {
            jdbc.update("update payment_intents set status='failed',result_desc=?,updated_at=? where id=?", (e.message ?: "").take(190), now(), id)
            event(id, provider.id, "push_failed", mapOf("error" to e.message))
            throw ApiException(HttpStatus.BAD_GATEWAY, "PROVIDER_ERROR", e.message ?: "The mobile money provider rejected the request")
        }
        return view(load(id))
    }

    private fun event(intentId: String?, provider: String, kind: String, payload: Any) {
        jdbc.update("insert into payment_events(id,intent_id,provider,kind,payload,created_at) values(?,?,?,?,?,?)", newId(), intentId, provider, kind, json.write(payload).take(3900), now())
    }

    /** Public webhook. Always answers quickly; whatever it cannot match is stored for reconciliation instead of being dropped. */
    fun handleCallback(providerId: String, token: String, body: String) {
        val provider = router.byId(providerId)
        val parsed = try { provider?.parseCallback(body) } catch (e: Exception) { null }
        val intent = jdbc.query("select $cols from payment_intents where callback_token=?", mapperRow, token).firstOrNull()
        if (provider == null || parsed == null || intent == null || (intent.providerRef != null && intent.providerRef != parsed.providerRef)) {
            event(intent?.id, providerId, "unmatched", mapOf("token" to token.take(6), "body" to body.take(1500)))
            return
        }
        event(intent.id, providerId, "callback", mapOf("body" to body.take(1500)))
        settle(intent.id, parsed, "callback")
    }

    /** Apply a provider outcome exactly once, under a row lock. Safe to call repeatedly with the same outcome. */
    fun settle(intentId: String, r: CallbackResult, source: String) {
        var changed: Map<String, Any?>? = null
        var received: Intent? = null
        tx.execute { _ ->
            val i = load(intentId, lock = true)
            when (r.state) {
                "succeeded" -> {
                    if (i.status == "succeeded") {
                        if (r.receipt != null && i.receipt != null && r.receipt != i.receipt) event(i.id, i.provider, "conflict", mapOf("have" to i.receipt, "got" to r.receipt))
                        return@execute
                    }
                    val late = i.status in setOf("expired", "failed")
                    if (r.amount != null && r.amount != i.amount) {
                        jdbc.update("update payment_intents set status='mismatch',receipt=?,result_desc=?,updated_at=? where id=?", r.receipt, "Paid ${r.amount}, expected ${i.amount}", now(), i.id)
                        event(i.id, i.provider, "mismatch", mapOf("expected" to i.amount, "paid" to r.amount, "receipt" to r.receipt))
                    } else {
                        try {
                            jdbc.update("update payment_intents set status='succeeded',receipt=?,result_desc=?,late=?,updated_at=? where id=?", r.receipt, r.desc, late, now(), i.id)
                        } catch (e: DuplicateKeyException) {
                            jdbc.update("update payment_intents set status='mismatch',result_desc=?,updated_at=? where id=?", "Receipt ${r.receipt} was already used", now(), i.id)
                            event(i.id, i.provider, "duplicate_receipt", mapOf("receipt" to r.receipt))
                        }
                    }
                    received = i
                }
                "failed" -> {
                    if (i.status in setOf("created", "pending")) {
                        jdbc.update("update payment_intents set status='failed',result_desc=?,result_code=?,updated_at=? where id=?", r.desc?.take(190), r.code, now(), i.id)
                    }
                }
                else -> return@execute
            }
            changed = view(load(i.id))
        }
        val v = changed ?: return
        val shopId = v["shopId"] as String
        hub.broadcastShop(shopId, mapOf("type" to "payment", "payment" to v))
        if (v["status"] == "succeeded") {
            val owner = access.shop(shopId)
            activity.log(shopId, null, "payment_received", mapOf("amount" to v["amount"], "network" to v["network"], "receipt" to v["receipt"], "currency" to owner.currency, "late" to v["late"]), "Mobile money")
        } else if (v["status"] == "mismatch") {
            activity.log(shopId, null, "payment_mismatch", mapOf("receipt" to v["receipt"], "currency" to access.shop(shopId).currency), "Mobile money")
        }
        received?.let { }
    }

    /** Ask the provider what happened to requests whose callback has not arrived; expire the ones nobody answered. */
    @Scheduled(fixedDelayString = "4000", initialDelayString = "4000")
    fun tick() {
        try { sweep() } catch (e: Exception) { /* a failed sweep must never stop the next one */ }
    }

    fun sweep() {
        val t = now()
        val pending = jdbc.query("select $cols from payment_intents where status='pending' and updated_at<?", mapperRow, t - 15_000)
        for (i in pending) {
            val p = router.byId(i.provider) ?: continue
            val ref = i.providerRef ?: continue
            try {
                val s = p.query(ref)
                event(i.id, i.provider, "query", mapOf("state" to s.state, "code" to s.code))
                if (s.state != "pending") settle(i.id, CallbackResult(ref, s.state, s.receipt, s.amount, s.code, s.desc), "query")
                else if (t > i.expiresAt) expire(i.id)
            } catch (e: ProviderException) {
                if (t > i.expiresAt) expire(i.id)
            }
        }
        for (i in jdbc.query("select $cols from payment_intents where status='succeeded' and sale_id is null and updated_at<?", mapperRow, t - 20_000)) {
            runCatching { complete(i.id) }
        }
    }

    private fun expire(id: String) {
        val n = jdbc.update("update payment_intents set status='expired',result_desc='No answer from the customer',updated_at=? where id=? and status='pending'", now(), id)
        if (n > 0) hub.broadcastShop(shopOf(id), mapOf("type" to "payment", "payment" to view(id)))
    }

    /** Money arrived: make sure a sale exists for it, even if the cashier's phone died. */
    fun complete(intentId: String): Map<String, Any?> {
        val i = load(intentId)
        if (i.status != "succeeded") conflict("NOT_PAID", "This payment has not been confirmed")
        i.saleId?.let { return sales.view(it) }
        val shop = access.shop(i.shopId)
        val user = jdbc.query("select id,name,email from users where id=?", RowMapper { r, _ -> AuthUser(r.getString(1), r.getString(2), r.getString(3)) }, i.userId).first()
        @Suppress("UNCHECKED_CAST")
        val lines = mapper.readValue(i.linesJson, mapper.typeFactory.constructCollectionType(List::class.java, SaleLineReq::class.java)) as List<SaleLineReq>
        val tender = if (shop.country == "KE") "mpesa_till" else "lipa_namba"
        return sales.record(shop, user, SaleReq(lines, tender, i.network, "pay-" + i.id, null, i.id), "Auto-settlement", force = true)
    }

    fun list(shopId: String, limit: Int): List<Map<String, Any?>> =
        jdbc.query("select $cols from payment_intents where shop_id=? order by created_at desc limit ?", mapperRow, shopId, limit).map { view(it) }

    fun resolve(paymentId: String, action: String): Map<String, Any?> {
        val i = load(paymentId)
        return when (action) {
            "complete" -> { complete(paymentId); view(paymentId) }
            "acknowledge" -> { jdbc.update("update payment_intents set acked=true,updated_at=? where id=?", now(), paymentId); event(paymentId, i.provider, "ack", mapOf("by" to "owner")); view(paymentId) }
            else -> bad("INVALID_ACTION", "Action must be complete or acknowledge")
        }
    }

    /** Daily money proof: what the networks confirmed, what became sales, and everything that still needs a person. */
    fun reconciliation(shop: Shop, days: Int): Map<String, Any?> {
        val region = Regions.get(shop.country)
        val off = region.utcOffsetMinutes * 60_000L
        val today = Math.floorDiv(now() + off, DAY_MS) * DAY_MS - off
        val from = today - (days - 1) * DAY_MS
        val intents = jdbc.query("select $cols from payment_intents where shop_id=? and created_at>=? order by created_at desc", mapperRow, shop.id, from)
        val voided = jdbc.queryForList("select id from sales where shop_id=? and status='void' and payment_id is not null", String::class.java, shop.id).toSet()
        val saleOf = jdbc.query("select payment_id,id,status,number,total from sales where shop_id=? and payment_id is not null", RowMapper { r, _ ->
            r.getString(1) to mapOf("id" to r.getString(2), "status" to r.getString(3), "number" to r.getInt(4), "total" to r.getLong(5)) }, shop.id).toMap()
        fun dayOf(ms: Long) = Math.floorDiv(ms + off, DAY_MS) * DAY_MS - off
        val rows = (0 until days).map { k ->
            val d = today - k * DAY_MS
            val day = intents.filter { dayOf(it.createdAt) == d }
            val ok = day.filter { it.status == "succeeded" }
            mapOf(
                "day" to d,
                "requested" to day.size.toLong(),
                "confirmed" to ok.sumOf { it.amount },
                "confirmedCount" to ok.size.toLong(),
                "matched" to ok.filter { it.saleId != null }.sumOf { it.amount },
                "unmatched" to ok.filter { it.saleId == null }.sumOf { it.amount },
                "mismatch" to day.filter { it.status == "mismatch" }.sumOf { it.amount },
                "failed" to day.count { it.status == "failed" || it.status == "expired" }.toLong(),
                "pending" to day.count { it.status == "pending" || it.status == "created" }.toLong()
            )
        }
        val needs = intents.filter { !it.acked && (
            (it.status == "succeeded" && it.saleId == null) || it.status == "mismatch" ||
                (it.status == "succeeded" && it.saleId != null && saleOf.values.any { s -> s["id"] == it.saleId && s["status"] == "void" })) }
            .map { i ->
                val kind = when {
                    i.status == "mismatch" -> "mismatch"
                    i.saleId == null -> "unmatched"
                    else -> "refund_due"
                }
                view(i) + mapOf("issue" to kind)
            }
        val unmatchedEvents = jdbc.queryForObject("select count(*) from payment_events where intent_id is null and kind='unmatched' and created_at>=?", Long::class.java, from)!!
        return mapOf("currency" to shop.currency, "days" to rows, "needsAttention" to needs, "unmatchedMessages" to unmatchedEvents, "voidedWithPayment" to voided.size)
    }

    fun openIssues(shopIds: List<String>): Long {
        if (shopIds.isEmpty()) return 0
        val marks = shopIds.joinToString(",") { "?" }
        return jdbc.queryForObject(
            "select count(*) from payment_intents p where p.shop_id in ($marks) and p.acked=false and (p.status='mismatch' or (p.status='succeeded' and (p.sale_id is null or exists (select 1 from sales s where s.id=p.sale_id and s.status='void'))))",
            Long::class.java, *shopIds.toTypedArray()
        )!!
    }
}

@RestController
@RequestMapping("/api")
class PaymentController(val access: Access, val billing: BillingService, val payments: PaymentService) {
    @PostMapping("/shops/{shopId}/payments")
    @ResponseStatus(HttpStatus.CREATED)
    fun create(
        @PathVariable shopId: String, @RequestAttribute("user") user: AuthUser, @RequestBody req: PaymentReq,
        @RequestHeader("X-Device", defaultValue = "Web") device: String
    ): Map<String, Any?> {
        val (shop, _) = access.member(shopId, user)
        billing.requireActive(shop.ownerId)
        return mapOf("payment" to payments.create(shop, user, req, device))
    }

    @GetMapping("/payments/{id}")
    fun get(@PathVariable id: String, @RequestAttribute("user") user: AuthUser): Map<String, Any?> {
        access.member(payments.shopOf(id), user)
        return mapOf("payment" to payments.view(id))
    }

    @GetMapping("/shops/{shopId}/payments")
    fun list(@PathVariable shopId: String, @RequestAttribute("user") user: AuthUser, @RequestParam(defaultValue = "30") limit: Int): Map<String, Any?> {
        access.member(shopId, user)
        return mapOf("payments" to payments.list(shopId, limit.coerceIn(1, 100)))
    }

    @GetMapping("/shops/{shopId}/reconciliation")
    fun reconciliation(@PathVariable shopId: String, @RequestAttribute("user") user: AuthUser, @RequestParam(defaultValue = "7") days: Int): Map<String, Any?> {
        val (shop, _) = access.need(shopId, user, "owner", "manager")
        return payments.reconciliation(shop, days.coerceIn(1, 31))
    }

    @PostMapping("/payments/{id}/resolve")
    fun resolve(@PathVariable id: String, @RequestAttribute("user") user: AuthUser, @RequestBody req: ResolveReq): Map<String, Any?> {
        access.need(payments.shopOf(id), user, "owner", "manager")
        return mapOf("payment" to payments.resolve(id, req.action))
    }

    /** Called by the mobile money network, not by a signed-in user. The secret is the random token in the URL. */
    @PostMapping("/payments/callback/{provider}/{token}")
    fun callback(@PathVariable provider: String, @PathVariable token: String, @RequestBody body: String): Map<String, Any?> {
        payments.handleCallback(provider, token, body)
        return mapOf("ResultCode" to 0, "ResultDesc" to "Accepted")
    }
}
