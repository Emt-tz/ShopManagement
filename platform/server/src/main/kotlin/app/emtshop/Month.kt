package app.emtshop

import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
import org.springframework.stereotype.Service
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestAttribute
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import java.util.Random

/**
 * A full month of trading for the showcase: a stationery shop with a standard catalogue and about 1000 customers,
 * and a mobile money agent counter with a month of float transactions. Deterministic, so every run tells the same story.
 */
@Service
class MonthDemoService(
    val jdbc: JdbcTemplate, val products: ProductService, val sales: SalesService, val float: FloatService, val activity: ActivityService
) {
    private data class Item(val name: String, val category: String, val tzs: Long, val pop: Int, val maxQty: Int = 3)

    private val stationery = listOf(
        Item("Exercise book 32 pages", "Books", 600, 30, 12), Item("Exercise book 64 pages", "Books", 1000, 28, 12), Item("Exercise book 96 pages", "Books", 1500, 16, 8),
        Item("Exercise book 200 pages", "Books", 2500, 10, 6), Item("Notebook A4 hardcover", "Books", 3500, 12, 4), Item("Notebook A5 spiral", "Books", 2200, 12, 4),
        Item("Graph book", "Books", 1800, 5, 4), Item("Drawing book A3", "Books", 3000, 4, 3), Item("Diary 2026", "Books", 7000, 3, 2),
        Item("Ballpoint pen blue", "Writing", 400, 40, 10), Item("Ballpoint pen black", "Writing", 400, 26, 10), Item("Ballpoint pen red", "Writing", 400, 14, 6),
        Item("Pens box (50)", "Writing", 15000, 4, 2), Item("Gel pen", "Writing", 1000, 8, 5), Item("HB pencil", "Writing", 300, 36, 12), Item("Pencils box (12)", "Writing", 2800, 10, 4),
        Item("Colour pencils (12)", "Writing", 4500, 8, 3), Item("Crayons (24)", "Writing", 3800, 6, 3), Item("Permanent marker", "Writing", 1800, 8, 4),
        Item("Whiteboard marker", "Writing", 1500, 8, 6), Item("Highlighter", "Writing", 1600, 8, 4), Item("Eraser", "Tools", 300, 24, 6), Item("Sharpener", "Tools", 300, 20, 6),
        Item("Ruler 30 cm", "Tools", 700, 14, 3), Item("Geometry set", "Tools", 6500, 6, 2), Item("Scissors", "Tools", 2500, 6, 2), Item("Glue stick", "Tools", 1200, 14, 4),
        Item("Liquid glue", "Tools", 1000, 8, 3), Item("Correction fluid", "Tools", 1500, 10, 3), Item("Sticky tape", "Tools", 1000, 10, 4), Item("Masking tape", "Tools", 1800, 4, 3),
        Item("Stapler", "Office", 5500, 5, 2), Item("Staples box", "Office", 1200, 7, 4), Item("Paper clips box", "Office", 1000, 8, 4), Item("Punch", "Office", 7500, 3, 1),
        Item("Calculator basic", "Office", 12000, 6, 2), Item("Calculator scientific", "Office", 28000, 4, 2), Item("A4 paper ream", "Paper", 14000, 18, 5),
        Item("A4 paper single sheet", "Paper", 100, 24, 30), Item("A3 paper ream", "Paper", 28000, 2, 1), Item("Manila paper", "Paper", 500, 10, 8),
        Item("Foolscap sheets (10)", "Paper", 1000, 8, 3), Item("Sticky notes", "Paper", 1800, 8, 3), Item("Flip chart pad", "Paper", 9000, 2, 1),
        Item("Plain envelope", "Paper", 200, 18, 20), Item("Brown envelope A4", "Paper", 300, 18, 20), Item("Box file", "Filing", 6500, 6, 2), Item("Lever arch file", "Filing", 5500, 6, 2),
        Item("Plastic folder", "Filing", 800, 20, 8), Item("Document wallet", "Filing", 1200, 12, 5), Item("Clipboard", "Filing", 3500, 3, 1),
        Item("School bag", "School", 28000, 3, 1), Item("Lunch box", "School", 9000, 3, 1), Item("Water bottle", "School", 7000, 4, 1), Item("Pencil case", "School", 4000, 8, 2),
        Item("Printing per page", "Services", 200, 30, 25), Item("Photocopy per page", "Services", 100, 40, 40), Item("Lamination A4", "Services", 1500, 10, 4),
        Item("Spiral binding", "Services", 3000, 8, 2), Item("Passport photo (4)", "Services", 5000, 6, 1)
    )

    private val devices = listOf("iPhone 15", "iPhone 14", "Android Pixel", "Mac app", "Web")

    private fun staff(shopId: String, owner: AuthUser): List<AuthUser> {
        val rows = jdbc.query(
            "select u.id,u.name,u.email from members m join users u on u.id=m.user_id where m.shop_id=?",
            RowMapper { rs, _ -> AuthUser(rs.getString(1), rs.getString(2), rs.getString(3)) }, shopId
        )
        return rows.ifEmpty { listOf(owner) }
    }

    private fun dayStart(region: Region): Long {
        val off = region.utcOffsetMinutes * 60_000L
        return Math.floorDiv(now() + off, DAY_MS) * DAY_MS - off
    }

    /** Relative footfall for a day of the month: busy at term start and month end, quiet on Sundays. */
    private fun weight(dayIndex: Int, weekday: Int): Double {
        val base = when (weekday) { 6 -> 0.35; 5 -> 0.85; else -> 1.0 }
        val surge = if (dayIndex in 0..4) 1.7 else if (dayIndex in 14..16) 1.25 else if (dayIndex >= 25) 1.3 else 1.0
        return base * surge
    }

    fun stationery(shop: Shop, owner: AuthUser, customers: Int = 1000): Map<String, Any?> {
        val region = Regions.get(shop.country)
        val unit = pow10(region.decimals)
        val rnd = Random(2026)
        val scale = if (region.currency == "TZS") 1.0 else when (region.currency) { "KES" -> 0.05; "INR" -> 0.033; "BRL" -> 0.002; else -> 0.0004 }
        jdbc.update("delete from sale_lines where sale_id in (select id from sales where shop_id=?)", shop.id)
        jdbc.update("delete from sales where shop_id=?", shop.id)
        jdbc.update("delete from activity where shop_id=?", shop.id)
        jdbc.update("delete from products where shop_id=?", shop.id)
        val ids = ArrayList<String>()
        for (it in stationery) {
            val id = newId(); ids.add(id)
            val price = Math.round(it.tzs * scale * unit).coerceAtLeast(unit)
            val stock = if (it.category == "Services") 9999 else 30 + rnd.nextInt(60)
            jdbc.update(
                "insert into products(id,shop_id,name,category,price,stock,barcode,low_at,active,updated_at) values(?,?,?,?,?,?,?,?,true,?)",
                id, shop.id, it.name, it.category, price, stock, null, 15, now()
            )
        }
        products.evict(shop.id)
        val team = staff(shop.id, owner)
        val tenders = region.tenders.filter { it != "credit" }
        val local = tenders.firstOrNull { it != "cash" && it != "card" } ?: "card"
        val nets = region.networks.map { it.id }
        val today = dayStart(region)
        val days = 30
        val weights = (0 until days).map { d ->
            val at = today - (days - 1 - d) * DAY_MS
            val wd = (Math.floorMod(Math.floorDiv(at + region.utcOffsetMinutes * 60_000L, DAY_MS) + 4, 7L)).toInt() // 0 = Monday
            weight(d, wd)
        }
        val sum = weights.sum()
        val perDay = weights.map { Math.round(it / sum * customers).toInt() }.toMutableList()
        perDay[days - 1] += customers - perDay.sum()
        val popTotal = stationery.sumOf { it.pop }
        fun pick(): Int { var r = rnd.nextInt(popTotal); for ((i, it) in stationery.withIndex()) { r -= it.pop; if (r < 0) return i }; return 0 }
        var key = 0; var made = 0; var voids = 0; var restocks = 0; var revenue = 0L
        val voidable = ArrayList<String>()
        for (d in 0 until days) {
            val start = today - (days - 1 - d) * DAY_MS
            // Morning restock of anything running low, logged under the manager.
            val lowList = jdbc.query(
                "select id,name,stock from products where shop_id=? and stock<25",
                RowMapper { rs, _ -> Triple(rs.getString(1), rs.getString(2), rs.getInt(3)) }, shop.id
            )
            for ((pid, name, stock) in lowList) {
                val to = stock + 60 + rnd.nextInt(80)
                jdbc.update("update products set stock=?,updated_at=? where id=?", to, start + 7 * 3_600_000L, pid)
                activity.log(shop.id, team.last(), "stock_adjust", mapOf("name" to name, "from" to stock, "to" to to), "Mac app", start + 7 * 3_600_000L)
                restocks++
            }
            products.evict(shop.id)
            val times = (0 until perDay[d]).map {
                val hour = when (rnd.nextInt(100)) { in 0..9 -> 7 + rnd.nextInt(2); in 10..39 -> 12 + rnd.nextInt(2); in 40..59 -> 15 + rnd.nextInt(3); else -> 8 + rnd.nextInt(10) }
                start + hour * 3_600_000L + rnd.nextInt(3_600_000)
            }.sorted()
            for (at in times) {
                if (at > now()) continue
                val n = 1 + (if (rnd.nextInt(100) < 45) rnd.nextInt(3) else 0) + (if (rnd.nextInt(100) < 10) rnd.nextInt(3) else 0)
                val seen = HashSet<Int>()
                val lines = (0 until n).mapNotNull {
                    val i = pick(); if (!seen.add(i)) null else SaleLineReq(ids[i], 1 + rnd.nextInt(stationery[i].maxQty))
                }
                val roll = rnd.nextInt(100)
                val tender = if (roll < 46) local else if (roll < 86) "cash" else "card"
                val ref = if (tender == local && nets.isNotEmpty()) nets[rnd.nextInt(nets.size)] else null
                val who = team[rnd.nextInt(team.size)]
                val device = devices[(team.indexOf(who) + rnd.nextInt(2)) % devices.size]
                val sale = runCatching { sales.record(shop, who, SaleReq(lines, tender, ref, "month-${shop.id}-${key++}"), device, at, true) }.getOrNull() ?: continue
                made++; revenue += sale["total"] as Long
                // Seed sales are silent, so move stock and write the live-feed entry here to keep the history truthful.
                for (l in lines) jdbc.update("update products set stock=greatest(stock-?,0) where id=?", l.qty, l.productId)
                activity.log(
                    shop.id, who, "sale",
                    mapOf("number" to sale["number"], "total" to sale["total"], "items" to lines.sumOf { it.qty }, "tender" to tender, "first" to stationery[ids.indexOf(lines.first().productId)].name, "serial" to null, "currency" to shop.currency),
                    device, at
                )
                if (rnd.nextInt(100) < 2) voidable.add(sale["id"] as String)
            }
        }
        for (sid in voidable) { if (runCatching { sales.void(sid, owner, "Mac app") }.isSuccess) voids++ }
        products.evict(shop.id)
        return mapOf("ok" to true, "customers" to made, "voids" to voids, "restocks" to restocks, "revenue" to revenue, "days" to days)
    }

    fun agent(shop: Shop, owner: AuthUser, perDayBase: Int = 34): Map<String, Any?> {
        val region = Regions.get(shop.country)
        val unit = pow10(region.decimals)
        val rnd = Random(77)
        jdbc.update("delete from float_tx where shop_id=?", shop.id)
        jdbc.update("delete from activity where shop_id=?", shop.id)
        val nets = region.networks.map { it.id }
        val team = staff(shop.id, owner)
        val today = dayStart(region)
        val days = 30
        val factor = if (region.currency == "TZS") 1.0 else 0.05
        var n = 0
        for (d in 0 until days) {
            val start = today - (days - 1 - d) * DAY_MS
            // Morning float rebalance: top each wallet up to a working level, recorded as an adjustment.
            for (net in nets + "cash") {
                val bal = jdbc.queryForObject("select balance from float_accounts where shop_id=? and network=?", Long::class.java, shop.id, net) ?: 0L
                val want = (if (net == "cash") 1_500_000L else 1_200_000L) * unit * factor.toLong().coerceAtLeast(1)
                if (bal < want / 2) runCatching { float.adjust(shop, owner, FloatAdjustReq(net, want - bal), "Mac app") }
            }
            val count = perDayBase - 8 + rnd.nextInt(16)
            val times = (0 until count).map { start + (7 + rnd.nextInt(13)) * 3_600_000L + rnd.nextInt(3_600_000) }.sorted()
            for (at in times) {
                if (at > now()) continue
                val kind = when (rnd.nextInt(100)) { in 0..39 -> "cash_in"; in 40..84 -> "cash_out"; else -> "airtime" }
                val amount = (listOf(2_000L, 5_000L, 10_000L, 20_000L, 30_000L, 50_000L, 100_000L)[rnd.nextInt(7)] * factor).toLong().coerceAtLeast(1) * unit
                val who = team[rnd.nextInt(team.size)]
                if (runCatching { float.transact(shop, who, FloatTxReq(nets[rnd.nextInt(nets.size)], kind, amount), devices[rnd.nextInt(devices.size)], at, true) }.isSuccess) n++
            }
        }
        return mapOf("ok" to true, "transactions" to n, "days" to days)
    }
}

@RestController
@RequestMapping("/api/shops/{shopId}")
class MonthDemoController(val access: Access, val month: MonthDemoService) {
    /** Replaces the shop's data with a month of showcase trading. Owner only; intended for demos and sandbox accounts. */
    @PostMapping("/demo-month")
    fun run(@PathVariable shopId: String, @RequestAttribute("user") user: AuthUser): Map<String, Any?> {
        val (shop, _) = access.need(shopId, user, "owner")
        return if (shop.type == "mobile_money") month.agent(shop, user) else month.stationery(shop, user)
    }
}
