# Graph Report - WORK  (2026-10-19)

## Corpus Check
- 230 files · ~613,750 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 33 file(s) not represented in the graph (top: .csv 15, (none) 9, .ipynb 3)

## Summary
- 2304 nodes · 4884 edges · 151 communities (100 shown, 51 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 113 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `be261626`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- cost_model.py
- Any
- quant
- app.py
- time
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
- atomic_json_read
- TechnicalIndicators
- watchdog.sh
- services.py
- news_fetcher.py
- alpha_client.py
- .filter_series
- ConvexTailEngine
- TradeReviewPacket
- core.py
- mirror_dispatcher.py
- TradeJournal
- BayesianConfidenceEngine
- shock_detector.py
- CryptoFuturesAutopilot
- TestMultiDeskArchitecture
- tunnel_manager.py
- dashboard.py
- council.py
- ForexStrategyEngine
- pandas
- hedging_engine.py
- financial_modeling.py
- json
- TestProjectOmega
- calculate_hedge_pair
- iOS Mobile App & Home Screen Widget Blueprint
- daily_routine.py
- get_book_allocations
- align_timestamp_point_in_time
- CryptoPerpStrategyEngine
- FactorDAG
- math
- run_diagnostic
- five_year_stats.py
- os
- mcp_server.py
- main.py
- tp1_scale_plan
- TestArchitectureFixes
- model/__init__.py
- .test_defensive_scaling_on_losing_streak
- PointInTimeAlignmentNode
- risk/__init__.py
- get_purchase_logs
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- numpy
- scenario_sniper.sh
- TestTechnicalIndicators
- TwentyYearStrategyEngine
- _leaderboard
- nlp/__init__.py
- run_instagram_extractor.sh
- dashboard/page.tsx
- compilerOptions
- run_ross_momentum_sim
- test_jev_scooper.py
- daily_sniper.py
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
- TestShockDetector
- store.ts
- Win-Rate Optimization & Diagnostic Report
- dependencies
- devDependencies
- run_experiment
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- check_trading_window
- scanner.py
- scripts
- Five-Year Market Statistics
- Five-Year Market Statistics
- TestInstitutionalBenchmarkEngine
- get_regime
- [...path]/route.ts
- README.md
- Candle
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
- evaluate_five_pillars
- TestJournalV3
- run_multi_asset_benchmark
- QuantDesk Project & Deployment Architecture
- TestArticleSelection
- calculate_exit_levels
- TestTimeDecay
- check_tail_risk
- api_remote_qr_svg
- month_folds
- host_architecture.md
- TestAlpacaNews
- remote_setup.sh
- TestDatasetGenerator

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 51 edges
2. `atomic_json_read()` - 39 edges
3. `atomic_json_write()` - 33 edges
4. `TechnicalIndicators` - 32 edges
5. `TradeJournal` - 25 edges
6. `AppDelegate` - 22 edges
7. `align_timestamp_point_in_time()` - 22 edges
8. `AgentCouncil` - 20 edges
9. `main()` - 20 edges
10. `get_book_allocations()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `_tunnel()` --calls--> `start_tunnel()`  [EXTRACTED]
  stock-signal-engine/webapp/app.py → stock-signal-engine/webapp/tunnel_manager.py
- `TestRossMomentumStrategy` --uses--> `RossSessionManager`  [INFERRED]
  stock-signal-engine/tests/test_units.py → stock-signal-engine/backtest/ross_momentum_sim.py
- `build_books()` --calls--> `calculate_exit_levels()`  [INFERRED]
  stock-signal-engine/backtest/sentiment_hedged_vs_unhedged.py → stock-signal-engine/risk/hedging_engine.py
- `build_books()` --calls--> `calculate_hedge_pair()`  [INFERRED]
  stock-signal-engine/backtest/sentiment_hedged_vs_unhedged.py → stock-signal-engine/risk/hedging_engine.py
- `process_trade_execution()` --calls--> `banned_ticker()`  [INFERRED]
  stock-signal-engine/api/services.py → stock-signal-engine/risk/hedging_engine.py

## Import Cycles
- None detected.

## Communities (151 total, 51 thin omitted)

### Community 0 - "cost_model.py"
Cohesion: 0.21
Nodes (4): breakeven_move_pct(), is_trade_viable(), round_trip_cost(), TestCostModel

### Community 1 - "Any"
Cohesion: 0.07
Nodes (18): api_benchmark_summary(), api_compliance_report(), api_council_status(), api_desks_benchmark(), api_gateway_list_subscribers(), api_gateway_mirror_history(), api_graphify_status(), get_active_tunnel_url() (+10 more)

### Community 3 - "app.py"
Cohesion: 0.08
Nodes (23): AIReviewRequest, api_auth_status(), api_compliance_ai_review(), api_desks_status(), api_flatten(), api_gateway_register_subscriber(), api_gateway_replicate(), api_model_confidence_evaluate() (+15 more)

### Community 4 - "time"
Cohesion: 0.24
Nodes (4): check_liveness(), get_autopilot_heartbeat(), main(), run_daemon()

### Community 5 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 6 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 7 - "get"
Cohesion: 0.05
Nodes (25): api_advisor_exit(), api_confluence_evaluate(), api_council_recent(), api_equity_curve(), api_evaluate(), api_farm_status(), api_graphify_query(), api_health() (+17 more)

### Community 9 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 10 - "test_units.py"
Cohesion: 0.12
Nodes (6): TestJournalV2, TestNewsMemory, TestPurchaseLogger, TestScannerQualityGate, TestTripleBarrier, TestTwitterSuppression

### Community 11 - "run_autopilot.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_autopilot.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 12 - "run_webapp.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_webapp.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 13 - "types.ts"
Cohesion: 0.19
Nodes (11): swr, ArticlesFeedProps, SentimentHeatmapProps, sources, api, Article, MarketFeatures, PortfolioResponse (+3 more)

### Community 14 - "post"
Cohesion: 0.09
Nodes (12): api_auth_logout(), api_council_convene(), api_council_decision(), api_farm_demote(), api_farm_promote(), api_memory_check(), api_purge_mock_trades(), api_reconcile_broker() (+4 more)

### Community 15 - "atomic_json_read"
Cohesion: 0.11
Nodes (4): atomic_json_read(), atomic_json_write(), StrategyFarmManager, StrategyItem

### Community 16 - "TechnicalIndicators"
Cohesion: 0.05
Nodes (14): BenchmarkMetrics, InstitutionalBenchmarkEngine, TechnicalIndicators, expected_move_pct(), analyze_stock(), _analyze_trend(), add(), _assess_entry() (+6 more)

### Community 17 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 19 - "services.py"
Cohesion: 0.16
Nodes (9): signal_endpoint(), get_hedge_evaluation(), get_processed_signal(), process_trade_execution(), fetch_all(), pick_best_article(), evaluate_trade(), score_trade() (+1 more)

### Community 20 - "news_fetcher.py"
Cohesion: 0.08
Nodes (24): get_settings(), Settings, fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news(), _get_alpaca_news_client() (+16 more)

### Community 21 - "alpha_client.py"
Cohesion: 0.18
Nodes (8): portfolio_endpoint(), get_portfolio_summary(), get_portfolio_value(), submit_market_order(), submit_order(), submit_pair_orders(), execute_hedged_trade(), execute_trade()

### Community 22 - ".filter_series"
Cohesion: 0.11
Nodes (3): AntiVolatilityModel, StabilizationResult, TestAntiVolatilityModel

### Community 24 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 25 - "core.py"
Cohesion: 0.07
Nodes (17): cmd_demo(), cmd_extract(), cmd_process(), main(), abstract_quant_content(), download_file(), encrypt_url_token(), extract_audio_tracks() (+9 more)

### Community 26 - "mirror_dispatcher.py"
Cohesion: 0.07
Nodes (7): BrokerClientFactory, MirrorDispatcher, MirrorTradeSignal, ReplicationSummary, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 27 - "TradeJournal"
Cohesion: 0.06
Nodes (3): FailureMemoryEngine, FailureRiskAssessment, TradeJournal

### Community 28 - "BayesianConfidenceEngine"
Cohesion: 0.07
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 29 - "shock_detector.py"
Cohesion: 0.24
Nodes (5): is_us_equity_market_open(), detect_intraday_shock(), _env_float(), gap_shock_threshold(), velocity_shock_threshold()

### Community 30 - "CryptoFuturesAutopilot"
Cohesion: 0.09
Nodes (3): CryptoFuturesAutopilot, main(), TestCryptoPerpFixes

### Community 31 - "TestMultiDeskArchitecture"
Cohesion: 0.05
Nodes (4): CMEFuturesAutopilot, main(), ForexAutopilot, TestMultiDeskArchitecture

### Community 32 - "tunnel_manager.py"
Cohesion: 0.17
Nodes (8): _conn(), _main(), remember(), similar(), stats(), _tokens(), _vec(), get_qr_png_bytes()

### Community 33 - "dashboard.py"
Cohesion: 0.21
Nodes (9): _esc(), _fmt_ts(), load_account(), load_journal(), main(), generate_once(), render_page(), seed_demo() (+1 more)

### Community 34 - "council.py"
Cohesion: 0.07
Nodes (9): AgentCouncil, convene_council_meeting(), CouncilMeetingResult, CouncilTurn, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision() (+1 more)

### Community 36 - "pandas"
Cohesion: 0.12
Nodes (15): main(), _print_report(), run_comparison(), _trim(), _window(), run_test(), run_mean_reversion(), calculate_asset_beta() (+7 more)

### Community 37 - "hedging_engine.py"
Cohesion: 0.13
Nodes (6): compute_book_exposure(), _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), is_hot_banned(), TestAdaptiveExitGeometry

### Community 38 - "financial_modeling.py"
Cohesion: 0.08
Nodes (20): baseline_profile(), build_bundle(), Bundle, load_ohlcv(), main(), per_year_stats(), pick_best(), Profile (+12 more)

### Community 39 - "json"
Cohesion: 0.11
Nodes (13): submit_bracket_buy(), backfill_historical_purchases(), format_purchase_log(), log_purchase(), fetch_prev_close(), build_candidate(), composite_score(), main() (+5 more)

### Community 41 - "calculate_hedge_pair"
Cohesion: 0.15
Nodes (4): calculate_hedge_pair(), _latest_close(), resolve_hedge_instrument(), TestDynamicHedgeRatio

### Community 42 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 43 - "daily_routine.py"
Cohesion: 0.17
Nodes (11): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), flat_universe() (+3 more)

### Community 44 - "get_book_allocations"
Cohesion: 0.09
Nodes (12): execute_jev_scoop_trade(), execute_ross_bracket_trade(), classify_position_book(), get_book_allocations(), get_split_ratios(), TestBookSplitArchitecture, _account_snapshot(), api_account() (+4 more)

### Community 45 - "align_timestamp_point_in_time"
Cohesion: 0.18
Nodes (5): align_timestamp_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), TestPointInTimeAlignment

### Community 47 - "FactorDAG"
Cohesion: 0.19
Nodes (3): FactorDAG, evaluate_factor_dag(), TestFactorDAG

### Community 48 - "math"
Cohesion: 0.14
Nodes (3): CMEFuturesSignal, CMEFuturesStrategyEngine, ForexSignal

### Community 50 - "five_year_stats.py"
Cohesion: 0.08
Nodes (19): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+11 more)

### Community 51 - "os"
Cohesion: 0.13
Nodes (14): auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open(), post_market_belief_cycle() (+6 more)

### Community 52 - "mcp_server.py"
Cohesion: 0.10
Nodes (16): get_client(), get_current_exposure(), align_event_point_in_time(), analyze_financial_sentiment(), check_alpaca_account(), convene_agent_council_meeting(), fetch_stock_prices(), find_codebase_path() (+8 more)

### Community 53 - "main.py"
Cohesion: 0.14
Nodes (14): autopilot_run_once(), domain_not_found_handler(), engine_logic_handler(), execute_endpoint(), global_crash_handler(), health(), hedge_evaluate_endpoint(), market_endpoint() (+6 more)

### Community 55 - "tp1_scale_plan"
Cohesion: 0.15
Nodes (4): ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 57 - "model/__init__.py"
Cohesion: 0.22
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 59 - "PointInTimeAlignmentNode"
Cohesion: 0.14
Nodes (4): PointInTimeAlignmentNode, enrich_article_point_in_time(), SessionInfo, validate_anti_leakage()

### Community 60 - "risk/__init__.py"
Cohesion: 0.17
Nodes (6): calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), TestRegimeAdaptivePositionSizing

### Community 61 - "get_purchase_logs"
Cohesion: 0.40
Nodes (4): purchases_endpoint(), get_purchase_log_text(), get_purchase_logs(), api_purchases()

### Community 62 - "🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan"
Cohesion: 0.08
Nodes (25): 10. Quick-Start Commands, 1. Complete System Architecture Map, 2. Capital Architecture & Current State, 3. Financial Model Honest Audit, 3A. Closed Trade Performance (The Hard Truth), 3B. Bayesian Confidence Model — Current Assessment, 4. Root Cause Diagnosis: Why the System is Losing Money, 5. Improvement Plan: 8 Concrete Upgrades (+17 more)

### Community 63 - "numpy"
Cohesion: 0.13
Nodes (13): crisis_pool(), monte_carlo(), _regime_mult(), _rolling_beta(), main(), simulate_night(), growth_optimal_f(), main() (+5 more)

### Community 65 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 67 - "TwentyYearStrategyEngine"
Cohesion: 0.39
Nodes (3): main(), save_report(), TwentyYearStrategyEngine

### Community 68 - "_leaderboard"
Cohesion: 0.18
Nodes (9): api_desks_scan(), api_scan(), _leaderboard(), _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel() (+1 more)

### Community 69 - "nlp/__init__.py"
Cohesion: 0.22
Nodes (6): analyze_sentiment(), _get_finbert(), analyze(), analyze_sentiment_only(), compute_time_decay(), directional_sentiment()

### Community 71 - "dashboard/page.tsx"
Cohesion: 0.24
Nodes (13): DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch(), useMarket() (+5 more)

### Community 72 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 74 - "run_ross_momentum_sim"
Cohesion: 0.20
Nodes (5): generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim()

### Community 75 - "test_jev_scooper.py"
Cohesion: 0.13
Nodes (3): JEVLiquidityScooper, ScoopOpportunity, TestJEVLiquidityScooper

### Community 76 - "daily_sniper.py"
Cohesion: 0.24
Nodes (4): get_sniper_setup(), main(), detect_market_regime(), earnings_blackout()

### Community 77 - "20-Year Institutional Strategy & Swing-Shield Benchmark"
Cohesion: 0.40
Nodes (4): 20-Year Institutional Strategy & Swing-Shield Benchmark, Multi-Desk 30% YoY Synergy Architecture, Performance Comparison vs Market Benchmark, Year-by-Year Historical Breakdown (2007 - 2026)

### Community 78 - "market_scanner.py"
Cohesion: 0.27
Nodes (5): main(), mass_backtest(), print_mass_report(), rank_market(), scan_dip_opportunities()

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
Cohesion: 0.16
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

### Community 102 - "run_experiment"
Cohesion: 0.11
Nodes (8): generate_realistic_news_stream(), run_experiment(), AlphaCompositeNode, NewsSourceNode, Node, PriceSourceNode, SentimentAggregatorNode, TechnicalFeaturesNode

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

### Community 114 - "[...path]/route.ts"
Cohesion: 0.46
Nodes (7): buildHeaders(), createBackendUrl(), DELETE(), GET(), POST(), proxy(), PUT()

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

### Community 125 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.15
Nodes (8): build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test(), add_indicators(), get_latest(), get_market_features()

### Community 126 - "RiskPanel.tsx"
Cohesion: 0.22
Nodes (5): recharts, PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps

### Community 134 - "evaluate_five_pillars"
Cohesion: 0.33
Nodes (3): evaluate_five_pillars(), evaluate_news_catalyst(), TestRossMomentumStrategy

### Community 137 - "QuantDesk Project & Deployment Architecture"
Cohesion: 0.33
Nodes (5): 1. Executive Summary & Host Topography, 2. Remote Access & Tailscale Networking Rules, 3. Core Desks & Automation Components, Critical Infrastructure Topology, QuantDesk Project & Deployment Architecture

### Community 139 - "calculate_exit_levels"
Cohesion: 0.20
Nodes (4): days_to_target(), banned_ticker(), calculate_exit_levels(), TestExitEngine

## Knowledge Gaps
- **83 isolated node(s):** `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED`, `TOKENIZERS_PARALLELISM`, `TRANSFORMERS_OFFLINE` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1050 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **51 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `app.py`, `get`, `pathlib`, `run_multi_asset_benchmark`, `TechnicalIndicators`, `council.py`, `hedging_engine.py`, `financial_modeling.py`, `json`, `calculate_hedge_pair`, `daily_routine.py`, `math`, `five_year_stats.py`, `mcp_server.py`, `TwentyYearStrategyEngine`, `_leaderboard`, `daily_sniper.py`, `market_scanner.py`, `dataset_generator.py`, `argparse`, `run_experiment`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **What connects `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Any` be split into smaller, more focused modules?**
  _Cohesion score 0.07226890756302522 - nodes in this community are weakly interconnected._
- **Why does `TechnicalIndicators` connect `TechnicalIndicators` to `pandas`, `financial_modeling.py`, `pathlib`, `test_units.py`, `daily_sniper.py`, `market_scanner.py`, `argparse`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Should `quant` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._
- **Why does `CryptoFuturesAutopilot` connect `CryptoFuturesAutopilot` to `math`, `unittest`, `atomic_json_read`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07560975609756097 - nodes in this community are weakly interconnected._