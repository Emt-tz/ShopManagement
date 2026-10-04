package app.emtshop

import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
import org.springframework.stereotype.Service
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestAttribute
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController

data class Limits(val products: Int?, val shops: Int?, val registers: Int?, val staff: Int?)

object Plans {
    val ids = listOf("starter", "business", "multi")
    val limits = mapOf(
        "starter" to Limits(200, 1, 1, 0),
        "business" to Limits(null, 1, 3, 5),
        "multi" to Limits(null, null, null, null)
    )
    // Example monthly prices in minor units. In production these come from the store catalogues (App Store, Play, Stripe).
    private val prices = mapOf(
        "TZS" to listOf(19900L, 49900L, 129000L),
        "KES" to listOf(99900L, 249900L, 649900L),
        "INR" to listOf(49900L, 149900L, 399900L),
        "BRL" to listOf(2900L, 7900L, 19900L),
        "USD" to listOf(900L, 2900L, 7900L)
    )
    fun monthly(plan: String, currency: String): Long = (prices[currency] ?: prices["USD"]!!)[ids.indexOf(plan)]
    fun yearly(plan: String, currency: String): Long = monthly(plan, currency) * 12 * 80 / 100
}

data class Entitlement(
    val plan: String, val period: String, val status: String, val channel: String,
    val trialEndsAt: Long, val renewsAt: Long, val active: Boolean, val limits: Limits
)

data class SubscribeReq(val plan: String, val period: String = "monthly", val channel: String = "web")

const val TRIAL_DAYS = 14L
const val DAY_MS = 86_400_000L

@Service
class BillingService(val jdbc: JdbcTemplate) {
    private val mapper = RowMapper<Entitlement> { rs, _ ->
        val plan = rs.getString(1)
        val status = rs.getString(3)
        val renews = rs.getLong(6)
        Entitlement(plan, rs.getString(2), status, rs.getString(4), rs.getLong(5), renews,
            status in setOf("trialing", "active", "canceled") && now() < renews, Plans.limits[plan]!!)
    }

    fun current(userId: String): Entitlement? =
        jdbc.query("select plan,period,status,channel,trial_ends_at,renews_at from subscriptions where user_id=?", mapper, userId).firstOrNull()

    fun requireActive(userId: String): Entitlement {
        val e = current(userId) ?: planLimit("SUBSCRIPTION_REQUIRED", "Choose a plan to continue")
        if (!e.active) planLimit("SUBSCRIPTION_EXPIRED", "Your plan has ended. Renew to continue")
        return e
    }

    fun subscribe(userId: String, req: SubscribeReq): Entitlement {
        if (req.plan !in Plans.ids) bad("INVALID_PLAN", "Unknown plan")
        if (req.period !in listOf("monthly", "yearly")) bad("INVALID_PERIOD", "Unknown billing period")
        if (req.channel !in listOf("web", "appstore", "play")) bad("INVALID_CHANNEL", "Unknown billing channel")
        val existing = current(userId)
        val t = now()
        val periodMs = if (req.period == "yearly") 365 * DAY_MS else 30 * DAY_MS
        val trialEnds: Long
        val renews: Long
        val status: String
        if (existing == null) {
            trialEnds = t + TRIAL_DAYS * DAY_MS; renews = trialEnds; status = "trialing"
        } else {
            trialEnds = existing.trialEndsAt
            status = if (t < trialEnds) "trialing" else "active"
            renews = if (t < trialEnds) trialEnds else t + periodMs
        }
        jdbc.update("delete from subscriptions where user_id=?", userId)
        jdbc.update(
            "insert into subscriptions(user_id,plan,period,status,channel,trial_ends_at,renews_at,created_at) values(?,?,?,?,?,?,?,?)",
            userId, req.plan, req.period, status, req.channel, trialEnds, renews, t
        )
        return current(userId)!!
    }

    fun cancel(userId: String): Entitlement {
        current(userId) ?: notFound("NO_SUBSCRIPTION", "No subscription to cancel")
        jdbc.update("update subscriptions set status='canceled' where user_id=?", userId)
        return current(userId)!!
    }

    fun view(e: Entitlement): Map<String, Any?> = mapOf(
        "plan" to e.plan, "period" to e.period, "status" to e.status, "channel" to e.channel,
        "trialEndsAt" to e.trialEndsAt, "renewsAt" to e.renewsAt, "active" to e.active,
        "limits" to mapOf("products" to e.limits.products, "shops" to e.limits.shops, "registers" to e.limits.registers, "staff" to e.limits.staff)
    )
}

@RestController
@RequestMapping("/api/billing")
class BillingController(val billing: BillingService) {
    @GetMapping("/plans")
    fun plans(@RequestParam(defaultValue = "US") country: String): Map<String, Any?> {
        val r = Regions.get(country.uppercase())
        return mapOf(
            "currency" to r.currency, "decimals" to r.decimals, "trialDays" to TRIAL_DAYS,
            "plans" to Plans.ids.map { id ->
                val l = Plans.limits[id]!!
                mapOf(
                    "id" to id, "monthly" to Plans.monthly(id, r.currency), "yearly" to Plans.yearly(id, r.currency),
                    "limits" to mapOf("products" to l.products, "shops" to l.shops, "registers" to l.registers, "staff" to l.staff)
                )
            }
        )
    }

    @GetMapping("/subscription")
    fun subscription(@RequestAttribute("user") user: AuthUser): Map<String, Any?> =
        mapOf("subscription" to billing.current(user.id)?.let { billing.view(it) })

    @PostMapping("/subscribe")
    fun subscribe(@RequestAttribute("user") user: AuthUser, @RequestBody req: SubscribeReq): Map<String, Any?> =
        mapOf("subscription" to billing.view(billing.subscribe(user.id, req)))

    @PostMapping("/cancel")
    fun cancel(@RequestAttribute("user") user: AuthUser): Map<String, Any?> =
        mapOf("subscription" to billing.view(billing.cancel(user.id)))
}
