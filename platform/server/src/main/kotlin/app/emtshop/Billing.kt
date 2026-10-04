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
    val trialEndsAt: Long, val renewsAt: Long, val active: Boolean, val limits: Limits,
    val free: Boolean, val plansOpen: Boolean
)

data class SubscribeReq(val plan: String, val period: String = "monthly", val channel: String = "web")

/** Every new account gets the whole platform free for 90 days. Plans and payment only open in the last PLANS_OPEN_DAYS. */
const val TRIAL_DAYS = 90L
const val PLANS_OPEN_DAYS = 14L
const val GRACE_DAYS = 7L
const val DAY_MS = 86_400_000L

@Service
class BillingService(val jdbc: JdbcTemplate) {
    private val mapper = RowMapper<Entitlement> { rs, _ ->
        val plan = rs.getString(1)
        val status = rs.getString(3)
        val trialEnds = rs.getLong(5)
        val renews = rs.getLong(6)
        val t = now()
        val free = t < trialEnds
        // During the free period everything is unlocked, whatever plan was picked for later.
        Entitlement(plan, rs.getString(2), status, rs.getString(4), trialEnds, renews,
            status in setOf("trialing", "active", "canceled") && t < renews + GRACE_DAYS * DAY_MS,
            if (free) Plans.limits["multi"]!! else Plans.limits[plan]!!, free,
            !free || trialEnds - t <= PLANS_OPEN_DAYS * DAY_MS)
    }

    fun current(userId: String): Entitlement? =
        jdbc.query("select plan,period,status,channel,trial_ends_at,renews_at from subscriptions where user_id=?", mapper, userId).firstOrNull()

    /** Called at sign-up: the full platform, free, for 90 days. */
    fun startFreePeriod(userId: String) {
        val t = now()
        val ends = t + TRIAL_DAYS * DAY_MS
        jdbc.update(
            "insert into subscriptions(user_id,plan,period,status,channel,trial_ends_at,renews_at,created_at) values(?,?,?,?,?,?,?,?)",
            userId, "multi", "monthly", "trialing", "free", ends, ends, t
        )
    }

    fun requireActive(userId: String): Entitlement {
        val e = current(userId) ?: planLimit("SUBSCRIPTION_REQUIRED", "Choose a plan to continue")
        if (!e.active) planLimit("SUBSCRIPTION_EXPIRED", "Your plan has ended. Renew to continue")
        return e
    }

    fun subscribe(userId: String, req: SubscribeReq): Entitlement {
        if (req.plan !in Plans.ids) bad("INVALID_PLAN", "Unknown plan")
        if (req.period !in listOf("monthly", "yearly")) bad("INVALID_PERIOD", "Unknown billing period")
        if (req.channel !in listOf("web", "appstore", "play")) bad("INVALID_CHANNEL", "Unknown billing channel")
        val existing = current(userId) ?: notFound("NO_SUBSCRIPTION", "No account period found")
        if (!existing.plansOpen) throw ApiException(HttpStatus.CONFLICT, "PLANS_NOT_OPEN", "Plans open ${PLANS_OPEN_DAYS} days before your free period ends")
        val t = now()
        val periodMs = if (req.period == "yearly") 365 * DAY_MS else 30 * DAY_MS
        // Billing starts when the free period ends, never earlier.
        val renews = maxOf(t, existing.trialEndsAt) + periodMs
        jdbc.update(
            "update subscriptions set plan=?,period=?,status='active',channel=?,renews_at=? where user_id=?",
            req.plan, req.period, req.channel, renews, userId
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
        "free" to e.free, "plansOpen" to e.plansOpen, "freeDaysLeft" to if (e.free) (e.trialEndsAt - now() + DAY_MS - 1) / DAY_MS else 0L,
        "graceUntil" to e.renewsAt + GRACE_DAYS * DAY_MS,
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
            "currency" to r.currency, "decimals" to r.decimals, "trialDays" to TRIAL_DAYS, "plansOpenDays" to PLANS_OPEN_DAYS,
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
