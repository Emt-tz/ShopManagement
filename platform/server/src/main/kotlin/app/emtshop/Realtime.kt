package app.emtshop

import com.fasterxml.jackson.databind.ObjectMapper
import org.springframework.context.annotation.Configuration
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
import org.springframework.stereotype.Component
import org.springframework.stereotype.Service
import org.springframework.transaction.support.TransactionSynchronization
import org.springframework.transaction.support.TransactionSynchronizationManager
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestAttribute
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.socket.CloseStatus
import org.springframework.web.socket.TextMessage
import org.springframework.web.socket.WebSocketSession
import org.springframework.web.socket.config.annotation.EnableWebSocket
import org.springframework.web.socket.config.annotation.WebSocketConfigurer
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry
import org.springframework.web.socket.handler.TextWebSocketHandler
import java.util.concurrent.ConcurrentHashMap

/** Fan-out of shop events to every connected member. One node here; Redis pub/sub or Kafka makes it multi-node. */
@Component
class Hub(val access: Access, val auth: AuthService, val mapper: ObjectMapper) : TextWebSocketHandler() {
    private val sessions = ConcurrentHashMap<String, MutableSet<WebSocketSession>>()

    override fun afterConnectionEstablished(session: WebSocketSession) {
        val query = session.uri?.query ?: ""
        val token = query.split("&").map { it.split("=", limit = 2) }.firstOrNull { it[0] == "token" }?.getOrNull(1)
        val user = token?.let { auth.userForToken(it) }
        if (user == null) {
            session.close(CloseStatus.POLICY_VIOLATION)
            return
        }
        session.attributes["uid"] = user.id
        sessions.computeIfAbsent(user.id) { ConcurrentHashMap.newKeySet() }.add(session)
        send(session, mapOf("type" to "hello", "user" to user.name))
    }

    override fun afterConnectionClosed(session: WebSocketSession, status: CloseStatus) {
        val uid = session.attributes["uid"] as? String ?: return
        sessions[uid]?.remove(session)
    }

    fun isOnline(userId: String): Boolean = sessions[userId]?.any { it.isOpen } == true

    private fun send(ws: WebSocketSession, payload: Any) {
        synchronized(ws) { if (ws.isOpen) ws.sendMessage(TextMessage(mapper.writeValueAsString(payload))) }
    }

    fun broadcastShop(shopId: String, payload: Any) {
        afterCommit {
            for (uid in access.memberIds(shopId)) sessions[uid]?.forEach { runCatching { send(it, payload) } }
        }
    }

    private fun afterCommit(block: () -> Unit) {
        if (TransactionSynchronizationManager.isActualTransactionActive()) {
            TransactionSynchronizationManager.registerSynchronization(object : TransactionSynchronization {
                override fun afterCommit() = block()
            })
        } else block()
    }
}

@Configuration
@EnableWebSocket
class WsConfig(val hub: Hub) : WebSocketConfigurer {
    override fun registerWebSocketHandlers(registry: WebSocketHandlerRegistry) {
        registry.addHandler(hub, "/ws").setAllowedOrigins("*")
    }
}

@Service
class ActivityService(val jdbc: JdbcTemplate, val json: Json, val hub: Hub) {
    private val mapper = RowMapper<Map<String, Any?>> { rs, _ ->
        mapOf(
            "id" to rs.getString("id"), "shopId" to rs.getString("shop_id"), "shopName" to rs.getString("shop_name"),
            "userName" to rs.getString("user_name"), "kind" to rs.getString("kind"),
            "data" to json.readMap(rs.getString("data")), "device" to rs.getString("device"), "at" to rs.getLong("created_at")
        )
    }

    fun log(shopId: String, user: AuthUser?, kind: String, data: Map<String, Any?>, device: String, at: Long = now()): Map<String, Any?> {
        val id = newId()
        val name = user?.name ?: "System"
        jdbc.update(
            "insert into activity(id,shop_id,user_id,user_name,kind,data,device,created_at) values(?,?,?,?,?,?,?,?)",
            id, shopId, user?.id, name, kind, json.write(data), device, at
        )
        val shopName = jdbc.queryForObject("select name from shops where id=?", String::class.java, shopId)!!
        val rec = mapOf("id" to id, "shopId" to shopId, "shopName" to shopName, "userName" to name, "kind" to kind, "data" to data, "device" to device, "at" to at)
        hub.broadcastShop(shopId, mapOf("type" to "activity", "activity" to rec))
        return rec
    }

    fun list(shopIds: List<String>, limit: Int, kinds: Set<String>? = null): List<Map<String, Any?>> {
        if (shopIds.isEmpty()) return emptyList()
        val marks = shopIds.joinToString(",") { "?" }
        val kindClause = if (kinds.isNullOrEmpty()) "" else " and a.kind in (${kinds.joinToString(",") { "?" }})"
        val args = ArrayList<Any>(shopIds)
        if (!kinds.isNullOrEmpty()) args.addAll(kinds)
        args.add(limit)
        return jdbc.query(
            "select a.id,a.shop_id,s.name as shop_name,a.user_name,a.kind,a.data,a.device,a.created_at from activity a join shops s on s.id=a.shop_id " +
                "where a.shop_id in ($marks)$kindClause order by a.created_at desc limit ?",
            mapper, *args.toTypedArray()
        )
    }
}

@RestController
@RequestMapping("/api")
class ActivityController(val access: Access, val activity: ActivityService) {
    @GetMapping("/activity")
    fun feed(
        @RequestAttribute("user") user: AuthUser,
        @RequestParam(required = false) shopId: String?,
        @RequestParam(defaultValue = "40") limit: Int,
        @RequestParam(required = false) kinds: String?
    ): Map<String, Any?> {
        val ids = if (shopId != null) { access.member(shopId, user); listOf(shopId) } else access.shopsOf(user.id).map { it.first.id }
        val kindSet = kinds?.split(",")?.filter { it.isNotBlank() }?.toSet()
        return mapOf("activity" to activity.list(ids, limit.coerceIn(1, 200), kindSet))
    }
}
