# Graph Report - WORK  (2026-10-20)

## Corpus Check
- 244 files · ~631,101 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 33 file(s) not represented in the graph (top: .csv 15, (none) 9, .ipynb 3)

## Summary
- 2489 nodes · 5474 edges · 149 communities (103 shown, 46 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 189 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0242414c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- pathlib
- tunnel_manager.py
- quant
- TriConfluenceMatrix
- FailureMemoryEngine
- scenario_small.sh
- AppDelegate
- [...path]/route.ts
- 📈 Stock Signal Engine — Personal Quant Desk
- manifest.json
- test_units.py
- run_autopilot.sh
- run_webapp.sh
- types.ts
- get
- atomic_json_read
- analyze_stock
- watchdog.sh
- score_trade
- news_fetcher.py
- EquitiesSelfLearningTracker
- .filter_series
- ConvexTailEngine
- TradeReviewPacket
- core.py
- SubscriberProfile
- TradeJournal
- BayesianConfidenceEngine
- CMEFuturesAutopilot
- CryptoFuturesAutopilot
- ForexAutopilot
- PairStrategySimulator
- dashboard.py
- AgentCouncil
- numpy
- shock_detector.py
- hedging_engine.py
- financial_modeling.py
- services.py
- TestProjectOmega
- dataset_generator.py
- iOS Mobile App & Home Screen Widget Blueprint
- argparse
- pandas
- align_timestamp_point_in_time
- TestSMCCryptoStrategy
- fetch_all
- CMEFuturesSelfLearningTracker
- pipeline.py
- five_year_stats.py
- autopilot.py
- mcp_server.py
- main.py
- ForexStrategyEngine
- tp1_scale_plan
- app.py
- sentiment_hedged_vs_unhedged.py
- .test_defensive_scaling_on_losing_streak
- run_comprehensive_simulation
- risk/__init__.py
- get_purchase_logs
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- TestArchitectureFixes
- news_memory.py
- scenario_sniper.sh
- TestTechnicalIndicators
- TwentyYearStrategyEngine
- TestMultiDeskArchitecture
- nlp/__init__.py
- run_instagram_extractor.sh
- dashboard/page.tsx
- compilerOptions
- walk_forward.py
- model/__init__.py
- .evaluate_ticker
- unittest
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- daily_routine.py
- test_project_omega.py
- fundamentals.py
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- generate_triple_barrier_labels
- api_remote_qr_svg
- validate_anti_leakage
- ForexSelfLearningTracker
- iOS Mobile App & Home Screen Widget Blueprint
- detect_market_regime
- evaluate_fundamental_quality
- package.json
- GEMINI.md
- reality_check.py
- analyze_exit
- scenario_c.sh
- next
- TestPhysicalRiskPipeline
- TestDynamicHedgeRatio
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
- _is_request_authenticated
- README.md
- features/__init__.py
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
- _normalize_alpaca
- _cancel_open_orders
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
7. `align_timestamp_point_in_time()` - 22 edges
8. `ForexAutopilot` - 22 edges
9. `AppDelegate` - 22 edges
10. `get_book_allocations()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `🛠️ The 9 Live MCP Tools Exposed` --references--> `fetch_stock_prices()`  [INFERRED]
  stock-signal-engine/MCP_SETUP_GUIDE.md → stock-signal-engine/mcp_server.py
- `🛠️ The 9 Live MCP Tools Exposed` --references--> `get_technical_indicators()`  [INFERRED]
  stock-signal-engine/MCP_SETUP_GUIDE.md → stock-signal-engine/mcp_server.py
- `🛠️ The 9 Live MCP Tools Exposed` --references--> `analyze_financial_sentiment()`  [INFERRED]
  stock-signal-engine/MCP_SETUP_GUIDE.md → stock-signal-engine/mcp_server.py
- `🛠️ The 9 Live MCP Tools Exposed` --references--> `check_alpaca_account()`  [INFERRED]
  stock-signal-engine/MCP_SETUP_GUIDE.md → stock-signal-engine/mcp_server.py
- `🛠️ The 9 Live MCP Tools Exposed` --references--> `align_event_point_in_time()`  [INFERRED]
  stock-signal-engine/MCP_SETUP_GUIDE.md → stock-signal-engine/mcp_server.py

## Import Cycles
- None detected.

## Communities (149 total, 46 thin omitted)

### Community 0 - "pathlib"
Cohesion: 0.09
Nodes (4): PointInTimeAlignmentNode, TechnicalFeaturesNode, enrich_article_point_in_time(), FailureEpisode

### Community 1 - "tunnel_manager.py"
Cohesion: 0.09
Nodes (18): _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel(), _warm(), get_active_tunnel_url(), get_local_ip() (+10 more)

### Community 3 - "TriConfluenceMatrix"
Cohesion: 0.25
Nodes (3): ConfluenceDecision, TriConfluenceMatrix, TestTriConfluenceMatrix

### Community 5 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 6 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 7 - "[...path]/route.ts"
Cohesion: 0.46
Nodes (7): buildHeaders(), createBackendUrl(), DELETE(), GET(), POST(), proxy(), PUT()

### Community 8 - "📈 Stock Signal Engine — Personal Quant Desk"
Cohesion: 0.12
Nodes (16): 🏗️ Architecture, Autopilot flags, 🧪 Backtesting Guide, 🧰 Command Reference, ⚙️ Configuration Knobs (env / .env — all optional), 📊 Dashboard, 📜 Disclaimer, 🖥️ Live Web App (`webapp/`) (+8 more)

### Community 9 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 10 - "test_units.py"
Cohesion: 0.07
Nodes (10): days_to_target(), is_trade_viable(), banned_ticker(), TestCostModel, TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory (+2 more)

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
Cohesion: 0.04
Nodes (34): TestSystemSelfLearningAPI, api_advisor_exit(), api_benchmark_summary(), api_compliance_report(), api_confluence_evaluate(), api_council_recent(), api_council_status(), api_desks_benchmark() (+26 more)

### Community 15 - "atomic_json_read"
Cohesion: 0.13
Nodes (4): atomic_json_read(), atomic_json_write(), StrategyFarmManager, main()

### Community 16 - "analyze_stock"
Cohesion: 0.10
Nodes (7): analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _project_1m(), _verdict()

### Community 17 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 20 - "news_fetcher.py"
Cohesion: 0.24
Nodes (11): fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news(), _get_alpaca_news_client(), _get_cache_path(), _load_cache() (+3 more)

### Community 21 - "EquitiesSelfLearningTracker"
Cohesion: 0.09
Nodes (3): EquitiesSelfLearningTracker, InstitutionalEquitiesStrategy, TestEquitiesDesk1Fixes

### Community 22 - ".filter_series"
Cohesion: 0.12
Nodes (3): AntiVolatilityModel, StabilizationResult, TestAntiVolatilityModel

### Community 24 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 25 - "core.py"
Cohesion: 0.07
Nodes (17): cmd_demo(), cmd_extract(), cmd_process(), main(), abstract_quant_content(), download_file(), encrypt_url_token(), extract_audio_tracks() (+9 more)

### Community 26 - "SubscriberProfile"
Cohesion: 0.08
Nodes (6): BrokerClientFactory, MirrorDispatcher, ReplicationSummary, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 27 - "TradeJournal"
Cohesion: 0.06
Nodes (9): Candle, generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), TradeJournal, evaluate_five_pillars() (+1 more)

### Community 28 - "BayesianConfidenceEngine"
Cohesion: 0.08
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 32 - "PairStrategySimulator"
Cohesion: 0.17
Nodes (4): PairStrategySimulator, simulate(), SimulationConfig, TestSimulatorSmoke

### Community 33 - "dashboard.py"
Cohesion: 0.21
Nodes (9): _esc(), _fmt_ts(), load_account(), load_journal(), main(), generate_once(), render_page(), seed_demo() (+1 more)

### Community 35 - "numpy"
Cohesion: 0.19
Nodes (9): run_multi_asset_benchmark(), simulate_asset_trades(), growth_optimal_f(), main(), mc_time_to_goal(), oos_r_pool(), pool_stats(), savings_months() (+1 more)

### Community 36 - "shock_detector.py"
Cohesion: 0.18
Nodes (7): fetch_latest_price(), detect_intraday_shock(), earnings_blackout(), _env_float(), gap_shock_threshold(), velocity_shock_threshold(), TestShockDetector

### Community 37 - "hedging_engine.py"
Cohesion: 0.10
Nodes (9): calculate_dynamic_hedge_ratio(), calculate_exit_levels(), _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), _latest_close(), resolve_hedge_instrument(), TestAdaptiveExitGeometry (+1 more)

### Community 38 - "financial_modeling.py"
Cohesion: 0.07
Nodes (23): baseline_profile(), build_bundle(), Bundle, crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats() (+15 more)

### Community 39 - "services.py"
Cohesion: 0.19
Nodes (11): portfolio_endpoint(), get_portfolio_summary(), process_trade_execution(), get_client(), get_current_exposure(), get_portfolio_value(), submit_order(), submit_pair_orders() (+3 more)

### Community 41 - "dataset_generator.py"
Cohesion: 0.14
Nodes (6): get_universe(), build_historical_dataset(), train(), build_bootstrap_dataframe(), load_or_build_training_dataframe(), main()

### Community 42 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 43 - "argparse"
Cohesion: 0.21
Nodes (5): run_diagnostic(), cross_reference_batch(), evaluate_ticker(), main(), print_alpha_report()

### Community 44 - "pandas"
Cohesion: 0.10
Nodes (22): get_sniper_setup(), main(), main(), performance_metrics(), _print_report(), run_comparison(), _strip_tz(), _trim() (+14 more)

### Community 45 - "align_timestamp_point_in_time"
Cohesion: 0.18
Nodes (5): align_timestamp_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), TestPointInTimeAlignment

### Community 47 - "fetch_all"
Cohesion: 0.25
Nodes (7): fetch_earnings(), _normalize(), fetch_all(), fetch_tweets(), _is_valid_token(), _normalize(), TestTwitterSuppression

### Community 48 - "CMEFuturesSelfLearningTracker"
Cohesion: 0.11
Nodes (4): CMEFuturesSelfLearningTracker, CMEFuturesSignal, CMEFuturesStrategyEngine, TestCMEFuturesDeskFixes

### Community 49 - "pipeline.py"
Cohesion: 0.12
Nodes (13): rank_market(), submit_bracket_buy(), format_purchase_log(), log_purchase(), fetch_prev_close(), build_candidate(), composite_score(), main() (+5 more)

### Community 50 - "five_year_stats.py"
Cohesion: 0.16
Nodes (12): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+4 more)

### Community 51 - "autopilot.py"
Cohesion: 0.12
Nodes (16): submit_market_order(), auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), post_market_belief_cycle() (+8 more)

### Community 52 - "mcp_server.py"
Cohesion: 0.06
Nodes (25): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision(), align_event_point_in_time(), analyze_financial_sentiment() (+17 more)

### Community 53 - "main.py"
Cohesion: 0.15
Nodes (13): autopilot_run_once(), execute_endpoint(), health(), hedge_evaluate_endpoint(), market_endpoint(), sentiment_endpoint(), signal_endpoint(), EngineException (+5 more)

### Community 55 - "tp1_scale_plan"
Cohesion: 0.13
Nodes (5): compute_book_exposure(), ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 56 - "app.py"
Cohesion: 0.06
Nodes (32): AIReviewRequest, api_compliance_ai_review(), api_council_convene(), api_council_decision(), api_desks_scan(), api_desks_status(), api_farm_demote(), api_farm_promote() (+24 more)

### Community 57 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.13
Nodes (11): get_hedge_evaluation(), build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test(), add_indicators(), get_latest() (+3 more)

### Community 59 - "run_comprehensive_simulation"
Cohesion: 0.24
Nodes (6): run_comprehensive_simulation(), simulate_crypto_desk(), simulate_forex_desk(), simulate_futures_desk(), simulate_stock_desk(), TradeRecord

### Community 60 - "risk/__init__.py"
Cohesion: 0.13
Nodes (8): calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), check_tail_risk(), TestRegimeAdaptivePositionSizing, TestRiskManager

### Community 61 - "get_purchase_logs"
Cohesion: 0.32
Nodes (5): purchases_endpoint(), backfill_historical_purchases(), get_purchase_log_text(), get_purchase_logs(), api_purchases()

### Community 62 - "🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan"
Cohesion: 0.08
Nodes (25): 10. Quick-Start Commands, 1. Complete System Architecture Map, 2. Capital Architecture & Current State, 3. Financial Model Honest Audit, 3A. Closed Trade Performance (The Hard Truth), 3B. Bayesian Confidence Model — Current Assessment, 4. Root Cause Diagnosis: Why the System is Losing Money, 5. Improvement Plan: 8 Concrete Upgrades (+17 more)

### Community 64 - "news_memory.py"
Cohesion: 0.29
Nodes (7): _conn(), _main(), remember(), similar(), stats(), _tokens(), _vec()

### Community 65 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 67 - "TwentyYearStrategyEngine"
Cohesion: 0.39
Nodes (3): main(), save_report(), TwentyYearStrategyEngine

### Community 69 - "nlp/__init__.py"
Cohesion: 0.22
Nodes (7): evaluate_news_catalyst(), analyze(), analyze_sentiment_only(), compute_time_decay(), extract_entities(), _get_nlp(), preprocess()

### Community 71 - "dashboard/page.tsx"
Cohesion: 0.24
Nodes (13): DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch(), useMarket() (+5 more)

### Community 72 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 73 - "walk_forward.py"
Cohesion: 0.25
Nodes (5): main(), month_folds(), _policy_summary(), _run_style(), walk_forward()

### Community 74 - "model/__init__.py"
Cohesion: 0.21
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 75 - ".evaluate_ticker"
Cohesion: 0.15
Nodes (3): JEVLiquidityScooper, ScoopOpportunity, TestJEVLiquidityScooper

### Community 76 - "unittest"
Cohesion: 0.11
Nodes (5): check_liveness(), get_autopilot_heartbeat(), main(), run_daemon(), EquitySignal

### Community 77 - "20-Year Institutional Strategy & Swing-Shield Benchmark"
Cohesion: 0.40
Nodes (4): 20-Year Institutional Strategy & Swing-Shield Benchmark, Multi-Desk 30% YoY Synergy Architecture, Performance Comparison vs Market Benchmark, Year-by-Year Historical Breakdown (2007 - 2026)

### Community 78 - "daily_routine.py"
Cohesion: 0.23
Nodes (9): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), flat_universe() (+1 more)

### Community 81 - "fundamentals.py"
Cohesion: 0.39
Nodes (5): _ensure_cache_dir(), fetch_fundamentals(), _load_cik_map(), _load_fundamentals_cache(), _save_fundamentals_cache()

### Community 82 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.29
Nodes (6): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 84 - "api_remote_qr_svg"
Cohesion: 0.20
Nodes (5): api_auth_logout(), api_remote_qr_svg(), graph_tree_view(), graph_view(), get_qr_svg()

### Community 87 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 88 - "detect_market_regime"
Cohesion: 0.29
Nodes (3): regime_endpoint(), get_regime(), detect_market_regime()

### Community 90 - "package.json"
Cohesion: 0.10
Nodes (18): axios, eslint, eslint-config-next, next-auth, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+10 more)

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

### Community 102 - "FactorDAG"
Cohesion: 0.07
Nodes (9): generate_realistic_news_stream(), run_experiment(), AlphaCompositeNode, FactorDAG, NewsSourceNode, Node, PriceSourceNode, SentimentAggregatorNode (+1 more)

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

### Community 114 - "_is_request_authenticated"
Cohesion: 0.38
Nodes (3): api_auth_status(), _is_request_authenticated(), pin_auth_middleware()

### Community 115 - "README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 116 - "features/__init__.py"
Cohesion: 0.70
Nodes (3): add_label(), build_feature_vector(), build_features()

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
Cohesion: 0.33
Nodes (4): main(), mass_backtest(), print_mass_report(), scan_dip_opportunities()

### Community 126 - "RiskPanel.tsx"
Cohesion: 0.22
Nodes (5): recharts, PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps

### Community 134 - "get_book_allocations"
Cohesion: 0.09
Nodes (12): get_settings(), Settings, execute_jev_scoop_trade(), execute_ross_bracket_trade(), classify_position_book(), get_book_allocations(), get_split_ratios(), TestBookSplitArchitecture (+4 more)

### Community 135 - "time"
Cohesion: 0.08
Nodes (5): StrategyItem, main(), migrate_desk_state(), CryptoFuturesSignal, ForexSignal

### Community 137 - "QuantDesk Project & Deployment Architecture"
Cohesion: 0.33
Nodes (5): 1. Executive Summary & Host Topography, 2. Remote Access & Tailscale Networking Rules, 3. Core Desks & Automation Components, Critical Infrastructure Topology, QuantDesk Project & Deployment Architecture

### Community 138 - "pick_best_article"
Cohesion: 0.21
Nodes (4): directional_sentiment(), pick_best_article(), TestArticleSelection, TestTimeDecay

## Knowledge Gaps
- **83 isolated node(s):** `axios`, `react-dom`, `@tailwindcss/postcss`, `@types/node`, `@types/react` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1097 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `pathlib`, `TriConfluenceMatrix`, `get_book_allocations`, `time`, `get`, `analyze_stock`, `.filter_series`, `ConvexTailEngine`, `TradeJournal`, `BayesianConfidenceEngine`, `CMEFuturesAutopilot`, `AgentCouncil`, `numpy`, `shock_detector.py`, `hedging_engine.py`, `financial_modeling.py`, `dataset_generator.py`, `argparse`, `pipeline.py`, `five_year_stats.py`, `autopilot.py`, `mcp_server.py`, `app.py`, `sentiment_hedged_vs_unhedged.py`, `run_comprehensive_simulation`, `TwentyYearStrategyEngine`, `daily_routine.py`, `detect_market_regime`, `analyze_exit`, `FactorDAG`, `InstitutionalBenchmarkEngine`, `.fetch_live_bars`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **What connects `axios`, `react-dom`, `@tailwindcss/postcss` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.09191583610188261 - nodes in this community are weakly interconnected._
- **Why does `atomic_json_read()` connect `atomic_json_read` to `pathlib`, `AgentCouncil`, `time`, `._load_state`, `unittest`, `get`, `.fetch_live_bars`, `autopilot.py`, `mcp_server.py`, `app.py`, `.fetch_live_order_book`, `CMEFuturesAutopilot`, `CryptoFuturesAutopilot`, `ForexAutopilot`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Should `tunnel_manager.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08888888888888889 - nodes in this community are weakly interconnected._
- **Why does `atomic_json_write()` connect `atomic_json_read` to `pathlib`, `AgentCouncil`, `time`, `unittest`, `TestArchitectureFixes`, `autopilot.py`, `mcp_server.py`, `CMEFuturesAutopilot`, `CryptoFuturesAutopilot`, `ForexAutopilot`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `quant` be split into smaller, more focused modules?**
  _Cohesion score 0.06794871794871794 - nodes in this community are weakly interconnected._