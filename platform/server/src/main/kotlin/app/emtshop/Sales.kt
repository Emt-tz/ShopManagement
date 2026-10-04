package app.emtshop

import org.springframework.dao.DuplicateKeyException
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
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.ResponseStatus
import org.springframework.web.bind.annotation.RestController

data class SaleLineReq(val productId: String = "", val qty: Int = 0, val serial: String? = null)
data class SaleReq(
    val lines: List<SaleLineReq> = emptyList(), val tender: String = "cash", val tenderRef: String? = null,
    val idempotencyKey: String = "", val cashReceived: Long? = null
)

@Service
class SalesService(
    val jdbc: JdbcTemplate, val tx: TransactionTemplate, val products: ProductService,
    val activity: ActivityService, val access: Access
) {
    fun record(shop: Shop, user: AuthUser, req: SaleReq, device: String, at: Long = now(), silent: Boolean = false): Map<String, Any?> {
        val region = Regions.get(shop.country)
        if (req.tender !in region.tenders) bad("INVALID_TENDER", "Payment method not available in this region")
        if (req.lines.isEmpty()) bad("EMPTY_SALE", "Add at least one item")
        if (req.idempotencyKey.isBlank()) bad("MISSING_KEY", "idempotencyKey is required")
        findByKey(shop.id, req.idempotencyKey)?.let { return it + ("duplicate" to true) }
        val saleId = try {
            tx.execute { _ -> insertSale(shop, user, req, device, at, silent, region) }!!
        } catch (e: DuplicateKeyException) {
            return findByKey(shop.id, req.idempotencyKey)!! + ("duplicate" to true)
        }
        products.evict(shop.id)
        val view = view(saleId)
        val change = if (req.tender == "cash" && req.cashReceived != null) req.cashReceived - (view["total"] as Long) else null
        return if (change != null) view + ("change" to change) else view
    }

    private fun insertSale(shop: Shop, user: AuthUser, req: SaleReq, device: String, at: Long, silent: Boolean, region: Region): String {
        // Serialise sales per shop so receipt numbers stay gapless and stock checks are exact.
        jdbc.queryForObject("select id from shops where id=? for update", String::class.java, shop.id)
        data class Row(val id: String, val name: String, val price: Long, val stock: Int, val lowAt: Int)
        val used = HashMap<String, Int>()
        val rows = HashMap<String, Row>()
        var total = 0L
        var items = 0
        for (l in req.lines) {
            if (l.qty <= 0) bad("INVALID_QTY", "Quantity must be at least 1")
            val row = rows.getOrPut(l.productId) {
                jdbc.query(
                    "select id,name,price,stock,low_at from products where id=? and shop_id=? and active=true for update",
                    RowMapper { rs, _ -> Row(rs.getString(1), rs.getString(2), rs.getLong(3), rs.getInt(4), rs.getInt(5)) }, l.productId, shop.id
                ).firstOrNull() ?: notFound("PRODUCT_NOT_FOUND", "Product not found in this shop")
            }
            val qty = (used[l.productId] ?: 0) + l.qty
            used[l.productId] = qty
            if (!silent && row.stock < qty) conflict("OUT_OF_STOCK", "Only ${row.stock} of ${row.name} left")
            total += row.price * l.qty
            items += l.qty
        }
        if (req.tender == "cash" && req.cashReceived != null && req.cashReceived < total) bad("CASH_SHORT", "Cash received is less than the total")
        val bps = region.taxBps.toLong()
        val vat = if (bps > 0) (total * bps + (10000 + bps) / 2) / (10000 + bps) else 0L
        val number = jdbc.queryForObject("select coalesce(max(number),0)+1 from sales where shop_id=?", Int::class.java, shop.id)!!
        val saleId = newId()
        jdbc.update(
            "insert into sales(id,shop_id,number,user_id,tender,tender_ref,total,vat,currency,status,idem_key,created_at) values(?,?,?,?,?,?,?,?,?,?,?,?)",
            saleId, shop.id, number, user.id, req.tender, req.tenderRef, total, vat, shop.currency, "completed", req.idempotencyKey, at
        )
        var serial: String? = null
        for (l in req.lines) {
            val r = rows[l.productId]!!
            jdbc.update(
                "insert into sale_lines(id,sale_id,product_id,name,qty,unit_price,serial) values(?,?,?,?,?,?,?)",
                newId(), saleId, r.id, r.name, l.qty, r.price, l.serial?.trim()?.ifBlank { null }
            )
            if (serial == null) serial = l.serial?.trim()?.ifBlank { null }
            if (!silent) jdbc.update("update products set stock=stock-?,updated_at=? where id=?", l.qty, now(), r.id)
        }
        if (!silent) {
            val first = rows[req.lines.first().productId]!!
            activity.log(
                shop.id, user, "sale",
                mapOf("number" to number, "total" to total, "items" to items, "tender" to req.tender, "first" to first.name, "serial" to serial, "currency" to shop.currency),
                device, at
            )
            for ((pid, qty) in used) {
                val r = rows[pid]!!
                val after = r.stock - qty
                if (r.stock > r.lowAt && after <= r.lowAt) activity.log(shop.id, null, "low_stock", mapOf("name" to r.name, "stock" to after), device, at)
            }
        }
        return saleId
    }

    private fun findByKey(shopId: String, key: String): Map<String, Any?>? =
        jdbc.queryForList("select id from sales where shop_id=? and idem_key=?", String::class.java, shopId, key).firstOrNull()?.let { view(it) }

    fun view(saleId: String): Map<String, Any?> {
        val head = jdbc.query(
            "select s.id,s.shop_id,s.number,s.tender,s.tender_ref,s.total,s.vat,s.currency,s.status,s.created_at,u.name from sales s join users u on u.id=s.user_id where s.id=?",
            RowMapper { rs, _ ->
                mutableMapOf<String, Any?>(
                    "id" to rs.getString(1), "shopId" to rs.getString(2), "number" to rs.getInt(3), "tender" to rs.getString(4), "tenderRef" to rs.getString(5),
                    "total" to rs.getLong(6), "vat" to rs.getLong(7), "currency" to rs.getString(8), "status" to rs.getString(9), "at" to rs.getLong(10), "cashier" to rs.getString(11)
                )
            }, saleId
        ).firstOrNull() ?: notFound("SALE_NOT_FOUND", "Sale not found")
        head["lines"] = jdbc.query(
            "select name,qty,unit_price,serial from sale_lines where sale_id=? order by name",
            RowMapper { rs, _ -> mapOf("name" to rs.getString(1), "qty" to rs.getInt(2), "unitPrice" to rs.getLong(3), "serial" to rs.getString(4)) }, saleId
        )
        return head
    }

    fun list(shopId: String, limit: Int): List<Map<String, Any?>> =
        jdbc.queryForList("select id from sales where shop_id=? order by created_at desc limit ?", String::class.java, shopId, limit).map { view(it) }

    fun void(saleId: String, user: AuthUser, device: String): Map<String, Any?> {
        val sale = view(saleId)
        val shopId = sale["shopId"] as String
        access.need(shopId, user, "owner", "manager")
        tx.execute { _ ->
            jdbc.queryForObject("select id from shops where id=? for update", String::class.java, shopId)
            val status = jdbc.queryForObject("select status from sales where id=?", String::class.java, saleId)
            if (status != "completed") conflict("ALREADY_VOID", "This sale was already voided")
            jdbc.update("update sales set status='void' where id=?", saleId)
            jdbc.query("select product_id,qty from sale_lines where sale_id=?", RowMapper { rs, _ -> rs.getString(1) to rs.getInt(2) }, saleId).forEach { (pid, qty) ->
                jdbc.update("update products set stock=stock+?,updated_at=? where id=?", qty, now(), pid)
            }
            activity.log(shopId, user, "void", mapOf("number" to sale["number"], "total" to sale["total"], "currency" to sale["currency"]), device)
        }
        products.evict(shopId)
        return view(saleId)
    }
}

@RestController
@RequestMapping("/api")
class SalesController(val access: Access, val billing: BillingService, val sales: SalesService) {
    @PostMapping("/shops/{shopId}/sales")
    @ResponseStatus(HttpStatus.CREATED)
    fun create(
        @PathVariable shopId: String, @RequestAttribute("user") user: AuthUser, @RequestBody req: SaleReq,
        @RequestHeader("X-Device", defaultValue = "Web") device: String
    ): Map<String, Any?> {
        val (shop, _) = access.member(shopId, user)
        billing.requireActive(shop.ownerId)
        return mapOf("sale" to sales.record(shop, user, req, device))
    }

    @GetMapping("/shops/{shopId}/sales")
    fun list(@PathVariable shopId: String, @RequestAttribute("user") user: AuthUser, @RequestParam(defaultValue = "30") limit: Int): Map<String, Any?> {
        access.member(shopId, user)
        return mapOf("sales" to sales.list(shopId, limit.coerceIn(1, 200)))
    }

    @GetMapping("/sales/{id}")
    fun get(@PathVariable id: String, @RequestAttribute("user") user: AuthUser): Map<String, Any?> {
        val s = sales.view(id)
        access.member(s["shopId"] as String, user)
        return mapOf("sale" to s)
    }

    @PostMapping("/sales/{id}/void")
    fun void(@PathVariable id: String, @RequestAttribute("user") user: AuthUser, @RequestHeader("X-Device", defaultValue = "Web") device: String): Map<String, Any?> =
        mapOf("sale" to sales.void(id, user, device))
}
