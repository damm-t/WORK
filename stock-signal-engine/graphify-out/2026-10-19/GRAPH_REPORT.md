# Graph Report - stock-signal-engine  (2026-10-16)

## Corpus Check
- 224 files · ~597,654 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: .csv 9, (none) 6, .bat 2)

## Summary
- 2291 nodes · 5033 edges · 117 communities (88 shown, 29 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 157 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2ec6d8a5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TradeJournal
- five_year_stats.py
- TestMultiDeskArchitecture
- time
- financial_modeling.py
- AppDelegate
- TradeReviewPacket
- mirror_dispatcher.py
- analyze_stock
- factor_dag.py
- app.py
- BayesianConfidenceEngine
- get
- quant
- os
- council.py
- core.py
- atomic_json_read
- argparse
- CryptoFuturesAutopilot
- tunnel_manager.py
- test_units.py
- FactorDAG
- autopilot.py
- calculate_hedge_pair
- scenario_small.sh
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- .filter_series
- mcp_server.py
- scenario_sniper.sh
- daily_routine.py
- cost_model.py
- TestPhysicalRiskPipeline
- InstitutionalBenchmarkEngine
- package.json
- pipeline.py
- layout.tsx
- dashboard/page.tsx
- risk/__init__.py
- market_scanner.py
- execute_ross_bracket_trade
- compilerOptions
- shock_detector.py
- analyze_exit
- external_alpha_bridge.py
- numpy
- pandas
- 📈 Stock Signal Engine — Personal Quant Desk
- tp1_scale_plan
- JEVLiquidityScooper
- TestArchitectureFixes
- iOS Mobile App & Home Screen Widget Blueprint
- iOS Mobile App & Home Screen Widget Blueprint
- news_fetcher.py
- sentiment_hedged_vs_unhedged.py
- dashboard.py
- train.py
- types.ts
- scenario_c.sh
- ForexStrategyEngine
- web_server.py
- add_indicators
- hedging_engine.py
- .test_defensive_scaling_on_losing_streak
- main.py
- news_memory.py
- manifest.json
- RiskPanel.tsx
- [...path]/route.ts
- Win-Rate Optimization & Diagnostic Report
- ConvexTailEngine
- dependencies
- devDependencies
- store.ts
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- banned_ticker
- TestTechnicalIndicators
- run_multi_asset_benchmark
- run_autopilot.sh
- run_webapp.sh
- deadmans_switch.py
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- QuantDesk Project & Deployment Architecture
- scanner.py
- CryptoPerpStrategyEngine
- scripts
- Five-Year Market Statistics
- Five-Year Market Statistics
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- CMEFuturesStrategyEngine
- watchdog.sh
- dashboard/README.md
- analyze_sentiment
- Pre-Market Plan — 2026-08-26
- Pre-Market Plan — 2026-08-27
- Pre-Market Plan — 2026-09-05
- Pre-Market Plan — 2026-09-07
- Pre-Market Plan — 2026-09-08
- Pre-Market Plan — 2026-09-14
- Pre-Market Plan — 2026-09-19
- Pre-Market Plan — 2026-09-21
- host_architecture.md
- AGENTS.md
- postcss.config.mjs
- GEMINI.md
- time_to_goal_2026-09-21.md
- run_instagram_extractor.sh
- remote_setup.sh

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 79 edges
2. `TechnicalIndicators` - 42 edges
3. `atomic_json_read()` - 32 edges
4. `atomic_json_write()` - 27 edges
5. `TradeJournal` - 27 edges
6. `align_timestamp_point_in_time()` - 22 edges
7. `AppDelegate` - 22 edges
8. `detect_intraday_shock()` - 21 edges
9. `get_book_allocations()` - 21 edges
10. `AgentCouncil` - 20 edges

## Surprising Connections (you probably didn't know these)
- `get_sniper_setup()` --uses--> `TechnicalIndicators`  [INFERRED]
  backtest/daily_sniper.py → market/technicals.py
- `build_bundle()` --uses--> `TechnicalIndicators`  [INFERRED]
  backtest/financial_modeling.py → market/technicals.py
- `PairStrategySimulator` --uses--> `TechnicalIndicators`  [INFERRED]
  backtest/hedging_backtester.py → market/technicals.py
- `rank_market()` --uses--> `TechnicalIndicators`  [INFERRED]
  backtest/market_scanner.py → market/technicals.py
- `TwentyYearStrategyEngine` --uses--> `TechnicalIndicators`  [INFERRED]
  backtest/twenty_year_strategy.py → market/technicals.py

## Import Cycles
- None detected.

## Communities (117 total, 29 thin omitted)

### Community 0 - "TradeJournal"
Cohesion: 0.06
Nodes (9): Candle, generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), TradeJournal, evaluate_five_pillars() (+1 more)

### Community 1 - "five_year_stats.py"
Cohesion: 0.08
Nodes (19): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+11 more)

### Community 2 - "TestMultiDeskArchitecture"
Cohesion: 0.05
Nodes (4): CMEFuturesAutopilot, main(), ForexAutopilot, TestMultiDeskArchitecture

### Community 4 - "financial_modeling.py"
Cohesion: 0.06
Nodes (31): baseline_profile(), build_bundle(), Bundle, crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats() (+23 more)

### Community 5 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 6 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 7 - "mirror_dispatcher.py"
Cohesion: 0.06
Nodes (10): BrokerClientFactory, MirrorDispatcher, MirrorTradeSignal, ReplicationSummary, SubscriberProfile, SubscriberRegistry, ConfluenceDecision, TriConfluenceMatrix (+2 more)

### Community 8 - "analyze_stock"
Cohesion: 0.10
Nodes (7): analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _project_1m(), _verdict()

### Community 9 - "factor_dag.py"
Cohesion: 0.07
Nodes (17): generate_realistic_news_stream(), run_experiment(), AlphaCompositeNode, NewsSourceNode, Node, PointInTimeAlignmentNode, PriceSourceNode, SentimentAggregatorNode (+9 more)

### Community 10 - "app.py"
Cohesion: 0.05
Nodes (36): _account_snapshot(), AIReviewRequest, api_account(), api_auth_logout(), api_auth_status(), api_compliance_ai_review(), api_council_convene(), api_council_decision() (+28 more)

### Community 11 - "BayesianConfidenceEngine"
Cohesion: 0.07
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 12 - "get"
Cohesion: 0.04
Nodes (32): api_advisor_exit(), api_benchmark_summary(), api_book_allocation(), api_compliance_report(), api_confluence_evaluate(), api_council_recent(), api_council_status(), api_desks_benchmark() (+24 more)

### Community 14 - "os"
Cohesion: 0.08
Nodes (19): get_hedge_evaluation(), get_portfolio_summary(), process_trade_execution(), get_settings(), Settings, get_current_exposure(), get_portfolio_value(), submit_bracket_buy() (+11 more)

### Community 15 - "council.py"
Cohesion: 0.09
Nodes (10): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision(), convene_agent_council_meeting(), get_virtual_office_status() (+2 more)

### Community 16 - "core.py"
Cohesion: 0.09
Nodes (14): cmd_demo(), cmd_extract(), cmd_process(), main(), abstract_quant_content(), download_file(), encrypt_url_token(), extract_audio_tracks() (+6 more)

### Community 17 - "atomic_json_read"
Cohesion: 0.13
Nodes (3): AgentCouncil, CouncilTurn, atomic_json_read()

### Community 18 - "argparse"
Cohesion: 0.11
Nodes (14): get_sniper_setup(), main(), main(), _print_report(), run_comparison(), _trim(), _window(), main() (+6 more)

### Community 19 - "CryptoFuturesAutopilot"
Cohesion: 0.09
Nodes (3): CryptoFuturesAutopilot, main(), TestCryptoPerpFixes

### Community 20 - "tunnel_manager.py"
Cohesion: 0.09
Nodes (17): _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel(), get_active_tunnel_url(), get_local_ip(), get_qr_png_bytes() (+9 more)

### Community 21 - "test_units.py"
Cohesion: 0.09
Nodes (8): check_tail_risk(), TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory, TestPurchaseLogger, TestRiskManager, TestScannerQualityGate

### Community 22 - "FactorDAG"
Cohesion: 0.12
Nodes (3): FactorDAG, evaluate_factor_dag(), TestFactorDAG

### Community 23 - "autopilot.py"
Cohesion: 0.07
Nodes (25): submit_market_order(), auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open() (+17 more)

### Community 24 - "calculate_hedge_pair"
Cohesion: 0.12
Nodes (6): calculate_dynamic_hedge_ratio(), calculate_hedge_pair(), compute_book_exposure(), _latest_close(), resolve_hedge_instrument(), TestDynamicHedgeRatio

### Community 25 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 26 - "🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan"
Cohesion: 0.08
Nodes (25): 10. Quick-Start Commands, 1. Complete System Architecture Map, 2. Capital Architecture & Current State, 3. Financial Model Honest Audit, 3A. Closed Trade Performance (The Hard Truth), 3B. Bayesian Confidence Model — Current Assessment, 4. Root Cause Diagnosis: Why the System is Losing Money, 5. Improvement Plan: 8 Concrete Upgrades (+17 more)

### Community 27 - ".filter_series"
Cohesion: 0.11
Nodes (3): AntiVolatilityModel, StabilizationResult, TestAntiVolatilityModel

### Community 28 - "mcp_server.py"
Cohesion: 0.14
Nodes (13): get_client(), align_event_point_in_time(), analyze_financial_sentiment(), check_alpaca_account(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health() (+5 more)

### Community 29 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 30 - "daily_routine.py"
Cohesion: 0.15
Nodes (13): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), flat_universe() (+5 more)

### Community 31 - "cost_model.py"
Cohesion: 0.17
Nodes (6): breakeven_move_pct(), days_to_target(), expected_move_pct(), is_trade_viable(), round_trip_cost(), TestCostModel

### Community 32 - "TestPhysicalRiskPipeline"
Cohesion: 0.22
Nodes (3): PhysicalRiskPipeline, RiskPipelineVerdict, TestPhysicalRiskPipeline

### Community 33 - "InstitutionalBenchmarkEngine"
Cohesion: 0.13
Nodes (3): BenchmarkMetrics, InstitutionalBenchmarkEngine, TestInstitutionalBenchmarkEngine

### Community 34 - "package.json"
Cohesion: 0.10
Nodes (18): eslintConfig, name, private, version, auth, authOptions, config, axios (+10 more)

### Community 35 - "pipeline.py"
Cohesion: 0.14
Nodes (10): format_purchase_log(), log_purchase(), fetch_prev_close(), build_candidate(), composite_score(), main(), news_deep_dive(), phase_night() (+2 more)

### Community 36 - "layout.tsx"
Cohesion: 0.15
Nodes (5): nextConfig, geistMono, geistSans, metadata, next

### Community 37 - "dashboard/page.tsx"
Cohesion: 0.24
Nodes (13): DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch(), useMarket() (+5 more)

### Community 38 - "risk/__init__.py"
Cohesion: 0.17
Nodes (6): calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), TestRegimeAdaptivePositionSizing

### Community 39 - "market_scanner.py"
Cohesion: 0.27
Nodes (5): main(), mass_backtest(), print_mass_report(), rank_market(), scan_dip_opportunities()

### Community 41 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 42 - "shock_detector.py"
Cohesion: 0.08
Nodes (7): is_us_equity_market_open(), detect_intraday_shock(), _env_float(), gap_shock_threshold(), velocity_shock_threshold(), TestProjectOmega, TestShockDetector

### Community 44 - "external_alpha_bridge.py"
Cohesion: 0.52
Nodes (4): cross_reference_batch(), evaluate_ticker(), main(), print_alpha_report()

### Community 45 - "numpy"
Cohesion: 0.12
Nodes (6): main(), simulate_night(), run_test(), run_mean_reversion(), TechnicalIndicators, ScoopOpportunity

### Community 46 - "pandas"
Cohesion: 0.17
Nodes (8): fetch_latest_price(), fetch_prices(), _fetch_with_yahoo_chart(), _fetch_with_yfinance(), _get_cache_path(), _load_cache(), _save_cache(), api_desks_scan()

### Community 47 - "📈 Stock Signal Engine — Personal Quant Desk"
Cohesion: 0.12
Nodes (16): 🏗️ Architecture, Autopilot flags, 🧪 Backtesting Guide, 🧰 Command Reference, ⚙️ Configuration Knobs (env / .env — all optional), 📊 Dashboard, 📜 Disclaimer, 🖥️ Live Web App (`webapp/`) (+8 more)

### Community 48 - "tp1_scale_plan"
Cohesion: 0.15
Nodes (4): ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 52 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 53 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 54 - "news_fetcher.py"
Cohesion: 0.07
Nodes (27): fetch_earnings(), _normalize(), fetch_all(), fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news() (+19 more)

### Community 55 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.06
Nodes (24): build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test(), add_label(), build_feature_vector(), build_features() (+16 more)

### Community 56 - "dashboard.py"
Cohesion: 0.21
Nodes (8): _esc(), _fmt_ts(), load_account(), load_journal(), generate_once(), render_page(), seed_demo(), _wr_color()

### Community 59 - "train.py"
Cohesion: 0.12
Nodes (7): build_historical_dataset(), generate_triple_barrier_labels(), train(), TestTripleBarrier, build_bootstrap_dataframe(), load_or_build_training_dataframe(), main()

### Community 60 - "types.ts"
Cohesion: 0.19
Nodes (11): ArticlesFeedProps, SentimentHeatmapProps, sources, api, Article, MarketFeatures, PortfolioResponse, RiskDecision (+3 more)

### Community 62 - "scenario_c.sh"
Cohesion: 0.14
Nodes (13): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+5 more)

### Community 64 - "web_server.py"
Cohesion: 0.18
Nodes (3): get_preset(), serve_index(), serve_media()

### Community 67 - "hedging_engine.py"
Cohesion: 0.12
Nodes (7): calculate_exit_levels(), _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), is_hot_banned(), TestAdaptiveExitGeometry, TestExitEngine

### Community 69 - "main.py"
Cohesion: 0.08
Nodes (25): autopilot_run_once(), domain_not_found_handler(), engine_logic_handler(), execute_endpoint(), global_crash_handler(), health(), hedge_evaluate_endpoint(), market_endpoint() (+17 more)

### Community 70 - "news_memory.py"
Cohesion: 0.29
Nodes (7): _conn(), _main(), remember(), similar(), stats(), _tokens(), _vec()

### Community 72 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 73 - "RiskPanel.tsx"
Cohesion: 0.22
Nodes (5): PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps, recharts

### Community 74 - "[...path]/route.ts"
Cohesion: 0.46
Nodes (7): buildHeaders(), createBackendUrl(), DELETE(), GET(), POST(), proxy(), PUT()

### Community 75 - "Win-Rate Optimization & Diagnostic Report"
Cohesion: 0.20
Nodes (9): 1. Empirical Loss Diagnostic (Baseline on 2024 -> today), 2. Validation Stability (2021-2023), 3. Out-of-Sample Performance Comparison (2024 -> today), 4. Crisis Stress Tests (Optimized Profile), 5. Summary & Takeaways, Per-Year Win Rate Comparison, Win Rate by SPY Regime at Entry, Win Rate by Year (+1 more)

### Community 77 - "dependencies"
Cohesion: 0.22
Nodes (9): dependencies, axios, next, next-auth, react, react-dom, recharts, swr (+1 more)

### Community 78 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 79 - "store.ts"
Cohesion: 0.24
Nodes (8): MessagePayload, useWebSocket(), AppState, Article, Signal, useAppStore, react, zustand

### Community 82 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 83 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 84 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 85 - "banned_ticker"
Cohesion: 0.23
Nodes (4): main(), save_report(), TwentyYearStrategyEngine, banned_ticker()

### Community 91 - "run_autopilot.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_autopilot.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 92 - "run_webapp.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_webapp.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 93 - "deadmans_switch.py"
Cohesion: 0.36
Nodes (4): check_liveness(), get_autopilot_heartbeat(), main(), run_daemon()

### Community 94 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.29
Nodes (6): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 96 - "QuantDesk Project & Deployment Architecture"
Cohesion: 0.33
Nodes (5): 1. Executive Summary & Host Topography, 2. Remote Access & Tailscale Networking Rules, 3. Core Desks & Automation Components, Critical Infrastructure Topology, QuantDesk Project & Deployment Architecture

### Community 98 - "scanner.py"
Cohesion: 0.53
Nodes (3): clamp(), main(), score_row()

### Community 101 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 102 - "Five-Year Market Statistics"
Cohesion: 0.40
Nodes (4): Benchmark — SPY buy & hold, Five-Year Market Statistics, Leaderboard (by engine strategy final equity), Sector rollup (avg per stock)

### Community 103 - "Five-Year Market Statistics"
Cohesion: 0.40
Nodes (4): Benchmark — SPY buy & hold, Five-Year Market Statistics, Leaderboard (by engine strategy final equity), Sector rollup (avg per stock)

### Community 104 - "20-Year Institutional Strategy & Swing-Shield Benchmark"
Cohesion: 0.40
Nodes (4): 20-Year Institutional Strategy & Swing-Shield Benchmark, Multi-Desk 30% YoY Synergy Architecture, Performance Comparison vs Market Benchmark, Year-by-Year Historical Breakdown (2007 - 2026)

### Community 106 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 107 - "dashboard/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 109 - "Pre-Market Plan — 2026-08-26"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-08-26

### Community 110 - "Pre-Market Plan — 2026-08-27"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-08-27

### Community 111 - "Pre-Market Plan — 2026-09-05"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-05

### Community 112 - "Pre-Market Plan — 2026-09-07"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-07

### Community 113 - "Pre-Market Plan — 2026-09-08"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-08

### Community 114 - "Pre-Market Plan — 2026-09-14"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-14

### Community 115 - "Pre-Market Plan — 2026-09-19"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-19

### Community 116 - "Pre-Market Plan — 2026-09-21"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-21

## Knowledge Gaps
- **83 isolated node(s):** `axios`, `react-dom`, `@tailwindcss/postcss`, `@types/node`, `@types/react` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1022 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `TradeJournal`, `five_year_stats.py`, `TestMultiDeskArchitecture`, `time`, `financial_modeling.py`, `mirror_dispatcher.py`, `analyze_stock`, `factor_dag.py`, `app.py`, `BayesianConfidenceEngine`, `get`, `os`, `council.py`, `atomic_json_read`, `argparse`, `FactorDAG`, `autopilot.py`, `calculate_hedge_pair`, `.filter_series`, `mcp_server.py`, `daily_routine.py`, `InstitutionalBenchmarkEngine`, `pipeline.py`, `market_scanner.py`, `execute_ross_bracket_trade`, `shock_detector.py`, `analyze_exit`, `external_alpha_bridge.py`, `numpy`, `train.py`, `add_indicators`, `hedging_engine.py`, `main.py`, `ConvexTailEngine`, `banned_ticker`, `run_multi_asset_benchmark`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **What connects `axios`, `react-dom`, `@tailwindcss/postcss` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TradeJournal` be split into smaller, more focused modules?**
  _Cohesion score 0.05654761904761905 - nodes in this community are weakly interconnected._
- **Why does `TechnicalIndicators` connect `numpy` to `five_year_stats.py`, `time`, `financial_modeling.py`, `market_scanner.py`, `analyze_stock`, `factor_dag.py`, `mirror_dispatcher.py`, `BayesianConfidenceEngine`, `external_alpha_bridge.py`, `pandas`, `JEVLiquidityScooper`, `argparse`, `banned_ticker`, `test_units.py`, `TestTechnicalIndicators`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Should `five_year_stats.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0797979797979798 - nodes in this community are weakly interconnected._
- **Why does `TradeJournal` connect `TradeJournal` to `execute_ross_bracket_trade`, `time`, `os`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `TestMultiDeskArchitecture` be split into smaller, more focused modules?**
  _Cohesion score 0.05182443151771549 - nodes in this community are weakly interconnected._