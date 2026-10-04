package app.emtshop.mobile

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val prefs = getSharedPreferences("emtshop", Context.MODE_PRIVATE)
        setContent { MaterialTheme(colorScheme = lightColorScheme(primary = androidx.compose.ui.graphics.Color(0xFF007AFF))) { Surface(Modifier.fillMaxSize()) { Root(prefs) } } }
    }
}

private suspend fun <T> io(f: () -> T): Result<T> = withContext(Dispatchers.IO) { runCatching(f) }

@Composable
fun Root(prefs: android.content.SharedPreferences) {
    val api = remember { Api(BuildConfig.BASE_URL, prefs.getString("token", null)) }
    var me by remember { mutableStateOf<JSONObject?>(null) }
    var loading by remember { mutableStateOf(api.token != null) }
    val scope = rememberCoroutineScope()
    fun refresh() { scope.launch { io { api.me() }.onSuccess { me = it }.onFailure { api.token = null; prefs.edit().remove("token").apply() }; loading = false } }
    LaunchedEffect(Unit) { if (api.token != null) refresh() }
    when {
        loading -> Box(Modifier.fillMaxSize(), Alignment.Center) { CircularProgressIndicator() }
        me == null -> AuthScreen(api) { prefs.edit().putString("token", api.token).apply(); loading = true; refresh() }
        else -> Home(api, me!!) { api.token = null; prefs.edit().remove("token").apply(); me = null }
    }
}

@Composable
fun AuthScreen(api: Api, done: () -> Unit) {
    var signup by remember { mutableStateOf(false) }
    var name by remember { mutableStateOf("") }; var email by remember { mutableStateOf("") }; var pass by remember { mutableStateOf("") }
    var err by remember { mutableStateOf<String?>(null) }; var busy by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    Column(Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.Center) {
        Text("Emt Shop", fontSize = 34.sp, fontWeight = FontWeight.Bold)
        Text("Free for 3 months. No card needed.", color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(24.dp))
        if (signup) OutlinedTextField(name, { name = it }, label = { Text("Your name") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(email, { email = it }, label = { Text("Email") }, singleLine = true, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(pass, { pass = it }, label = { Text("Password") }, singleLine = true, visualTransformation = PasswordVisualTransformation(), modifier = Modifier.fillMaxWidth())
        err?.let { Text(it, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp)) }
        Spacer(Modifier.height(16.dp))
        Button(enabled = !busy, modifier = Modifier.fillMaxWidth().height(52.dp), onClick = {
            busy = true; err = null
            scope.launch { io { if (signup) api.signup(name, email, pass) else api.login(email, pass) }.onSuccess { done() }.onFailure { err = it.message }; busy = false }
        }) { Text(if (signup) "Create account" else "Sign in") }
        TextButton(onClick = { signup = !signup }) { Text(if (signup) "I already have an account" else "Create an account") }
    }
}

data class ShopCtx(val id: String, val name: String, val type: String, val decimals: Int, val currency: String, val tenders: List<Pair<String, String>>, val networks: List<Pair<String, String>>)

@Composable
fun Home(api: Api, me: JSONObject, signOut: () -> Unit) {
    val shops = me.getJSONArray("shops")
    var picked by remember { mutableStateOf(0) }
    var ctx by remember { mutableStateOf<ShopCtx?>(null) }
    var err by remember { mutableStateOf<String?>(null) }
    LaunchedEffect(picked, shops.length()) {
        if (shops.length() == 0) return@LaunchedEffect
        val s = shops.getJSONObject(picked)
        io { api.config(s.getString("id")) }.onSuccess { c ->
            val cur = c.getJSONObject("currency")
            val tenders = c.getJSONArray("tenders").let { a -> (0 until a.length()).map { a.getJSONObject(it) } }
            val flat = tenders.map { it.getString("id") }.filter { it != "credit" }.map { it to it.split("_").joinToString(" ") { w -> w.replaceFirstChar(Char::uppercase) } }
            val nets = tenders.flatMap { t -> t.optJSONArray("networks")?.let { n -> (0 until n.length()).map { n.getJSONObject(it).let { o -> o.getString("id") to o.getString("name") } } } ?: emptyList() }
            ctx = ShopCtx(s.getString("id"), s.getString("name"), s.getString("type"), cur.getInt("decimals"), cur.getString("code"), flat, nets)
        }.onFailure { err = it.message }
    }
    if (shops.length() == 0) { Box(Modifier.fillMaxSize(), Alignment.Center) { Text("Create your first shop on the web or Mac app, then come back.") }; return }
    val c = ctx ?: Box(Modifier.fillMaxSize(), Alignment.Center) { if (err != null) Text(err!!) else CircularProgressIndicator() }.let { return }
    val agent = c.type == "mobile_money"
    var tab by remember(c.id) { mutableStateOf(0) }
    val tabs = if (agent) listOf("Float" to Icons.Filled.AccountBalanceWallet, "History" to Icons.Filled.Receipt, "Shops" to Icons.Filled.Store)
    else listOf("Sell" to Icons.Filled.ShoppingCart, "Products" to Icons.Filled.Inventory2, "Insights" to Icons.Filled.BarChart, "Receipts" to Icons.Filled.Receipt, "Shops" to Icons.Filled.Store)
    Scaffold(bottomBar = {
        NavigationBar { tabs.forEachIndexed { i, (l, ic) -> NavigationBarItem(selected = tab == i, onClick = { tab = i }, icon = { Icon(ic, l) }, label = { Text(l) }) } }
    }) { pad ->
        Box(Modifier.padding(pad).fillMaxSize()) {
            when (tabs[tab].first) {
                "Sell" -> SellScreen(api, c)
                "Products" -> ProductsScreen(api, c)
                "Insights" -> InsightsScreen(api, c)
                "Receipts", "History" -> ReceiptsScreen(api, c)
                "Float" -> FloatScreen(api, c)
                else -> ShopsScreen(shops, picked, { picked = it; ctx = null }, signOut)
            }
        }
    }
}

@Composable fun Title(t: String, sub: String? = null) = Column(Modifier.padding(16.dp, 16.dp, 16.dp, 8.dp)) {
    Text(t, fontSize = 30.sp, fontWeight = FontWeight.Bold); sub?.let { Text(it, color = MaterialTheme.colorScheme.onSurfaceVariant) }
}

@Composable fun <T> Loader(key: Any, load: () -> T, content: @Composable (T, () -> Unit) -> Unit) {
    var data by remember(key) { mutableStateOf<T?>(null) }; var err by remember(key) { mutableStateOf<String?>(null) }; var tick by remember(key) { mutableStateOf(0) }
    LaunchedEffect(key, tick) { io(load).onSuccess { data = it; err = null }.onFailure { err = it.message } }
    when { data != null -> content(data!!) { tick++ }; err != null -> Column(Modifier.padding(24.dp)) { Text(err!!); Button({ tick++ }) { Text("Try again") } }; else -> Box(Modifier.fillMaxSize(), Alignment.Center) { CircularProgressIndicator() } }
}

@Composable
fun SellScreen(api: Api, c: ShopCtx) = Loader(c.id, { api.products(c.id) }) { products, reload ->
    val cart = remember { mutableStateMapOf<String, Int>() }
    var tender by remember { mutableStateOf("cash") }; var net by remember { mutableStateOf<String?>(null) }
    var msg by remember { mutableStateOf<String?>(null) }; var busy by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    val list = (0 until products.length()).map { products.getJSONObject(it) }
    val total = list.sumOf { it.getLong("price") * (cart[it.getString("id")] ?: 0) }
    Column(Modifier.fillMaxSize()) {
        Title("Sell", c.name)
        LazyColumn(Modifier.weight(1f)) {
            items(list) { p ->
                val id = p.getString("id"); val q = cart[id] ?: 0
                ListItem(headlineContent = { Text(p.getString("name")) }, supportingContent = { Text("${money(p.getLong("price"), c.decimals, c.currency)} · ${p.getInt("stock")} left") },
                    trailingContent = { Row(verticalAlignment = Alignment.CenterVertically) {
                        if (q > 0) { IconButton({ if (q == 1) cart.remove(id) else cart[id] = q - 1 }) { Icon(Icons.Filled.Remove, "less") }; Text("$q") }
                        IconButton({ cart[id] = q + 1 }) { Icon(Icons.Filled.Add, "more") } } })
                HorizontalDivider()
            }
        }
        Column(Modifier.padding(16.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                c.tenders.forEach { (id, n) -> FilterChip(selected = tender == id, onClick = { tender = id; net = c.networks.firstOrNull()?.first.takeIf { id == "lipa_namba" } }, label = { Text(n) }) }
            }
            if (tender == "lipa_namba") Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) { c.networks.forEach { (id, n) -> FilterChip(selected = net == id, onClick = { net = id }, label = { Text(n) }) } }
            msg?.let { Text(it, color = MaterialTheme.colorScheme.primary) }
            Button(enabled = cart.isNotEmpty() && !busy, modifier = Modifier.fillMaxWidth().height(52.dp), onClick = {
                busy = true
                scope.launch {
                    io { api.sell(c.id, cart.toMap(), tender, net) }
                        .onSuccess { msg = "Receipt #${it.optInt("number")} · ${money(it.getLong("total"), c.decimals, c.currency)}"; cart.clear(); reload() }
                        .onFailure { msg = it.message }
                    busy = false
                }
            }) { Text("Charge ${money(total, c.decimals, c.currency)}") }
        }
    }
}

@Composable
fun ProductsScreen(api: Api, c: ShopCtx) = Loader(c.id, { api.products(c.id) }) { products, _ ->
    var q by remember { mutableStateOf("") }
    val list = (0 until products.length()).map { products.getJSONObject(it) }.filter { it.getString("name").contains(q, true) }
    Column {
        Title("Products", "${products.length()} items")
        OutlinedTextField(q, { q = it }, placeholder = { Text("Search") }, singleLine = true, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp))
        LazyColumn { items(list) { p ->
            ListItem(headlineContent = { Text(p.getString("name")) }, supportingContent = { Text(p.optString("category")) },
                trailingContent = { Column(horizontalAlignment = Alignment.End) { Text(money(p.getLong("price"), c.decimals, c.currency), fontWeight = FontWeight.SemiBold)
                    val s = p.getInt("stock"); Text("$s in stock", color = if (s <= p.optInt("lowAt", 10)) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurfaceVariant) } })
            HorizontalDivider() } }
    }
}

@Composable
fun InsightsScreen(api: Api, c: ShopCtx) {
    var range by remember { mutableStateOf("week") }
    Column {
        Title("Insights", c.name)
        Row(Modifier.padding(horizontal = 16.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) { listOf("day", "week", "month", "year").forEach { FilterChip(range == it, { range = it }, { Text(it.replaceFirstChar(Char::uppercase)) }) } }
        Loader(c.id + range, { api.insights(c.id, range) }) { d, _ ->
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(16.dp)) { Text("Revenue", color = MaterialTheme.colorScheme.onSurfaceVariant); Text(money(d.getLong("revenue"), c.decimals, c.currency), fontSize = 30.sp, fontWeight = FontWeight.Bold) } }
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Card(Modifier.weight(1f)) { Column(Modifier.padding(16.dp)) { Text("Sales"); Text("${d.getInt("count")}", fontSize = 24.sp, fontWeight = FontWeight.Bold) } }
                    Card(Modifier.weight(1f)) { Column(Modifier.padding(16.dp)) { Text("Average"); Text(money(d.getLong("average"), c.decimals, c.currency), fontSize = 24.sp, fontWeight = FontWeight.Bold) } }
                }
                Text("Top products", fontWeight = FontWeight.SemiBold)
                val tp = d.optJSONArray("topProducts") ?: JSONArray()
                (0 until tp.length()).forEach { i -> tp.getJSONObject(i).let { Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) { Text("${i + 1}. ${it.getString("name")}"); Text("${it.getInt("units")} sold") } } }
            }
        }
    }
}

@Composable
fun ReceiptsScreen(api: Api, c: ShopCtx) {
    if (c.type == "mobile_money") return FloatHistory(api, c)
    Loader(c.id, { api.sales(c.id) }) { s, _ ->
        Column { Title("Receipts", c.name); LazyColumn { items((0 until s.length()).map { s.getJSONObject(it) }) { r ->
            ListItem(headlineContent = { Text("Receipt #${r.optInt("number")}") }, supportingContent = { Text("${r.optString("cashier")} · ${r.optString("tender")}" + if (r.optString("status") == "voided") " · voided" else "") },
                trailingContent = { Text(money(r.getLong("total"), c.decimals, c.currency), fontWeight = FontWeight.SemiBold) }); HorizontalDivider() } } }
    }
}

@Composable
fun FloatHistory(api: Api, c: ShopCtx) = Loader(c.id, { api.float(c.id) }) { f, _ ->
    val rec = f.optJSONArray("recent") ?: JSONArray()
    Column { Title("History", c.name); LazyColumn { items((0 until rec.length()).map { rec.getJSONObject(it) }) { r ->
        ListItem(headlineContent = { Text(r.getString("kind").replace('_', ' ').replaceFirstChar(Char::uppercase) + " · " + r.getString("network")) }, supportingContent = { Text(r.optString("userName")) },
            trailingContent = { Text(money(r.getLong("amount"), c.decimals, c.currency), fontWeight = FontWeight.SemiBold) }); HorizontalDivider() } } }
}

@Composable
fun FloatScreen(api: Api, c: ShopCtx) = Loader(c.id, { api.float(c.id) }) { f, reload ->
    val acc = f.getJSONArray("accounts").let { a -> (0 until a.length()).map { a.getJSONObject(it) } }
    var kind by remember { mutableStateOf("cash_out") }; var net by remember { mutableStateOf(acc.firstOrNull { it.getString("network") != "cash" }?.getString("network") ?: "") }
    var amount by remember { mutableStateOf("") }; var msg by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()
    var p = 1L; repeat(c.decimals) { p *= 10 }
    Column(Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text("Float", fontSize = 30.sp, fontWeight = FontWeight.Bold)
        Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(16.dp)) { Text("Total cash and e-float"); Text(money(f.getLong("total"), c.decimals, c.currency), fontSize = 30.sp, fontWeight = FontWeight.Bold)
            Text("${f.optInt("todayCount")} transactions today · commission ${money(f.optLong("todayCommission"), c.decimals, c.currency)}") } }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) { listOf("cash_in" to "Cash in", "cash_out" to "Cash out", "airtime" to "Airtime").forEach { (k, l) -> FilterChip(kind == k, { kind = k }, { Text(l) }) } }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) { acc.filter { it.getString("network") != "cash" }.forEach { a -> FilterChip(net == a.getString("network"), { net = a.getString("network") }, { Text(a.getString("name")) }) } }
        OutlinedTextField(amount, { amount = it.filter(Char::isDigit) }, label = { Text("Amount (${c.currency})") }, singleLine = true, modifier = Modifier.fillMaxWidth())
        msg?.let { Text(it, color = MaterialTheme.colorScheme.primary) }
        Button(enabled = amount.isNotEmpty() && net.isNotEmpty(), modifier = Modifier.fillMaxWidth().height(52.dp), onClick = {
            scope.launch { io { api.floatTx(c.id, net, kind, amount.toLong() * p) }.onSuccess { msg = "Recorded"; amount = ""; reload() }.onFailure { msg = it.message } }
        }) { Text("Record") }
        acc.forEach { a -> Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) { Text(a.getString("name")); Text(money(a.getLong("balance"), c.decimals, c.currency) + if (a.optBoolean("low")) " · Low" else "", color = if (a.optBoolean("low")) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurface) } }
    }
}

@Composable
fun ShopsScreen(shops: JSONArray, picked: Int, pick: (Int) -> Unit, signOut: () -> Unit) {
    Column { Title("Shops"); LazyColumn { items((0 until shops.length()).map { shops.getJSONObject(it) }.withIndex().toList()) { (i, s) ->
        ListItem(headlineContent = { Text(s.getString("name")) }, supportingContent = { Text("${s.getString("type").replace('_', ' ')} · ${s.getString("role")}") },
            trailingContent = { if (i == picked) Icon(Icons.Filled.Check, "current") }, modifier = Modifier.then(Modifier)); TextButton({ pick(i) }) { Text("Use this shop") }; HorizontalDivider() } }
        TextButton(signOut, Modifier.padding(16.dp)) { Text("Sign out") } }
}
