# Graph Report - WORK  (2026-10-19)

## Corpus Check
- 230 files · ~613,750 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 33 file(s) not represented in the graph (top: .csv 15, (none) 9, .ipynb 3)

## Summary
- 2305 nodes · 4885 edges · 149 communities (97 shown, 52 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 113 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3e4696aa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- cost_model.py
- tunnel_manager.py
- quant
- post
- time
- scenario_small.sh
- AppDelegate
- app.py
- logging
- manifest.json
- test_units.py
- run_autopilot.sh
- run_webapp.sh
- types.ts
- api_remote_qr_svg
- atomic_json_read
- analyze_exit
- watchdog.sh
- dataset_generator.py
- news_fetcher.py
- alpha_client.py
- .filter_series
- ConvexTailEngine
- TradeReviewPacket
- core.py
- SubscriberProfile
- TradeJournal
- BayesianConfidenceEngine
- daily_sniper.py
- CryptoFuturesAutopilot
- TestMultiDeskArchitecture
- hedging_backtester.py
- dashboard.py
- AgentCouncil
- ForexStrategyEngine
- pandas
- hedging_engine.py
- financial_modeling.py
- argparse
- council.py
- Any
- iOS Mobile App & Home Screen Widget Blueprint
- daily_routine.py
- get_book_allocations
- align_timestamp_point_in_time
- CryptoPerpStrategyEngine
- FactorDAG
- CMEFuturesStrategyEngine
- Profile
- five_year_stats.py
- autopilot.py
- mcp_server.py
- services.py
- pathlib
- tp1_scale_plan
- TestArchitectureFixes
- CMEFuturesAutopilot
- .test_defensive_scaling_on_losing_streak
- FailureMemoryEngine
- risk/__init__.py
- get_purchase_logs
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- numpy
- scenario_sniper.sh
- TestTechnicalIndicators
- TwentyYearStrategyEngine
- web_server.py
- Request
- run_instagram_extractor.sh
- dashboard/page.tsx
- compilerOptions
- run_ross_momentum_sim
- .evaluate_ticker
- mirror_dispatcher.py
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- TestAgentCouncilArchitecture
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- iOS Mobile App & Home Screen Widget Blueprint
- train.py
- package.json
- GEMINI.md
- walk_forward.py
- execute_ross_bracket_trade
- scenario_c.sh
- next
- TestPhysicalRiskPipeline
- TriConfluenceMatrix
- store.ts
- Win-Rate Optimization & Diagnostic Report
- dependencies
- devDependencies
- factor_dag.py
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- low_float_scanner.py
- scanner.py
- scripts
- Five-Year Market Statistics
- Five-Year Market Statistics
- TestInstitutionalBenchmarkEngine
- _simulate_bars
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
- api_desks_status
- run_multi_asset_benchmark
- QuantDesk Project & Deployment Architecture
- TestArticleSelection
- process_trade_execution
- check_tail_risk
- profile_from_row
- sensitivity_grid
- host_architecture.md
- remote_setup.sh

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
- `analyze_stock()` --uses--> `TechnicalIndicators`  [INFERRED]
  stock-signal-engine/risk/stock_analysis.py → stock-signal-engine/market/technicals.py
- `_analyze_trend()` --uses--> `TechnicalIndicators`  [INFERRED]
  stock-signal-engine/risk/stock_analysis.py → stock-signal-engine/market/technicals.py
- `_assess_entry()` --uses--> `TechnicalIndicators`  [INFERRED]
  stock-signal-engine/risk/stock_analysis.py → stock-signal-engine/market/technicals.py
- `TriConfluenceMatrix` --uses--> `TechnicalIndicators`  [INFERRED]
  stock-signal-engine/strategy/confluence_matrix.py → stock-signal-engine/market/technicals.py
- `BrokerClientFactory` --uses--> `SubscriberProfile`  [INFERRED]
  stock-signal-engine/gateway/broker_client.py → stock-signal-engine/gateway/subscriber_registry.py

## Import Cycles
- None detected.

## Communities (149 total, 52 thin omitted)

### Community 0 - "cost_model.py"
Cohesion: 0.24
Nodes (3): breakeven_move_pct(), is_trade_viable(), round_trip_cost()

### Community 1 - "tunnel_manager.py"
Cohesion: 0.08
Nodes (19): api_remote_restart(), _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel(), _warm(), get_active_tunnel_url() (+11 more)

### Community 3 - "post"
Cohesion: 0.07
Nodes (23): autopilot_run_once(), execute_endpoint(), ExecuteRequest, AIReviewRequest, api_compliance_ai_review(), api_farm_demote(), api_farm_promote(), api_gateway_register_subscriber() (+15 more)

### Community 4 - "time"
Cohesion: 0.23
Nodes (5): check_liveness(), get_autopilot_heartbeat(), main(), run_daemon(), main()

### Community 5 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 6 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 7 - "app.py"
Cohesion: 0.04
Nodes (39): api_account(), api_advisor_exit(), api_benchmark_summary(), api_book_allocation(), api_compliance_report(), api_confluence_evaluate(), api_council_recent(), api_council_status() (+31 more)

### Community 8 - "logging"
Cohesion: 0.11
Nodes (3): FailureEpisode, StrategyItem, ScoopOpportunity

### Community 9 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 10 - "test_units.py"
Cohesion: 0.05
Nodes (13): score_trade(), TestAlpacaNews, TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory, TestPurchaseLogger, TestScannerQualityGate (+5 more)

### Community 11 - "run_autopilot.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_autopilot.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 12 - "run_webapp.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_webapp.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 13 - "types.ts"
Cohesion: 0.19
Nodes (11): swr, ArticlesFeedProps, SentimentHeatmapProps, sources, api, Article, MarketFeatures, PortfolioResponse (+3 more)

### Community 14 - "api_remote_qr_svg"
Cohesion: 0.20
Nodes (5): api_auth_logout(), api_remote_qr_svg(), graph_tree_view(), graph_view(), get_qr_svg()

### Community 15 - "atomic_json_read"
Cohesion: 0.15
Nodes (3): atomic_json_read(), atomic_json_write(), StrategyFarmManager

### Community 16 - "analyze_exit"
Cohesion: 0.05
Nodes (11): BenchmarkMetrics, InstitutionalBenchmarkEngine, analyze_exit(), analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct() (+3 more)

### Community 17 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 19 - "dataset_generator.py"
Cohesion: 0.17
Nodes (5): get_universe(), build_historical_dataset(), generate_triple_barrier_labels(), add_indicators(), get_latest()

### Community 20 - "news_fetcher.py"
Cohesion: 0.08
Nodes (24): get_settings(), Settings, fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news(), _get_alpaca_news_client() (+16 more)

### Community 21 - "alpha_client.py"
Cohesion: 0.15
Nodes (12): portfolio_endpoint(), signal_endpoint(), get_portfolio_summary(), get_client(), get_current_exposure(), get_portfolio_value(), submit_market_order(), submit_order() (+4 more)

### Community 22 - ".filter_series"
Cohesion: 0.11
Nodes (3): AntiVolatilityModel, StabilizationResult, TestAntiVolatilityModel

### Community 24 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 25 - "core.py"
Cohesion: 0.12
Nodes (11): cmd_demo(), cmd_extract(), cmd_process(), main(), abstract_quant_content(), download_file(), encrypt_url_token(), extract_audio_tracks() (+3 more)

### Community 26 - "SubscriberProfile"
Cohesion: 0.08
Nodes (4): MirrorDispatcher, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 28 - "BayesianConfidenceEngine"
Cohesion: 0.07
Nodes (5): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, TestBayesianConfidence

### Community 29 - "daily_sniper.py"
Cohesion: 0.12
Nodes (10): get_sniper_setup(), main(), is_us_equity_market_open(), calculate_asset_beta(), detect_intraday_shock(), earnings_blackout(), _env_float(), gap_shock_threshold() (+2 more)

### Community 30 - "CryptoFuturesAutopilot"
Cohesion: 0.09
Nodes (3): CryptoFuturesAutopilot, main(), TestCryptoPerpFixes

### Community 32 - "hedging_backtester.py"
Cohesion: 0.15
Nodes (9): main(), PairStrategySimulator, _print_report(), run_comparison(), simulate(), SimulationConfig, _strip_tz(), _trim() (+1 more)

### Community 33 - "dashboard.py"
Cohesion: 0.21
Nodes (8): _esc(), _fmt_ts(), load_account(), load_journal(), generate_once(), render_page(), seed_demo(), _wr_color()

### Community 36 - "pandas"
Cohesion: 0.17
Nodes (14): run_test(), run_mean_reversion(), cross_reference_batch(), evaluate_ticker(), main(), print_alpha_report(), fetch_latest_price(), fetch_prices() (+6 more)

### Community 37 - "hedging_engine.py"
Cohesion: 0.10
Nodes (10): days_to_target(), expected_move_pct(), calculate_exit_levels(), _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), is_hot_banned(), TestAdaptiveExitGeometry (+2 more)

### Community 38 - "financial_modeling.py"
Cohesion: 0.14
Nodes (12): build_bundle(), crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats(), pick_best(), rank_candidates() (+4 more)

### Community 39 - "argparse"
Cohesion: 0.09
Nodes (20): submit_bracket_buy(), backfill_historical_purchases(), format_purchase_log(), log_purchase(), fetch_all(), fetch_prev_close(), _conn(), _main() (+12 more)

### Community 40 - "council.py"
Cohesion: 0.16
Nodes (8): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision(), api_council_convene(), api_council_decision()

### Community 41 - "Any"
Cohesion: 0.11
Nodes (7): get_hedge_evaluation(), calculate_dynamic_hedge_ratio(), calculate_hedge_pair(), compute_book_exposure(), _latest_close(), resolve_hedge_instrument(), TestDynamicHedgeRatio

### Community 42 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 43 - "daily_routine.py"
Cohesion: 0.12
Nodes (16): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), flat_universe() (+8 more)

### Community 44 - "get_book_allocations"
Cohesion: 0.16
Nodes (5): execute_jev_scoop_trade(), classify_position_book(), get_book_allocations(), get_split_ratios(), _account_snapshot()

### Community 45 - "align_timestamp_point_in_time"
Cohesion: 0.11
Nodes (8): align_timestamp_point_in_time(), enrich_article_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), SessionInfo, validate_anti_leakage(), TestPointInTimeAlignment

### Community 47 - "FactorDAG"
Cohesion: 0.19
Nodes (3): FactorDAG, evaluate_factor_dag(), TestFactorDAG

### Community 49 - "Profile"
Cohesion: 0.13
Nodes (6): baseline_profile(), Profile, build_hunt_grid(), main(), run_diagnostic(), TestFinancialModelingAdaptive

### Community 50 - "five_year_stats.py"
Cohesion: 0.16
Nodes (13): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+5 more)

### Community 51 - "autopilot.py"
Cohesion: 0.06
Nodes (17): auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open(), post_market_belief_cycle() (+9 more)

### Community 52 - "mcp_server.py"
Cohesion: 0.12
Nodes (13): align_event_point_in_time(), analyze_financial_sentiment(), convene_agent_council_meeting(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health(), get_multi_desk_status() (+5 more)

### Community 53 - "services.py"
Cohesion: 0.08
Nodes (21): health(), hedge_evaluate_endpoint(), market_endpoint(), regime_endpoint(), sentiment_endpoint(), EngineException, MarketDataNotFoundError, NLPAnalysisError (+13 more)

### Community 55 - "tp1_scale_plan"
Cohesion: 0.15
Nodes (4): ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 60 - "risk/__init__.py"
Cohesion: 0.16
Nodes (7): evaluate_trade(), calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), TestRegimeAdaptivePositionSizing

### Community 61 - "get_purchase_logs"
Cohesion: 0.40
Nodes (4): purchases_endpoint(), get_purchase_log_text(), get_purchase_logs(), api_purchases()

### Community 62 - "🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan"
Cohesion: 0.08
Nodes (25): 10. Quick-Start Commands, 1. Complete System Architecture Map, 2. Capital Architecture & Current State, 3. Financial Model Honest Audit, 3A. Closed Trade Performance (The Hard Truth), 3B. Bayesian Confidence Model — Current Assessment, 4. Root Cause Diagnosis: Why the System is Losing Money, 5. Improvement Plan: 8 Concrete Upgrades (+17 more)

### Community 63 - "numpy"
Cohesion: 0.21
Nodes (9): main(), simulate_night(), growth_optimal_f(), main(), mc_time_to_goal(), oos_r_pool(), pool_stats(), savings_months() (+1 more)

### Community 65 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 67 - "TwentyYearStrategyEngine"
Cohesion: 0.33
Nodes (3): main(), save_report(), TwentyYearStrategyEngine

### Community 68 - "web_server.py"
Cohesion: 0.13
Nodes (6): api_extract_only(), api_process(), ExtractRequest, get_preset(), serve_index(), serve_media()

### Community 69 - "Request"
Cohesion: 0.24
Nodes (6): domain_not_found_handler(), engine_logic_handler(), global_crash_handler(), api_auth_status(), _is_request_authenticated(), pin_auth_middleware()

### Community 71 - "dashboard/page.tsx"
Cohesion: 0.24
Nodes (13): DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch(), useMarket() (+5 more)

### Community 72 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 74 - "run_ross_momentum_sim"
Cohesion: 0.20
Nodes (5): generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim()

### Community 76 - "mirror_dispatcher.py"
Cohesion: 0.23
Nodes (3): BrokerClientFactory, MirrorTradeSignal, ReplicationSummary

### Community 77 - "20-Year Institutional Strategy & Swing-Shield Benchmark"
Cohesion: 0.40
Nodes (4): 20-Year Institutional Strategy & Swing-Shield Benchmark, Multi-Desk 30% YoY Synergy Architecture, Performance Comparison vs Market Benchmark, Year-by-Year Historical Breakdown (2007 - 2026)

### Community 82 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.25
Nodes (7): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🛠️ The 9 Live MCP Tools Exposed, 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 87 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 88 - "train.py"
Cohesion: 0.11
Nodes (9): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict(), train(), build_bootstrap_dataframe(), load_or_build_training_dataframe() (+1 more)

### Community 90 - "package.json"
Cohesion: 0.10
Nodes (18): axios, eslint, eslint-config-next, next-auth, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+10 more)

### Community 92 - "walk_forward.py"
Cohesion: 0.25
Nodes (5): main(), month_folds(), _policy_summary(), _run_style(), walk_forward()

### Community 94 - "scenario_c.sh"
Cohesion: 0.14
Nodes (13): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+5 more)

### Community 95 - "next"
Cohesion: 0.15
Nodes (5): next, nextConfig, geistMono, geistSans, metadata

### Community 96 - "TestPhysicalRiskPipeline"
Cohesion: 0.22
Nodes (3): PhysicalRiskPipeline, RiskPipelineVerdict, TestPhysicalRiskPipeline

### Community 97 - "TriConfluenceMatrix"
Cohesion: 0.24
Nodes (3): ConfluenceDecision, TriConfluenceMatrix, TestTriConfluenceMatrix

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

### Community 107 - "low_float_scanner.py"
Cohesion: 0.27
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

### Community 113 - "_simulate_bars"
Cohesion: 0.27
Nodes (4): Bundle, run_profile(), _simulate_bars(), window_run()

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
Cohesion: 0.29
Nodes (5): build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test()

### Community 126 - "RiskPanel.tsx"
Cohesion: 0.22
Nodes (5): recharts, PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps

### Community 134 - "evaluate_five_pillars"
Cohesion: 0.33
Nodes (3): evaluate_five_pillars(), evaluate_news_catalyst(), TestRossMomentumStrategy

### Community 135 - "api_desks_status"
Cohesion: 0.40
Nodes (4): api_desks_status(), _find_process_pid(), _is_pid_alive(), _read_pid()

### Community 137 - "QuantDesk Project & Deployment Architecture"
Cohesion: 0.33
Nodes (5): 1. Executive Summary & Host Topography, 2. Remote Access & Tailscale Networking Rules, 3. Core Desks & Automation Components, Critical Infrastructure Topology, QuantDesk Project & Deployment Architecture

## Knowledge Gaps
- **83 isolated node(s):** `USE_LGBM_RUNTIME`, `OMP_NUM_THREADS`, `TOKENIZERS_PARALLELISM`, `HF_HUB_OFFLINE`, `TRANSFORMERS_OFFLINE` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1050 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **52 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FailureMemoryEngine` connect `FailureMemoryEngine` to `logging`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **What connects `USE_LGBM_RUNTIME`, `OMP_NUM_THREADS`, `TOKENIZERS_PARALLELISM` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tunnel_manager.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0796221322537112 - nodes in this community are weakly interconnected._
- **Why does `fetch_prices()` connect `pandas` to `app.py`, `logging`, `run_multi_asset_benchmark`, `analyze_exit`, `dataset_generator.py`, `daily_sniper.py`, `hedging_backtester.py`, `AgentCouncil`, `hedging_engine.py`, `financial_modeling.py`, `argparse`, `council.py`, `Any`, `daily_routine.py`, `five_year_stats.py`, `mcp_server.py`, `pathlib`, `TwentyYearStrategyEngine`, `TriConfluenceMatrix`, `factor_dag.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Should `quant` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._
- **Why does `TestArchitectureFixes` connect `TestArchitectureFixes` to `time`, `atomic_json_read`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Should `post` be split into smaller, more focused modules?**
  _Cohesion score 0.06606606606606606 - nodes in this community are weakly interconnected._