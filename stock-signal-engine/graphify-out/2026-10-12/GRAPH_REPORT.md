# Graph Report - stock-signal-engine  (2026-10-12)

## Corpus Check
- 204 files · ~411,536 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 50 file(s) not represented in the graph (top: .log 19, .csv 9, .db 7)

## Summary
- 2176 nodes · 4750 edges · 124 communities (93 shown, 31 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 146 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `da195636`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TradeJournal
- five_year_stats.py
- daily_sniper.py
- AppDelegate
- TradeReviewPacket
- SubscriberProfile
- pathlib
- TechnicalIndicators
- post
- BayesianConfidenceEngine
- app.py
- logging
- start_tunnel
- quant
- news_fetcher.py
- Any
- financial_modeling.py
- factor_dag.py
- os
- align_timestamp_point_in_time
- main.py
- AgentCouncil
- .filter_series
- scenario_small.sh
- mcp_server.py
- Profile
- scenario_sniper.sh
- pipeline.py
- InstitutionalBenchmarkEngine
- atomic_json_read
- hedging_engine.py
- risk/__init__.py
- test_units.py
- test_jev_scooper.py
- api_flatten
- package.json
- TestMultiDeskArchitecture
- layout.tsx
- types.ts
- process_trade_execution
- pandas
- train.py
- compilerOptions
- CryptoFuturesAutopilot
- numpy
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- tp1_scale_plan
- daily_routine.py
- sentiment_hedged_vs_unhedged.py
- FactorDAG
- dashboard.py
- cost_model.py
- services.py
- model/__init__.py
- hedging_backtester.py
- scenario_c.sh
- ForexStrategyEngine
- run_ross_momentum_sim
- pick_best_article
- time
- .test_defensive_scaling_on_losing_streak
- nlp/__init__.py
- api_remote_qr_svg
- 📈 Stock Signal Engine — Personal Quant Desk
- TestProjectOmega
- manifest.json
- score_trade
- iOS Mobile App & Home Screen Widget Blueprint
- mirror_dispatcher.py
- dependencies
- devDependencies
- store.ts
- iOS Mobile App & Home Screen Widget Blueprint
- walk_forward.py
- analyze_exit
- Win-Rate Optimization & Diagnostic Report
- run_autopilot.sh
- run_webapp.sh
- scanner.py
- ConvexTailEngine
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- domain_not_found_handler
- run_diagnostic
- run_multi_asset_benchmark
- CryptoPerpStrategyEngine
- scripts
- Crisis-Tested Financial Model
- watchdog.sh
- calculate_dynamic_hedge_ratio
- analyze_sentiment
- TestTechnicalIndicators
- postcss.config.mjs
- _simulate_bars
- [...path]/route.ts
- _start_port_8081_forwarder
- Candle
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- tunnel_manager.py
- api_desks_status
- Five-Year Market Statistics
- Five-Year Market Statistics
- dashboard/README.md
- [...nextauth]/route.ts
- Pre-Market Plan — 2026-08-26
- Pre-Market Plan — 2026-08-27
- Pre-Market Plan — 2026-09-05
- Pre-Market Plan — 2026-09-07
- Pre-Market Plan — 2026-09-08
- Pre-Market Plan — 2026-09-14
- Pre-Market Plan — 2026-09-19
- Pre-Market Plan — 2026-09-21
- tailwind.config.ts
- AGENTS.md
- GEMINI.md
- time_to_goal_2026-09-21.md

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 71 edges
2. `TechnicalIndicators` - 34 edges
3. `atomic_json_read()` - 33 edges
4. `atomic_json_write()` - 28 edges
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
- `run_ross_momentum_sim()` --uses--> `TradeJournal`  [INFERRED]
  backtest/ross_momentum_sim.py → execution/trade_journal.py

## Import Cycles
- None detected.

## Communities (124 total, 31 thin omitted)

### Community 0 - "TradeJournal"
Cohesion: 0.07
Nodes (3): execute_ross_bracket_trade(), TradeJournal, TestBookSplitArchitecture

### Community 1 - "five_year_stats.py"
Cohesion: 0.13
Nodes (15): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+7 more)

### Community 2 - "daily_sniper.py"
Cohesion: 0.11
Nodes (11): get_sniper_setup(), main(), calculate_asset_beta(), detect_market_regime(), fetch_latest_price(), detect_intraday_shock(), earnings_blackout(), _env_float() (+3 more)

### Community 3 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 4 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 5 - "SubscriberProfile"
Cohesion: 0.09
Nodes (4): MirrorDispatcher, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 6 - "pathlib"
Cohesion: 0.11
Nodes (5): main(), main(), backfill_historical_purchases(), format_purchase_log(), log_purchase()

### Community 7 - "TechnicalIndicators"
Cohesion: 0.08
Nodes (12): TechnicalIndicators, expected_move_pct(), analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _project_1m() (+4 more)

### Community 8 - "post"
Cohesion: 0.08
Nodes (17): AIReviewRequest, api_compliance_ai_review(), api_council_convene(), api_council_decision(), api_gateway_register_subscriber(), api_gateway_replicate(), api_jev_execute(), api_model_confidence_evaluate() (+9 more)

### Community 9 - "BayesianConfidenceEngine"
Cohesion: 0.08
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 10 - "app.py"
Cohesion: 0.05
Nodes (35): _account_snapshot(), api_account(), api_advisor_exit(), api_benchmark_summary(), api_book_allocation(), api_compliance_report(), api_confluence_evaluate(), api_council_recent() (+27 more)

### Community 11 - "logging"
Cohesion: 0.13
Nodes (4): get_settings(), Settings, get_book_allocations(), get_split_ratios()

### Community 12 - "start_tunnel"
Cohesion: 0.13
Nodes (11): get_active_tunnel_url(), get_local_ip(), get_remote_status(), is_caffeinate_running(), is_tunnel_evicted(), print_cli_summary(), restart_tunnel(), start_tunnel() (+3 more)

### Community 14 - "news_fetcher.py"
Cohesion: 0.07
Nodes (27): fetch_earnings(), _normalize(), fetch_all(), fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news() (+19 more)

### Community 15 - "Any"
Cohesion: 0.14
Nodes (12): align_event_point_in_time(), analyze_financial_sentiment(), check_alpaca_account(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health(), get_multi_desk_status() (+4 more)

### Community 16 - "financial_modeling.py"
Cohesion: 0.15
Nodes (11): crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats(), pick_best(), rank_candidates(), refine_grid() (+3 more)

### Community 17 - "factor_dag.py"
Cohesion: 0.11
Nodes (9): generate_realistic_news_stream(), run_experiment(), AlphaCompositeNode, NewsSourceNode, Node, PointInTimeAlignmentNode, PriceSourceNode, SentimentAggregatorNode (+1 more)

### Community 18 - "os"
Cohesion: 0.08
Nodes (18): auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open(), post_market_belief_cycle() (+10 more)

### Community 19 - "align_timestamp_point_in_time"
Cohesion: 0.11
Nodes (8): align_timestamp_point_in_time(), enrich_article_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), SessionInfo, validate_anti_leakage(), TestPointInTimeAlignment

### Community 20 - "main.py"
Cohesion: 0.11
Nodes (13): autopilot_run_once(), execute_endpoint(), health(), hedge_evaluate_endpoint(), market_endpoint(), portfolio_endpoint(), purchases_endpoint(), regime_endpoint() (+5 more)

### Community 22 - ".filter_series"
Cohesion: 0.11
Nodes (3): AntiVolatilityModel, StabilizationResult, TestAntiVolatilityModel

### Community 23 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 24 - "mcp_server.py"
Cohesion: 0.09
Nodes (10): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision(), convene_agent_council_meeting(), get_virtual_office_status() (+2 more)

### Community 25 - "Profile"
Cohesion: 0.11
Nodes (8): baseline_profile(), build_bundle(), Profile, profile_from_row(), sensitivity_grid(), build_hunt_grid(), main(), TestFinancialModelingAdaptive

### Community 26 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 27 - "pipeline.py"
Cohesion: 0.15
Nodes (9): submit_bracket_buy(), fetch_prev_close(), build_candidate(), composite_score(), main(), news_deep_dive(), phase_night(), premarket_snapshot() (+1 more)

### Community 28 - "InstitutionalBenchmarkEngine"
Cohesion: 0.13
Nodes (3): BenchmarkMetrics, InstitutionalBenchmarkEngine, TestInstitutionalBenchmarkEngine

### Community 29 - "atomic_json_read"
Cohesion: 0.08
Nodes (8): check_liveness(), get_autopilot_heartbeat(), is_us_equity_market_open(), main(), run_daemon(), atomic_json_read(), atomic_json_write(), TestArchitectureFixes

### Community 30 - "hedging_engine.py"
Cohesion: 0.13
Nodes (9): days_to_target(), calculate_exit_levels(), calculate_hedge_pair(), compute_book_exposure(), _env_float(), get_exit_geometry(), _latest_close(), resolve_hedge_instrument() (+1 more)

### Community 31 - "risk/__init__.py"
Cohesion: 0.10
Nodes (8): get_adaptive_exit_geometry(), calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), TestAdaptiveExitGeometry, TestRegimeAdaptivePositionSizing

### Community 32 - "test_units.py"
Cohesion: 0.07
Nodes (11): generate_triple_barrier_labels(), check_tail_risk(), TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory, TestPurchaseLogger, TestRiskManager (+3 more)

### Community 33 - "test_jev_scooper.py"
Cohesion: 0.14
Nodes (3): JEVLiquidityScooper, ScoopOpportunity, TestJEVLiquidityScooper

### Community 34 - "api_flatten"
Cohesion: 0.15
Nodes (10): unwind_paired_hedge(), api_desks_scan(), api_flatten(), api_rescan(), api_scan(), _cancel_open_orders(), FlattenRequest, _leaderboard() (+2 more)

### Community 35 - "package.json"
Cohesion: 0.14
Nodes (13): eslintConfig, name, private, version, axios, eslint, eslint-config-next, react-dom (+5 more)

### Community 36 - "TestMultiDeskArchitecture"
Cohesion: 0.06
Nodes (3): CMEFuturesAutopilot, ForexAutopilot, TestMultiDeskArchitecture

### Community 37 - "layout.tsx"
Cohesion: 0.15
Nodes (5): nextConfig, geistMono, geistSans, metadata, next

### Community 38 - "types.ts"
Cohesion: 0.08
Nodes (29): DashboardPage(), ArticlesFeedProps, IndicatorPanel(), PortfolioBar(), PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps (+21 more)

### Community 39 - "process_trade_execution"
Cohesion: 0.16
Nodes (11): signal_endpoint(), get_portfolio_summary(), process_trade_execution(), get_client(), get_current_exposure(), get_portfolio_value(), submit_market_order(), submit_order() (+3 more)

### Community 40 - "pandas"
Cohesion: 0.16
Nodes (12): build_historical_dataset(), add_indicators(), get_latest(), get_market_features(), fetch_prices(), _fetch_with_yahoo_chart(), _fetch_with_yfinance(), _get_cache_path() (+4 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 44 - "numpy"
Cohesion: 0.21
Nodes (9): main(), simulate_night(), growth_optimal_f(), main(), mc_time_to_goal(), oos_r_pool(), pool_stats(), savings_months() (+1 more)

### Community 45 - "🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan"
Cohesion: 0.08
Nodes (25): 10. Quick-Start Commands, 1. Complete System Architecture Map, 2. Capital Architecture & Current State, 3. Financial Model Honest Audit, 3A. Closed Trade Performance (The Hard Truth), 3B. Bayesian Confidence Model — Current Assessment, 4. Root Cause Diagnosis: Why the System is Losing Money, 5. Improvement Plan: 8 Concrete Upgrades (+17 more)

### Community 46 - "tp1_scale_plan"
Cohesion: 0.15
Nodes (4): ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 47 - "daily_routine.py"
Cohesion: 0.10
Nodes (16): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), flat_universe() (+8 more)

### Community 48 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.21
Nodes (9): build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test(), add_label(), build_feature_vector(), build_features() (+1 more)

### Community 49 - "FactorDAG"
Cohesion: 0.20
Nodes (3): FactorDAG, evaluate_factor_dag(), TestFactorDAG

### Community 50 - "dashboard.py"
Cohesion: 0.21
Nodes (9): _esc(), _fmt_ts(), load_account(), load_journal(), main(), generate_once(), render_page(), seed_demo() (+1 more)

### Community 51 - "cost_model.py"
Cohesion: 0.21
Nodes (4): breakeven_move_pct(), is_trade_viable(), round_trip_cost(), TestCostModel

### Community 52 - "services.py"
Cohesion: 0.24
Nodes (7): EngineException, MarketDataNotFoundError, NLPAnalysisError, NoArticlesFoundError, get_hedge_evaluation(), get_processed_signal(), get_regime()

### Community 53 - "model/__init__.py"
Cohesion: 0.21
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 54 - "hedging_backtester.py"
Cohesion: 0.16
Nodes (8): main(), PairStrategySimulator, _print_report(), run_comparison(), simulate(), _strip_tz(), _trim(), _window()

### Community 55 - "scenario_c.sh"
Cohesion: 0.14
Nodes (13): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+5 more)

### Community 57 - "run_ross_momentum_sim"
Cohesion: 0.17
Nodes (7): generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), evaluate_five_pillars(), TestRossMomentumStrategy

### Community 58 - "pick_best_article"
Cohesion: 0.21
Nodes (4): directional_sentiment(), pick_best_article(), TestArticleSelection, TestTimeDecay

### Community 59 - "time"
Cohesion: 0.12
Nodes (10): _conn(), _main(), remember(), similar(), stats(), _tokens(), _vec(), CMEFuturesSignal (+2 more)

### Community 62 - "nlp/__init__.py"
Cohesion: 0.22
Nodes (7): evaluate_news_catalyst(), analyze(), analyze_sentiment_only(), compute_time_decay(), extract_entities(), _get_nlp(), preprocess()

### Community 63 - "api_remote_qr_svg"
Cohesion: 0.12
Nodes (10): api_auth_logout(), api_auth_status(), api_remote_qr_svg(), api_verify_pin(), graph_tree_view(), graph_view(), _is_request_authenticated(), pin_auth_middleware() (+2 more)

### Community 64 - "📈 Stock Signal Engine — Personal Quant Desk"
Cohesion: 0.12
Nodes (16): 🏗️ Architecture, Autopilot flags, 🧪 Backtesting Guide, 🧰 Command Reference, ⚙️ Configuration Knobs (env / .env — all optional), 📊 Dashboard, 📜 Disclaimer, 🖥️ Live Web App (`webapp/`) (+8 more)

### Community 66 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 68 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 69 - "mirror_dispatcher.py"
Cohesion: 0.22
Nodes (3): BrokerClientFactory, MirrorTradeSignal, ReplicationSummary

### Community 70 - "dependencies"
Cohesion: 0.22
Nodes (9): dependencies, axios, next, next-auth, react, react-dom, recharts, swr (+1 more)

### Community 71 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 72 - "store.ts"
Cohesion: 0.24
Nodes (8): MessagePayload, useWebSocket(), AppState, Article, Signal, useAppStore, react, zustand

### Community 73 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 74 - "walk_forward.py"
Cohesion: 0.25
Nodes (5): main(), month_folds(), _policy_summary(), _run_style(), walk_forward()

### Community 76 - "Win-Rate Optimization & Diagnostic Report"
Cohesion: 0.20
Nodes (9): 1. Empirical Loss Diagnostic (Baseline on 2024 -> today), 2. Validation Stability (2021-2023), 3. Out-of-Sample Performance Comparison (2024 -> today), 4. Crisis Stress Tests (Optimized Profile), 5. Summary & Takeaways, Per-Year Win Rate Comparison, Win Rate by SPY Regime at Entry, Win Rate by Year (+1 more)

### Community 78 - "run_autopilot.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_autopilot.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 79 - "run_webapp.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_webapp.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 80 - "scanner.py"
Cohesion: 0.53
Nodes (3): clamp(), main(), score_row()

### Community 82 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 83 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 84 - "domain_not_found_handler"
Cohesion: 0.53
Nodes (3): domain_not_found_handler(), engine_logic_handler(), global_crash_handler()

### Community 88 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 89 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 90 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 96 - "_simulate_bars"
Cohesion: 0.32
Nodes (4): Bundle, run_profile(), _simulate_bars(), window_run()

### Community 99 - "[...path]/route.ts"
Cohesion: 0.46
Nodes (7): buildHeaders(), createBackendUrl(), DELETE(), GET(), POST(), proxy(), PUT()

### Community 100 - "_start_port_8081_forwarder"
Cohesion: 0.32
Nodes (5): _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel()

### Community 102 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.29
Nodes (6): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 105 - "api_desks_status"
Cohesion: 0.40
Nodes (4): api_desks_status(), _find_process_pid(), _is_pid_alive(), _read_pid()

### Community 106 - "Five-Year Market Statistics"
Cohesion: 0.40
Nodes (4): Benchmark — SPY buy & hold, Five-Year Market Statistics, Leaderboard (by engine strategy final equity), Sector rollup (avg per stock)

### Community 107 - "Five-Year Market Statistics"
Cohesion: 0.40
Nodes (4): Benchmark — SPY buy & hold, Five-Year Market Statistics, Leaderboard (by engine strategy final equity), Sector rollup (avg per stock)

### Community 108 - "dashboard/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 109 - "[...nextauth]/route.ts"
Cohesion: 0.50
Nodes (3): auth, authOptions, next-auth

### Community 110 - "Pre-Market Plan — 2026-08-26"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-08-26

### Community 111 - "Pre-Market Plan — 2026-08-27"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-08-27

### Community 112 - "Pre-Market Plan — 2026-09-05"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-05

### Community 113 - "Pre-Market Plan — 2026-09-07"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-07

### Community 114 - "Pre-Market Plan — 2026-09-08"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-08

### Community 115 - "Pre-Market Plan — 2026-09-14"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-14

### Community 116 - "Pre-Market Plan — 2026-09-19"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-19

### Community 117 - "Pre-Market Plan — 2026-09-21"
Cohesion: 0.50
Nodes (3): Candidate detail, Launch tonight, Pre-Market Plan — 2026-09-21

## Knowledge Gaps
- **83 isolated node(s):** `axios`, `react-dom`, `@tailwindcss/postcss`, `@types/node`, `@types/react` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 980 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `TradeJournal`, `five_year_stats.py`, `daily_sniper.py`, `pathlib`, `TechnicalIndicators`, `BayesianConfidenceEngine`, `app.py`, `logging`, `Any`, `financial_modeling.py`, `factor_dag.py`, `os`, `AgentCouncil`, `.filter_series`, `mcp_server.py`, `pipeline.py`, `InstitutionalBenchmarkEngine`, `hedging_engine.py`, `api_flatten`, `TestMultiDeskArchitecture`, `daily_routine.py`, `hedging_backtester.py`, `run_ross_momentum_sim`, `time`, `analyze_exit`, `Any`, `ConvexTailEngine`, `run_multi_asset_benchmark`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **What connects `axios`, `react-dom`, `@tailwindcss/postcss` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TradeJournal` be split into smaller, more focused modules?**
  _Cohesion score 0.07400555041628122 - nodes in this community are weakly interconnected._
- **Why does `TestArchitectureFixes` connect `atomic_json_read` to `pipeline.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Should `five_year_stats.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12561576354679804 - nodes in this community are weakly interconnected._
- **Why does `CryptoFuturesAutopilot` connect `CryptoFuturesAutopilot` to `TestMultiDeskArchitecture`, `pathlib`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Should `daily_sniper.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10967741935483871 - nodes in this community are weakly interconnected._