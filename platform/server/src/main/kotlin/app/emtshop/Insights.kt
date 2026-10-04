package app.emtshop

import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
import org.springframework.stereotype.Service
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestAttribute
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController

private const val HOUR_MS = 3_600_000L

private data class Span(val start: Long, val bucketMs: Long, val buckets: Int) {
    val length get() = bucketMs * buckets
    val end get() = start + length
}

@Service
class InsightService(val jdbc: JdbcTemplate, val access: Access, val hub: Hub, val billing: BillingService) {
    private fun span(kind: String, offsetMin: Int, nowMs: Long): Span {
        val off = offsetMin * 60_000L
        val dayStart = Math.floorDiv(nowMs + off, DAY_MS) * DAY_MS - off
        return when (kind) {
            "day" -> Span(dayStart, HOUR_MS, 24)
            "week" -> Span(dayStart - 6 * DAY_MS, DAY_MS, 7)
            "month" -> Span(dayStart - 29 * DAY_MS, DAY_MS, 30)
            "year" -> Span(dayStart - 359 * DAY_MS, 30 * DAY_MS, 12)
            else -> bad("INVALID_RANGE", "Range must be day, week, month or year")
        }
    }

    fun compute(shop: Shop, kind: String, nowMs: Long = now()): Map<String, Any?> {
        val region = Regions.get(shop.country)
        val cur = span(kind, region.utcOffsetMinutes, nowMs)
        val prev = Span(cur.start - cur.length, cur.bucketMs, cur.buckets)
        data class Row(val at: Long, val total: Long, val tender: String)
        val rows = jdbc.query(
            "select created_at,total,tender from sales where shop_id=? and status='completed' and created_at>=? and created_at<?",
            RowMapper { rs, _ -> Row(rs.getLong(1), rs.getLong(2), rs.getString(3)) }, shop.id, prev.start, cur.end
        )
        val now = rows.filter { it.at >= cur.start }
        val before = rows.filter { it.at < cur.start }
        val series = (0 until cur.buckets).map { i ->
            val from = cur.start + i * cur.bucketMs
            mapOf("t" to from, "value" to now.filter { it.at >= from && it.at < from + cur.bucketMs }.sumOf { it.total })
        }
        val revenue = now.sumOf { it.total }
        val prevRevenue = before.sumOf { it.total }
        val count = now.size
        val mix = now.groupBy { it.tender }.map { (t, list) -> mapOf("tender" to t, "amount" to list.sumOf { it.total }, "count" to list.size) }.sortedByDescending { it["amount"] as Long }
        val off = region.utcOffsetMinutes * 60_000L
        val busiest = now.groupBy { Math.floorMod((it.at + off) / HOUR_MS, 24L).toInt() }.maxByOrNull { it.value.size }?.key
        val top = jdbc.query(
            "select l.name,sum(l.qty),sum(l.qty*l.unit_price) from sale_lines l join sales s on s.id=l.sale_id " +
                "where s.shop_id=? and s.status='completed' and s.created_at>=? and s.created_at<? group by l.name order by 3 desc limit 5",
            RowMapper { rs, _ -> mapOf("name" to rs.getString(1), "units" to rs.getLong(2), "revenue" to rs.getLong(3)) }, shop.id, cur.start, cur.end
        )
        val refunds = jdbc.queryForObject(
            "select coalesce(sum(total),0) from sales where shop_id=? and status='void' and created_at>=? and created_at<?",
            Long::class.java, shop.id, cur.start, cur.end
        )!!
        return mapOf(
            "range" to kind, "currency" to shop.currency, "start" to cur.start, "end" to cur.end, "bucketMs" to cur.bucketMs,
            "revenue" to revenue, "previousRevenue" to prevRevenue, "count" to count, "previousCount" to before.size,
            "average" to if (count > 0) revenue / count else 0L, "refunds" to refunds,
            "series" to series, "topProducts" to top, "paymentMix" to mix, "busiestHour" to busiest
        )
    }

    fun overview(user: AuthUser): Map<String, Any?> {
        val shops = access.shopsOf(user.id)
        val cards = shops.map { (s, role) ->
            val day = compute(s, "day")
            val week = compute(s, "week")
            val low = jdbc.queryForObject("select count(*) from products where shop_id=? and active=true and stock<=low_at", Long::class.java, s.id)!!
            val members = access.memberIds(s.id)
            val online = members.count { hub.isOnline(it) }
            val lowFloat = if (s.type == "mobile_money")
                jdbc.queryForList("select network from float_accounts where shop_id=? and low_at>0 and balance<low_at", String::class.java, s.id) else emptyList()
            val floatTotal = if (s.type == "mobile_money")
                jdbc.queryForObject("select coalesce(sum(balance),0) from float_accounts where shop_id=?", Long::class.java, s.id) else null
            mapOf(
                "id" to s.id, "name" to s.name, "type" to s.type, "currency" to s.currency, "role" to role,
                "todayRevenue" to day["revenue"], "todayCount" to day["count"], "yesterdayRevenue" to day["previousRevenue"],
                "spark" to (week["series"] as List<*>).map { (it as Map<*, *>)["value"] },
                "lowStock" to low, "online" to online, "lowFloat" to lowFloat, "floatTotal" to floatTotal
            )
        }
        val actions = recommendedActions(user, shops, cards)
        val totals = cards.groupBy { it["currency"] as String }.map { (cur, list) ->
            mapOf("currency" to cur, "today" to list.sumOf { it["todayRevenue"] as Long }, "yesterday" to list.sumOf { it["yesterdayRevenue"] as Long })
        }
        return mapOf("shops" to cards, "totals" to totals, "actions" to actions)
    }

    /** What the owner should do next, most urgent first. The client turns each kind into translated copy and a link. */
    private fun recommendedActions(user: AuthUser, shops: List<Pair<Shop, String>>, cards: List<Map<String, Any?>>): List<Map<String, Any?>> {
        val out = ArrayList<Map<String, Any?>>()
        for (c in cards) {
            val low = c["lowFloat"] as List<*>
            if (low.isNotEmpty()) out.add(mapOf("kind" to "topup", "shopId" to c["id"], "shopName" to c["name"], "networks" to low))
        }
        for (c in cards) {
            val n = c["lowStock"] as Long
            if (n > 0) {
                val items = jdbc.queryForList("select name from products where shop_id=? and active=true and stock<=low_at order by stock,name limit 3", String::class.java, c["id"])
                out.add(mapOf("kind" to "restock", "shopId" to c["id"], "shopName" to c["name"], "count" to n, "items" to items))
            }
        }
        val ent = billing.current(user.id)
        if (ent != null) {
            val max = ent.limits.products
            if (max != null) for ((s, role) in shops) if (role == "owner") {
                val used = jdbc.queryForObject("select count(*) from products where shop_id=? and active=true", Long::class.java, s.id)!!
                if (used * 10 >= max * 8L) out.add(mapOf("kind" to "limit", "shopId" to s.id, "shopName" to s.name, "used" to used, "max" to max))
            }
            if (ent.status == "trialing") out.add(mapOf("kind" to "trial", "days" to ((ent.renewsAt - now() + DAY_MS - 1) / DAY_MS)))
        }
        return out
    }
}

@RestController
@RequestMapping("/api")
class InsightController(val access: Access, val insights: InsightService) {
    @GetMapping("/shops/{shopId}/insights")
    fun shopInsights(@PathVariable shopId: String, @RequestAttribute("user") user: AuthUser, @RequestParam(defaultValue = "week") range: String): Map<String, Any?> {
        val (shop, _) = access.member(shopId, user)
        return insights.compute(shop, range)
    }

    @GetMapping("/overview")
    fun overview(@RequestAttribute("user") user: AuthUser): Map<String, Any?> = insights.overview(user)
}
