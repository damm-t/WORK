# Graph Report - WORK  (2026-10-20)

## Corpus Check
- 244 files · ~631,101 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 33 file(s) not represented in the graph (top: .csv 15, (none) 9, .ipynb 3)

## Summary
- 2494 nodes · 5470 edges · 149 communities (100 shown, 49 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 189 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `05da349a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- logging
- tunnel_manager.py
- quant
- TriConfluenceMatrix
- FailureMemoryEngine
- scenario_small.sh
- AppDelegate
- app.py
- 📈 Stock Signal Engine — Personal Quant Desk
- manifest.json
- test_units.py
- run_autopilot.sh
- run_webapp.sh
- types.ts
- get
- atomic_json_read
- analyze_exit
- watchdog.sh
- score_trade
- align_timestamp_point_in_time
- EquitiesSelfLearningTracker
- .filter_series
- ConvexTailEngine
- TradeReviewPacket
- core.py
- mirror_dispatcher.py
- TradeJournal
- BayesianConfidenceEngine
- mcp_server.py
- CryptoFuturesAutopilot
- ForexAutopilot
- run_ross_momentum_sim
- dashboard.py
- AgentCouncil
- time_to_goal.py
- os
- hedging_engine.py
- financial_modeling.py
- services.py
- TestProjectOmega
- dataset_generator.py
- iOS Mobile App & Home Screen Widget Blueprint
- external_alpha_bridge.py
- pandas
- Profile
- TestSMCCryptoStrategy
- cost_model.py
- CMEFuturesAutopilot
- phase_night
- five_year_stats.py
- autopilot.py
- council.py
- main.py
- ForexStrategyEngine
- tp1_scale_plan
- post
- sentiment_hedged_vs_unhedged.py
- .test_defensive_scaling_on_losing_streak
- unified_four_desk_simulation.py
- risk/__init__.py
- FileResponse
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- TestArchitectureFixes
- news_memory.py
- scenario_sniper.sh
- TestTechnicalIndicators
- banned_ticker
- TestMultiDeskArchitecture
- nlp/__init__.py
- run_instagram_extractor.sh
- dashboard/page.tsx
- compilerOptions
- argparse
- model/__init__.py
- test_jev_scooper.py
- main
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- daily_routine.py
- get_market_features
- _simulate_bars
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- generate_triple_barrier_labels
- api_remote_qr_svg
- Candle
- ForexSelfLearningTracker
- iOS Mobile App & Home Screen Widget Blueprint
- TestShockDetector
- analyze_sentiment
- package.json
- GEMINI.md
- reality_check.py
- news_deep_dive
- scenario_c.sh
- [...path]/route.ts
- TestPhysicalRiskPipeline
- calculate_dynamic_hedge_ratio
- store.ts
- Win-Rate Optimization & Diagnostic Report
- dependencies
- devDependencies
- FactorDAG
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- domain_not_found_handler
- check_trading_window
- scanner.py
- scripts
- Five-Year Market Statistics
- Five-Year Market Statistics
- InstitutionalBenchmarkEngine
- README.md
- Pre-Market Plan — 2026-08-26
- Pre-Market Plan — 2026-08-27
- Pre-Market Plan — 2026-09-05
- Pre-Market Plan — 2026-09-07
- Pre-Market Plan — 2026-09-08
- Pre-Market Plan — 2026-09-14
- Pre-Market Plan — 2026-09-19
- Pre-Market Plan — 2026-09-21
- main
- RiskPanel.tsx
- AGENTS.md
- postcss.config.mjs
- dfs
- time_to_goal_2026-09-21.md
- get_book_allocations
- time
- QuantDesk Project & Deployment Architecture
- pick_best_article
- SelfImprovingExpectancyTracker
- TestCryptoPerpFixes
- host_architecture.md
- remote_setup.sh

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 83 edges
2. `TechnicalIndicators` - 42 edges
3. `atomic_json_read()` - 40 edges
4. `atomic_json_write()` - 34 edges
5. `TradeJournal` - 27 edges
6. `CryptoFuturesAutopilot` - 23 edges
7. `ForexAutopilot` - 22 edges
8. `AppDelegate` - 22 edges
9. `align_timestamp_point_in_time()` - 22 edges
10. `get_book_allocations()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `🛠️ The 9 Live MCP Tools Exposed` --references--> `evaluate_factor_dag()`  [INFERRED]
  stock-signal-engine/MCP_SETUP_GUIDE.md → stock-signal-engine/mcp_server.py
- `🛠️ The 9 Live MCP Tools Exposed` --references--> `align_event_point_in_time()`  [INFERRED]
  stock-signal-engine/MCP_SETUP_GUIDE.md → stock-signal-engine/mcp_server.py
- `🛠️ The 9 Live MCP Tools Exposed` --references--> `analyze_financial_sentiment()`  [INFERRED]
  stock-signal-engine/MCP_SETUP_GUIDE.md → stock-signal-engine/mcp_server.py
- `🛠️ The 9 Live MCP Tools Exposed` --references--> `check_alpaca_account()`  [INFERRED]
  stock-signal-engine/MCP_SETUP_GUIDE.md → stock-signal-engine/mcp_server.py
- `🛠️ The 9 Live MCP Tools Exposed` --references--> `fetch_stock_prices()`  [INFERRED]
  stock-signal-engine/MCP_SETUP_GUIDE.md → stock-signal-engine/mcp_server.py

## Import Cycles
- None detected.

## Communities (149 total, 49 thin omitted)

### Community 1 - "tunnel_manager.py"
Cohesion: 0.09
Nodes (18): _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel(), _warm(), get_active_tunnel_url(), get_local_ip() (+10 more)

### Community 3 - "TriConfluenceMatrix"
Cohesion: 0.22
Nodes (3): ConfluenceDecision, TriConfluenceMatrix, TestTriConfluenceMatrix

### Community 5 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 6 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 7 - "app.py"
Cohesion: 0.08
Nodes (15): get_preset(), serve_index(), serve_media(), api_desks_status(), api_equity_curve(), api_health(), api_journal_summary(), api_journal_trades() (+7 more)

### Community 8 - "📈 Stock Signal Engine — Personal Quant Desk"
Cohesion: 0.12
Nodes (16): 🏗️ Architecture, Autopilot flags, 🧪 Backtesting Guide, 🧰 Command Reference, ⚙️ Configuration Knobs (env / .env — all optional), 📊 Dashboard, 📜 Disclaimer, 🖥️ Live Web App (`webapp/`) (+8 more)

### Community 9 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 10 - "test_units.py"
Cohesion: 0.09
Nodes (8): check_tail_risk(), TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory, TestPurchaseLogger, TestRiskManager, TestScannerQualityGate

### Community 11 - "run_autopilot.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_autopilot.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 12 - "run_webapp.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_webapp.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 13 - "types.ts"
Cohesion: 0.19
Nodes (11): swr, ArticlesFeedProps, SentimentHeatmapProps, sources, api, Article, MarketFeatures, PortfolioResponse (+3 more)

### Community 14 - "get"
Cohesion: 0.05
Nodes (24): TestSystemSelfLearningAPI, api_advisor_exit(), api_benchmark_summary(), api_compliance_report(), api_confluence_evaluate(), api_council_recent(), api_council_status(), api_desks_benchmark() (+16 more)

### Community 16 - "analyze_exit"
Cohesion: 0.08
Nodes (9): analyze_exit(), analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _project_1m(), _verdict() (+1 more)

### Community 17 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 19 - "score_trade"
Cohesion: 0.22
Nodes (4): build_candidate(), composite_score(), score_trade(), TestScorer

### Community 20 - "align_timestamp_point_in_time"
Cohesion: 0.05
Nodes (32): align_timestamp_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), fetch_earnings(), _normalize(), fetch_all(), fetch_alpaca_news() (+24 more)

### Community 21 - "EquitiesSelfLearningTracker"
Cohesion: 0.09
Nodes (3): EquitiesSelfLearningTracker, InstitutionalEquitiesStrategy, TestEquitiesDesk1Fixes

### Community 22 - ".filter_series"
Cohesion: 0.11
Nodes (3): AntiVolatilityModel, StabilizationResult, TestAntiVolatilityModel

### Community 24 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 25 - "core.py"
Cohesion: 0.09
Nodes (14): cmd_demo(), cmd_extract(), cmd_process(), main(), abstract_quant_content(), download_file(), encrypt_url_token(), extract_audio_tracks() (+6 more)

### Community 26 - "mirror_dispatcher.py"
Cohesion: 0.08
Nodes (7): BrokerClientFactory, MirrorDispatcher, MirrorTradeSignal, ReplicationSummary, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 28 - "BayesianConfidenceEngine"
Cohesion: 0.08
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 29 - "mcp_server.py"
Cohesion: 0.13
Nodes (14): get_client(), align_event_point_in_time(), analyze_financial_sentiment(), check_alpaca_account(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health() (+6 more)

### Community 32 - "run_ross_momentum_sim"
Cohesion: 0.17
Nodes (7): generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), evaluate_five_pillars(), TestRossMomentumStrategy

### Community 33 - "dashboard.py"
Cohesion: 0.21
Nodes (9): _esc(), _fmt_ts(), load_account(), load_journal(), main(), generate_once(), render_page(), seed_demo() (+1 more)

### Community 35 - "time_to_goal.py"
Cohesion: 0.29
Nodes (7): growth_optimal_f(), main(), mc_time_to_goal(), oos_r_pool(), pool_stats(), savings_months(), tuned_profile()

### Community 36 - "os"
Cohesion: 0.07
Nodes (16): get_sniper_setup(), main(), check_liveness(), get_autopilot_heartbeat(), is_us_equity_market_open(), main(), run_daemon(), backfill_historical_purchases() (+8 more)

### Community 37 - "hedging_engine.py"
Cohesion: 0.11
Nodes (8): calculate_exit_levels(), _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), _latest_close(), resolve_hedge_instrument(), TestAdaptiveExitGeometry, TestExitEngine

### Community 38 - "financial_modeling.py"
Cohesion: 0.15
Nodes (11): crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats(), pick_best(), rank_candidates(), refine_grid() (+3 more)

### Community 39 - "services.py"
Cohesion: 0.14
Nodes (15): portfolio_endpoint(), signal_endpoint(), get_hedge_evaluation(), get_portfolio_summary(), get_processed_signal(), process_trade_execution(), get_current_exposure(), get_portfolio_value() (+7 more)

### Community 41 - "dataset_generator.py"
Cohesion: 0.16
Nodes (5): build_historical_dataset(), train(), build_bootstrap_dataframe(), load_or_build_training_dataframe(), main()

### Community 42 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 43 - "external_alpha_bridge.py"
Cohesion: 0.52
Nodes (4): cross_reference_batch(), evaluate_ticker(), main(), print_alpha_report()

### Community 44 - "pandas"
Cohesion: 0.12
Nodes (12): run_multi_asset_benchmark(), simulate_asset_trades(), run_test(), run_mean_reversion(), fetch_latest_price(), fetch_prices(), _fetch_with_yahoo_chart(), _fetch_with_yfinance() (+4 more)

### Community 45 - "Profile"
Cohesion: 0.15
Nodes (5): baseline_profile(), Profile, profile_from_row(), sensitivity_grid(), TestFinancialModelingAdaptive

### Community 47 - "cost_model.py"
Cohesion: 0.17
Nodes (6): breakeven_move_pct(), days_to_target(), expected_move_pct(), is_trade_viable(), round_trip_cost(), TestCostModel

### Community 48 - "CMEFuturesAutopilot"
Cohesion: 0.07
Nodes (5): CMEFuturesAutopilot, CMEFuturesSelfLearningTracker, CMEFuturesSignal, CMEFuturesStrategyEngine, TestCMEFuturesDeskFixes

### Community 49 - "phase_night"
Cohesion: 0.24
Nodes (6): fetch_prev_close(), main(), phase_night(), premarket_snapshot(), load_leaderboard(), _leaderboard()

### Community 50 - "five_year_stats.py"
Cohesion: 0.09
Nodes (18): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+10 more)

### Community 51 - "autopilot.py"
Cohesion: 0.09
Nodes (18): submit_market_order(), auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open() (+10 more)

### Community 52 - "council.py"
Cohesion: 0.09
Nodes (10): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision(), convene_agent_council_meeting(), get_virtual_office_status() (+2 more)

### Community 53 - "main.py"
Cohesion: 0.10
Nodes (17): autopilot_run_once(), execute_endpoint(), health(), hedge_evaluate_endpoint(), market_endpoint(), purchases_endpoint(), regime_endpoint(), sentiment_endpoint() (+9 more)

### Community 55 - "tp1_scale_plan"
Cohesion: 0.13
Nodes (5): compute_book_exposure(), ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 56 - "post"
Cohesion: 0.07
Nodes (19): AIReviewRequest, api_compliance_ai_review(), api_council_convene(), api_council_decision(), api_farm_demote(), api_farm_promote(), api_gateway_register_subscriber(), api_gateway_replicate() (+11 more)

### Community 57 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.22
Nodes (8): build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test(), add_label(), build_feature_vector(), build_features()

### Community 59 - "unified_four_desk_simulation.py"
Cohesion: 0.22
Nodes (6): run_comprehensive_simulation(), simulate_crypto_desk(), simulate_forex_desk(), simulate_futures_desk(), simulate_stock_desk(), TradeRecord

### Community 60 - "risk/__init__.py"
Cohesion: 0.17
Nodes (6): calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), TestRegimeAdaptivePositionSizing

### Community 61 - "FileResponse"
Cohesion: 0.17
Nodes (6): index(), manifest(), office_view(), overview(), terminal(), widget()

### Community 62 - "🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan"
Cohesion: 0.08
Nodes (25): 10. Quick-Start Commands, 1. Complete System Architecture Map, 2. Capital Architecture & Current State, 3. Financial Model Honest Audit, 3A. Closed Trade Performance (The Hard Truth), 3B. Bayesian Confidence Model — Current Assessment, 4. Root Cause Diagnosis: Why the System is Losing Money, 5. Improvement Plan: 8 Concrete Upgrades (+17 more)

### Community 64 - "news_memory.py"
Cohesion: 0.29
Nodes (7): _conn(), _main(), remember(), similar(), stats(), _tokens(), _vec()

### Community 65 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 67 - "banned_ticker"
Cohesion: 0.23
Nodes (4): main(), save_report(), TwentyYearStrategyEngine, banned_ticker()

### Community 69 - "nlp/__init__.py"
Cohesion: 0.22
Nodes (7): evaluate_news_catalyst(), analyze(), analyze_sentiment_only(), compute_time_decay(), extract_entities(), _get_nlp(), preprocess()

### Community 71 - "dashboard/page.tsx"
Cohesion: 0.22
Nodes (14): zustand, DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch() (+6 more)

### Community 72 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 73 - "argparse"
Cohesion: 0.12
Nodes (12): main(), _print_report(), run_comparison(), _trim(), _window(), mass_backtest(), main(), month_folds() (+4 more)

### Community 74 - "model/__init__.py"
Cohesion: 0.22
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 75 - "test_jev_scooper.py"
Cohesion: 0.14
Nodes (3): JEVLiquidityScooper, ScoopOpportunity, TestJEVLiquidityScooper

### Community 76 - "main"
Cohesion: 0.18
Nodes (4): build_bundle(), build_hunt_grid(), main(), run_diagnostic()

### Community 77 - "20-Year Institutional Strategy & Swing-Shield Benchmark"
Cohesion: 0.40
Nodes (4): 20-Year Institutional Strategy & Swing-Shield Benchmark, Multi-Desk 30% YoY Synergy Architecture, Performance Comparison vs Market Benchmark, Year-by-Year Historical Breakdown (2007 - 2026)

### Community 78 - "daily_routine.py"
Cohesion: 0.19
Nodes (11): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), flat_universe() (+3 more)

### Community 80 - "get_market_features"
Cohesion: 0.31
Nodes (3): add_indicators(), get_latest(), get_market_features()

### Community 81 - "_simulate_bars"
Cohesion: 0.32
Nodes (4): Bundle, run_profile(), _simulate_bars(), window_run()

### Community 82 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.29
Nodes (6): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 84 - "api_remote_qr_svg"
Cohesion: 0.12
Nodes (10): api_auth_logout(), api_auth_status(), api_remote_qr_svg(), api_verify_pin(), graph_tree_view(), graph_view(), _is_request_authenticated(), pin_auth_middleware() (+2 more)

### Community 87 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 90 - "package.json"
Cohesion: 0.10
Nodes (18): axios, eslint, eslint-config-next, next-auth, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+10 more)

### Community 94 - "scenario_c.sh"
Cohesion: 0.14
Nodes (13): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+5 more)

### Community 95 - "[...path]/route.ts"
Cohesion: 0.12
Nodes (12): next, nextConfig, buildHeaders(), createBackendUrl(), DELETE(), GET(), POST(), proxy() (+4 more)

### Community 96 - "TestPhysicalRiskPipeline"
Cohesion: 0.22
Nodes (3): PhysicalRiskPipeline, RiskPipelineVerdict, TestPhysicalRiskPipeline

### Community 98 - "store.ts"
Cohesion: 0.28
Nodes (7): react, MessagePayload, useWebSocket(), AppState, Article, Signal, useAppStore

### Community 99 - "Win-Rate Optimization & Diagnostic Report"
Cohesion: 0.20
Nodes (9): 1. Empirical Loss Diagnostic (Baseline on 2024 -> today), 2. Validation Stability (2021-2023), 3. Out-of-Sample Performance Comparison (2024 -> today), 4. Crisis Stress Tests (Optimized Profile), 5. Summary & Takeaways, Per-Year Win Rate Comparison, Win Rate by SPY Regime at Entry, Win Rate by Year (+1 more)

### Community 100 - "dependencies"
Cohesion: 0.22
Nodes (9): dependencies, axios, next, next-auth, react, react-dom, recharts, swr (+1 more)

### Community 101 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 102 - "FactorDAG"
Cohesion: 0.06
Nodes (14): generate_realistic_news_stream(), run_experiment(), AlphaCompositeNode, FactorDAG, NewsSourceNode, Node, PointInTimeAlignmentNode, PriceSourceNode (+6 more)

### Community 103 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 104 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 105 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 106 - "domain_not_found_handler"
Cohesion: 0.53
Nodes (3): domain_not_found_handler(), engine_logic_handler(), global_crash_handler()

### Community 107 - "check_trading_window"
Cohesion: 0.25
Nodes (5): check_trading_window(), discover_market_universe(), scan_momentum_market(), api_ross_runners(), api_ross_window()

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

### Community 112 - "InstitutionalBenchmarkEngine"
Cohesion: 0.13
Nodes (3): BenchmarkMetrics, InstitutionalBenchmarkEngine, TestInstitutionalBenchmarkEngine

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

### Community 125 - "main"
Cohesion: 0.50
Nodes (3): main(), print_mass_report(), scan_dip_opportunities()

### Community 126 - "RiskPanel.tsx"
Cohesion: 0.22
Nodes (5): recharts, PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps

### Community 134 - "get_book_allocations"
Cohesion: 0.08
Nodes (15): get_settings(), Settings, submit_bracket_buy(), execute_jev_scoop_trade(), execute_ross_bracket_trade(), classify_position_book(), get_book_allocations(), get_split_ratios() (+7 more)

### Community 135 - "time"
Cohesion: 0.08
Nodes (7): atomic_json_write(), StrategyItem, main(), migrate_desk_state(), CryptoFuturesSignal, EquitySignal, ForexSignal

### Community 137 - "QuantDesk Project & Deployment Architecture"
Cohesion: 0.33
Nodes (5): 1. Executive Summary & Host Topography, 2. Remote Access & Tailscale Networking Rules, 3. Core Desks & Automation Components, Critical Infrastructure Topology, QuantDesk Project & Deployment Architecture

### Community 138 - "pick_best_article"
Cohesion: 0.21
Nodes (4): directional_sentiment(), pick_best_article(), TestArticleSelection, TestTimeDecay

## Knowledge Gaps
- **83 isolated node(s):** `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED`, `TOKENIZERS_PARALLELISM`, `TRANSFORMERS_OFFLINE` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1102 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **49 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `logging`, `TriConfluenceMatrix`, `get_book_allocations`, `time`, `app.py`, `get`, `analyze_exit`, `.filter_series`, `ConvexTailEngine`, `BayesianConfidenceEngine`, `mcp_server.py`, `run_ross_momentum_sim`, `AgentCouncil`, `os`, `hedging_engine.py`, `financial_modeling.py`, `dataset_generator.py`, `external_alpha_bridge.py`, `CMEFuturesAutopilot`, `phase_night`, `five_year_stats.py`, `autopilot.py`, `council.py`, `unified_four_desk_simulation.py`, `banned_ticker`, `argparse`, `daily_routine.py`, `get_market_features`, `FactorDAG`, `InstitutionalBenchmarkEngine`, `.fetch_live_bars`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **What connects `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `logging` be split into smaller, more focused modules?**
  _Cohesion score 0.1141025641025641 - nodes in this community are weakly interconnected._
- **Why does `TradeJournal` connect `TradeJournal` to `logging`, `run_ross_momentum_sim`, `get_book_allocations`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `tunnel_manager.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08888888888888889 - nodes in this community are weakly interconnected._
- **Why does `AutonomousComplianceChecker` connect `TradeReviewPacket` to `time`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `quant` be split into smaller, more focused modules?**
  _Cohesion score 0.06794871794871794 - nodes in this community are weakly interconnected._