package app.emtshop

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestAttribute
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

data class FastForwardReq(val days: Long = 0)
data class ApproveReq(val amount: Long? = null)

/** Sandbox-only helpers. They exist so tests and demos can play the customer's phone and move the clock. Never enabled in production. */
@RestController
@RequestMapping("/api/dev")
@ConditionalOnProperty("emtshop.sandbox", havingValue = "true")
class DevController(val jdbc: JdbcTemplate, val access: Access, val payments: PaymentService, val sim: SimulatedProvider, val router: PaymentRouter) {
    @PostMapping("/billing/fast-forward")
    fun fastForward(@RequestAttribute("user") user: AuthUser, @RequestBody req: FastForwardReq): Map<String, Any?> {
        val ms = req.days * DAY_MS
        jdbc.update("update subscriptions set trial_ends_at=trial_ends_at-?, renews_at=renews_at-? where user_id=?", ms, ms, user.id)
        return mapOf("ok" to true)
    }

    private fun intentRef(id: String): String {
        val shop = payments.shopOf(id)
        return jdbc.queryForObject("select provider_ref from payment_intents where id=?", String::class.java, id) ?: bad("NO_REF", "Payment has no provider reference for $shop")
    }
    private fun token(id: String) = jdbc.queryForObject("select callback_token from payment_intents where id=?", String::class.java, id)!!

    /** The customer approves on their phone: the network then calls our webhook, exactly as in production. */
    @PostMapping("/payments/{id}/approve")
    fun approve(@PathVariable id: String, @RequestAttribute("user") user: AuthUser, @RequestBody(required = false) req: ApproveReq?): Map<String, Any?> {
        access.member(payments.shopOf(id), user)
        payments.handleCallback("simulator", token(id), sim.approve(intentRef(id), req?.amount))
        return mapOf("payment" to payments.view(id))
    }

    @PostMapping("/payments/{id}/decline")
    fun decline(@PathVariable id: String, @RequestAttribute("user") user: AuthUser): Map<String, Any?> {
        access.member(payments.shopOf(id), user)
        payments.handleCallback("simulator", token(id), sim.decline(intentRef(id)))
        return mapOf("payment" to payments.view(id))
    }
}
