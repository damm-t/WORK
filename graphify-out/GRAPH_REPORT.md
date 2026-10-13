# Graph Report - WORK  (2026-10-13)

## Corpus Check
- 212 files · ~436,246 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 31 file(s) not represented in the graph (top: .csv 15, (none) 9, .ipynb 3)

## Summary
- 2175 nodes · 4549 edges · 134 communities (97 shown, 37 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 99 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `635501a4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Profile
- tunnel_manager.py
- app.py
- daily_sniper.py
- scenario_small.sh
- AppDelegate
- get
- pathlib
- manifest.json
- test_units.py
- run_autopilot.sh
- run_webapp.sh
- types.ts
- post
- api_desks_status
- TechnicalIndicators
- watchdog.sh
- sentiment_hedged_vs_unhedged.py
- news_fetcher.py
- process_trade_execution
- .filter_series
- ConvexTailEngine
- AutonomousComplianceChecker
- AgentCouncil
- SubscriberProfile
- TradeJournal
- BayesianConfidenceEngine
- FactorDAG
- CryptoFuturesAutopilot
- TestMultiDeskArchitecture
- argparse
- pipeline.py
- align_timestamp_point_in_time
- ForexStrategyEngine
- pandas
- hedging_engine.py
- financial_modeling.py
- expected_move_pct
- council.py
- run_ross_momentum_sim
- iOS Mobile App & Home Screen Widget Blueprint
- check_liveness
- time
- TriConfluenceMatrix
- CryptoPerpStrategyEngine
- factor_dag.py
- CMEFuturesStrategyEngine
- market_scanner.py
- five_year_stats.py
- os
- mcp_server.py
- main.py
- numpy
- tp1_scale_plan
- TestArchitectureFixes
- daily_routine.py
- .test_defensive_scaling_on_losing_streak
- evaluate_five_pillars
- risk/__init__.py
- TestProjectOmega
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- purchase_logger.py
- _start_port_8081_forwarder
- scenario_sniper.sh
- TestTechnicalIndicators
- TwentyYearStrategyEngine
- Request
- Any
- shock_detector.py
- trade_journal.py
- compilerOptions
- analyze_exit
- TestArticleSelection
- .evaluate_ticker
- dashboard.py
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- calculate_hedge_pair
- SentimentAggregatorNode
- validate_anti_leakage
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- Candle
- run_multi_asset_benchmark
- InstitutionalBenchmarkEngine
- iOS Mobile App & Home Screen Widget Blueprint
- model/__init__.py
- package.json
- GEMINI.md
- nlp/__init__.py
- services.py
- scenario_c.sh
- next
- news_memory.py
- execute_ross_bracket_trade
- store.ts
- Win-Rate Optimization & Diagnostic Report
- dependencies
- devDependencies
- build_historical_dataset
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- [...path]/route.ts
- low_float_scanner.py
- scanner.py
- scripts
- Five-Year Market Statistics
- Five-Year Market Statistics
- TestInstitutionalBenchmarkEngine
- [...nextauth]/route.ts
- get_regime
- README.md
- build.sh script
- Pre-Market Plan — 2026-08-26
- Pre-Market Plan — 2026-08-27
- Pre-Market Plan — 2026-09-05
- Pre-Market Plan — 2026-09-07
- Pre-Market Plan — 2026-09-08
- Pre-Market Plan — 2026-09-14
- Pre-Market Plan — 2026-09-19
- Pre-Market Plan — 2026-09-21
- tailwindcss
- AGENTS.md
- postcss.config.mjs
- time_to_goal_2026-09-21.md

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 39 edges
2. `atomic_json_read()` - 33 edges
3. `TechnicalIndicators` - 30 edges
4. `atomic_json_write()` - 28 edges
5. `TradeJournal` - 25 edges
6. `AppDelegate` - 22 edges
7. `align_timestamp_point_in_time()` - 22 edges
8. `AgentCouncil` - 20 edges
9. `main()` - 20 edges
10. `Profile` - 19 edges

## Surprising Connections (you probably didn't know these)
- `process_trade_execution()` --calls--> `banned_ticker()`  [INFERRED]
  stock-signal-engine/api/services.py → stock-signal-engine/risk/hedging_engine.py
- `process_trade_execution()` --calls--> `calculate_exit_levels()`  [INFERRED]
  stock-signal-engine/api/services.py → stock-signal-engine/risk/hedging_engine.py
- `process_trade_execution()` --calls--> `calculate_hedge_pair()`  [INFERRED]
  stock-signal-engine/api/services.py → stock-signal-engine/risk/hedging_engine.py
- `get_hedge_evaluation()` --calls--> `calculate_exit_levels()`  [INFERRED]
  stock-signal-engine/api/services.py → stock-signal-engine/risk/hedging_engine.py
- `get_hedge_evaluation()` --calls--> `calculate_hedge_pair()`  [INFERRED]
  stock-signal-engine/api/services.py → stock-signal-engine/risk/hedging_engine.py

## Import Cycles
- None detected.

## Communities (134 total, 37 thin omitted)

### Community 0 - "Profile"
Cohesion: 0.09
Nodes (9): baseline_profile(), build_bundle(), Profile, profile_from_row(), sensitivity_grid(), build_hunt_grid(), main(), run_diagnostic() (+1 more)

### Community 1 - "tunnel_manager.py"
Cohesion: 0.10
Nodes (14): api_remote_qr_svg(), get_active_tunnel_url(), get_local_ip(), get_qr_png_bytes(), get_qr_svg(), get_remote_status(), is_caffeinate_running(), is_tunnel_evicted() (+6 more)

### Community 3 - "app.py"
Cohesion: 0.08
Nodes (18): unwind_paired_hedge(), _account_snapshot(), api_account(), api_desks_scan(), api_equity_curve(), api_flatten(), api_journal_summary(), api_journal_trades() (+10 more)

### Community 4 - "daily_sniper.py"
Cohesion: 0.16
Nodes (9): run_analyze(), get_sniper_setup(), main(), flat_universe(), rank_market(), calculate_asset_beta(), detect_market_regime(), earnings_blackout() (+1 more)

### Community 5 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 6 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 7 - "get"
Cohesion: 0.06
Nodes (21): health(), api_advisor_exit(), api_book_allocation(), api_evaluate(), api_jev_opportunities(), api_journal_exits(), api_model_confidence(), api_model_learning_log() (+13 more)

### Community 8 - "pathlib"
Cohesion: 0.11
Nodes (3): main(), atomic_json_read(), atomic_json_write()

### Community 9 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 10 - "test_units.py"
Cohesion: 0.06
Nodes (12): check_tail_risk(), TestAlpacaNews, TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory, TestPurchaseLogger, TestRiskManager (+4 more)

### Community 11 - "run_autopilot.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_autopilot.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 12 - "run_webapp.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_webapp.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 13 - "types.ts"
Cohesion: 0.08
Nodes (29): recharts, swr, DashboardPage(), ArticlesFeedProps, IndicatorPanel(), PortfolioBar(), PriceChartProps, formatValue() (+21 more)

### Community 14 - "post"
Cohesion: 0.09
Nodes (15): AIReviewRequest, api_compliance_ai_review(), api_council_convene(), api_council_decision(), api_gateway_register_subscriber(), api_gateway_replicate(), api_jev_execute(), api_model_confidence_evaluate() (+7 more)

### Community 15 - "api_desks_status"
Cohesion: 0.40
Nodes (4): api_desks_status(), _find_process_pid(), _is_pid_alive(), _read_pid()

### Community 16 - "TechnicalIndicators"
Cohesion: 0.12
Nodes (8): TechnicalIndicators, analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _project_1m(), _verdict()

### Community 17 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 19 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.16
Nodes (7): main(), print_comparison(), run_signal_pipeline(), stress_test(), add_indicators(), get_latest(), get_market_features()

### Community 20 - "news_fetcher.py"
Cohesion: 0.08
Nodes (25): get_settings(), Settings, fetch_all(), fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news() (+17 more)

### Community 21 - "process_trade_execution"
Cohesion: 0.15
Nodes (12): portfolio_endpoint(), signal_endpoint(), get_portfolio_summary(), process_trade_execution(), get_client(), get_current_exposure(), get_portfolio_value(), submit_market_order() (+4 more)

### Community 22 - ".filter_series"
Cohesion: 0.11
Nodes (3): AntiVolatilityModel, StabilizationResult, TestAntiVolatilityModel

### Community 24 - "AutonomousComplianceChecker"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 26 - "SubscriberProfile"
Cohesion: 0.07
Nodes (7): BrokerClientFactory, MirrorDispatcher, MirrorTradeSignal, ReplicationSummary, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 28 - "BayesianConfidenceEngine"
Cohesion: 0.07
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 29 - "FactorDAG"
Cohesion: 0.18
Nodes (4): run_experiment(), FactorDAG, evaluate_factor_dag(), TestFactorDAG

### Community 31 - "TestMultiDeskArchitecture"
Cohesion: 0.05
Nodes (3): CMEFuturesAutopilot, ForexAutopilot, TestMultiDeskArchitecture

### Community 32 - "argparse"
Cohesion: 0.19
Nodes (4): main(), train(), main(), main()

### Community 33 - "pipeline.py"
Cohesion: 0.15
Nodes (11): run_morning(), get_universe(), submit_bracket_buy(), fetch_prev_close(), build_candidate(), composite_score(), main(), news_deep_dive() (+3 more)

### Community 34 - "align_timestamp_point_in_time"
Cohesion: 0.16
Nodes (6): align_timestamp_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), SessionInfo, TestPointInTimeAlignment

### Community 36 - "pandas"
Cohesion: 0.21
Nodes (9): run_test(), run_mean_reversion(), fetch_latest_price(), fetch_prices(), _fetch_with_yahoo_chart(), _fetch_with_yfinance(), _get_cache_path(), _load_cache() (+1 more)

### Community 37 - "hedging_engine.py"
Cohesion: 0.11
Nodes (9): days_to_target(), banned_ticker(), calculate_exit_levels(), _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), is_hot_banned(), TestAdaptiveExitGeometry (+1 more)

### Community 38 - "financial_modeling.py"
Cohesion: 0.10
Nodes (17): Bundle, crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats(), pick_best(), rank_candidates() (+9 more)

### Community 39 - "expected_move_pct"
Cohesion: 0.25
Nodes (3): expected_move_pct(), is_trade_viable(), TestCostModel

### Community 40 - "council.py"
Cohesion: 0.11
Nodes (7): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision(), TestAgentCouncilArchitecture

### Community 41 - "run_ross_momentum_sim"
Cohesion: 0.20
Nodes (5): generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim()

### Community 42 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 43 - "check_liveness"
Cohesion: 0.28
Nodes (5): check_liveness(), get_autopilot_heartbeat(), is_us_equity_market_open(), main(), run_daemon()

### Community 44 - "time"
Cohesion: 0.12
Nodes (3): classify_position_book(), ForexSignal, api_health()

### Community 45 - "TriConfluenceMatrix"
Cohesion: 0.24
Nodes (3): ConfluenceDecision, TriConfluenceMatrix, TestTriConfluenceMatrix

### Community 47 - "factor_dag.py"
Cohesion: 0.12
Nodes (6): generate_realistic_news_stream(), AlphaCompositeNode, NewsSourceNode, Node, PointInTimeAlignmentNode, TechnicalFeaturesNode

### Community 49 - "market_scanner.py"
Cohesion: 0.31
Nodes (4): main(), mass_backtest(), print_mass_report(), scan_dip_opportunities()

### Community 50 - "five_year_stats.py"
Cohesion: 0.06
Nodes (28): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+20 more)

### Community 51 - "os"
Cohesion: 0.12
Nodes (13): auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open(), post_market_belief_cycle() (+5 more)

### Community 52 - "mcp_server.py"
Cohesion: 0.11
Nodes (14): align_event_point_in_time(), analyze_financial_sentiment(), check_alpaca_account(), convene_agent_council_meeting(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health() (+6 more)

### Community 53 - "main.py"
Cohesion: 0.14
Nodes (15): autopilot_run_once(), domain_not_found_handler(), engine_logic_handler(), execute_endpoint(), global_crash_handler(), market_endpoint(), purchases_endpoint(), sentiment_endpoint() (+7 more)

### Community 54 - "numpy"
Cohesion: 0.13
Nodes (9): main(), simulate_night(), growth_optimal_f(), main(), mc_time_to_goal(), oos_r_pool(), pool_stats(), savings_months() (+1 more)

### Community 55 - "tp1_scale_plan"
Cohesion: 0.15
Nodes (4): ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 57 - "daily_routine.py"
Cohesion: 0.31
Nodes (5): _briefing_path(), load_today_briefing(), main(), _plan_path(), scrape_ticker()

### Community 59 - "evaluate_five_pillars"
Cohesion: 0.33
Nodes (3): evaluate_five_pillars(), evaluate_news_catalyst(), TestRossMomentumStrategy

### Community 60 - "risk/__init__.py"
Cohesion: 0.17
Nodes (6): calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), TestRegimeAdaptivePositionSizing

### Community 62 - "🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan"
Cohesion: 0.08
Nodes (25): 10. Quick-Start Commands, 1. Complete System Architecture Map, 2. Capital Architecture & Current State, 3. Financial Model Honest Audit, 3A. Closed Trade Performance (The Hard Truth), 3B. Bayesian Confidence Model — Current Assessment, 4. Root Cause Diagnosis: Why the System is Losing Money, 5. Improvement Plan: 8 Concrete Upgrades (+17 more)

### Community 63 - "purchase_logger.py"
Cohesion: 0.27
Nodes (4): backfill_historical_purchases(), format_purchase_log(), get_purchase_logs(), log_purchase()

### Community 64 - "_start_port_8081_forwarder"
Cohesion: 0.32
Nodes (5): _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel()

### Community 65 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 67 - "TwentyYearStrategyEngine"
Cohesion: 0.33
Nodes (3): main(), save_report(), TwentyYearStrategyEngine

### Community 68 - "Request"
Cohesion: 0.15
Nodes (8): api_auth_logout(), api_auth_status(), api_verify_pin(), graph_tree_view(), graph_view(), _is_request_authenticated(), pin_auth_middleware(), PinVerifyRequest

### Community 69 - "Any"
Cohesion: 0.10
Nodes (10): api_benchmark_summary(), api_compliance_report(), api_confluence_evaluate(), api_council_recent(), api_council_status(), api_desks_benchmark(), api_gateway_list_subscribers(), api_gateway_mirror_history() (+2 more)

### Community 70 - "shock_detector.py"
Cohesion: 0.24
Nodes (5): detect_intraday_shock(), _env_float(), gap_shock_threshold(), velocity_shock_threshold(), TestShockDetector

### Community 71 - "trade_journal.py"
Cohesion: 0.12
Nodes (3): execute_jev_scoop_trade(), get_book_allocations(), get_split_ratios()

### Community 72 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 75 - ".evaluate_ticker"
Cohesion: 0.13
Nodes (3): JEVLiquidityScooper, ScoopOpportunity, TestJEVLiquidityScooper

### Community 76 - "dashboard.py"
Cohesion: 0.18
Nodes (9): _esc(), _fmt_ts(), load_account(), load_journal(), load_leaderboard(), generate_once(), render_page(), seed_demo() (+1 more)

### Community 77 - "20-Year Institutional Strategy & Swing-Shield Benchmark"
Cohesion: 0.40
Nodes (4): 20-Year Institutional Strategy & Swing-Shield Benchmark, Multi-Desk 30% YoY Synergy Architecture, Performance Comparison vs Market Benchmark, Year-by-Year Historical Breakdown (2007 - 2026)

### Community 78 - "calculate_hedge_pair"
Cohesion: 0.11
Nodes (7): build_books(), calculate_dynamic_hedge_ratio(), calculate_hedge_pair(), compute_book_exposure(), _latest_close(), resolve_hedge_instrument(), TestDynamicHedgeRatio

### Community 82 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.25
Nodes (7): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🛠️ The 9 Live MCP Tools Exposed, 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 87 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 88 - "model/__init__.py"
Cohesion: 0.21
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 90 - "package.json"
Cohesion: 0.14
Nodes (13): axios, eslint, eslint-config-next, react-dom, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+5 more)

### Community 92 - "nlp/__init__.py"
Cohesion: 0.19
Nodes (7): analyze_sentiment(), _get_finbert(), analyze(), analyze_sentiment_only(), compute_time_decay(), directional_sentiment(), pick_best_article()

### Community 93 - "services.py"
Cohesion: 0.20
Nodes (5): hedge_evaluate_endpoint(), get_hedge_evaluation(), evaluate_trade(), score_trade(), TestScorer

### Community 94 - "scenario_c.sh"
Cohesion: 0.14
Nodes (13): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+5 more)

### Community 95 - "next"
Cohesion: 0.15
Nodes (5): next, nextConfig, geistMono, geistSans, metadata

### Community 96 - "news_memory.py"
Cohesion: 0.30
Nodes (7): _conn(), _main(), remember(), similar(), stats(), _tokens(), _vec()

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

### Community 102 - "build_historical_dataset"
Cohesion: 0.28
Nodes (4): build_historical_dataset(), generate_triple_barrier_labels(), build_bootstrap_dataframe(), load_or_build_training_dataframe()

### Community 103 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 104 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 105 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 106 - "[...path]/route.ts"
Cohesion: 0.46
Nodes (7): buildHeaders(), createBackendUrl(), DELETE(), GET(), POST(), proxy(), PUT()

### Community 107 - "low_float_scanner.py"
Cohesion: 0.32
Nodes (3): check_trading_window(), discover_market_universe(), scan_momentum_market()

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

### Community 113 - "[...nextauth]/route.ts"
Cohesion: 0.50
Nodes (3): next-auth, auth, authOptions

### Community 115 - "README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

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

## Knowledge Gaps
- **83 isolated node(s):** `axios`, `react-dom`, `@tailwindcss/postcss`, `@types/node`, `@types/react` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 991 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **37 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TradeJournal` connect `TradeJournal` to `trade_journal.py`, `run_ross_momentum_sim`, `time`, `.reconcile_with_broker`, `.__init__`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **What connects `axios`, `react-dom`, `@tailwindcss/postcss` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Profile` be split into smaller, more focused modules?**
  _Cohesion score 0.08912655971479501 - nodes in this community are weakly interconnected._
- **Why does `TestArchitectureFixes` connect `TestArchitectureFixes` to `pathlib`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `tunnel_manager.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09659090909090909 - nodes in this community are weakly interconnected._
- **Why does `atomic_json_read()` connect `pathlib` to `app.py`, `council.py`, `check_liveness`, `time`, `os`, `mcp_server.py`, `AgentCouncil`, `CryptoFuturesAutopilot`, `TestMultiDeskArchitecture`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `quant` be split into smaller, more focused modules?**
  _Cohesion score 0.08669354838709678 - nodes in this community are weakly interconnected._