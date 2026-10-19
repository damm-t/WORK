# Graph Report - WORK  (2026-10-19)

## Corpus Check
- 230 files · ~614,041 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 33 file(s) not represented in the graph (top: .csv 15, (none) 9, .ipynb 3)

## Summary
- 2308 nodes · 4938 edges · 145 communities (95 shown, 50 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 117 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `83806723`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- get
- tunnel_manager.py
- quant
- Request
- FailureMemoryEngine
- scenario_small.sh
- AppDelegate
- FileResponse
- time
- manifest.json
- test_units.py
- run_autopilot.sh
- run_webapp.sh
- types.ts
- app.py
- atomic_json_read
- Series
- watchdog.sh
- score_trade
- news_fetcher.py
- process_trade_execution
- .filter_series
- ConvexTailEngine
- TradeReviewPacket
- json
- SubscriberProfile
- TradeJournal
- BayesianConfidenceEngine
- shock_detector.py
- CryptoFuturesAutopilot
- ForexAutopilot
- news_memory.py
- dashboard.py
- AgentCouncil
- ForexStrategyEngine
- pandas
- hedging_engine.py
- numpy
- pipeline.py
- TestProjectOmega
- iOS Mobile App & Home Screen Widget Blueprint
- daily_routine.py
- get_book_allocations
- align_timestamp_point_in_time
- CryptoPerpStrategyEngine
- FactorDAG
- CMEFuturesStrategyEngine
- CMEFuturesAutopilot
- five_year_stats.py
- os
- mcp_server.py
- services.py
- crypto_futures_autopilot.py
- tp1_scale_plan
- web_server.py
- model/__init__.py
- .test_defensive_scaling_on_losing_streak
- validate_anti_leakage
- risk/__init__.py
- get_purchase_logs
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- TestArchitectureFixes
- SentimentAggregatorNode
- scenario_sniper.sh
- TestTechnicalIndicators
- TwentyYearStrategyEngine
- _start_port_8081_forwarder
- nlp/__init__.py
- run_instagram_extractor.sh
- dashboard/page.tsx
- compilerOptions
- council.py
- test_jev_scooper.py
- deadmans_switch.py
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- market_scanner.py
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- iOS Mobile App & Home Screen Widget Blueprint
- dataset_generator.py
- package.json
- GEMINI.md
- argparse
- analyze_exit
- scenario_c.sh
- next
- TestPhysicalRiskPipeline
- add_indicators
- store.ts
- Win-Rate Optimization & Diagnostic Report
- dependencies
- devDependencies
- factor_dag.py
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- check_trading_window
- scanner.py
- scripts
- Five-Year Market Statistics
- Five-Year Market Statistics
- TestInstitutionalBenchmarkEngine
- _read_pid
- [...path]/route.ts
- README.md
- TriConfluenceMatrix
- Pre-Market Plan — 2026-08-26
- Pre-Market Plan — 2026-08-27
- Pre-Market Plan — 2026-09-05
- Pre-Market Plan — 2026-09-07
- Pre-Market Plan — 2026-09-08
- Pre-Market Plan — 2026-09-14
- Pre-Market Plan — 2026-09-19
- Pre-Market Plan — 2026-09-21
- sentiment_hedged_vs_unhedged.py
- RiskPanel.tsx
- AGENTS.md
- postcss.config.mjs
- time_to_goal_2026-09-21.md
- log_purchase
- QuantDesk Project & Deployment Architecture
- TestArticleSelection
- cost_model.py
- month_folds
- host_architecture.md
- remote_setup.sh

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 55 edges
2. `atomic_json_read()` - 38 edges
3. `TechnicalIndicators` - 32 edges
4. `atomic_json_write()` - 32 edges
5. `TradeJournal` - 25 edges
6. `AppDelegate` - 22 edges
7. `align_timestamp_point_in_time()` - 22 edges
8. `AgentCouncil` - 20 edges
9. `main()` - 20 edges
10. `get_book_allocations()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `TriConfluenceMatrix` --uses--> `TechnicalIndicators`  [INFERRED]
  stock-signal-engine/strategy/confluence_matrix.py → stock-signal-engine/market/technicals.py
- `BrokerClientFactory` --uses--> `SubscriberProfile`  [INFERRED]
  stock-signal-engine/gateway/broker_client.py → stock-signal-engine/gateway/subscriber_registry.py
- `analyze_stock()` --uses--> `TechnicalIndicators`  [INFERRED]
  stock-signal-engine/risk/stock_analysis.py → stock-signal-engine/market/technicals.py
- `_analyze_trend()` --uses--> `TechnicalIndicators`  [INFERRED]
  stock-signal-engine/risk/stock_analysis.py → stock-signal-engine/market/technicals.py
- `_assess_entry()` --uses--> `TechnicalIndicators`  [INFERRED]
  stock-signal-engine/risk/stock_analysis.py → stock-signal-engine/market/technicals.py

## Import Cycles
- None detected.

## Communities (145 total, 50 thin omitted)

### Community 0 - "get"
Cohesion: 0.07
Nodes (20): health(), api_account(), api_benchmark_summary(), api_compliance_report(), api_confluence_evaluate(), api_council_recent(), api_council_status(), api_desks_benchmark() (+12 more)

### Community 1 - "tunnel_manager.py"
Cohesion: 0.10
Nodes (15): api_remote_access(), api_remote_qr_svg(), get_active_tunnel_url(), get_local_ip(), get_qr_png_bytes(), get_qr_svg(), get_remote_status(), is_caffeinate_running() (+7 more)

### Community 3 - "Request"
Cohesion: 0.24
Nodes (6): domain_not_found_handler(), engine_logic_handler(), global_crash_handler(), api_auth_status(), _is_request_authenticated(), pin_auth_middleware()

### Community 5 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 6 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 7 - "FileResponse"
Cohesion: 0.17
Nodes (6): index(), manifest(), office_view(), overview(), terminal(), widget()

### Community 8 - "time"
Cohesion: 0.11
Nodes (4): FailureEpisode, StrategyItem, BrokerClientFactory, ReplicationSummary

### Community 9 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 10 - "test_units.py"
Cohesion: 0.05
Nodes (14): banned_ticker(), without_banned(), check_tail_risk(), TestAlpacaNews, TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory (+6 more)

### Community 11 - "run_autopilot.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_autopilot.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 12 - "run_webapp.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_webapp.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 13 - "types.ts"
Cohesion: 0.19
Nodes (11): swr, ArticlesFeedProps, SentimentHeatmapProps, sources, api, Article, MarketFeatures, PortfolioResponse (+3 more)

### Community 14 - "app.py"
Cohesion: 0.04
Nodes (39): AIReviewRequest, api_advisor_exit(), api_auth_logout(), api_book_allocation(), api_compliance_ai_review(), api_council_convene(), api_council_decision(), api_equity_curve() (+31 more)

### Community 15 - "atomic_json_read"
Cohesion: 0.14
Nodes (3): atomic_json_read(), atomic_json_write(), StrategyFarmManager

### Community 16 - "Series"
Cohesion: 0.06
Nodes (9): BenchmarkMetrics, InstitutionalBenchmarkEngine, analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _project_1m() (+1 more)

### Community 17 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 20 - "news_fetcher.py"
Cohesion: 0.08
Nodes (25): get_settings(), Settings, fetch_all(), fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news() (+17 more)

### Community 21 - "process_trade_execution"
Cohesion: 0.15
Nodes (12): signal_endpoint(), process_trade_execution(), get_client(), get_current_exposure(), get_portfolio_value(), submit_bracket_buy(), submit_market_order(), submit_order() (+4 more)

### Community 22 - ".filter_series"
Cohesion: 0.11
Nodes (3): AntiVolatilityModel, StabilizationResult, TestAntiVolatilityModel

### Community 24 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 25 - "json"
Cohesion: 0.10
Nodes (13): backfill_historical_purchases(), cmd_demo(), cmd_extract(), cmd_process(), main(), abstract_quant_content(), download_file(), encrypt_url_token() (+5 more)

### Community 26 - "SubscriberProfile"
Cohesion: 0.08
Nodes (4): MirrorDispatcher, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 27 - "TradeJournal"
Cohesion: 0.05
Nodes (10): Candle, generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), TradeJournal, evaluate_five_pillars() (+2 more)

### Community 28 - "BayesianConfidenceEngine"
Cohesion: 0.07
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 29 - "shock_detector.py"
Cohesion: 0.19
Nodes (6): detect_intraday_shock(), earnings_blackout(), _env_float(), gap_shock_threshold(), velocity_shock_threshold(), TestShockDetector

### Community 30 - "CryptoFuturesAutopilot"
Cohesion: 0.09
Nodes (3): CryptoFuturesAutopilot, main(), TestCryptoPerpFixes

### Community 32 - "news_memory.py"
Cohesion: 0.30
Nodes (7): _conn(), _main(), remember(), similar(), stats(), _tokens(), _vec()

### Community 33 - "dashboard.py"
Cohesion: 0.21
Nodes (9): _esc(), _fmt_ts(), load_account(), load_journal(), main(), generate_once(), render_page(), seed_demo() (+1 more)

### Community 36 - "pandas"
Cohesion: 0.12
Nodes (14): get_sniper_setup(), main(), run_test(), run_mean_reversion(), calculate_asset_beta(), fetch_latest_price(), fetch_prices(), _fetch_with_yahoo_chart() (+6 more)

### Community 37 - "hedging_engine.py"
Cohesion: 0.12
Nodes (7): calculate_exit_levels(), _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), is_hot_banned(), TestAdaptiveExitGeometry, TestExitEngine

### Community 38 - "numpy"
Cohesion: 0.05
Nodes (33): baseline_profile(), build_bundle(), Bundle, crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats() (+25 more)

### Community 39 - "pipeline.py"
Cohesion: 0.17
Nodes (10): fetch_prev_close(), build_candidate(), composite_score(), main(), news_deep_dive(), phase_night(), premarket_snapshot(), _seen_titles() (+2 more)

### Community 42 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 43 - "daily_routine.py"
Cohesion: 0.18
Nodes (9): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), get_universe() (+1 more)

### Community 44 - "get_book_allocations"
Cohesion: 0.13
Nodes (7): execute_jev_scoop_trade(), execute_ross_bracket_trade(), classify_position_book(), get_book_allocations(), get_split_ratios(), TestBookSplitArchitecture, _account_snapshot()

### Community 45 - "align_timestamp_point_in_time"
Cohesion: 0.16
Nodes (6): align_timestamp_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), SessionInfo, TestPointInTimeAlignment

### Community 47 - "FactorDAG"
Cohesion: 0.18
Nodes (4): run_experiment(), FactorDAG, evaluate_factor_dag(), TestFactorDAG

### Community 50 - "five_year_stats.py"
Cohesion: 0.07
Nodes (24): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+16 more)

### Community 51 - "os"
Cohesion: 0.11
Nodes (17): auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open(), post_market_belief_cycle() (+9 more)

### Community 52 - "mcp_server.py"
Cohesion: 0.12
Nodes (13): align_event_point_in_time(), analyze_financial_sentiment(), convene_agent_council_meeting(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health(), get_multi_desk_status() (+5 more)

### Community 53 - "services.py"
Cohesion: 0.09
Nodes (20): autopilot_run_once(), execute_endpoint(), hedge_evaluate_endpoint(), market_endpoint(), portfolio_endpoint(), regime_endpoint(), sentiment_endpoint(), EngineException (+12 more)

### Community 55 - "tp1_scale_plan"
Cohesion: 0.15
Nodes (4): ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 56 - "web_server.py"
Cohesion: 0.13
Nodes (6): api_extract_only(), api_process(), ExtractRequest, get_preset(), serve_index(), serve_media()

### Community 57 - "model/__init__.py"
Cohesion: 0.21
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 60 - "risk/__init__.py"
Cohesion: 0.15
Nodes (7): compute_book_exposure(), calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), TestRegimeAdaptivePositionSizing

### Community 61 - "get_purchase_logs"
Cohesion: 0.40
Nodes (4): purchases_endpoint(), get_purchase_log_text(), get_purchase_logs(), api_purchases()

### Community 62 - "🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan"
Cohesion: 0.08
Nodes (25): 10. Quick-Start Commands, 1. Complete System Architecture Map, 2. Capital Architecture & Current State, 3. Financial Model Honest Audit, 3A. Closed Trade Performance (The Hard Truth), 3B. Bayesian Confidence Model — Current Assessment, 4. Root Cause Diagnosis: Why the System is Losing Money, 5. Improvement Plan: 8 Concrete Upgrades (+17 more)

### Community 65 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 67 - "TwentyYearStrategyEngine"
Cohesion: 0.33
Nodes (3): main(), save_report(), TwentyYearStrategyEngine

### Community 68 - "_start_port_8081_forwarder"
Cohesion: 0.28
Nodes (6): _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel(), _warm()

### Community 69 - "nlp/__init__.py"
Cohesion: 0.22
Nodes (6): analyze_sentiment(), _get_finbert(), analyze(), analyze_sentiment_only(), compute_time_decay(), directional_sentiment()

### Community 71 - "dashboard/page.tsx"
Cohesion: 0.24
Nodes (13): DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch(), useMarket() (+5 more)

### Community 72 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 74 - "council.py"
Cohesion: 0.11
Nodes (7): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision(), TestAgentCouncilArchitecture

### Community 75 - "test_jev_scooper.py"
Cohesion: 0.13
Nodes (3): JEVLiquidityScooper, ScoopOpportunity, TestJEVLiquidityScooper

### Community 76 - "deadmans_switch.py"
Cohesion: 0.24
Nodes (5): check_liveness(), get_autopilot_heartbeat(), is_us_equity_market_open(), main(), run_daemon()

### Community 77 - "20-Year Institutional Strategy & Swing-Shield Benchmark"
Cohesion: 0.40
Nodes (4): 20-Year Institutional Strategy & Swing-Shield Benchmark, Multi-Desk 30% YoY Synergy Architecture, Performance Comparison vs Market Benchmark, Year-by-Year Historical Breakdown (2007 - 2026)

### Community 78 - "market_scanner.py"
Cohesion: 0.26
Nodes (6): flat_universe(), main(), mass_backtest(), print_mass_report(), rank_market(), scan_dip_opportunities()

### Community 82 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.25
Nodes (7): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🛠️ The 9 Live MCP Tools Exposed, 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 87 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 88 - "dataset_generator.py"
Cohesion: 0.14
Nodes (6): build_historical_dataset(), generate_triple_barrier_labels(), train(), build_bootstrap_dataframe(), load_or_build_training_dataframe(), main()

### Community 90 - "package.json"
Cohesion: 0.10
Nodes (18): axios, eslint, eslint-config-next, next-auth, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+10 more)

### Community 92 - "argparse"
Cohesion: 0.21
Nodes (6): main(), _policy_summary(), cross_reference_batch(), evaluate_ticker(), main(), print_alpha_report()

### Community 94 - "scenario_c.sh"
Cohesion: 0.14
Nodes (13): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+5 more)

### Community 95 - "next"
Cohesion: 0.15
Nodes (5): next, nextConfig, geistMono, geistSans, metadata

### Community 96 - "TestPhysicalRiskPipeline"
Cohesion: 0.22
Nodes (3): PhysicalRiskPipeline, RiskPipelineVerdict, TestPhysicalRiskPipeline

### Community 98 - "store.ts"
Cohesion: 0.24
Nodes (8): react, zustand, MessagePayload, useWebSocket(), AppState, Article, Signal, useAppStore

### Community 99 - "Win-Rate Optimization & Diagnostic Report"
Cohesion: 0.20
Nodes (9): 1. Empirical Loss Diagnostic (Baseline on 2024 -> today), 2. Validation Stability (2021-2023), 3. Out-of-Sample Performance Comparison (2024 -> today), 4. Crisis Stress Tests (Optimized Profile), 5. Summary & Takeaways, Per-Year Win Rate Comparison, Win Rate by SPY Regime at Entry, Win Rate by Year (+1 more)

### Community 100 - "dependencies"
Cohesion: 0.22
Nodes (9): dependencies, axios, next, next-auth, react, react-dom, recharts, swr (+1 more)

### Community 101 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 102 - "factor_dag.py"
Cohesion: 0.12
Nodes (6): generate_realistic_news_stream(), AlphaCompositeNode, NewsSourceNode, Node, PointInTimeAlignmentNode, TechnicalFeaturesNode

### Community 103 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 104 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 105 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 107 - "check_trading_window"
Cohesion: 0.29
Nodes (4): check_trading_window(), discover_market_universe(), scan_momentum_market(), api_ross_runners()

### Community 108 - "scanner.py"
Cohesion: 0.53
Nodes (3): clamp(), main(), score_row()

### Community 109 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 110 - "Five-Year Market Statistics"
Cohesion: 0.40
Nodes (4): Benchmark — SPY buy & hold, Five-Year Market Statistics, Leaderboard (by engine strategy final equity), Sector rollup (avg per stock)

### Community 111 - "Five-Year Market Statistics"
Cohesion: 0.40
Nodes (4): Benchmark — SPY buy & hold, Five-Year Market Statistics, Leaderboard (by engine strategy final equity), Sector rollup (avg per stock)

### Community 113 - "_read_pid"
Cohesion: 0.67
Nodes (3): _find_process_pid(), _is_pid_alive(), _read_pid()

### Community 114 - "[...path]/route.ts"
Cohesion: 0.46
Nodes (7): buildHeaders(), createBackendUrl(), DELETE(), GET(), POST(), proxy(), PUT()

### Community 115 - "README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 116 - "TriConfluenceMatrix"
Cohesion: 0.24
Nodes (3): ConfluenceDecision, TriConfluenceMatrix, TestTriConfluenceMatrix

### Community 117 - "Pre-Market Plan — 2026-08-26"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-08-26

### Community 118 - "Pre-Market Plan — 2026-08-27"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-08-27

### Community 119 - "Pre-Market Plan — 2026-09-05"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-05

### Community 120 - "Pre-Market Plan — 2026-09-07"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-07

### Community 121 - "Pre-Market Plan — 2026-09-08"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-08

### Community 122 - "Pre-Market Plan — 2026-09-14"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-14

### Community 123 - "Pre-Market Plan — 2026-09-19"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-19

### Community 124 - "Pre-Market Plan — 2026-09-21"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-21

### Community 125 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.10
Nodes (11): build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test(), calculate_dynamic_hedge_ratio(), calculate_hedge_pair(), _latest_close() (+3 more)

### Community 126 - "RiskPanel.tsx"
Cohesion: 0.22
Nodes (5): recharts, PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps

### Community 137 - "QuantDesk Project & Deployment Architecture"
Cohesion: 0.33
Nodes (5): 1. Executive Summary & Host Topography, 2. Remote Access & Tailscale Networking Rules, 3. Core Desks & Automation Components, Critical Infrastructure Topology, QuantDesk Project & Deployment Architecture

### Community 139 - "cost_model.py"
Cohesion: 0.17
Nodes (6): breakeven_move_pct(), days_to_target(), expected_move_pct(), is_trade_viable(), round_trip_cost(), TestCostModel

## Knowledge Gaps
- **83 isolated node(s):** `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED`, `TOKENIZERS_PARALLELISM`, `TRANSFORMERS_OFFLINE` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1050 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `get`, `time`, `app.py`, `Series`, `ForexAutopilot`, `AgentCouncil`, `hedging_engine.py`, `numpy`, `pipeline.py`, `logging`, `daily_routine.py`, `FactorDAG`, `CMEFuturesAutopilot`, `five_year_stats.py`, `mcp_server.py`, `crypto_futures_autopilot.py`, `TwentyYearStrategyEngine`, `council.py`, `market_scanner.py`, `dataset_generator.py`, `argparse`, `factor_dag.py`, `TriConfluenceMatrix`, `sentiment_hedged_vs_unhedged.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **What connects `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `get` be split into smaller, more focused modules?**
  _Cohesion score 0.07207207207207207 - nodes in this community are weakly interconnected._
- **Why does `calculate_streak_compounding_factor()` connect `risk/__init__.py` to `.test_defensive_scaling_on_losing_streak`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Should `tunnel_manager.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0967741935483871 - nodes in this community are weakly interconnected._
- **Why does `atomic_json_read()` connect `atomic_json_read` to `AgentCouncil`, `pandas`, `time`, `council.py`, `deadmans_switch.py`, `app.py`, `CMEFuturesAutopilot`, `os`, `mcp_server.py`, `crypto_futures_autopilot.py`, `json`, `CryptoFuturesAutopilot`, `ForexAutopilot`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Should `quant` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._