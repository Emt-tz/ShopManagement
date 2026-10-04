package app.emtshop

import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
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

data class SignupReq(val email: String = "", val password: String = "", val name: String = "")
data class LoginReq(val email: String = "", val password: String = "")
data class CreateShopReq(val name: String = "", val type: String = "", val country: String = "", val till: String? = null, val locale: String? = null)
data class UpdateShopReq(val name: String? = null, val till: String? = null, val locale: String? = null)
data class InviteReq(val name: String = "", val email: String = "", val password: String = "", val role: String = "cashier")

@RestController
@RequestMapping("/api")
class AuthController(
    val auth: AuthService, val access: Access, val billing: BillingService, val config: ConfigService, val jdbc: JdbcTemplate
) {
    @PostMapping("/auth/signup")
    @ResponseStatus(HttpStatus.CREATED)
    fun signup(@RequestBody req: SignupReq): Map<String, Any?> {
        val user = auth.createUser(req.email, req.name, req.password)
        return mapOf("token" to auth.issueToken(user.id), "user" to user)
    }

    @PostMapping("/auth/login")
    fun login(@RequestBody req: LoginReq): Map<String, Any?> {
        val (token, user) = auth.login(req.email, req.password)
        return mapOf("token" to token, "user" to user)
    }

    @PostMapping("/auth/logout")
    fun logout(@RequestAttribute("token") token: String): Map<String, Any?> {
        auth.logout(token)
        return mapOf("ok" to true)
    }

    @GetMapping("/me")
    fun me(@RequestAttribute("user") user: AuthUser): Map<String, Any?> {
        val shops = access.shopsOf(user.id)
        return mapOf(
            "user" to user,
            "subscription" to billing.current(user.id)?.let { billing.view(it) },
            "shops" to shops.map { (s, role) ->
                mapOf("id" to s.id, "name" to s.name, "type" to s.type, "country" to s.country, "currency" to s.currency, "role" to role, "owner" to (s.ownerId == user.id),
                    "members" to jdbc.queryForObject("select count(*) from members where shop_id=?", Long::class.java, s.id))
            }
        )
    }
}

@RestController
@RequestMapping("/api/shops")
class ShopController(
    val jdbc: JdbcTemplate, val access: Access, val billing: BillingService, val activity: ActivityService,
    val configCache: ShopConfigCache, val config: ConfigService, val hub: Hub
) {
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    fun create(
        @RequestAttribute("user") user: AuthUser, @RequestBody req: CreateShopReq,
        @RequestHeader("X-Device", defaultValue = "Web") device: String
    ): Map<String, Any?> {
        val ent = billing.requireActive(user.id)
        if (req.name.isBlank()) bad("INVALID_NAME", "Enter a shop name")
        ShopTypes.find(req.type) ?: bad("INVALID_TYPE", "Unknown shop type")
        val region = Regions.find(req.country.uppercase()) ?: bad("INVALID_COUNTRY", "Unsupported country")
        val owned = jdbc.queryForObject("select count(*) from shops where owner_id=?", Long::class.java, user.id)!!
        val maxShops = ent.limits.shops
        if (maxShops != null && owned >= maxShops) planLimit("PLAN_LIMIT_SHOPS", "Your plan includes $maxShops shop. Upgrade to add more")
        val locale = req.locale?.takeIf { it in region.locales } ?: region.locales.first()
        val id = newId()
        jdbc.update(
            "insert into shops(id,owner_id,name,type,country,currency,locale,till,created_at) values(?,?,?,?,?,?,?,?,?)",
            id, user.id, req.name.trim(), req.type, region.code, region.currency, locale, req.till?.trim()?.ifBlank { null }, now()
        )
        jdbc.update("insert into members(shop_id,user_id,role) values(?,?,?)", id, user.id, "owner")
        if (req.type == "mobile_money") {
            val low = (if (region.currency == "TZS") 1_500_000L else 10_000L) * pow10(region.decimals)
            jdbc.update("insert into float_accounts(shop_id,network,balance,low_at) values(?,?,?,?)", id, "cash", 0L, 0L)
            region.networks.forEach { jdbc.update("insert into float_accounts(shop_id,network,balance,low_at) values(?,?,?,?)", id, it.id, 0L, low) }
        }
        activity.log(id, user, "shop_created", mapOf("name" to req.name.trim()), device)
        return config.full(id)
    }

    @GetMapping
    fun list(@RequestAttribute("user") user: AuthUser): Map<String, Any?> =
        mapOf("shops" to access.shopsOf(user.id).map { (s, role) ->
            mapOf("id" to s.id, "name" to s.name, "type" to s.type, "country" to s.country, "currency" to s.currency, "role" to role)
        })

    @PutMapping("/{id}")
    fun update(@PathVariable id: String, @RequestAttribute("user") user: AuthUser, @RequestBody req: UpdateShopReq): Map<String, Any?> {
        val (shop, _) = access.need(id, user, "owner", "manager")
        val region = Regions.get(shop.country)
        req.name?.let { if (it.isBlank()) bad("INVALID_NAME", "Enter a shop name"); jdbc.update("update shops set name=? where id=?", it.trim(), id) }
        req.till?.let { jdbc.update("update shops set till=? where id=?", it.trim().ifBlank { null }, id) }
        req.locale?.let { if (it !in region.locales) bad("INVALID_LOCALE", "Language not available in this region"); jdbc.update("update shops set locale=? where id=?", it, id) }
        configCache.evict(id)
        return config.full(id)
    }
}

fun pow10(n: Int): Long { var r = 1L; repeat(n) { r *= 10 }; return r }

@RestController
@RequestMapping("/api/shops/{shopId}/members")
class TeamController(
    val jdbc: JdbcTemplate, val access: Access, val auth: AuthService, val billing: BillingService,
    val activity: ActivityService, val hub: Hub, val json: Json
) {
    @GetMapping
    fun list(@PathVariable shopId: String, @RequestAttribute("user") user: AuthUser): Map<String, Any?> {
        access.member(shopId, user)
        val rows = jdbc.query(
            "select u.id,u.name,u.email,m.role from members m join users u on u.id=m.user_id where m.shop_id=? order by u.name",
            RowMapper { rs, _ -> listOf(rs.getString(1), rs.getString(2), rs.getString(3), rs.getString(4)) }, shopId
        )
        val members = rows.map { (id, name, email, role) ->
            val last = jdbc.query(
                "select kind,data,device,created_at from activity where shop_id=? and user_id=? order by created_at desc limit 1",
                RowMapper { rs, _ -> mapOf("kind" to rs.getString(1), "data" to json.readMap(rs.getString(2)), "device" to rs.getString(3), "at" to rs.getLong(4)) },
                shopId, id
            ).firstOrNull()
            mapOf("id" to id, "name" to name, "email" to email, "role" to role, "online" to hub.isOnline(id), "last" to last)
        }
        return mapOf("members" to members)
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    fun invite(
        @PathVariable shopId: String, @RequestAttribute("user") user: AuthUser, @RequestBody req: InviteReq,
        @RequestHeader("X-Device", defaultValue = "Web") device: String
    ): Map<String, Any?> {
        val (shop, _) = access.need(shopId, user, "owner")
        val ent = billing.requireActive(shop.ownerId)
        if (req.role !in listOf("cashier", "manager")) bad("INVALID_ROLE", "Role must be cashier or manager")
        if (req.role == "manager" && ent.plan != "multi") planLimit("PLAN_LIMIT_ROLES", "Manager roles are included in Multi-shop")
        val staff = jdbc.queryForObject("select count(*) from members where shop_id=? and role<>'owner'", Long::class.java, shopId)!!
        val max = ent.limits.staff
        if (max != null && staff >= max) planLimit("PLAN_LIMIT_STAFF", if (max == 0) "Your plan does not include staff accounts" else "Your plan includes $max staff accounts")
        val u = auth.createUser(req.email, req.name, req.password)
        jdbc.update("insert into members(shop_id,user_id,role) values(?,?,?)", shopId, u.id, req.role)
        activity.log(shopId, user, "member_added", mapOf("name" to u.name, "role" to req.role), device)
        return mapOf("member" to mapOf("id" to u.id, "name" to u.name, "email" to u.email, "role" to req.role))
    }
}
