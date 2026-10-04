package app.emtshop

import com.fasterxml.jackson.databind.ObjectMapper
import org.springframework.cache.annotation.CacheEvict
import org.springframework.cache.annotation.Cacheable
import org.springframework.core.io.ClassPathResource
import org.springframework.stereotype.Service
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestAttribute
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

data class Network(val id: String, val name: String)

data class Region(
    val code: String, val name: String, val currency: String, val decimals: Int, val locales: List<String>,
    val taxName: String, val taxBps: Int, val tenders: List<String>, val networks: List<Network>, val utcOffsetMinutes: Int, val timeZone: String
)

/** Region configuration. Adding a country is a data change here (or a table in production), not an app release. */
object Regions {
    val all = listOf(
        Region("TZ", "Tanzania", "TZS", 0, listOf("sw-TZ", "en-TZ"), "VAT", 1800, listOf("cash", "lipa_namba", "card", "credit"),
            listOf(Network("mpesa", "M-Pesa"), Network("mixx", "Mixx by Yas"), Network("airtel", "Airtel Money"), Network("halopesa", "HaloPesa")), 180, "Africa/Dar_es_Salaam"),
        Region("KE", "Kenya", "KES", 2, listOf("en-KE", "sw-KE"), "VAT", 1600, listOf("cash", "mpesa_till", "card", "credit"),
            listOf(Network("mpesa", "M-Pesa"), Network("airtel", "Airtel Money")), 180, "Africa/Nairobi"),
        Region("IN", "India", "INR", 2, listOf("en-IN", "hi-IN"), "GST", 1800, listOf("cash", "upi", "card", "credit"), emptyList(), 330, "Asia/Kolkata"),
        Region("BR", "Brazil", "BRL", 2, listOf("pt-BR"), "Tax", 0, listOf("cash", "pix", "card", "credit"), emptyList(), -180, "America/Sao_Paulo"),
        Region("US", "United States", "USD", 2, listOf("en-US", "es-US"), "Sales tax", 0, listOf("cash", "card", "credit"), emptyList(), -300, "America/New_York")
    )
    fun get(code: String): Region = all.firstOrNull { it.code == code } ?: all.first { it.code == "US" }
    fun find(code: String): Region? = all.firstOrNull { it.code == code }
}

data class ShopType(val id: String, val tools: List<String>, val categories: List<String>)

object ShopTypes {
    val all = listOf(
        ShopType("retail", listOf("barcode", "stock", "receipts"), listOf("Food", "Household", "Stationery", "Drinks")),
        ShopType("grocery", listOf("barcode", "stock", "receipts", "weights"), listOf("Produce", "Dairy", "Pantry", "Drinks")),
        ShopType("mobile_money", listOf("float", "commission"), emptyList()),
        ShopType("phones", listOf("barcode", "stock", "serial", "receipts"), listOf("Phones", "Accessories", "Repairs")),
        ShopType("restaurant", listOf("stock", "receipts"), listOf("Meals", "Drinks", "Snacks"))
    )
    fun find(id: String): ShopType? = all.firstOrNull { it.id == id }
}

@Service
class ShopConfigCache(val access: Access) {
    /** Static per-shop configuration. Cached (Caffeine) and evicted whenever the shop changes. */
    @Cacheable("shopConfig", key = "#shopId")
    fun get(shopId: String): Map<String, Any?> {
        val s = access.shop(shopId)
        val r = Regions.get(s.country)
        val t = ShopTypes.find(s.type)!!
        val tenders = r.tenders.map { id ->
            mapOf("id" to id, "networks" to if (id == "lipa_namba" || id == "mpesa_till") r.networks.map { mapOf("id" to it.id, "name" to it.name) } else emptyList<Any>())
        }
        val body = mapOf(
            "shop" to mapOf("id" to s.id, "name" to s.name, "type" to s.type, "country" to s.country, "till" to s.till),
            "locale" to s.locale,
            "locales" to r.locales,
            "timeZone" to r.timeZone,
            "currency" to mapOf("code" to r.currency, "decimals" to r.decimals),
            "tax" to mapOf("name" to r.taxName, "bps" to r.taxBps, "inclusive" to true),
            "tenders" to tenders,
            "networks" to r.networks.map { mapOf("id" to it.id, "name" to it.name) },
            "tools" to t.tools,
            "categories" to t.categories
        )
        return body + ("version" to body.toString().hashCode().toLong().and(0xffffffffL))
    }

    @CacheEvict("shopConfig", key = "#shopId")
    fun evict(shopId: String) {}
}

@Service
class ConfigService(val cache: ShopConfigCache, val access: Access, val billing: BillingService) {
    fun full(shopId: String): Map<String, Any?> {
        val ownerId = access.shop(shopId).ownerId
        return cache.get(shopId) + ("plan" to billing.current(ownerId)?.let { billing.view(it) })
    }
}

@Service
class I18n(val mapper: ObjectMapper) {
    private val cache = HashMap<String, Map<String, String>>()

    @Suppress("UNCHECKED_CAST")
    private fun load(lang: String): Map<String, String> = cache.getOrPut(lang) {
        val res = ClassPathResource("i18n/$lang.json")
        if (!res.exists()) emptyMap() else mapper.readValue(res.inputStream, Map::class.java) as Map<String, String>
    }

    /** Catalog for a language with English fallback for any missing key. */
    fun catalog(locale: String): Map<String, String> {
        val lang = locale.substringBefore("-").lowercase()
        return load("en") + load(lang)
    }
}

@RestController
@RequestMapping("/api")
class ConfigController(val i18n: I18n, val config: ConfigService, val access: Access) {
    @GetMapping("/i18n/{locale}")
    fun catalog(@PathVariable locale: String) = mapOf("locale" to locale, "strings" to i18n.catalog(locale))

    @GetMapping("/regions")
    fun regions() = mapOf(
        "regions" to Regions.all.map { r ->
            mapOf("code" to r.code, "name" to r.name, "currency" to r.currency, "decimals" to r.decimals, "locales" to r.locales)
        },
        "shopTypes" to ShopTypes.all.map { mapOf("id" to it.id, "tools" to it.tools) }
    )

    @GetMapping("/shops/{id}/config")
    fun shopConfig(@PathVariable id: String, @RequestAttribute("user") user: AuthUser): Map<String, Any?> {
        access.member(id, user)
        return config.full(id)
    }

    @GetMapping("/health")
    fun health() = mapOf("status" to "ok")
}
