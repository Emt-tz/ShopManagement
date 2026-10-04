package app.emtshop.mobile

import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID

class ApiError(val code: String, message: String) : Exception(message)

/** Thin client for the Emt Shop server. Amounts are minor units; the shop's currency decimals say where the point goes. */
class Api(private val base: String, var token: String?, private val device: String = "Android") {
    private fun call(method: String, path: String, body: JSONObject? = null): JSONObject {
        val c = URL("$base/api$path").openConnection() as HttpURLConnection
        c.requestMethod = method; c.connectTimeout = 10_000; c.readTimeout = 20_000
        c.setRequestProperty("Content-Type", "application/json"); c.setRequestProperty("X-Device", device)
        token?.let { c.setRequestProperty("Authorization", "Bearer $it") }
        if (body != null) { c.doOutput = true; c.outputStream.use { it.write(body.toString().toByteArray()) } }
        val code = c.responseCode
        val text = (if (code < 400) c.inputStream else c.errorStream)?.bufferedReader()?.use { it.readText() } ?: "{}"
        val json = runCatching { JSONObject(text) }.getOrDefault(JSONObject())
        if (code >= 400) throw ApiError(json.optString("code", "HTTP_$code"), json.optString("message", "Request failed ($code)"))
        return json
    }

    fun login(email: String, password: String): JSONObject = call("POST", "/auth/login", JSONObject().put("email", email).put("password", password)).also { token = it.getString("token") }
    fun signup(name: String, email: String, password: String): JSONObject =
        call("POST", "/auth/signup", JSONObject().put("name", name).put("email", email).put("password", password)).also { token = it.getString("token") }
    fun me(): JSONObject = call("GET", "/me")
    fun config(shopId: String): JSONObject = call("GET", "/shops/$shopId/config")
    fun products(shopId: String): JSONArray = call("GET", "/shops/$shopId/products").getJSONArray("products")
    fun sales(shopId: String): JSONArray = call("GET", "/shops/$shopId/sales?limit=50").getJSONArray("sales")
    fun insights(shopId: String, range: String): JSONObject = call("GET", "/shops/$shopId/insights?range=$range")
    fun float(shopId: String): JSONObject = call("GET", "/shops/$shopId/float")
    fun floatTx(shopId: String, network: String, kind: String, amount: Long): JSONObject =
        call("POST", "/shops/$shopId/float/tx", JSONObject().put("network", network).put("kind", kind).put("amount", amount))

    /** One idempotency key per cart: a retry after a dropped connection returns the same receipt instead of a second sale. */
    fun sell(shopId: String, lines: Map<String, Int>, tender: String, tenderRef: String?, key: String = UUID.randomUUID().toString()): JSONObject {
        val arr = JSONArray(); lines.forEach { (id, q) -> arr.put(JSONObject().put("productId", id).put("qty", q)) }
        val b = JSONObject().put("lines", arr).put("tender", tender).put("idempotencyKey", key)
        if (tenderRef != null) b.put("tenderRef", tenderRef)
        return call("POST", "/shops/$shopId/sales", b).getJSONObject("sale")
    }
}

fun money(minor: Long, decimals: Int, currency: String): String {
    var p = 1L; repeat(decimals) { p *= 10 }
    val whole = minor / p
    val s = "%,d".format(whole)
    return if (decimals == 0) "$currency $s" else "$currency $s.${(minor % p).toString().padStart(decimals, '0')}"
}
