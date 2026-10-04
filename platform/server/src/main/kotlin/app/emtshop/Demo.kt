package app.emtshop

import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Service
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestAttribute
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import java.util.Random

/** Sample catalogue and a week of sales so a new shop is not empty. Prices are TZS major units scaled to the shop's currency. */
@Service
class DemoService(
    val jdbc: JdbcTemplate, val products: ProductService, val sales: SalesService, val float: FloatService
) {
    private data class Sample(val name: String, val category: String, val tzs: Long, val stock: Int)

    private val catalogue = mapOf(
        "retail" to listOf(
            Sample("Rice 5 kg", "Food", 18000, 24), Sample("Cooking oil 1 L", "Food", 7500, 12), Sample("Soap bar", "Household", 2500, 60),
            Sample("Sugar 1 kg", "Food", 3200, 31), Sample("Bread", "Food", 1800, 8), Sample("Bottled water", "Drinks", 1000, 96),
            Sample("Salt 500 g", "Food", 900, 5), Sample("Notebook A4", "Stationery", 1800, 140), Sample("Ballpoint pens (box)", "Stationery", 6000, 40)
        ),
        "grocery" to listOf(
            Sample("Tomatoes 1 kg", "Produce", 3000, 40), Sample("Milk 1 L", "Dairy", 2800, 30), Sample("Maize flour 2 kg", "Pantry", 4500, 45),
            Sample("Bananas 1 kg", "Produce", 2000, 25), Sample("Soda 500 ml", "Drinks", 1200, 80)
        ),
        "phones" to listOf(
            Sample("iPhone 15 Pro", "Phones", 3200000, 6), Sample("iPhone 14", "Phones", 2300000, 8), Sample("USB-C cable", "Accessories", 25000, 60),
            Sample("Screen protector", "Accessories", 15000, 90), Sample("Screen repair", "Repairs", 120000, 999)
        ),
        "restaurant" to listOf(
            Sample("Chips mayai", "Meals", 5000, 99), Sample("Chicken and rice", "Meals", 9000, 99), Sample("Mandazi", "Snacks", 500, 200), Sample("Fresh juice", "Drinks", 3000, 99)
        )
    )

    private fun scale(currency: String): Double = when (currency) { "TZS" -> 1.0; "KES" -> 0.05; "INR" -> 0.033; "BRL" -> 0.002; else -> 0.0004 }

    fun seed(shop: Shop, owner: AuthUser) {
        val region = Regions.get(shop.country)
        val rnd = Random(42)
        if (shop.type == "mobile_money") {
            val unit = pow10(region.decimals)
            val base = mapOf("cash" to 2_000_000L, "mpesa" to 2_450_000L, "mixx" to 1_980_000L, "airtel" to 1_320_000L, "halopesa" to 700_000L)
            val factor = scale(region.currency).let { if (region.currency == "TZS") 1.0 else it * 20 }
            jdbc.update("update float_accounts set balance=0 where shop_id=?", shop.id)
            for ((net, amt) in base) {
                jdbc.update("update float_accounts set balance=? where shop_id=? and network=?", (amt * factor).toLong() * unit, shop.id, net)
            }
            val nets = region.networks.map { it.id }
            repeat(16) {
                val kind = listOf("cash_in", "cash_out", "cash_out", "airtime")[rnd.nextInt(4)]
                val amount = (listOf(5_000L, 10_000L, 20_000L, 50_000L)[rnd.nextInt(4)] * factor).toLong() * unit
                runCatching {
                    float.transact(shop, owner, FloatTxReq(nets[rnd.nextInt(nets.size)], kind, amount), "Seed", now() - rnd.nextInt(6 * 3600) * 1000L, true)
                }
            }
            return
        }
        val items = catalogue[shop.type] ?: return
        if (products.count(shop.id) == 0L) {
            val unit = pow10(region.decimals)
            for (s in items) {
                val price = Math.round(s.tzs * scale(region.currency) * unit).coerceAtLeast(unit)
                jdbc.update(
                    "insert into products(id,shop_id,name,category,price,stock,barcode,low_at,active,updated_at) values(?,?,?,?,?,?,?,?,true,?)",
                    newId(), shop.id, s.name, s.category, price, s.stock, null, 10, now()
                )
            }
            products.evict(shop.id)
        }
        val list = products.list(shop.id)
        val tenders = region.tenders.filter { it != "credit" }
        val local = tenders.firstOrNull { it != "cash" && it != "card" } ?: "card"
        val off = region.utcOffsetMinutes * 60_000L
        val dayStart = Math.floorDiv(now() + off, DAY_MS) * DAY_MS - off
        var key = 0
        for (d in 6 downTo 0) {
            val count = 12 + rnd.nextInt(14) + if (d == 1) 12 else 0
            repeat(count) {
                val hour = (if (rnd.nextInt(100) < 35) 12 else 8 + rnd.nextInt(12)).toLong()
                val at = dayStart - d * DAY_MS + hour * 3_600_000L + rnd.nextInt(3_600_000)
                if (at > now()) return@repeat
                val lines = (0 until 1 + rnd.nextInt(3)).map { SaleLineReq(list[rnd.nextInt(list.size)].id, 1 + rnd.nextInt(3)) }
                val roll = rnd.nextInt(100)
                val tender = if (roll < 48) local else if (roll < 80) "cash" else "card"
                runCatching {
                    sales.record(shop, owner, SaleReq(lines, tender, null, "seed-${shop.id}-${key++}"), "Seed", at, true)
                }
            }
        }
    }
}

@RestController
@RequestMapping("/api/shops/{shopId}")
class DemoController(val access: Access, val demo: DemoService) {
    @PostMapping("/demo-data")
    fun seed(@PathVariable shopId: String, @RequestAttribute("user") user: AuthUser): Map<String, Any?> {
        val (shop, _) = access.need(shopId, user, "owner")
        demo.seed(shop, user)
        return mapOf("ok" to true)
    }
}
