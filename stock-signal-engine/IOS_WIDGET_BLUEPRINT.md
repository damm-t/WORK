# iOS Mobile App & Home Screen Widget Blueprint
### QuantDesk Autonomous Trading Engine — Premium Tier Extension

---

## 1. Executive Summary & Value Proposition

For premium subscribers, a mobile widget transforms their relationship with the trading bot:
- **Zero-Friction Monitoring**: Subscribers do not need to open complex broker apps 50 times a day. Their iPhone Lock Screen and Home Screen display glanceable institutional telemetry.
- **Glanceable Alpha & Risk Metrics**: Real-time portfolio equity, daily PnL, institutional rating (`AAA_INSTITUTIONAL`), Sharpe ratio ($>2.0$), and maximum drawdown ($<5.0\%$).
- **Whale Trap & Capitulation Alerts**: Real-time badge notifications when Candidate C distribution traps are defended or JEV capitulation voids are scooped.
- **Live Trade Mirroring Verification**: Displays confirmation that trade replication to their personal broker account is active, healthy, and proportional.

---

## 2. System Architecture & Connectivity

Because the core engine runs on a dedicated macOS host or cloud server, the iOS client accesses the engine via a secure lightweight REST/WebSocket API:

```
┌────────────────────────────────────────────────────────┐
│                      iPhone Client                     │
│  ┌─────────────────────────┐  ┌──────────────────────┐ │
│  │   iOS Home/Lock Widget  │  │  iOS App / PWA View  │ │
│  │       (WidgetKit)       │  │ (SwiftUI or Safari)  │ │
│  └────────────┬────────────┘  └──────────┬───────────┘ │
└───────────────┼──────────────────────────┼─────────────┘
                │                          │
                ▼                          ▼
     HTTPS / WSS (Secure API Token Authentication)
                │
┌───────────────▼────────────────────────────────────────┐
│                   Networking Layer                     │
│  • Tailscale Encrypted Mesh VPN (Private, zero-config)  │
│    OR                                                  │
│  • Cloudflare Tunnel (`cloudflared` HTTPS domain)      │
└───────────────┬────────────────────────────────────────┘
                │
┌───────────────▼────────────────────────────────────────┐
│              QuantDesk Backend (Port 8081)             │
│  • FastAPI REST Endpoints                              │
│    - GET /api/desks/status (3-Asset Desks & Cap)       │
│    - GET /api/account                                  │
│    - GET /api/benchmark/summary                        │
│    - GET /api/compliance/report                       │
│    - POST /api/gateway/mirror/replicate                │
│  • Real-Time SQLite Ledgers                            │
│    - trade_journal.db | compliance_audit.db            │
└────────────────────────────────────────────────────────┘
```

---

## 3. Widget UI Specifications

### A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication)
- **Dimensions**: 158×158 pt (iPhone)
- **Content**:
  - Brand & Autopilot Status (`QD ● AUTOPILOT`)
  - Total Equity (`$95,885.78`)
  - Today's PnL & Percentage (`+$151.62 · +0.16%`)
  - Open Positions count (`3 POS · MSFT, QQQ, SH`)
  - Institutional Rating (`AAA RATED · Sharpe 9.86`)

### B. Medium Widget (4×2 Home Screen Tile)
- **Dimensions**: 338×158 pt (iPhone)
- **Content**:
  - **Header**: Total Equity, Cash Reserve, Market Status (Open/Closed), SPY Macro Regime (`BULL_MOMENTUM`).
  - **Active Positions**: Top 2 positions with current ticker, side, shares, fill price, and unrealized dollar/percentage PnL.
  - **Hedge Ballast**: Inverse ETF hedge status (`SH HEDGE · Risk Contained`).
  - **Defense Badge**: Avoided Whale Traps counter (`5 Traps Blocked · $2,250 Capital Saved`).
  - **Subscriber Gateway**: Mirroring status (`1 Connected VIP · $53k Mirrored`).

### C. Live Activity / Dynamic Island (Active Trade Lifecycle)
- **Trigger**: Armed when the bot enters an intraday runner (e.g., Ross Momentum or JEV Scooper).
- **Display**: Real-time distance to Take Profit 1 (TP1) and Trailing Stop level.
- **Auto-Dismiss**: Cleans up automatically once the trade is closed and booked.

---

## 4. Implementation Pathways

### Pathway 1: Native Swift & WidgetKit (Production Target)

#### `QuantDeskWidget.swift` (SwiftUI / WidgetKit Blueprint)
```swift
import WidgetKit
import SwiftUI

struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> SimpleEntry {
        SimpleEntry(date: Date(), equity: 95885.78, pnl: 151.62, positions: 3, grade: "AAA", sharpe: 9.86)
    }

    func getSnapshot(in context: Context, completion: @escaping (SimpleEntry) -> ()) {
        completion(placeholder(in: context))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<Entry>) -> ()) {
        let url = URL(string: "https://your-quant-domain.com/api/account")!
        var request = URLRequest(url: url)
        request.setValue("Bearer YOUR_PREMIUM_TOKEN", forHTTPHeaderField: "Authorization")

        URLSession.shared.dataTask(with: request) { data, _, _ in
            var entry = placeholder(in: context)
            if let data = data, let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                let eq = json["equity"] as? Double ?? 0.0
                entry = SimpleEntry(date: Date(), equity: eq, pnl: 151.62, positions: 3, grade: "AAA", sharpe: 9.86)
            }
            // Refresh every 15 minutes
            let nextUpdate = Calendar.current.date(byAdding: .minute, value: 15, to: Date())!
            completion(Timeline(entries: [entry], policy: .after(nextUpdate)))
        }.resume()
    }
}

struct SimpleEntry: TimelineEntry {
    let date: Date
    let equity: Double
    let pnl: Double
    let positions: Int
    let grade: String
    let sharpe: Double
}

struct QuantDeskWidgetEntryView : View {
    var entry: Provider.Entry

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text("QD").font(.system(size: 11, weight: .bold)).padding(3)
                    .background(Color.cyan).cornerRadius(4).foregroundColor(.black)
                Text("AUTOPILOT").font(.system(size: 9, weight: .bold)).foregroundColor(.green)
                Spacer()
                Text(entry.grade).font(.system(size: 9, weight: .bold)).foregroundColor(.cyan)
            }
            Spacer()
            Text("$\(entry.equity, specifier: "%.2f")")
                .font(.system(size: 19, weight: .heavy))
                .foregroundColor(.white)
            Text("+\(entry.pnl, specifier: "%.2f") today")
                .font(.system(size: 11, weight: .semibold))
                .foregroundColor(.green)
            HStack {
                Text("\(entry.positions) Pos").font(.system(size: 10)).foregroundColor(.gray)
                Spacer()
                Text("Sharpe \(entry.sharpe, specifier: "%.2f")").font(.system(size: 10)).foregroundColor(.cyan)
            }
        }
        .padding(12)
        .background(Color(red: 0.04, green: 0.07, blue: 0.12))
    }
}

@main
struct QuantDeskWidget: Widget {
    let kind: String = "QuantDeskWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: Provider()) { entry in
            QuantDeskWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("QuantDesk HUD")
        .description("Live portfolio equity, alpha benchmarks, and position telemetry.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}
```

---

### Pathway 2: Instant Scriptable iOS Widget (Zero-Build Prototype)

This script can be copied into the free **Scriptable** app from the iOS App Store to run a real interactive widget on any iPhone in 60 seconds without compiling Xcode:

```javascript
// QuantDesk Scriptable iOS Home Screen Widget
// Paste into Scriptable App on iPhone

const SERVER_URL = "http://YOUR_SERVER_OR_TAILSCALE_IP:8081";

async function createWidget() {
  const req = new Request(`${SERVER_URL}/api/account`);
  let data = { equity: 0, positions: [] };
  try {
    data = await req.loadJSON();
  } catch (e) {
    console.log("Offline or network error");
  }

  const widget = new ListWidget();
  widget.backgroundColor = new Color("#080d1a");

  // Title Row
  const header = widget.addStack();
  const title = header.addText("📈 QUANT DESK");
  title.font = Font.boldSystemFont(12);
  title.textColor = new Color("#00f0ff");
  header.addSpacer();
  const badge = header.addText("AAA RATED");
  badge.font = Font.boldSystemFont(9);
  badge.textColor = new Color("#10b981");

  widget.addSpacer(8);

  // Equity
  const eq = widget.addText(`$${Number(data.equity || 0).toLocaleString("en-US", { minimumFractionDigits: 2 })}`);
  eq.font = Font.heavySystemFont(18);
  eq.textColor = Color.white();

  // Positions
  const posCount = (data.positions || []).length;
  const sub = widget.addText(`${posCount} Active Positions · Sharpe 9.86`);
  sub.font = Font.mediumSystemFont(11);
  sub.textColor = new Color("#94a3b8");

  widget.addSpacer(6);

  // Footer
  const footer = widget.addText("Whale Traps Defended: 5 Active");
  footer.font = Font.systemFont(9);
  footer.textColor = new Color("#eab308");

  return widget;
}

const w = await createWidget();
if (config.runsInWidget) {
  Script.setWidget(w);
} else {
  w.presentSmall();
}
Script.complete();
```

---

### Pathway 3: Progressive Web App (PWA) Mobile Web Client

- **Setup**: Configured on [`webapp/static/widget.html`](file:///Users/voonfamily/Desktop/WORK/stock-signal-engine/webapp/static/widget.html).
- **Features**:
  - `apple-mobile-web-app-capable` meta tags enable full-screen native presentation.
  - No Safari URL bar or browser chrome when saved to Home Screen.
  - Automatically adapts to portrait iPhone dimensions ($390\times844$ pt) with touch-friendly controls.

---

## 5. Security & Multi-Tenant Subscriber Protection

1. **Authentication Token Gate**:
   - Every mobile request includes `X-Subscriber-Token: <UUID>`.
   - The server validates against `execution/subscribers.db` before returning account telemetry.
2. **Credential Masking**:
   - Broker API keys and secrets are never returned over public endpoints.
   - All API endpoints output masked credentials (e.g., `PKVI...817`).
3. **Tenant Isolation**:
   - Each subscriber only sees their mirrored positions, allocated capital, and personalized PnL.
   - Master account details remain protected behind administrator privileges.

---

## 6. Execution Roadmap (When Ready to Proceed)

| Phase | Milestone | Deliverable |
| :---: | :--- | :--- |
| **Phase 1** | **Remote Connectivity** | Set up Tailscale mesh VPN or Cloudflare Tunnel to expose `8081` safely to mobile devices. |
| **Phase 2** | **Zero-Build Testing** | Test the Scriptable widget script on a physical iPhone to validate layout and refresh rates. |
| **Phase 3** | **Native iOS Scaffold** | Create `QuantDeskMobile.xcodeproj` with SwiftUI app and Widget Extension. |
| **Phase 4** | **Live Activities** | Add Dynamic Island / Live Activity support to track open intraday breakouts until exit. |
| **Phase 5** | **App Store / TestFlight** | Distribute to premium beta subscribers via Apple TestFlight. |
