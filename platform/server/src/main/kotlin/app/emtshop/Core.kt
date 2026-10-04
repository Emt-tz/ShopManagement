package app.emtshop

import com.fasterxml.jackson.databind.ObjectMapper
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.cache.annotation.EnableCaching
import org.springframework.context.annotation.Configuration
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.http.converter.HttpMessageNotReadableException
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder
import org.springframework.stereotype.Component
import org.springframework.stereotype.Service
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.RestControllerAdvice
import org.springframework.web.servlet.HandlerInterceptor
import org.springframework.web.servlet.config.annotation.InterceptorRegistry
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer
import java.security.SecureRandom
import java.util.Base64
import java.util.UUID

@SpringBootApplication
@EnableCaching
@org.springframework.scheduling.annotation.EnableScheduling
class Application

fun main(args: Array<String>) {
    runApplication<Application>(*args)
}

fun newId(): String = UUID.randomUUID().toString().replace("-", "")
fun now(): Long = System.currentTimeMillis()

class ApiException(val status: HttpStatus, val code: String, message: String) : RuntimeException(message)

fun bad(code: String, msg: String): Nothing = throw ApiException(HttpStatus.BAD_REQUEST, code, msg)
fun conflict(code: String, msg: String): Nothing = throw ApiException(HttpStatus.CONFLICT, code, msg)
fun notFound(code: String, msg: String): Nothing = throw ApiException(HttpStatus.NOT_FOUND, code, msg)
fun planLimit(code: String, msg: String): Nothing = throw ApiException(HttpStatus.PAYMENT_REQUIRED, code, msg)

@RestControllerAdvice
class Errors {
    @ExceptionHandler(ApiException::class)
    fun api(e: ApiException): ResponseEntity<Map<String, Any>> =
        ResponseEntity.status(e.status).body(mapOf("error" to mapOf("code" to e.code, "message" to (e.message ?: ""))))

    @ExceptionHandler(HttpMessageNotReadableException::class)
    fun unreadable(e: HttpMessageNotReadableException): ResponseEntity<Map<String, Any>> =
        ResponseEntity.badRequest().body(mapOf("error" to mapOf("code" to "BAD_REQUEST", "message" to "Invalid request body")))
}

data class AuthUser(val id: String, val name: String, val email: String)

@Service
class AuthService(val jdbc: JdbcTemplate) {
    private val enc = BCryptPasswordEncoder()
    private val rnd = SecureRandom()

    private val userMapper = RowMapper<AuthUser> { rs, _ -> AuthUser(rs.getString(1), rs.getString(2), rs.getString(3)) }

    fun createUser(email: String, name: String, password: String): AuthUser {
        val e = email.trim().lowercase()
        if (!e.contains("@") || e.length < 5) bad("INVALID_EMAIL", "Enter a valid email address")
        if (password.length < 8) bad("WEAK_PASSWORD", "Password must be at least 8 characters")
        if (name.isBlank()) bad("INVALID_NAME", "Enter your name")
        val exists = jdbc.queryForObject("select count(*) from users where email=?", Long::class.java, e)!! > 0
        if (exists) conflict("EMAIL_TAKEN", "An account with this email already exists")
        val id = newId()
        jdbc.update("insert into users(id,email,name,pw_hash,created_at) values(?,?,?,?,?)", id, e, name.trim(), enc.encode(password), now())
        return AuthUser(id, name.trim(), e)
    }

    fun issueToken(userId: String): String {
        val bytes = ByteArray(24).also { rnd.nextBytes(it) }
        val token = Base64.getUrlEncoder().withoutPadding().encodeToString(bytes)
        jdbc.update("insert into sessions(token,user_id,created_at) values(?,?,?)", token, userId, now())
        return token
    }

    fun login(email: String, password: String): Pair<String, AuthUser> {
        val row = jdbc.query("select id,name,email,pw_hash from users where email=?", RowMapper { rs, _ ->
            Pair(AuthUser(rs.getString(1), rs.getString(2), rs.getString(3)), rs.getString(4))
        }, email.trim().lowercase()).firstOrNull()
        if (row == null || !enc.matches(password, row.second)) throw ApiException(HttpStatus.UNAUTHORIZED, "BAD_CREDENTIALS", "Email or password is incorrect")
        return issueToken(row.first.id) to row.first
    }

    fun userForToken(token: String): AuthUser? =
        jdbc.query(
            "select u.id,u.name,u.email from sessions s join users u on u.id=s.user_id where s.token=?",
            userMapper, token
        ).firstOrNull()

    fun logout(token: String) {
        jdbc.update("delete from sessions where token=?", token)
    }
}

@Component
class AuthInterceptor(val auth: AuthService) : HandlerInterceptor {
    override fun preHandle(req: HttpServletRequest, res: HttpServletResponse, handler: Any): Boolean {
        if (req.method == "OPTIONS") return true
        val header = req.getHeader("Authorization")
        val token = if (header != null && header.startsWith("Bearer ")) header.substring(7) else null
        val user = token?.let { auth.userForToken(it) }
            ?: throw ApiException(HttpStatus.UNAUTHORIZED, "UNAUTHENTICATED", "Sign in required")
        req.setAttribute("user", user)
        req.setAttribute("token", token)
        return true
    }
}

@Configuration
class WebConfig(val interceptor: AuthInterceptor) : WebMvcConfigurer {
    override fun addInterceptors(registry: InterceptorRegistry) {
        registry.addInterceptor(interceptor)
            .addPathPatterns("/api/**")
            .excludePathPatterns("/api/auth/signup", "/api/auth/login", "/api/i18n/**", "/api/regions", "/api/billing/plans", "/api/health", "/api/payments/callback/**")
    }
}

data class Shop(
    val id: String, val ownerId: String, val name: String, val type: String, val country: String,
    val currency: String, val locale: String, val till: String?, val createdAt: Long
)

@Service
class Access(val jdbc: JdbcTemplate) {
    private val shopMapper = RowMapper<Shop> { rs, _ ->
        Shop(rs.getString(1), rs.getString(2), rs.getString(3), rs.getString(4), rs.getString(5), rs.getString(6), rs.getString(7), rs.getString(8), rs.getLong(9))
    }
    private val cols = "id,owner_id,name,type,country,currency,locale,till,created_at"

    fun shop(id: String): Shop =
        jdbc.query("select $cols from shops where id=?", shopMapper, id).firstOrNull() ?: notFound("SHOP_NOT_FOUND", "Shop not found")

    fun role(shopId: String, userId: String): String? =
        jdbc.queryForList("select role from members where shop_id=? and user_id=?", String::class.java, shopId, userId).firstOrNull()

    /** Any member of the shop. Non-members get 404 so shop ids cannot be probed. */
    fun member(shopId: String, user: AuthUser): Pair<Shop, String> {
        val shop = shop(shopId)
        val role = role(shopId, user.id) ?: notFound("SHOP_NOT_FOUND", "Shop not found")
        return shop to role
    }

    fun need(shopId: String, user: AuthUser, vararg roles: String): Pair<Shop, String> {
        val (shop, role) = member(shopId, user)
        if (role !in roles) throw ApiException(HttpStatus.FORBIDDEN, "FORBIDDEN", "Your role cannot do this")
        return shop to role
    }

    fun memberIds(shopId: String): List<String> =
        jdbc.queryForList("select user_id from members where shop_id=?", String::class.java, shopId)

    fun shopsOf(userId: String): List<Pair<Shop, String>> =
        jdbc.query(
            "select s.id,s.owner_id,s.name,s.type,s.country,s.currency,s.locale,s.till,s.created_at,m.role from shops s join members m on m.shop_id=s.id where m.user_id=? order by s.created_at",
            RowMapper { rs, _ -> shopMapper.mapRow(rs, 0)!! to rs.getString(10) }, userId
        )
}

@Component
class Json(val mapper: ObjectMapper) {
    fun write(v: Any?): String = mapper.writeValueAsString(v)
    @Suppress("UNCHECKED_CAST")
    fun readMap(s: String): Map<String, Any?> = mapper.readValue(s, Map::class.java) as Map<String, Any?>
}
