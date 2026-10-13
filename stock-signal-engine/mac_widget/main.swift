import Cocoa
import Foundation
import SwiftUI

// MARK: - Data Models
struct PositionItem: Codable, Identifiable {
    var id: String { symbol }
    let symbol: String
    let book: String?
    let qty: Double
    let avg_entry: Double
    let now: Double
    let pnl_dollars: Double
    let pnl_pct: Double
}

struct AccountResponse: Codable {
    let equity: Double
    let cash: Double
    let buying_power: Double
    let market_open: Bool
    let positions: [PositionItem]?
}

struct DesksSummary: Codable {
    let total_desks: Int?
    let running_desks: Int?
    let combined_portfolio_equity: Double?
}

struct DeskItem: Codable {
    let desk_id: String?
    let display_name: String?
    let pid: Int?
    let status: String?
    let broker: String?
    let mode: String?
    let equity: Double?
    let cash: Double?
    let buying_power: Double?
    let positions_count: Int?
}

struct DesksResponse: Codable {
    let timestamp: Double?
    let summary: DesksSummary?
    let desks: [String: DeskItem]?
}

struct StrategyWeightItem: Codable {
    let multiplier: Double?
    let praises: Int?
    let punishments: Int?
}

struct AIReviewItem: Codable {
    let ticker: String?
    let verdict: String?
    let rule_learned: String?
}

struct ComplianceReport: Codable {
    let strategy_weights: [String: StrategyWeightItem]?
    let recent_ai_model_reviews: [AIReviewItem]?
}

struct JournalStats: Codable {
    let n: Int?
    let win_rate: Double?
    let avg_pnl: Double?
    let total: Double?
}

struct JournalSummary: Codable {
    let stats: JournalStats?
}

// MARK: - Currency Formatter Helper
func formatCurrency(_ val: Double) -> String {
    let formatter = NumberFormatter()
    formatter.numberStyle = .decimal
    formatter.minimumFractionDigits = 2
    formatter.maximumFractionDigits = 2
    let str = formatter.string(from: NSNumber(value: val)) ?? String(format: "%.2f", val)
    return "$" + str
}

// MARK: - Observable State Store
class WidgetStateStore: ObservableObject {
    // Desk 1 / Alpaca
    @Published var equity: Double = 95808.73
    @Published var cash: Double = 14456.53
    @Published var buyingPower: Double = 285612.28
    @Published var marketOpen: Bool = false
    @Published var positions: [PositionItem] = []

    // 4-Asset Multi-Desk System
    @Published var combinedEquity: Double = 220808.73
    @Published var runningDesks: Int = 4
    @Published var totalDesks: Int = 4
    @Published var d1Pid: String = "72697"
    @Published var d2Pid: String = "4454"
    @Published var d3Pid: String = "4463"
    @Published var d4Pid: String = "4438"
    @Published var d1Equity: Double = 96000.00
    @Published var d2Equity: Double = 50000.00
    @Published var d3Equity: Double = 25000.00
    @Published var d4Equity: Double = 50000.00
    @Published var d1Status: String = "RUNNING"
    @Published var d2Status: String = "RUNNING"
    @Published var d3Status: String = "RUNNING"
    @Published var d4Status: String = "RUNNING"

    // AI Compliance & Strategy Matrix
    @Published var praisesCount: Int = 18
    @Published var punishCount: Int = 0
    @Published var jevMult: Double = 1.00
    @Published var rossMult: Double = 1.00
    @Published var coreMult: Double = 1.00
    @Published var latestRuleLearned: String = "Pre-trade excellence: High-confluence setup passed institutional gates."

    // App state
    @Published var winRate: Double = 66.7
    @Published var totalTrades: Int = 15
    @Published var isOnline: Bool = false
    @Published var isPinnedToDesktop: Bool = true
    @Published var lastUpdated: String = "Connecting..."
    @Published var sniperPick: String = "MSFT"
    @Published var sniperGrade: String = "Grade A"
    @Published var sniperScore: Double = 76.4

    func update(with account: AccountResponse) {
        self.equity = account.equity
        self.cash = account.cash
        self.buyingPower = account.buying_power
        self.marketOpen = account.market_open
        self.positions = account.positions ?? []
        self.isOnline = true

        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        self.lastUpdated = formatter.string(from: Date())
    }

    func updateDesks(with res: DesksResponse) {
        if let sum = res.summary {
            if let c = sum.combined_portfolio_equity { self.combinedEquity = c }
            if let r = sum.running_desks { self.runningDesks = r }
            if let t = sum.total_desks { self.totalDesks = t }
        }

        if let d = res.desks {
            if let st = d["stocks"] {
                if let pid = st.pid { self.d1Pid = "\(pid)" }
                if let eq = st.equity { self.d1Equity = eq }
                if let s = st.status { self.d1Status = s }
            }
            if let cr = d["crypto_perp"] {
                if let pid = cr.pid { self.d2Pid = "\(pid)" }
                if let eq = cr.equity { self.d2Equity = eq }
                if let s = cr.status { self.d2Status = s }
            }
            if let fut = d["cme_futures"] {
                if let pid = fut.pid { self.d3Pid = "\(pid)" }
                if let eq = fut.equity { self.d3Equity = eq }
                if let s = fut.status { self.d3Status = s }
            }
            if let fx = d["forex"] {
                if let pid = fx.pid { self.d4Pid = "\(pid)" }
                if let eq = fx.equity { self.d4Equity = eq }
                if let s = fx.status { self.d4Status = s }
            }
        }
        self.isOnline = true
    }

    func updateCompliance(with report: ComplianceReport) {
        if let weights = report.strategy_weights {
            var pr = 0
            var pu = 0
            if let jev = weights["jev_scooper"] {
                self.jevMult = jev.multiplier ?? 1.0
                pr += jev.praises ?? 0
                pu += jev.punishments ?? 0
            }
            if let ross = weights["ross_momentum"] {
                self.rossMult = ross.multiplier ?? 1.0
                pr += ross.praises ?? 0
                pu += ross.punishments ?? 0
            }
            if let core = weights["core_swing"] {
                self.coreMult = core.multiplier ?? 1.0
                pr += core.praises ?? 0
                pu += core.punishments ?? 0
            }
            self.praisesCount = pr
            self.punishCount = pu
        }

        if let reviews = report.recent_ai_model_reviews, let first = reviews.first, let rule = first.rule_learned {
            let t = first.ticker ?? "DESK"
            self.latestRuleLearned = "[\(t)] \(rule)"
        }
    }

    func updateStats(with stats: JournalStats) {
        if let wr = stats.win_rate { self.winRate = wr }
        if let n = stats.n { self.totalTrades = n }
    }
}

// MARK: - macOS Desktop Widget SwiftUI View
struct DesktopWidgetView: View {
    @ObservedObject var store: WidgetStateStore
    var onTogglePin: () -> Void
    var onOpenDashboard: () -> Void
    var onOpenWidgetWeb: () -> Void
    var onRefresh: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header Bar
            HStack(alignment: .center, spacing: 8) {
                // Status Indicator
                HStack(spacing: 5) {
                    Circle()
                        .fill(store.isOnline ? Color.green : Color.red)
                        .frame(width: 8, height: 8)
                        .shadow(color: store.isOnline ? Color.green : Color.red, radius: 4)

                    Text(store.isOnline ? "\(store.runningDesks)/\(store.totalDesks) DESKS ACTIVE" : "OFFLINE")
                        .font(.system(size: 10, weight: .bold, design: .rounded))
                        .foregroundColor(store.isOnline ? .green : .red)
                }

                Spacer()

                // Actions: Pin, Dash, Widget Web, Refresh
                HStack(spacing: 6) {
                    Button(action: onTogglePin) {
                        Image(systemName: store.isPinnedToDesktop ? "pin.fill" : "macwindow.on.rectangle")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.white.opacity(0.7))
                    }
                    .buttonStyle(.plain)
                    .help(store.isPinnedToDesktop ? "Pinned to Desktop (Click to float on top)" : "Floating on Top (Click to pin to desktop)")

                    Button(action: onRefresh) {
                        Image(systemName: "arrow.clockwise")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.white.opacity(0.7))
                    }
                    .buttonStyle(.plain)
                    .help("Refresh live data")

                    Button(action: onOpenWidgetWeb) {
                        Image(systemName: "iphone.gen3")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.cyan)
                    }
                    .buttonStyle(.plain)
                    .help("Open Web HUD Widget (/widget)")

                    Button(action: onOpenDashboard) {
                        Image(systemName: "safari")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.white.opacity(0.8))
                    }
                    .buttonStyle(.plain)
                    .help("Open Web Terminal Dashboard")
                }
            }
            .padding(.bottom, 8)

            // Combined Multi-Desk Capital Hero
            VStack(alignment: .leading, spacing: 2) {
                HStack {
                    Text("COMBINED PORTFOLIO CAPITAL")
                        .font(.system(size: 9, weight: .bold, design: .rounded))
                        .foregroundColor(.cyan.opacity(0.85))
                        .tracking(0.5)

                    Spacer()

                    Text(store.marketOpen ? "EQUITY OPEN" : "24/7 PERPS ACTIVE")
                        .font(.system(size: 8, weight: .bold))
                        .padding(.horizontal, 5)
                        .padding(.vertical, 2)
                        .background(Color.green.opacity(0.18))
                        .foregroundColor(.green)
                        .cornerRadius(4)
                }

                Text(formatCurrency(store.combinedEquity))
                    .font(.system(size: 25, weight: .heavy, design: .rounded))
                    .foregroundColor(.white)
            }
            .padding(.bottom, 8)

            // 3-Asset Desks Micro-Strip
            VStack(spacing: 4) {
                // Desk 1: US Equities
                HStack(spacing: 6) {
                    Text("🏛️ D1")
                        .font(.system(size: 9, weight: .bold))
                        .foregroundColor(.cyan)
                    Text("STOCKS")
                        .font(.system(size: 9, weight: .semibold, design: .rounded))
                        .foregroundColor(.white.opacity(0.7))
                    Text("PID \(store.d1Pid)")
                        .font(.system(size: 8, weight: .medium, design: .monospaced))
                        .foregroundColor(.white.opacity(0.4))

                    Spacer()

                    Text(formatCurrency(store.d1Equity))
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.white.opacity(0.04))
                .cornerRadius(6)

                // Desk 2: Crypto Perps
                HStack(spacing: 6) {
                    Text("⚡ D2")
                        .font(.system(size: 9, weight: .bold))
                        .foregroundColor(.orange)
                    Text("CRYPTO 3x")
                        .font(.system(size: 9, weight: .semibold, design: .rounded))
                        .foregroundColor(.white.opacity(0.7))
                    Text("PID \(store.d2Pid)")
                        .font(.system(size: 8, weight: .medium, design: .monospaced))
                        .foregroundColor(.white.opacity(0.4))

                    Spacer()

                    Text(formatCurrency(store.d2Equity))
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.white.opacity(0.04))
                .cornerRadius(6)

                // Desk 3: CME Micro Futures
                HStack(spacing: 6) {
                    Text("📈 D3")
                        .font(.system(size: 9, weight: .bold))
                        .foregroundColor(.green)
                    Text("CME FUT")
                        .font(.system(size: 9, weight: .semibold, design: .rounded))
                        .foregroundColor(.white.opacity(0.7))
                    Text("PID \(store.d3Pid)")
                        .font(.system(size: 8, weight: .medium, design: .monospaced))
                        .foregroundColor(.white.opacity(0.4))

                    Spacer()

                    Text(formatCurrency(store.d3Equity))
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.white.opacity(0.04))
                .cornerRadius(6)

                // Desk 4: Forex 24/5 Macro
                HStack(spacing: 6) {
                    Text("💱 D4")
                        .font(.system(size: 9, weight: .bold))
                        .foregroundColor(.purple)
                    Text("FOREX")
                        .font(.system(size: 9, weight: .semibold, design: .rounded))
                        .foregroundColor(.white.opacity(0.7))
                    Text("PID \(store.d4Pid)")
                        .font(.system(size: 8, weight: .medium, design: .monospaced))
                        .foregroundColor(.white.opacity(0.4))

                    Spacer()

                    Text(formatCurrency(store.d4Equity))
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.white.opacity(0.04))
                .cornerRadius(6)
            }
            .padding(.bottom, 8)

            Divider()
                .background(Color.white.opacity(0.12))
                .padding(.bottom, 6)

            // Active Holdings Section
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text("ACTIVE HOLDINGS")
                        .font(.system(size: 8, weight: .bold, design: .rounded))
                        .foregroundColor(.white.opacity(0.5))
                        .tracking(0.5)

                    Spacer()

                    Text("\(store.positions.count) Positions")
                        .font(.system(size: 8, weight: .semibold, design: .monospaced))
                        .foregroundColor(.cyan)
                }

                if store.positions.isEmpty {
                    HStack {
                        Spacer()
                        Text("100% Cash — Scanning for Grade A Setups")
                            .font(.system(size: 10, weight: .medium))
                            .foregroundColor(.white.opacity(0.4))
                            .padding(.vertical, 8)
                        Spacer()
                    }
                } else {
                    VStack(spacing: 3) {
                        ForEach(store.positions.prefix(3)) { pos in
                            HStack(alignment: .center, spacing: 5) {
                                Text(pos.pnl_dollars >= 0 ? "▲" : "▼")
                                    .font(.system(size: 8, weight: .bold))
                                    .foregroundColor(pos.pnl_dollars >= 0 ? .green : .red)

                                Text(pos.symbol)
                                    .font(.system(size: 11, weight: .bold, design: .rounded))
                                    .foregroundColor(.white)
                                    .frame(width: 48, alignment: .leading)

                                Text(pos.symbol == "SH" ? "HEDGE" : (pos.book?.uppercased() ?? "CORE"))
                                    .font(.system(size: 7, weight: .bold))
                                    .padding(.horizontal, 4)
                                    .padding(.vertical, 1)
                                    .background(pos.symbol == "SH" ? Color.orange.opacity(0.25) : Color.cyan.opacity(0.2))
                                    .foregroundColor(pos.symbol == "SH" ? .orange : .cyan)
                                    .cornerRadius(3)

                                Spacer()

                                Text(String(format: "$%.2f", pos.now))
                                    .font(.system(size: 10, weight: .medium, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.7))

                                Text(String(format: "%@$%.2f", pos.pnl_dollars >= 0 ? "+" : "", pos.pnl_dollars))
                                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                                    .foregroundColor(pos.pnl_dollars >= 0 ? .green : .red)
                                    .frame(width: 65, alignment: .trailing)
                            }
                            .padding(.vertical, 1)
                        }
                    }
                }
            }
            .padding(.bottom, 6)

            Divider()
                .background(Color.white.opacity(0.12))
                .padding(.bottom, 6)

            // Autonomous AI Compliance & Reinforcement Matrix
            VStack(alignment: .leading, spacing: 3) {
                HStack {
                    Text("AI COMPLIANCE & MATRIX")
                        .font(.system(size: 8, weight: .bold, design: .rounded))
                        .foregroundColor(.cyan)

                    Spacer()

                    HStack(spacing: 6) {
                        Text("🟢 \(store.praisesCount) Praise")
                            .font(.system(size: 8, weight: .bold))
                            .foregroundColor(.green)
                        Text("🔴 \(store.punishCount) Pen")
                            .font(.system(size: 8, weight: .bold))
                            .foregroundColor(.red)
                    }
                }

                HStack(spacing: 8) {
                    Text(String(format: "JEV: %.2fx", store.jevMult))
                        .font(.system(size: 8, weight: .semibold, design: .monospaced))
                        .foregroundColor(.white.opacity(0.8))
                    Text(String(format: "Ross: %.2fx", store.rossMult))
                        .font(.system(size: 8, weight: .semibold, design: .monospaced))
                        .foregroundColor(.white.opacity(0.8))
                    Text(String(format: "Core: %.2fx", store.coreMult))
                        .font(.system(size: 8, weight: .semibold, design: .monospaced))
                        .foregroundColor(.white.opacity(0.8))
                    Spacer()
                    Text("Kelly 1.5% Strict")
                        .font(.system(size: 8, weight: .medium))
                        .foregroundColor(.orange)
                }

                Text(store.latestRuleLearned)
                    .font(.system(size: 8, weight: .medium))
                    .foregroundColor(.white.opacity(0.45))
                    .lineLimit(1)
            }

            Spacer(minLength: 0)

            // Bottom Sync Bar
            HStack {
                Text("Autonomous 3-Desk Mesh · Watchdog Active")
                    .font(.system(size: 8, weight: .medium))
                    .foregroundColor(.white.opacity(0.3))
                Spacer()
                Text("Sync: \(store.lastUpdated)")
                    .font(.system(size: 8, weight: .medium, design: .monospaced))
                    .foregroundColor(.white.opacity(0.3))
            }
            .padding(.top, 4)
        }
        .padding(14)
        .frame(width: 350, height: 460)
        .background(
            ZStack {
                Color(red: 0.06, green: 0.08, blue: 0.12).opacity(0.88)
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .stroke(Color.white.opacity(0.14), lineWidth: 1)
            }
        )
        .cornerRadius(22)
        .shadow(color: Color.black.opacity(0.5), radius: 18, x: 0, y: 8)
    }
}

// MARK: - Native Desktop Widget Window (AppKit)
class DesktopWidgetWindow: NSWindow {
    let store: WidgetStateStore

    init(store: WidgetStateStore) {
        self.store = store

        let savedX = UserDefaults.standard.double(forKey: "QuantDeskWidget_OriginX")
        let savedY = UserDefaults.standard.double(forKey: "QuantDeskWidget_OriginY")
        let initialX = savedX > 0 ? savedX : 380.0
        let initialY = savedY > 0 ? savedY : 240.0

        let rect = NSRect(x: initialX, y: initialY, width: 350, height: 460)
        super.init(
            contentRect: rect,
            styleMask: [.borderless, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )

        self.isOpaque = false
        self.backgroundColor = .clear
        self.hasShadow = true
        self.isMovableByWindowBackground = true // Draggable anywhere on desktop
        self.collectionBehavior = [.canJoinAllSpaces, .stationary, .ignoresCycle]

        updateWindowLevel(isPinned: store.isPinnedToDesktop)

        NotificationCenter.default.addObserver(
            self,
            selector: #selector(windowDidMoveNotification),
            name: NSWindow.didMoveNotification,
            object: self
        )
    }

    func updateWindowLevel(isPinned: Bool) {
        if isPinned {
            self.level = .init(Int(CGWindowLevelForKey(.desktopWindow)) + 1)
        } else {
            self.level = .floating
        }
    }

    @objc func windowDidMoveNotification() {
        let origin = self.frame.origin
        UserDefaults.standard.set(origin.x, forKey: "QuantDeskWidget_OriginX")
        UserDefaults.standard.set(origin.y, forKey: "QuantDeskWidget_OriginY")
    }
}

// MARK: - App Delegate (Menu Bar Item + Desktop Widget Manager)
class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem!
    var desktopWindow: DesktopWidgetWindow?
    var timer: Timer?
    let store = WidgetStateStore()
    var isFetching = false
    let projectDir = FileManager.default.currentDirectoryPath

    func applicationDidFinishLaunching(_ notification: Notification) {
        // 1. Setup macOS Menu Bar Extra
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        if let button = statusItem.button {
            button.title = "📈 QD: Starting..."
        }
        buildMenu()

        // 2. Setup Native Desktop Widget Window
        let contentView = DesktopWidgetView(
            store: store,
            onTogglePin: { [weak self] in
                self?.toggleDesktopPin()
            },
            onOpenDashboard: { [weak self] in
                self?.openWeb()
            },
            onOpenWidgetWeb: { [weak self] in
                self?.openWidgetWeb()
            },
            onRefresh: { [weak self] in
                self?.fetchData()
            }
        )

        let hostingView = NSHostingView(rootView: contentView)
        hostingView.frame = NSRect(x: 0, y: 0, width: 350, height: 460)

        let window = DesktopWidgetWindow(store: store)
        window.contentView = hostingView
        window.makeKeyAndOrderFront(nil)
        self.desktopWindow = window

        // 3. Start live data poll
        fetchData()
        timer = Timer.scheduledTimer(withTimeInterval: 8.0, repeats: true) { [weak self] _ in
            self?.fetchData()
        }
    }

    func toggleDesktopPin() {
        store.isPinnedToDesktop.toggle()
        desktopWindow?.updateWindowLevel(isPinned: store.isPinnedToDesktop)
        buildMenu()
    }

    func toggleWidgetVisibility() {
        guard let window = desktopWindow else { return }
        if window.isVisible {
            window.orderOut(nil)
        } else {
            window.makeKeyAndOrderFront(nil)
        }
        buildMenu()
    }

    func fetchData() {
        guard !isFetching else { return }
        isFetching = true

        let group = DispatchGroup()

        // 1. Fetch Alpaca / Account
        if let url = URL(string: "http://127.0.0.1:8081/api/account") {
            group.enter()
            let task = URLSession.shared.dataTask(with: url) { [weak self] data, _, _ in
                defer { group.leave() }
                if let data = data, let account = try? JSONDecoder().decode(AccountResponse.self, from: data) {
                    DispatchQueue.main.async {
                        self?.store.update(with: account)
                    }
                }
            }
            task.resume()
        }

        // 2. Fetch 3-Asset Multi-Desk Status
        if let desksUrl = URL(string: "http://127.0.0.1:8081/api/desks/status") {
            group.enter()
            let task = URLSession.shared.dataTask(with: desksUrl) { [weak self] data, _, _ in
                defer { group.leave() }
                if let data = data, let desksRes = try? JSONDecoder().decode(DesksResponse.self, from: data) {
                    DispatchQueue.main.async {
                        self?.store.updateDesks(with: desksRes)
                    }
                }
            }
            task.resume()
        }

        // 3. Fetch Compliance Report
        if let compUrl = URL(string: "http://127.0.0.1:8081/api/compliance/report") {
            group.enter()
            let task = URLSession.shared.dataTask(with: compUrl) { [weak self] data, _, _ in
                defer { group.leave() }
                if let data = data, let comp = try? JSONDecoder().decode(ComplianceReport.self, from: data) {
                    DispatchQueue.main.async {
                        self?.store.updateCompliance(with: comp)
                    }
                }
            }
            task.resume()
        }

        // 4. Fetch Journal Summary
        if let statsUrl = URL(string: "http://127.0.0.1:8081/api/journal/summary") {
            group.enter()
            let task = URLSession.shared.dataTask(with: statsUrl) { [weak self] data, _, _ in
                defer { group.leave() }
                if let data = data, let summary = try? JSONDecoder().decode(JournalSummary.self, from: data), let stats = summary.stats {
                    DispatchQueue.main.async {
                        self?.store.updateStats(with: stats)
                    }
                }
            }
            task.resume()
        }

        group.notify(queue: .main) { [weak self] in
            self?.isFetching = false
            self?.updateStatusTitle()
            self?.buildMenu()
        }
    }

    func updateStatusTitle() {
        guard let button = statusItem.button else { return }
        let combK = store.combinedEquity / 1000.0
        let statusEmoji = store.runningDesks == store.totalDesks ? "🟢" : "🟡"
        button.title = String(format: "📈 $%.1fK %@ (%d/%d)", combK, statusEmoji, store.runningDesks, store.totalDesks)
    }

    func buildMenu() {
        let menu = NSMenu()
        menu.autoenablesItems = false

        let statusTitle = "🟢 AUTONOMOUS MULTI-DESK (\(store.runningDesks)/\(store.totalDesks) ACTIVE)"
        let header = NSMenuItem(title: statusTitle, action: nil, keyEquivalent: "")
        header.isEnabled = false
        menu.addItem(header)

        let autoDesc = NSMenuItem(title: "🤖 24/7 Multi-PID Loop: Active through Oct 31+", action: nil, keyEquivalent: "")
        autoDesc.isEnabled = false
        menu.addItem(autoDesc)

        menu.addItem(NSMenuItem.separator())

        let combStr = "💰 Combined Cap: \(formatCurrency(store.combinedEquity))"
        let combItem = NSMenuItem(title: combStr, action: nil, keyEquivalent: "")
        combItem.isEnabled = false
        menu.addItem(combItem)

        let d1Str = "  🏛️ Desk 1 (Equities): \(formatCurrency(store.d1Equity)) (PID \(store.d1Pid))"
        let d1Item = NSMenuItem(title: d1Str, action: nil, keyEquivalent: "")
        d1Item.isEnabled = false
        menu.addItem(d1Item)

        let d2Str = "  ⚡ Desk 2 (Crypto 3x): \(formatCurrency(store.d2Equity)) (PID \(store.d2Pid))"
        let d2Item = NSMenuItem(title: d2Str, action: nil, keyEquivalent: "")
        d2Item.isEnabled = false
        menu.addItem(d2Item)

        let d3Str = "  📈 Desk 3 (CME Fut): \(formatCurrency(store.d3Equity)) (PID \(store.d3Pid))"
        let d3Item = NSMenuItem(title: d3Str, action: nil, keyEquivalent: "")
        d3Item.isEnabled = false
        menu.addItem(d3Item)

        let d4Str = "  💱 Desk 4 (Forex Macro): \(formatCurrency(store.d4Equity)) (PID \(store.d4Pid))"
        let d4Item = NSMenuItem(title: d4Str, action: nil, keyEquivalent: "")
        d4Item.isEnabled = false
        menu.addItem(d4Item)

        menu.addItem(NSMenuItem.separator())

        let compStr = "🧠 AI Compliance: \(store.praisesCount) Praises | \(store.punishCount) Penalties"
        let compItem = NSMenuItem(title: compStr, action: nil, keyEquivalent: "")
        compItem.isEnabled = false
        menu.addItem(compItem)

        menu.addItem(NSMenuItem.separator())

        // Desktop Widget Controls
        let isVis = desktopWindow?.isVisible ?? true
        let toggleVisItem = NSMenuItem(
            title: isVis ? "Hide Desktop Widget" : "Show Desktop Widget",
            action: #selector(toggleVisibilityAction),
            keyEquivalent: "h"
        )
        toggleVisItem.target = self
        menu.addItem(toggleVisItem)

        let pinTitle = store.isPinnedToDesktop ? "🪟 Float Widget on Top" : "📌 Pin Widget to Desktop Wallpaper"
        let pinItem = NSMenuItem(title: pinTitle, action: #selector(togglePinAction), keyEquivalent: "p")
        pinItem.target = self
        menu.addItem(pinItem)

        let resetPosItem = NSMenuItem(title: "📍 Reset Widget to Desktop Center", action: #selector(resetPosition), keyEquivalent: "")
        resetPosItem.target = self
        menu.addItem(resetPosItem)

        menu.addItem(NSMenuItem.separator())

        let openWidget = NSMenuItem(title: "📱 Open Web HUD Widget (localhost:8081/widget)", action: #selector(openWidgetWeb), keyEquivalent: "w")
        openWidget.target = self
        menu.addItem(openWidget)

        let openDash = NSMenuItem(title: "🌐 Open Web Terminal (localhost:8081)", action: #selector(openWeb), keyEquivalent: "o")
        openDash.target = self
        menu.addItem(openDash)

        let openLogsItem = NSMenuItem(title: "📋 View Autopilot Logs", action: #selector(openLogs), keyEquivalent: "l")
        openLogsItem.target = self
        menu.addItem(openLogsItem)

        let refreshItem = NSMenuItem(title: "🔄 Refresh Status Now", action: #selector(refresh), keyEquivalent: "r")
        refreshItem.target = self
        menu.addItem(refreshItem)

        let restartItem = NSMenuItem(title: "🛑 Restart / Sync All 3 Desks", action: #selector(restartDesk), keyEquivalent: "")
        restartItem.target = self
        menu.addItem(restartItem)

        menu.addItem(NSMenuItem.separator())

        let quitItem = NSMenuItem(title: "🚪 Quit Widget", action: #selector(quitApp), keyEquivalent: "q")
        quitItem.target = self
        menu.addItem(quitItem)

        statusItem.menu = menu
    }

    @objc func toggleVisibilityAction() {
        toggleWidgetVisibility()
    }

    @objc func togglePinAction() {
        toggleDesktopPin()
    }

    @objc func resetPosition() {
        desktopWindow?.setFrameOrigin(NSPoint(x: 380, y: 240))
        desktopWindow?.makeKeyAndOrderFront(nil)
    }

    @objc func openWeb() {
        if let url = URL(string: "http://localhost:8081") {
            NSWorkspace.shared.open(url)
        }
    }

    @objc func openWidgetWeb() {
        if let url = URL(string: "http://localhost:8081/widget") {
            NSWorkspace.shared.open(url)
        }
    }

    @objc func openLogs() {
        let repo = projectDir
        let script = "tell application \"Terminal\" to do script \"cd '\(repo)' && tail -n 60 -f logs/autopilot.log\""
        if let appleScript = NSAppleScript(source: script) {
            var error: NSDictionary?
            appleScript.executeAndReturnError(&error)
        }
    }

    @objc func refresh() {
        fetchData()
    }

    @objc func restartDesk() {
        let repo = projectDir
        let script = "tell application \"Terminal\" to do script \"cd '\(repo)' && ./quant restart\""
        if let appleScript = NSAppleScript(source: script) {
            var error: NSDictionary?
            appleScript.executeAndReturnError(&error)
        }
    }

    @objc func quitApp() {
        NSApplication.shared.terminate(nil)
    }
}

// MARK: - App Entrypoint
let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.accessory) // Pure Desktop/Menu Widget - No Dock Icon
app.run()
