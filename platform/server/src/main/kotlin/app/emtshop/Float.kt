package app.emtshop

import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
import org.springframework.stereotype.Service
import org.springframework.transaction.support.TransactionTemplate
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestAttribute
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestHeader
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.ResponseStatus
import org.springframework.web.bind.annotation.RestController

data class FloatTxReq(val network: String = "", val kind: String = "", val amount: Long = 0)
data class FloatAdjustReq(val network: String = "", val delta: Long = 0)

@Service
class FloatService(val jdbc: JdbcTemplate, val tx: TransactionTemplate, val activity: ActivityService) {
    // Commission in basis points of the amount.
    private val commissionBps = mapOf("cash_in" to 40L, "cash_out" to 80L, "airtime" to 500L)

    private fun requireAgentShop(shop: Shop) {
        if (shop.type != "mobile_money") bad("NOT_AGENT_SHOP", "This shop does not use mobile money float")
    }

    fun overview(shop: Shop): Map<String, Any?> {
        requireAgentShop(shop)
        val region = Regions.get(shop.country)
        val names = region.networks.associate { it.id to it.name } + ("cash" to "Cash")
        val accounts = jdbc.query(
            "select network,balance,low_at from float_accounts where shop_id=?",
            RowMapper { rs, _ -> Triple(rs.getString(1), rs.getLong(2), rs.getLong(3)) }, shop.id
        ).sortedBy { if (it.first == "cash") "" else it.first }
        val off = region.utcOffsetMinutes * 60_000L
        val dayStart = Math.floorDiv(now() + off, DAY_MS) * DAY_MS - off
        val today = jdbc.query(
            "select count(*),coalesce(sum(commission),0) from float_tx where shop_id=? and created_at>=?",
            RowMapper { rs, _ -> rs.getLong(1) to rs.getLong(2) }, shop.id, dayStart
        ).first()
        val recent = jdbc.query(
            "select network,kind,amount,user_name,created_at from float_tx where shop_id=? order by created_at desc limit 20",
            RowMapper { rs, _ -> mapOf("network" to rs.getString(1), "kind" to rs.getString(2), "amount" to rs.getLong(3), "userName" to rs.getString(4), "at" to rs.getLong(5)) }, shop.id
        )
        return mapOf(
            "currency" to shop.currency,
            "accounts" to accounts.map { (n, bal, low) -> mapOf("network" to n, "name" to (names[n] ?: n), "balance" to bal, "lowAt" to low, "low" to (low > 0 && bal < low)) },
            "total" to accounts.sumOf { it.second },
            "todayCount" to today.first, "todayCommission" to today.second, "recent" to recent
        )
    }

    fun transact(shop: Shop, user: AuthUser, req: FloatTxReq, device: String, at: Long = now(), silent: Boolean = false) {
        requireAgentShop(shop)
        val bps = commissionBps[req.kind] ?: bad("INVALID_KIND", "Kind must be cash_in, cash_out or airtime")
        if (req.amount <= 0) bad("INVALID_AMOUNT", "Enter an amount")
        val region = Regions.get(shop.country)
        if (region.networks.none { it.id == req.network }) bad("INVALID_NETWORK", "Unknown network")
        // cash_in / airtime: customer pays cash, e-float goes down. cash_out: customer takes cash, e-float goes up.
        val floatDelta = if (req.kind == "cash_out") req.amount else -req.amount
        val cashDelta = -floatDelta
        tx.execute { _ ->
            val f = balance(shop.id, req.network)
            val c = balance(shop.id, "cash")
            if (f + floatDelta < 0) conflict("INSUFFICIENT_FLOAT", "Not enough ${req.network} float")
            if (c + cashDelta < 0) conflict("INSUFFICIENT_CASH", "Not enough cash in the drawer")
            jdbc.update("update float_accounts set balance=balance+? where shop_id=? and network=?", floatDelta, shop.id, req.network)
            jdbc.update("update float_accounts set balance=balance+? where shop_id=? and network='cash'", cashDelta, shop.id)
            jdbc.update(
                "insert into float_tx(id,shop_id,user_id,user_name,network,kind,amount,commission,created_at) values(?,?,?,?,?,?,?,?,?)",
                newId(), shop.id, user.id, user.name, req.network, req.kind, req.amount, req.amount * bps / 10000, at
            )
            if (!silent) {
                activity.log(shop.id, user, "float_tx", mapOf("network" to req.network, "kind" to req.kind, "amount" to req.amount, "currency" to shop.currency), device, at)
                val after = f + floatDelta
                val low = jdbc.queryForObject("select low_at from float_accounts where shop_id=? and network=?", Long::class.java, shop.id, req.network)!!
                if (low > 0 && f >= low && after < low) activity.log(shop.id, null, "low_float", mapOf("network" to req.network), device, at)
            }
        }
    }

    fun adjust(shop: Shop, user: AuthUser, req: FloatAdjustReq, device: String) {
        requireAgentShop(shop)
        val region = Regions.get(shop.country)
        if (req.network != "cash" && region.networks.none { it.id == req.network }) bad("INVALID_NETWORK", "Unknown network")
        if (req.delta == 0L) bad("INVALID_AMOUNT", "Enter an amount")
        tx.execute { _ ->
            if (balance(shop.id, req.network) + req.delta < 0) conflict("INSUFFICIENT_FLOAT", "Balance cannot go below zero")
            jdbc.update("update float_accounts set balance=balance+? where shop_id=? and network=?", req.delta, shop.id, req.network)
            activity.log(shop.id, user, "float_adjust", mapOf("network" to req.network, "delta" to req.delta, "currency" to shop.currency), device)
        }
    }

    private fun balance(shopId: String, network: String): Long =
        jdbc.queryForObject("select balance from float_accounts where shop_id=? and network=? for update", Long::class.java, shopId, network)
            ?: bad("INVALID_NETWORK", "Unknown network")
}

@RestController
@RequestMapping("/api/shops/{shopId}/float")
class FloatController(val access: Access, val float: FloatService) {
    @GetMapping
    fun overview(@PathVariable shopId: String, @RequestAttribute("user") user: AuthUser): Map<String, Any?> {
        val (shop, _) = access.member(shopId, user)
        return float.overview(shop)
    }

    @PostMapping("/tx")
    @ResponseStatus(HttpStatus.CREATED)
    fun tx(
        @PathVariable shopId: String, @RequestAttribute("user") user: AuthUser, @RequestBody req: FloatTxReq,
        @RequestHeader("X-Device", defaultValue = "Web") device: String
    ): Map<String, Any?> {
        val (shop, _) = access.member(shopId, user)
        float.transact(shop, user, req, device)
        return float.overview(shop)
    }

    @PostMapping("/adjust")
    fun adjust(
        @PathVariable shopId: String, @RequestAttribute("user") user: AuthUser, @RequestBody req: FloatAdjustReq,
        @RequestHeader("X-Device", defaultValue = "Web") device: String
    ): Map<String, Any?> {
        val (shop, _) = access.need(shopId, user, "owner", "manager")
        float.adjust(shop, user, req, device)
        return float.overview(shop)
    }
}
