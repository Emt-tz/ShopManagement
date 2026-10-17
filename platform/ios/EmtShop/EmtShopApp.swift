import SwiftUI

@main struct EmtShopApp: App {
    @StateObject var api = Api()
    var body: some Scene { WindowGroup { RootView().environmentObject(api) } }
}

struct ShopCtx {
    let id: String, name: String, type: String, decimals: Int, currency: String
    let tenders: [String], networks: [(id: String, name: String)]
    func fmt(_ v: Int64) -> String { money(v, decimals, currency) }
    var isAgent: Bool { type == "mobile_money" }
}

struct RootView: View {
    @EnvironmentObject var api: Api
    @State private var me: JSON?
    @State private var loading = true
    var body: some View {
        Group {
            if api.token == nil { AuthView() }
            else if let me { HomeView(me: me, signOut: { api.token = nil; self.me = nil }) }
            else if loading { ProgressView() } else { AuthView() }
        }
        .task(id: api.token) {
            guard api.token != nil else { me = nil; return }
            loading = true; me = try? await api.me(); loading = false
        }
    }
}

struct AuthView: View {
    @EnvironmentObject var api: Api
    @State private var signup = false, name = "", email = "", pass = "", err: String?, busy = false
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Spacer()
            Text("Emt Shop").font(.largeTitle.bold())
            Text("Free for 3 months. No card needed.").foregroundStyle(.secondary)
            if signup { TextField("Your name", text: $name).textFieldStyle(.roundedBorder) }
            TextField("Email", text: $email).textInputAutocapitalization(.never).keyboardType(.emailAddress).textFieldStyle(.roundedBorder)
            SecureField("Password", text: $pass).textFieldStyle(.roundedBorder)
            if let err { Text(err).foregroundStyle(.red).font(.footnote) }
            Button { Task {
                busy = true; err = nil
                do { signup ? try await api.signup(name, email, pass) : try await api.login(email, pass) } catch { err = error.localizedDescription }
                busy = false
            } } label: { Text(signup ? "Create account" : "Sign in").frame(maxWidth: .infinity) }
                .buttonStyle(.borderedProminent).controlSize(.large).disabled(busy)
            Button(signup ? "I already have an account" : "Create an account") { signup.toggle() }
            Spacer()
        }.padding(24)
    }
}

struct HomeView: View {
    @EnvironmentObject var api: Api
    let me: JSON; let signOut: () -> Void
    @State private var picked = 0
    @State private var ctx: ShopCtx?
    @State private var err: String?
    var shops: [JSON] { me["shops"] as? [JSON] ?? [] }
    var body: some View {
        Group {
            if shops.isEmpty { Text("Create your first shop on the web or Mac app, then come back.").padding() }
            else if let c = ctx {
                TabView {
                    if c.isAgent {
                        FloatView(c: c).tabItem { Label("Float", systemImage: "creditcard") }
                        ReceiptsView(c: c).tabItem { Label("History", systemImage: "list.bullet.rectangle") }
                    } else {
                        SellView(c: c).tabItem { Label("Sell", systemImage: "cart") }
                        ProductsView(c: c).tabItem { Label("Products", systemImage: "shippingbox") }
                        InsightsView(c: c).tabItem { Label("Insights", systemImage: "chart.bar") }
                        ReceiptsView(c: c).tabItem { Label("Receipts", systemImage: "receipt") }
                    }
                    ShopsView(shops: shops, picked: $picked, signOut: signOut).tabItem { Label("Shops", systemImage: "storefront") }
                }.id(c.id)
            } else if let err { Text(err).padding() } else { ProgressView() }
        }
        .task(id: picked) {
            guard !shops.isEmpty else { return }
            ctx = nil; let s = shops[picked]
            do {
                let c = try await api.config(s.s("id"))
                let cur = c["currency"] as? JSON ?? [:]
                let tenders = (c["tenders"] as? [JSON] ?? [])
                let nets = tenders.flatMap { ($0["networks"] as? [JSON] ?? []) }.map { (id: $0.s("id"), name: $0.s("name")) }
                ctx = ShopCtx(id: s.s("id"), name: s.s("name"), type: s.s("type"), decimals: cur.i("decimals"), currency: cur.s("code"),
                              tenders: tenders.map { $0.s("id") }.filter { $0 != "credit" }, networks: nets)
            } catch { err = error.localizedDescription }
        }
    }
}

/// Loads once, supports pull to refresh, and shows the server's own error message with a retry.
struct Loading<T, Content: View>: View {
    let load: () async throws -> T; @ViewBuilder let content: (T) -> Content
    @State private var value: T?; @State private var err: String?
    var body: some View {
        Group {
            if let value { content(value) }
            else if let err { VStack(spacing: 12) { Text(err); Button("Try again") { Task { await run() } } }.padding() }
            else { ProgressView() }
        }.task { await run() }.refreshable { await run() }
    }
    func run() async { do { value = try await load(); err = nil } catch { if value == nil { err = error.localizedDescription } } }
}

struct SellView: View {
    @EnvironmentObject var api: Api
    let c: ShopCtx
    @State private var products: [JSON] = []
    @State private var cart: [String: Int] = [:]
    @State private var tender = "cash", net: String?
    @State private var msg: String?, busy = false
    @State private var key = UUID().uuidString
    var total: Int64 { products.reduce(0) { $0 + $1.l("price") * Int64(cart[$1.s("id")] ?? 0) } }
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                List(products.indices, id: \.self) { i in
                    let p = products[i]; let id = p.s("id"); let q = cart[id] ?? 0
                    HStack {
                        VStack(alignment: .leading) { Text(p.s("name")); Text("\(c.fmt(p.l("price"))) · \(p.i("stock")) left").font(.footnote).foregroundStyle(.secondary) }
                        Spacer()
                        if q > 0 { Button { cart[id] = q == 1 ? nil : q - 1 } label: { Image(systemName: "minus.circle") }.buttonStyle(.borderless); Text("\(q)") }
                        Button { cart[id] = q + 1 } label: { Image(systemName: "plus.circle.fill") }.buttonStyle(.borderless)
                    }
                }.listStyle(.plain)
                VStack(spacing: 8) {
                    Picker("Pay with", selection: $tender) { ForEach(c.tenders, id: \.self) { Text($0.replacingOccurrences(of: "_", with: " ").capitalized).tag($0) } }.pickerStyle(.segmented)
                        .onChange(of: tender) { _, t in net = t == "lipa_namba" ? c.networks.first?.id : nil }
                    if tender == "lipa_namba" { Picker("Network", selection: Binding(get: { net ?? "" }, set: { net = $0 })) { ForEach(c.networks, id: \.id) { Text($0.name).tag($0.id) } }.pickerStyle(.menu) }
                    if let msg { Text(msg).font(.footnote).foregroundStyle(.tint) }
                    Button { Task { await charge() } } label: { Text("Charge \(c.fmt(total))").frame(maxWidth: .infinity) }
                        .buttonStyle(.borderedProminent).controlSize(.large).disabled(cart.isEmpty || busy)
                }.padding()
            }
            .navigationTitle("Sell").navigationBarTitleDisplayMode(.large)
            .task { await reload() }
        }
    }
    func reload() async { products = (try? await api.products(c.id)) ?? products }
    func charge() async {
        busy = true; defer { busy = false }
        do {
            let s = try await api.sell(c.id, lines: cart, tender: tender, ref: net, key: key)
            msg = "Receipt #\(s.i("number")) · \(c.fmt(s.l("total")))"; cart = [:]; key = UUID().uuidString; await reload()
        } catch { msg = error.localizedDescription }   // key kept on failure so a retry cannot double-charge
    }
}

struct ProductsView: View {
    @EnvironmentObject var api: Api
    let c: ShopCtx; @State private var q = ""
    var body: some View {
        NavigationStack {
            Loading(load: { try await api.products(c.id) }) { list in
                let items = list.filter { q.isEmpty || $0.s("name").localizedCaseInsensitiveContains(q) }
                List(Array(items.enumerated()), id: \.offset) { _, p in
                    HStack {
                        VStack(alignment: .leading) { Text(p.s("name")); Text(p.s("category")).font(.footnote).foregroundStyle(.secondary) }
                        Spacer()
                        VStack(alignment: .trailing) {
                            Text(c.fmt(p.l("price"))).bold()
                            Text("\(p.i("stock")) in stock").font(.footnote).foregroundStyle(p.i("stock") <= p.i("lowAt") ? .red : .secondary)
                        }
                    }
                }
            }.navigationTitle("Products").searchable(text: $q)
        }
    }
}

struct InsightsView: View {
    @EnvironmentObject var api: Api
    let c: ShopCtx; @State private var range = "week"
    var body: some View {
        NavigationStack {
            VStack {
                Picker("Range", selection: $range) { ForEach(["day", "week", "month", "year"], id: \.self) { Text($0.capitalized) } }.pickerStyle(.segmented).padding(.horizontal)
                Loading(load: { try await api.insights(c.id, range) }) { d in
                    List {
                        Section("Revenue") { Text(c.fmt(d.l("revenue"))).font(.title.bold()) }
                        Section { LabeledContent("Sales", value: "\(d.i("count"))"); LabeledContent("Average sale", value: c.fmt(d.l("average"))); LabeledContent("Refunds", value: c.fmt(d.l("refunds"))) }
                        Section("Top products") { ForEach(Array((d["topProducts"] as? [JSON] ?? []).enumerated()), id: \.offset) { i, p in LabeledContent("\(i + 1). \(p.s("name"))", value: "\(p.i("units")) sold") } }
                    }
                }.id(range)
            }.navigationTitle("Insights")
        }
    }
}

struct ReceiptsView: View {
    @EnvironmentObject var api: Api
    let c: ShopCtx
    var body: some View {
        NavigationStack {
            Group {
                if c.isAgent {
                    Loading(load: { try await api.float(c.id) }) { f in
                        List(Array((f["recent"] as? [JSON] ?? []).enumerated()), id: \.offset) { _, r in
                            LabeledContent("\(r.s("kind").replacingOccurrences(of: "_", with: " ").capitalized) · \(r.s("network"))", value: c.fmt(r.l("amount")))
                        }
                    }
                } else {
                    Loading(load: { try await api.sales(c.id) }) { list in
                        List(Array(list.enumerated()), id: \.offset) { _, r in
                            VStack(alignment: .leading) {
                                HStack { Text("Receipt #\(r.i("number"))"); Spacer(); Text(c.fmt(r.l("total"))).bold() }
                                Text("\(r.s("cashier")) · \(r.s("tender"))" + (r.s("status") == "voided" ? " · voided" : "")).font(.footnote).foregroundStyle(.secondary)
                            }
                        }
                    }
                }
            }.navigationTitle(c.isAgent ? "History" : "Receipts")
        }
    }
}

struct FloatView: View {
    @EnvironmentObject var api: Api
    let c: ShopCtx
    @State private var kind = "cash_out", net = "", amount = "", msg: String?, tick = 0
    var body: some View {
        NavigationStack {
            Loading(load: { try await api.float(c.id) }) { f in
                let acc = f["accounts"] as? [JSON] ?? []
                List {
                    Section { Text(c.fmt(f.l("total"))).font(.largeTitle.bold()); Text("\(f.i("todayCount")) transactions today · commission \(c.fmt(f.l("todayCommission")))").font(.footnote).foregroundStyle(.secondary) } header: { Text("Total cash and e-float") }
                    Section("New transaction") {
                        Picker("Type", selection: $kind) { Text("Cash in").tag("cash_in"); Text("Cash out").tag("cash_out"); Text("Airtime").tag("airtime") }.pickerStyle(.segmented)
                        Picker("Network", selection: $net) { ForEach(acc.filter { $0.s("network") != "cash" }.map { $0.s("network") }, id: \.self) { n in Text(acc.first { $0.s("network") == n }?.s("name") ?? n).tag(n) } }
                        TextField("Amount (\(c.currency))", text: $amount).keyboardType(.numberPad)
                        if let msg { Text(msg).font(.footnote).foregroundStyle(.tint) }
                        Button("Record") { Task { await record(acc) } }.disabled(amount.isEmpty)
                    }
                    Section("Float by network") { ForEach(acc.indices, id: \.self) { i in
                        LabeledContent(acc[i].s("name")) { Text(c.fmt(acc[i].l("balance")) + (acc[i].b("low") ? " · Low" : "")).foregroundStyle(acc[i].b("low") ? .red : .primary) } } }
                }.onAppear { if net.isEmpty { net = acc.first { $0.s("network") != "cash" }?.s("network") ?? "" } }
            }.id(tick).navigationTitle("Float")
        }
    }
    func record(_ acc: [JSON]) async {
        var p: Int64 = 1; for _ in 0..<c.decimals { p *= 10 }
        do { try await api.floatTx(c.id, network: net, kind: kind, amount: (Int64(amount) ?? 0) * p); msg = "Recorded"; amount = ""; tick += 1 }
        catch { msg = error.localizedDescription }
    }
}

struct ShopsView: View {
    let shops: [JSON]; @Binding var picked: Int; let signOut: () -> Void
    var body: some View {
        NavigationStack {
            List {
                Section { ForEach(shops.indices, id: \.self) { i in
                    Button { picked = i } label: { HStack { VStack(alignment: .leading) { Text(shops[i].s("name")).foregroundStyle(.primary); Text("\(shops[i].s("type").replacingOccurrences(of: "_", with: " ")) · \(shops[i].s("role"))").font(.footnote).foregroundStyle(.secondary) }
                        Spacer(); if i == picked { Image(systemName: "checkmark") } } } } }
                Section { Button("Sign out", role: .destructive, action: signOut) }
            }.navigationTitle("Shops")
        }
    }
}
