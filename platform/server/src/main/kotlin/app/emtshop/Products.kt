package app.emtshop

import org.springframework.cache.annotation.CacheEvict
import org.springframework.cache.annotation.Cacheable
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
import org.springframework.stereotype.Service
import org.springframework.web.bind.annotation.DeleteMapping
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.PutMapping
import org.springframework.web.bind.annotation.RequestAttribute
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestHeader
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.ResponseStatus
import org.springframework.web.bind.annotation.RestController

data class Product(
    val id: String, val shopId: String, val name: String, val category: String, val price: Long,
    val stock: Int, val barcode: String?, val lowAt: Int
)

data class ProductReq(val name: String = "", val category: String = "", val price: Long = 0, val stock: Int = 0, val barcode: String? = null)
data class AvailabilityReq(val shopId: String = "", val available: Boolean = false)

@Service
class ProductService(val jdbc: JdbcTemplate) {
    private val mapper = RowMapper<Product> { rs, _ ->
        Product(rs.getString(1), rs.getString(2), rs.getString(3), rs.getString(4), rs.getLong(5), rs.getInt(6), rs.getString(7), rs.getInt(8))
    }
    private val cols = "id,shop_id,name,category,price,stock,barcode,low_at"

    /** Hot read path: the product list is cached per shop and evicted on every write. */
    @Cacheable("products", key = "#shopId")
    fun list(shopId: String): List<Product> =
        jdbc.query("select $cols from products where shop_id=? and active=true order by name", mapper, shopId)

    @CacheEvict("products", key = "#shopId")
    fun evict(shopId: String) {}

    fun get(id: String): Product =
        jdbc.query("select $cols from products where id=? and active=true", mapper, id).firstOrNull() ?: notFound("PRODUCT_NOT_FOUND", "Product not found")

    fun count(shopId: String): Long = jdbc.queryForObject("select count(*) from products where shop_id=? and active=true", Long::class.java, shopId)!!
}

@RestController
@RequestMapping("/api")
class ProductController(
    val jdbc: JdbcTemplate, val access: Access, val products: ProductService, val billing: BillingService, val activity: ActivityService
) {
    @GetMapping("/shops/{shopId}/products")
    fun list(@PathVariable shopId: String, @RequestAttribute("user") user: AuthUser): Map<String, Any?> {
        access.member(shopId, user)
        return mapOf("products" to products.list(shopId))
    }

    @PostMapping("/shops/{shopId}/products")
    @ResponseStatus(HttpStatus.CREATED)
    fun create(
        @PathVariable shopId: String, @RequestAttribute("user") user: AuthUser, @RequestBody req: ProductReq,
        @RequestHeader("X-Device", defaultValue = "Web") device: String
    ): Map<String, Any?> {
        val (shop, _) = access.need(shopId, user, "owner", "manager")
        validate(req)
        val ent = billing.requireActive(shop.ownerId)
        val max = ent.limits.products
        if (max != null && products.count(shopId) >= max) planLimit("PLAN_LIMIT_PRODUCTS", "Your plan includes $max products. Upgrade for unlimited")
        val id = newId()
        jdbc.update(
            "insert into products(id,shop_id,name,category,price,stock,barcode,low_at,active,updated_at) values(?,?,?,?,?,?,?,?,true,?)",
            id, shopId, req.name.trim(), req.category.trim().ifBlank { "General" }, req.price, req.stock, req.barcode?.trim()?.ifBlank { null }, 10, now()
        )
        products.evict(shopId)
        activity.log(shopId, user, "product_added", mapOf("name" to req.name.trim()), device)
        return mapOf("product" to products.get(id))
    }

    @PutMapping("/products/{id}")
    fun update(
        @PathVariable id: String, @RequestAttribute("user") user: AuthUser, @RequestBody req: ProductReq,
        @RequestHeader("X-Device", defaultValue = "Web") device: String
    ): Map<String, Any?> {
        val old = products.get(id)
        access.need(old.shopId, user, "owner", "manager")
        validate(req)
        jdbc.update(
            "update products set name=?,category=?,price=?,stock=?,barcode=?,updated_at=? where id=?",
            req.name.trim(), req.category.trim().ifBlank { "General" }, req.price, req.stock, req.barcode?.trim()?.ifBlank { null }, now(), id
        )
        products.evict(old.shopId)
        if (old.price != req.price) activity.log(old.shopId, user, "price_change", mapOf("name" to req.name.trim(), "from" to old.price, "to" to req.price), device)
        if (old.stock != req.stock) activity.log(old.shopId, user, "stock_adjust", mapOf("name" to req.name.trim(), "from" to old.stock, "to" to req.stock), device)
        return mapOf("product" to products.get(id))
    }

    @DeleteMapping("/products/{id}")
    fun delete(
        @PathVariable id: String, @RequestAttribute("user") user: AuthUser,
        @RequestHeader("X-Device", defaultValue = "Web") device: String
    ): Map<String, Any?> {
        val old = products.get(id)
        access.need(old.shopId, user, "owner", "manager")
        jdbc.update("update products set active=false,updated_at=? where id=?", now(), id)
        products.evict(old.shopId)
        activity.log(old.shopId, user, "product_removed", mapOf("name" to old.name), device)
        return mapOf("ok" to true)
    }

    /** Which of the owner's shops sell this product (matched by name). */
    @GetMapping("/products/{id}/availability")
    fun availability(@PathVariable id: String, @RequestAttribute("user") user: AuthUser): Map<String, Any?> {
        val p = products.get(id)
        access.member(p.shopId, user)
        val shops = access.shopsOf(user.id).filter { it.second == "owner" || it.second == "manager" }
        return mapOf("shops" to shops.map { (s, _) ->
            val copy = products.list(s.id).firstOrNull { it.name.equals(p.name, ignoreCase = true) }
            mapOf("shopId" to s.id, "shopName" to s.name, "available" to (copy != null), "price" to copy?.price, "stock" to copy?.stock, "productId" to copy?.id, "currency" to s.currency)
        })
    }

    @PutMapping("/products/{id}/availability")
    fun setAvailability(
        @PathVariable id: String, @RequestAttribute("user") user: AuthUser, @RequestBody req: AvailabilityReq,
        @RequestHeader("X-Device", defaultValue = "Web") device: String
    ): Map<String, Any?> {
        val p = products.get(id)
        access.need(p.shopId, user, "owner", "manager")
        val (target, _) = access.need(req.shopId, user, "owner", "manager")
        val sourceShop = access.shop(p.shopId)
        if (target.currency != sourceShop.currency) bad("CURRENCY_MISMATCH", "Shops use different currencies. Add the product there directly")
        val existing = products.list(target.id).firstOrNull { it.name.equals(p.name, ignoreCase = true) }
        if (req.available && existing == null) {
            val ent = billing.requireActive(target.ownerId)
            val max = ent.limits.products
            if (max != null && products.count(target.id) >= max) planLimit("PLAN_LIMIT_PRODUCTS", "Your plan includes $max products")
            jdbc.update(
                "insert into products(id,shop_id,name,category,price,stock,barcode,low_at,active,updated_at) values(?,?,?,?,?,?,?,?,true,?)",
                newId(), target.id, p.name, p.category, p.price, 0, p.barcode, p.lowAt, now()
            )
            products.evict(target.id)
            activity.log(target.id, user, "product_added", mapOf("name" to p.name), device)
        } else if (!req.available && existing != null) {
            jdbc.update("update products set active=false,updated_at=? where id=?", now(), existing.id)
            products.evict(target.id)
            activity.log(target.id, user, "product_removed", mapOf("name" to p.name), device)
        }
        return availability(id, user)
    }

    private fun validate(r: ProductReq) {
        if (r.name.isBlank()) bad("INVALID_NAME", "Enter a product name")
        if (r.price < 0) bad("INVALID_PRICE", "Price cannot be negative")
        if (r.stock < 0) bad("INVALID_STOCK", "Stock cannot be negative")
    }
}
