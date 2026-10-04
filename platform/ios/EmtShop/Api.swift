import Foundation

struct ApiError: LocalizedError { let code: String; let message: String; var errorDescription: String? { message } }
typealias JSON = [String: Any]

/// Thin client for the Emt Shop server. Amounts are minor units; the shop's currency decimals say where the point goes.
final class Api: ObservableObject {
    // Simulator reaches the Mac at localhost. Set EmtShopBaseURL in Info.plist (or EMTSHOP_URL build setting) for a real server.
    let base = (Bundle.main.object(forInfoDictionaryKey: "EmtShopBaseURL") as? String).flatMap { $0.isEmpty ? nil : $0 } ?? "http://localhost:8080"
    @Published var token: String? = UserDefaults.standard.string(forKey: "token") {
        didSet { UserDefaults.standard.set(token, forKey: "token") }
    }

    func call(_ method: String, _ path: String, _ body: JSON? = nil) async throws -> JSON {
        var r = URLRequest(url: URL(string: base + "/api" + path)!)
        r.httpMethod = method; r.timeoutInterval = 20
        r.setValue("application/json", forHTTPHeaderField: "Content-Type")
        r.setValue("iPhone", forHTTPHeaderField: "X-Device")
        if let t = token { r.setValue("Bearer " + t, forHTTPHeaderField: "Authorization") }
        if let b = body { r.httpBody = try JSONSerialization.data(withJSONObject: b) }
        let (data, resp) = try await URLSession.shared.data(for: r)
        let json = (try? JSONSerialization.jsonObject(with: data)) as? JSON ?? [:]
        let code = (resp as? HTTPURLResponse)?.statusCode ?? 0
        if code >= 400 {
            if code == 401 && token != nil { await MainActor.run { token = nil } }
            throw ApiError(code: json["code"] as? String ?? "HTTP_\(code)", message: json["message"] as? String ?? "Request failed (\(code))")
        }
        return json
    }

    func login(_ email: String, _ pass: String) async throws { let j = try await call("POST", "/auth/login", ["email": email, "password": pass]); await MainActor.run { token = j["token"] as? String } }
    func signup(_ name: String, _ email: String, _ pass: String) async throws { let j = try await call("POST", "/auth/signup", ["name": name, "email": email, "password": pass]); await MainActor.run { token = j["token"] as? String } }
    func me() async throws -> JSON { try await call("GET", "/me") }
    func config(_ shop: String) async throws -> JSON { try await call("GET", "/shops/\(shop)/config") }
    func products(_ shop: String) async throws -> [JSON] { try await call("GET", "/shops/\(shop)/products")["products"] as? [JSON] ?? [] }
    func sales(_ shop: String) async throws -> [JSON] { try await call("GET", "/shops/\(shop)/sales?limit=50")["sales"] as? [JSON] ?? [] }
    func insights(_ shop: String, _ range: String) async throws -> JSON { try await call("GET", "/shops/\(shop)/insights?range=\(range)") }
    func float(_ shop: String) async throws -> JSON { try await call("GET", "/shops/\(shop)/float") }
    func floatTx(_ shop: String, network: String, kind: String, amount: Int64) async throws { _ = try await call("POST", "/shops/\(shop)/float/tx", ["network": network, "kind": kind, "amount": amount]) }

    /// One idempotency key per cart: a retry after a dropped connection returns the same receipt instead of a second sale.
    func sell(_ shop: String, lines: [String: Int], tender: String, ref: String?, key: String) async throws -> JSON {
        var b: JSON = ["lines": lines.map { ["productId": $0.key, "qty": $0.value] }, "tender": tender, "idempotencyKey": key]
        if let ref { b["tenderRef"] = ref }
        return try await call("POST", "/shops/\(shop)/sales", b)["sale"] as? JSON ?? [:]
    }
}

func money(_ minor: Int64, _ decimals: Int, _ cur: String) -> String {
    var p: Int64 = 1; for _ in 0..<decimals { p *= 10 }
    let f = NumberFormatter(); f.numberStyle = .decimal; f.groupingSeparator = ","
    let whole = f.string(from: NSNumber(value: minor / p)) ?? "\(minor / p)"
    return decimals == 0 ? "\(cur) \(whole)" : "\(cur) \(whole).\(String(format: "%0\(decimals)d", Int(minor % p)))"
}
extension Dictionary where Key == String, Value == Any {
    func s(_ k: String) -> String { self[k] as? String ?? "" }
    func i(_ k: String) -> Int { (self[k] as? NSNumber)?.intValue ?? 0 }
    func l(_ k: String) -> Int64 { (self[k] as? NSNumber)?.int64Value ?? 0 }
    func b(_ k: String) -> Bool { self[k] as? Bool ?? false }
}
