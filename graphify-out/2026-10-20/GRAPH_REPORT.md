# Graph Report - WORK  (2026-10-20)

## Corpus Check
- 243 files · ~786,441 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 33 file(s) not represented in the graph (top: .csv 15, (none) 9, .ipynb 3)

## Summary
- 2442 nodes · 5266 edges · 144 communities (95 shown, 49 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 151 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0242414c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Any
- tunnel_manager.py
- quant
- TriConfluenceMatrix
- FailureMemoryEngine
- scenario_small.sh
- AppDelegate
- [...path]/route.ts
- unittest
- manifest.json
- test_units.py
- run_autopilot.sh
- run_webapp.sh
- types.ts
- get
- atomic_json_read
- stock_analysis.py
- watchdog.sh
- score_trade
- news_fetcher.py
- EquitiesSelfLearningTracker
- .filter_series
- ConvexTailEngine
- TradeReviewPacket
- core.py
- mirror_dispatcher.py
- TradeJournal
- BayesianConfidenceEngine
- CMEFuturesAutopilot
- CryptoFuturesAutopilot
- ForexAutopilot
- web_server.py
- argparse
- AgentCouncil
- run_multi_asset_benchmark
- pandas
- hedging_engine.py
- financial_modeling.py
- alpha_client.py
- detect_intraday_shock
- dataset_generator.py
- iOS Mobile App & Home Screen Widget Blueprint
- council.py
- numpy
- align_timestamp_point_in_time
- TestSMCCryptoStrategy
- FactorDAG
- CMEFuturesSelfLearningTracker
- pipeline.py
- five_year_stats.py
- autopilot.py
- mcp_server.py
- services.py
- ForexStrategyEngine
- tp1_scale_plan
- app.py
- sentiment_hedged_vs_unhedged.py
- .test_defensive_scaling_on_losing_streak
- calculate_exit_levels
- risk/__init__.py
- get_purchase_logs
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- TestArchitectureFixes
- scenario_sniper.sh
- TestTechnicalIndicators
- banned_ticker
- TestMultiDeskArchitecture
- nlp/__init__.py
- run_instagram_extractor.sh
- dashboard/page.tsx
- compilerOptions
- model/__init__.py
- .evaluate_ticker
- time
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- daily_routine.py
- TestAgentCouncilArchitecture
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- api_desks_status
- api_remote_qr_svg
- ForexSelfLearningTracker
- iOS Mobile App & Home Screen Widget Blueprint
- post
- package.json
- GEMINI.md
- reality_check.py
- analyze_exit
- scenario_c.sh
- next
- test_physical_risk_pipeline.py
- api_self_learning
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
- Request
- README.md
- Pre-Market Plan — 2026-08-26
- Pre-Market Plan — 2026-08-27
- Pre-Market Plan — 2026-09-05
- Pre-Market Plan — 2026-09-07
- Pre-Market Plan — 2026-09-08
- Pre-Market Plan — 2026-09-14
- Pre-Market Plan — 2026-09-19
- Pre-Market Plan — 2026-09-21
- RiskPanel.tsx
- AGENTS.md
- postcss.config.mjs
- time_to_goal_2026-09-21.md
- get_book_allocations
- pathlib
- QuantDesk Project & Deployment Architecture
- TestArticleSelection
- SelfImprovingExpectancyTracker
- TestCryptoPerpFixes
- host_architecture.md
- remote_setup.sh

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 61 edges
2. `atomic_json_read()` - 40 edges
3. `atomic_json_write()` - 34 edges
4. `TechnicalIndicators` - 32 edges
5. `TradeJournal` - 25 edges
6. `CryptoFuturesAutopilot` - 22 edges
7. `AppDelegate` - 22 edges
8. `align_timestamp_point_in_time()` - 22 edges
9. `ForexAutopilot` - 21 edges
10. `TestMultiDeskArchitecture` - 20 edges

## Surprising Connections (you probably didn't know these)
- `TestCMEFuturesDeskFixes` --uses--> `CMEFuturesAutopilot`  [INFERRED]
  stock-signal-engine/tests/test_cme_forex_desk_fixes.py → stock-signal-engine/execution/cme_futures_autopilot.py
- `TestMultiDeskArchitecture` --uses--> `CMEFuturesAutopilot`  [INFERRED]
  stock-signal-engine/tests/test_multi_desk.py → stock-signal-engine/execution/cme_futures_autopilot.py
- `TestMultiDeskArchitecture` --uses--> `CryptoFuturesAutopilot`  [INFERRED]
  stock-signal-engine/tests/test_multi_desk.py → stock-signal-engine/execution/crypto_futures_autopilot.py
- `TestSMCCryptoStrategy` --uses--> `CryptoFuturesAutopilot`  [INFERRED]
  stock-signal-engine/tests/test_smc_crypto_strategy.py → stock-signal-engine/execution/crypto_futures_autopilot.py
- `TestForexDeskFixes` --uses--> `ForexAutopilot`  [INFERRED]
  stock-signal-engine/tests/test_cme_forex_desk_fixes.py → stock-signal-engine/execution/forex_autopilot.py

## Import Cycles
- None detected.

## Communities (144 total, 49 thin omitted)

### Community 0 - "Any"
Cohesion: 0.06
Nodes (17): api_benchmark_summary(), api_compliance_report(), api_confluence_evaluate(), api_council_convene(), api_council_decision(), api_council_recent(), api_council_status(), api_desks_benchmark() (+9 more)

### Community 1 - "tunnel_manager.py"
Cohesion: 0.06
Nodes (25): run_comprehensive_simulation(), simulate_crypto_desk(), simulate_forex_desk(), simulate_futures_desk(), simulate_stock_desk(), TradeRecord, api_remote_restart(), _start_port_8081_forwarder() (+17 more)

### Community 3 - "TriConfluenceMatrix"
Cohesion: 0.24
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

### Community 8 - "unittest"
Cohesion: 0.13
Nodes (3): StabilizationResult, ThesisStatement, EquitySignal

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
Cohesion: 0.19
Nodes (11): swr, ArticlesFeedProps, SentimentHeatmapProps, sources, api, Article, MarketFeatures, PortfolioResponse (+3 more)

### Community 14 - "get"
Cohesion: 0.07
Nodes (20): health(), api_advisor_exit(), api_equity_curve(), api_evaluate(), api_health(), api_jev_opportunities(), api_journal_exits(), api_journal_summary() (+12 more)

### Community 15 - "atomic_json_read"
Cohesion: 0.15
Nodes (3): atomic_json_read(), atomic_json_write(), StrategyFarmManager

### Community 16 - "stock_analysis.py"
Cohesion: 0.07
Nodes (9): BenchmarkMetrics, InstitutionalBenchmarkEngine, analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _project_1m() (+1 more)

### Community 17 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 20 - "news_fetcher.py"
Cohesion: 0.09
Nodes (23): fetch_all(), fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news(), _get_alpaca_news_client(), _get_cache_path() (+15 more)

### Community 21 - "EquitiesSelfLearningTracker"
Cohesion: 0.09
Nodes (3): EquitiesSelfLearningTracker, InstitutionalEquitiesStrategy, TestEquitiesDesk1Fixes

### Community 24 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 25 - "core.py"
Cohesion: 0.12
Nodes (11): cmd_demo(), cmd_extract(), cmd_process(), main(), abstract_quant_content(), download_file(), encrypt_url_token(), extract_audio_tracks() (+3 more)

### Community 26 - "mirror_dispatcher.py"
Cohesion: 0.07
Nodes (7): BrokerClientFactory, MirrorDispatcher, MirrorTradeSignal, ReplicationSummary, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 27 - "TradeJournal"
Cohesion: 0.05
Nodes (10): Candle, generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), TradeJournal, evaluate_five_pillars() (+2 more)

### Community 28 - "BayesianConfidenceEngine"
Cohesion: 0.07
Nodes (5): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, TestBayesianConfidence

### Community 32 - "web_server.py"
Cohesion: 0.13
Nodes (6): api_extract_only(), api_process(), ExtractRequest, get_preset(), serve_index(), serve_media()

### Community 33 - "argparse"
Cohesion: 0.13
Nodes (13): cross_reference_batch(), evaluate_ticker(), main(), print_alpha_report(), _esc(), _fmt_ts(), load_account(), load_journal() (+5 more)

### Community 36 - "pandas"
Cohesion: 0.18
Nodes (7): fetch_latest_price(), fetch_prices(), _fetch_with_yahoo_chart(), _fetch_with_yfinance(), _get_cache_path(), _load_cache(), _save_cache()

### Community 37 - "hedging_engine.py"
Cohesion: 0.11
Nodes (8): calculate_asset_beta(), calculate_dynamic_hedge_ratio(), calculate_hedge_pair(), compute_book_exposure(), _env_float(), _latest_close(), resolve_hedge_instrument(), TestDynamicHedgeRatio

### Community 38 - "financial_modeling.py"
Cohesion: 0.06
Nodes (31): baseline_profile(), build_bundle(), Bundle, crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats() (+23 more)

### Community 39 - "alpha_client.py"
Cohesion: 0.12
Nodes (15): portfolio_endpoint(), get_portfolio_summary(), get_settings(), Settings, get_client(), get_current_exposure(), get_portfolio_value(), submit_bracket_buy() (+7 more)

### Community 40 - "detect_intraday_shock"
Cohesion: 0.09
Nodes (6): detect_intraday_shock(), _env_float(), gap_shock_threshold(), velocity_shock_threshold(), TestProjectOmega, TestShockDetector

### Community 41 - "dataset_generator.py"
Cohesion: 0.12
Nodes (7): get_universe(), build_historical_dataset(), generate_triple_barrier_labels(), train(), build_bootstrap_dataframe(), load_or_build_training_dataframe(), main()

### Community 42 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 43 - "council.py"
Cohesion: 0.22
Nodes (6): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision()

### Community 44 - "numpy"
Cohesion: 0.11
Nodes (3): run_test(), run_mean_reversion(), TechnicalIndicators

### Community 45 - "align_timestamp_point_in_time"
Cohesion: 0.11
Nodes (8): align_timestamp_point_in_time(), enrich_article_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), SessionInfo, validate_anti_leakage(), TestPointInTimeAlignment

### Community 47 - "FactorDAG"
Cohesion: 0.19
Nodes (3): FactorDAG, evaluate_factor_dag(), TestFactorDAG

### Community 48 - "CMEFuturesSelfLearningTracker"
Cohesion: 0.11
Nodes (4): CMEFuturesSelfLearningTracker, CMEFuturesSignal, CMEFuturesStrategyEngine, TestCMEFuturesDeskFixes

### Community 49 - "pipeline.py"
Cohesion: 0.10
Nodes (18): format_purchase_log(), log_purchase(), fetch_prev_close(), _conn(), _main(), remember(), similar(), stats() (+10 more)

### Community 50 - "five_year_stats.py"
Cohesion: 0.06
Nodes (28): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+20 more)

### Community 51 - "autopilot.py"
Cohesion: 0.10
Nodes (17): _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open(), post_market_belief_cycle(), run_autopilot() (+9 more)

### Community 52 - "mcp_server.py"
Cohesion: 0.11
Nodes (14): align_event_point_in_time(), analyze_financial_sentiment(), check_alpaca_account(), convene_agent_council_meeting(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health() (+6 more)

### Community 53 - "services.py"
Cohesion: 0.12
Nodes (18): autopilot_run_once(), execute_endpoint(), hedge_evaluate_endpoint(), market_endpoint(), regime_endpoint(), sentiment_endpoint(), signal_endpoint(), EngineException (+10 more)

### Community 55 - "tp1_scale_plan"
Cohesion: 0.15
Nodes (4): ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 56 - "app.py"
Cohesion: 0.11
Nodes (15): AIReviewRequest, api_compliance_ai_review(), api_gateway_register_subscriber(), api_gateway_replicate(), api_jev_execute(), api_model_confidence_evaluate(), api_ross_execute(), api_verify_pin() (+7 more)

### Community 57 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.15
Nodes (8): build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test(), add_indicators(), get_latest(), get_market_features()

### Community 59 - "calculate_exit_levels"
Cohesion: 0.13
Nodes (8): breakeven_move_pct(), days_to_target(), expected_move_pct(), is_trade_viable(), round_trip_cost(), calculate_exit_levels(), TestCostModel, TestExitEngine

### Community 60 - "risk/__init__.py"
Cohesion: 0.10
Nodes (9): get_adaptive_exit_geometry(), get_exit_geometry(), calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), TestAdaptiveExitGeometry (+1 more)

### Community 61 - "get_purchase_logs"
Cohesion: 0.40
Nodes (4): purchases_endpoint(), get_purchase_log_text(), get_purchase_logs(), api_purchases()

### Community 62 - "🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan"
Cohesion: 0.08
Nodes (25): 10. Quick-Start Commands, 1. Complete System Architecture Map, 2. Capital Architecture & Current State, 3. Financial Model Honest Audit, 3A. Closed Trade Performance (The Hard Truth), 3B. Bayesian Confidence Model — Current Assessment, 4. Root Cause Diagnosis: Why the System is Losing Money, 5. Improvement Plan: 8 Concrete Upgrades (+17 more)

### Community 65 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 67 - "banned_ticker"
Cohesion: 0.23
Nodes (4): main(), save_report(), TwentyYearStrategyEngine, banned_ticker()

### Community 69 - "nlp/__init__.py"
Cohesion: 0.22
Nodes (6): analyze_sentiment(), _get_finbert(), analyze(), analyze_sentiment_only(), compute_time_decay(), directional_sentiment()

### Community 71 - "dashboard/page.tsx"
Cohesion: 0.24
Nodes (13): DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch(), useMarket() (+5 more)

### Community 72 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 74 - "model/__init__.py"
Cohesion: 0.23
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 75 - ".evaluate_ticker"
Cohesion: 0.13
Nodes (3): JEVLiquidityScooper, ScoopOpportunity, TestJEVLiquidityScooper

### Community 76 - "time"
Cohesion: 0.18
Nodes (8): check_liveness(), get_autopilot_heartbeat(), is_us_equity_market_open(), main(), run_daemon(), api_desks_scan(), api_scan(), _leaderboard()

### Community 77 - "20-Year Institutional Strategy & Swing-Shield Benchmark"
Cohesion: 0.40
Nodes (4): 20-Year Institutional Strategy & Swing-Shield Benchmark, Multi-Desk 30% YoY Synergy Architecture, Performance Comparison vs Market Benchmark, Year-by-Year Historical Breakdown (2007 - 2026)

### Community 78 - "daily_routine.py"
Cohesion: 0.10
Nodes (18): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), get_sniper_setup() (+10 more)

### Community 82 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.25
Nodes (7): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🛠️ The 9 Live MCP Tools Exposed, 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 83 - "api_desks_status"
Cohesion: 0.40
Nodes (4): api_desks_status(), _find_process_pid(), _is_pid_alive(), _read_pid()

### Community 84 - "api_remote_qr_svg"
Cohesion: 0.20
Nodes (5): api_auth_logout(), api_remote_qr_svg(), graph_tree_view(), graph_view(), get_qr_svg()

### Community 87 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 88 - "post"
Cohesion: 0.29
Nodes (4): api_purge_mock_trades(), api_reconcile_broker(), api_rescan(), _require_token()

### Community 90 - "package.json"
Cohesion: 0.10
Nodes (18): axios, eslint, eslint-config-next, next-auth, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+10 more)

### Community 94 - "scenario_c.sh"
Cohesion: 0.14
Nodes (13): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+5 more)

### Community 95 - "next"
Cohesion: 0.15
Nodes (5): next, nextConfig, geistMono, geistSans, metadata

### Community 96 - "test_physical_risk_pipeline.py"
Cohesion: 0.19
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
Cohesion: 0.11
Nodes (9): generate_realistic_news_stream(), run_experiment(), AlphaCompositeNode, NewsSourceNode, Node, PointInTimeAlignmentNode, PriceSourceNode, SentimentAggregatorNode (+1 more)

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

### Community 114 - "Request"
Cohesion: 0.24
Nodes (6): domain_not_found_handler(), engine_logic_handler(), global_crash_handler(), api_auth_status(), _is_request_authenticated(), pin_auth_middleware()

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

### Community 126 - "RiskPanel.tsx"
Cohesion: 0.22
Nodes (5): recharts, PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps

### Community 134 - "get_book_allocations"
Cohesion: 0.10
Nodes (10): execute_jev_scoop_trade(), execute_ross_bracket_trade(), classify_position_book(), get_book_allocations(), get_split_ratios(), TestBookSplitArchitecture, _account_snapshot(), api_account() (+2 more)

### Community 135 - "pathlib"
Cohesion: 0.09
Nodes (7): main(), main(), FailureEpisode, backfill_historical_purchases(), StrategyItem, CryptoFuturesSignal, ForexSignal

### Community 137 - "QuantDesk Project & Deployment Architecture"
Cohesion: 0.33
Nodes (5): 1. Executive Summary & Host Topography, 2. Remote Access & Tailscale Networking Rules, 3. Core Desks & Automation Components, Critical Infrastructure Topology, QuantDesk Project & Deployment Architecture

## Knowledge Gaps
- **83 isolated node(s):** `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED`, `TOKENIZERS_PARALLELISM`, `TRANSFORMERS_OFFLINE` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1094 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **49 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `tunnel_manager.py`, `TriConfluenceMatrix`, `get_book_allocations`, `pathlib`, `get`, `stock_analysis.py`, `CMEFuturesAutopilot`, `ForexAutopilot`, `argparse`, `AgentCouncil`, `run_multi_asset_benchmark`, `hedging_engine.py`, `financial_modeling.py`, `dataset_generator.py`, `council.py`, `numpy`, `pipeline.py`, `five_year_stats.py`, `autopilot.py`, `mcp_server.py`, `app.py`, `banned_ticker`, `time`, `daily_routine.py`, `factor_dag.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **What connects `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Any` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._
- **Why does `atomic_json_read()` connect `atomic_json_read` to `AgentCouncil`, `pathlib`, `alpha_client.py`, `council.py`, `time`, `numpy`, `get`, `._load_state`, `autopilot.py`, `mcp_server.py`, `app.py`, `.fetch_live_order_book`, `CMEFuturesAutopilot`, `CryptoFuturesAutopilot`, `ForexAutopilot`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Should `tunnel_manager.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06274509803921569 - nodes in this community are weakly interconnected._
- **Why does `TradeJournal` connect `TradeJournal` to `numpy`, `get_book_allocations`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `quant` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._