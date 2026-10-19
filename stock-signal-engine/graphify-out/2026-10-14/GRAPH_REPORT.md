# Graph Report - stock-signal-engine  (2026-10-14)

## Corpus Check
- 208 files · ~434,267 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: .csv 9, (none) 6, .ico 1)

## Summary
- 2208 nodes · 4859 edges · 130 communities (102 shown, 28 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 148 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2ec6d8a5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TradeJournal
- five_year_stats.py
- get_market_features
- AppDelegate
- TradeReviewPacket
- SubscriberProfile
- pandas
- analyze_exit
- post
- BayesianConfidenceEngine
- Any
- os
- tunnel_manager.py
- quant
- news_fetcher.py
- mcp_server.py
- TestProjectOmega
- FactorDAG
- autopilot.py
- align_timestamp_point_in_time
- main.py
- atomic_json_read
- .filter_series
- scenario_small.sh
- council.py
- financial_modeling.py
- scenario_sniper.sh
- pipeline.py
- InstitutionalBenchmarkEngine
- sys
- run_ross_momentum_sim
- risk/__init__.py
- test_units.py
- JEVLiquidityScooper
- app.py
- package.json
- TestMultiDeskArchitecture
- [...path]/route.ts
- dashboard/page.tsx
- services.py
- time
- train.py
- compilerOptions
- CryptoFuturesAutopilot
- numpy
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- tp1_scale_plan
- daily_routine.py
- model/__init__.py
- get_processed_signal
- dashboard.py
- argparse
- sentiment_hedged_vs_unhedged.py
- hedging_engine.py
- TestTechnicalIndicators
- scenario_c.sh
- ForexStrategyEngine
- .test_defensive_scaling_on_losing_streak
- pick_best_article
- news_memory.py
- walk_forward.py
- TestArchitectureFixes
- nlp/__init__.py
- api_remote_qr_svg
- 📈 Stock Signal Engine — Personal Quant Desk
- shock_detector.py
- manifest.json
- score_trade
- iOS Mobile App & Home Screen Widget Blueprint
- types.ts
- dependencies
- devDependencies
- store.ts
- iOS Mobile App & Home Screen Widget Blueprint
- RiskPanel.tsx
- execute_ross_bracket_trade
- Win-Rate Optimization & Diagnostic Report
- market_scanner.py
- run_autopilot.sh
- run_webapp.sh
- scanner.py
- ConvexTailEngine
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- domain_not_found_handler
- atomic_json_write
- check_trading_window
- calculate_exit_levels
- scripts
- Crisis-Tested Financial Model
- watchdog.sh
- run_autopilot
- analyze_sentiment
- _is_request_authenticated
- postcss.config.mjs
- get_purchase_log_text
- banned_ticker
- _start_port_8081_forwarder
- Article
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- get
- Candle
- Five-Year Market Statistics
- Five-Year Market Statistics
- dashboard/README.md
- check_tail_risk
- Pre-Market Plan — 2026-08-26
- Pre-Market Plan — 2026-08-27
- Pre-Market Plan — 2026-09-05
- Pre-Market Plan — 2026-09-07
- Pre-Market Plan — 2026-09-08
- Pre-Market Plan — 2026-09-14
- Pre-Market Plan — 2026-09-19
- Pre-Market Plan — 2026-09-21
- generate_realistic_news_stream
- AGENTS.md
- GEMINI.md
- time_to_goal_2026-09-21.md
- CryptoPerpStrategyEngine
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- CMEFuturesStrategyEngine
- build_historical_dataset
- _cancel_open_orders

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 77 edges
2. `TechnicalIndicators` - 40 edges
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

## Communities (130 total, 28 thin omitted)

### Community 1 - "five_year_stats.py"
Cohesion: 0.08
Nodes (19): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+11 more)

### Community 2 - "get_market_features"
Cohesion: 0.27
Nodes (4): market_endpoint(), add_indicators(), get_latest(), get_market_features()

### Community 3 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 4 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 5 - "SubscriberProfile"
Cohesion: 0.09
Nodes (4): MirrorDispatcher, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 6 - "pandas"
Cohesion: 0.15
Nodes (9): run_test(), run_mean_reversion(), fetch_prices(), _fetch_with_yahoo_chart(), _fetch_with_yfinance(), _get_cache_path(), _load_cache(), _save_cache() (+1 more)

### Community 7 - "analyze_exit"
Cohesion: 0.08
Nodes (9): analyze_exit(), analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _project_1m(), _verdict() (+1 more)

### Community 8 - "post"
Cohesion: 0.08
Nodes (18): AIReviewRequest, api_compliance_ai_review(), api_council_convene(), api_council_decision(), api_gateway_register_subscriber(), api_gateway_replicate(), api_jev_execute(), api_model_confidence_evaluate() (+10 more)

### Community 9 - "BayesianConfidenceEngine"
Cohesion: 0.08
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 10 - "Any"
Cohesion: 0.10
Nodes (10): api_benchmark_summary(), api_compliance_report(), api_confluence_evaluate(), api_council_recent(), api_council_status(), api_desks_benchmark(), api_gateway_list_subscribers(), api_gateway_mirror_history() (+2 more)

### Community 11 - "os"
Cohesion: 0.16
Nodes (6): get_settings(), Settings, execute_jev_scoop_trade(), classify_position_book(), get_book_allocations(), get_split_ratios()

### Community 12 - "tunnel_manager.py"
Cohesion: 0.10
Nodes (14): api_remote_access(), _tunnel(), get_active_tunnel_url(), get_local_ip(), get_qr_png_bytes(), get_remote_status(), is_caffeinate_running(), is_tunnel_evicted() (+6 more)

### Community 14 - "news_fetcher.py"
Cohesion: 0.07
Nodes (26): fetch_earnings(), _normalize(), fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news(), _get_alpaca_news_client() (+18 more)

### Community 15 - "mcp_server.py"
Cohesion: 0.14
Nodes (13): get_client(), align_event_point_in_time(), analyze_financial_sentiment(), check_alpaca_account(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health() (+5 more)

### Community 17 - "FactorDAG"
Cohesion: 0.08
Nodes (11): run_experiment(), AlphaCompositeNode, FactorDAG, NewsSourceNode, Node, PointInTimeAlignmentNode, PriceSourceNode, SentimentAggregatorNode (+3 more)

### Community 18 - "autopilot.py"
Cohesion: 0.17
Nodes (11): submit_market_order(), _await_fill(), _day_guard(), load_state(), manage_open_positions(), run_scan(), save_state(), unwind_paired_hedge() (+3 more)

### Community 19 - "align_timestamp_point_in_time"
Cohesion: 0.10
Nodes (8): align_timestamp_point_in_time(), enrich_article_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), SessionInfo, validate_anti_leakage(), TestPointInTimeAlignment

### Community 20 - "main.py"
Cohesion: 0.13
Nodes (9): autopilot_run_once(), execute_endpoint(), regime_endpoint(), EngineException, ExecuteRequest, MarketDataNotFoundError, NLPAnalysisError, NoArticlesFoundError (+1 more)

### Community 21 - "atomic_json_read"
Cohesion: 0.14
Nodes (4): AgentCouncil, CouncilTurn, get_recent_meetings(), atomic_json_read()

### Community 22 - ".filter_series"
Cohesion: 0.11
Nodes (3): AntiVolatilityModel, StabilizationResult, TestAntiVolatilityModel

### Community 23 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 24 - "council.py"
Cohesion: 0.09
Nodes (9): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), resolve_council_decision(), convene_agent_council_meeting(), get_virtual_office_status(), submit_human_decision() (+1 more)

### Community 25 - "financial_modeling.py"
Cohesion: 0.06
Nodes (24): baseline_profile(), build_bundle(), Bundle, crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats() (+16 more)

### Community 26 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 27 - "pipeline.py"
Cohesion: 0.12
Nodes (13): rank_market(), get_universe(), submit_bracket_buy(), format_purchase_log(), log_purchase(), build_candidate(), composite_score(), main() (+5 more)

### Community 28 - "InstitutionalBenchmarkEngine"
Cohesion: 0.08
Nodes (6): BenchmarkMetrics, InstitutionalBenchmarkEngine, ConfluenceDecision, TriConfluenceMatrix, TestTriConfluenceMatrix, TestInstitutionalBenchmarkEngine

### Community 29 - "sys"
Cohesion: 0.16
Nodes (4): check_liveness(), get_autopilot_heartbeat(), main(), run_daemon()

### Community 30 - "run_ross_momentum_sim"
Cohesion: 0.22
Nodes (6): generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), TestRossMomentumStrategy

### Community 31 - "risk/__init__.py"
Cohesion: 0.18
Nodes (6): calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), TestRegimeAdaptivePositionSizing

### Community 32 - "test_units.py"
Cohesion: 0.07
Nodes (9): evaluate_five_pillars(), days_to_target(), TestCostModel, TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory, TestPurchaseLogger (+1 more)

### Community 33 - "JEVLiquidityScooper"
Cohesion: 0.15
Nodes (3): JEVLiquidityScooper, ScoopOpportunity, TestJEVLiquidityScooper

### Community 34 - "app.py"
Cohesion: 0.11
Nodes (14): get_purchase_logs(), _account_snapshot(), api_account(), api_desks_scan(), api_desks_status(), api_purchases(), api_rescan(), api_scan() (+6 more)

### Community 35 - "package.json"
Cohesion: 0.10
Nodes (18): eslintConfig, name, private, version, auth, authOptions, config, axios (+10 more)

### Community 36 - "TestMultiDeskArchitecture"
Cohesion: 0.05
Nodes (4): CMEFuturesAutopilot, main(), ForexAutopilot, TestMultiDeskArchitecture

### Community 37 - "[...path]/route.ts"
Cohesion: 0.12
Nodes (12): nextConfig, buildHeaders(), createBackendUrl(), DELETE(), GET(), POST(), proxy(), PUT() (+4 more)

### Community 38 - "dashboard/page.tsx"
Cohesion: 0.22
Nodes (14): DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch(), useMarket() (+6 more)

### Community 39 - "services.py"
Cohesion: 0.21
Nodes (8): get_portfolio_summary(), process_trade_execution(), get_current_exposure(), get_portfolio_value(), submit_order(), submit_pair_orders(), execute_hedged_trade(), execute_trade()

### Community 40 - "time"
Cohesion: 0.10
Nodes (3): BrokerClientFactory, ReplicationSummary, ForexSignal

### Community 41 - "train.py"
Cohesion: 0.21
Nodes (4): train(), build_bootstrap_dataframe(), load_or_build_training_dataframe(), main()

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "CryptoFuturesAutopilot"
Cohesion: 0.09
Nodes (3): CryptoFuturesAutopilot, main(), TestCryptoPerpFixes

### Community 44 - "numpy"
Cohesion: 0.14
Nodes (11): run_multi_asset_benchmark(), simulate_asset_trades(), main(), simulate_night(), growth_optimal_f(), main(), mc_time_to_goal(), oos_r_pool() (+3 more)

### Community 45 - "🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan"
Cohesion: 0.08
Nodes (25): 10. Quick-Start Commands, 1. Complete System Architecture Map, 2. Capital Architecture & Current State, 3. Financial Model Honest Audit, 3A. Closed Trade Performance (The Hard Truth), 3B. Bayesian Confidence Model — Current Assessment, 4. Root Cause Diagnosis: Why the System is Losing Money, 5. Improvement Plan: 8 Concrete Upgrades (+17 more)

### Community 46 - "tp1_scale_plan"
Cohesion: 0.13
Nodes (5): compute_book_exposure(), ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 47 - "daily_routine.py"
Cohesion: 0.21
Nodes (10): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), flat_universe() (+2 more)

### Community 48 - "model/__init__.py"
Cohesion: 0.21
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 49 - "get_processed_signal"
Cohesion: 0.18
Nodes (9): health(), hedge_evaluate_endpoint(), portfolio_endpoint(), sentiment_endpoint(), signal_endpoint(), get_hedge_evaluation(), get_processed_signal(), build_books() (+1 more)

### Community 50 - "dashboard.py"
Cohesion: 0.21
Nodes (9): _esc(), _fmt_ts(), load_account(), load_journal(), main(), generate_once(), render_page(), seed_demo() (+1 more)

### Community 51 - "argparse"
Cohesion: 0.12
Nodes (8): main(), _print_report(), run_comparison(), _window(), breakeven_move_pct(), expected_move_pct(), is_trade_viable(), round_trip_cost()

### Community 52 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.26
Nodes (7): main(), print_comparison(), run_signal_pipeline(), stress_test(), add_label(), build_feature_vector(), build_features()

### Community 53 - "hedging_engine.py"
Cohesion: 0.10
Nodes (10): get_sniper_setup(), main(), calculate_asset_beta(), detect_market_regime(), calculate_dynamic_hedge_ratio(), calculate_hedge_pair(), is_hot_banned(), _latest_close() (+2 more)

### Community 55 - "scenario_c.sh"
Cohesion: 0.14
Nodes (13): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+5 more)

### Community 58 - "pick_best_article"
Cohesion: 0.19
Nodes (4): directional_sentiment(), pick_best_article(), TestArticleSelection, TestTimeDecay

### Community 59 - "news_memory.py"
Cohesion: 0.29
Nodes (7): _conn(), _main(), remember(), similar(), stats(), _tokens(), _vec()

### Community 60 - "walk_forward.py"
Cohesion: 0.25
Nodes (5): main(), month_folds(), _policy_summary(), _run_style(), walk_forward()

### Community 62 - "nlp/__init__.py"
Cohesion: 0.24
Nodes (7): evaluate_news_catalyst(), analyze(), analyze_sentiment_only(), compute_time_decay(), extract_entities(), _get_nlp(), preprocess()

### Community 63 - "api_remote_qr_svg"
Cohesion: 0.17
Nodes (7): api_auth_logout(), api_remote_qr_svg(), api_verify_pin(), graph_tree_view(), graph_view(), PinVerifyRequest, get_qr_svg()

### Community 64 - "📈 Stock Signal Engine — Personal Quant Desk"
Cohesion: 0.12
Nodes (16): 🏗️ Architecture, Autopilot flags, 🧪 Backtesting Guide, 🧰 Command Reference, ⚙️ Configuration Knobs (env / .env — all optional), 📊 Dashboard, 📜 Disclaimer, 🖥️ Live Web App (`webapp/`) (+8 more)

### Community 65 - "shock_detector.py"
Cohesion: 0.15
Nodes (8): is_us_equity_market_open(), fetch_latest_price(), detect_intraday_shock(), earnings_blackout(), _env_float(), gap_shock_threshold(), velocity_shock_threshold(), TestShockDetector

### Community 66 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 68 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 69 - "types.ts"
Cohesion: 0.33
Nodes (7): api, MarketFeatures, PortfolioResponse, RiskDecision, SignalResponse, SignalResult, swr

### Community 70 - "dependencies"
Cohesion: 0.22
Nodes (9): dependencies, axios, next, next-auth, react, react-dom, recharts, swr (+1 more)

### Community 71 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 72 - "store.ts"
Cohesion: 0.28
Nodes (7): MessagePayload, useWebSocket(), AppState, Article, Signal, useAppStore, react

### Community 73 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 74 - "RiskPanel.tsx"
Cohesion: 0.22
Nodes (5): PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps, recharts

### Community 76 - "Win-Rate Optimization & Diagnostic Report"
Cohesion: 0.20
Nodes (9): 1. Empirical Loss Diagnostic (Baseline on 2024 -> today), 2. Validation Stability (2021-2023), 3. Out-of-Sample Performance Comparison (2024 -> today), 4. Crisis Stress Tests (Optimized Profile), 5. Summary & Takeaways, Per-Year Win Rate Comparison, Win Rate by SPY Regime at Entry, Win Rate by Year (+1 more)

### Community 77 - "market_scanner.py"
Cohesion: 0.31
Nodes (4): main(), mass_backtest(), print_mass_report(), scan_dip_opportunities()

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

### Community 85 - "atomic_json_write"
Cohesion: 0.22
Nodes (3): _sleep_with_heartbeat(), update_heartbeat(), atomic_json_write()

### Community 86 - "check_trading_window"
Cohesion: 0.29
Nodes (4): auto_select(), check_trading_window(), discover_market_universe(), scan_momentum_market()

### Community 87 - "calculate_exit_levels"
Cohesion: 0.15
Nodes (6): calculate_exit_levels(), _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), TestAdaptiveExitGeometry, TestExitEngine

### Community 88 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 89 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 90 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 91 - "run_autopilot"
Cohesion: 0.25
Nodes (4): main(), market_is_open(), post_market_belief_cycle(), run_autopilot()

### Community 93 - "_is_request_authenticated"
Cohesion: 0.38
Nodes (3): api_auth_status(), _is_request_authenticated(), pin_auth_middleware()

### Community 96 - "get_purchase_log_text"
Cohesion: 0.40
Nodes (3): purchases_endpoint(), backfill_historical_purchases(), get_purchase_log_text()

### Community 99 - "banned_ticker"
Cohesion: 0.23
Nodes (4): main(), save_report(), TwentyYearStrategyEngine, banned_ticker()

### Community 100 - "_start_port_8081_forwarder"
Cohesion: 0.38
Nodes (4): _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache()

### Community 101 - "Article"
Cohesion: 0.32
Nodes (4): ArticlesFeedProps, SentimentHeatmapProps, sources, Article

### Community 102 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.29
Nodes (6): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 104 - "get"
Cohesion: 0.06
Nodes (23): api_advisor_exit(), api_book_allocation(), api_equity_curve(), api_evaluate(), api_health(), api_jev_opportunities(), api_journal_exits(), api_journal_summary() (+15 more)

### Community 106 - "Five-Year Market Statistics"
Cohesion: 0.40
Nodes (4): Benchmark — SPY buy & hold, Five-Year Market Statistics, Leaderboard (by engine strategy final equity), Sector rollup (avg per stock)

### Community 107 - "Five-Year Market Statistics"
Cohesion: 0.40
Nodes (4): Benchmark — SPY buy & hold, Five-Year Market Statistics, Leaderboard (by engine strategy final equity), Sector rollup (avg per stock)

### Community 108 - "dashboard/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

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

### Community 125 - "20-Year Institutional Strategy & Swing-Shield Benchmark"
Cohesion: 0.40
Nodes (4): 20-Year Institutional Strategy & Swing-Shield Benchmark, Multi-Desk 30% YoY Synergy Architecture, Performance Comparison vs Market Benchmark, Year-by-Year Historical Breakdown (2007 - 2026)

### Community 127 - "build_historical_dataset"
Cohesion: 0.27
Nodes (3): build_historical_dataset(), generate_triple_barrier_labels(), TestTripleBarrier

## Knowledge Gaps
- **83 isolated node(s):** `axios`, `react-dom`, `@tailwindcss/postcss`, `@types/node`, `@types/react` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 988 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `five_year_stats.py`, `get_market_features`, `analyze_exit`, `BayesianConfidenceEngine`, `mcp_server.py`, `FactorDAG`, `autopilot.py`, `atomic_json_read`, `.filter_series`, `council.py`, `financial_modeling.py`, `pipeline.py`, `InstitutionalBenchmarkEngine`, `test_units.py`, `app.py`, `TestMultiDeskArchitecture`, `time`, `numpy`, `daily_routine.py`, `argparse`, `hedging_engine.py`, `shock_detector.py`, `execute_ross_bracket_trade`, `market_scanner.py`, `ConvexTailEngine`, `banned_ticker`, `get`, `build_historical_dataset`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **What connects `axios`, `react-dom`, `@tailwindcss/postcss` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TradeJournal` be split into smaller, more focused modules?**
  _Cohesion score 0.10873440285204991 - nodes in this community are weakly interconnected._
- **Why does `TechnicalIndicators` connect `pandas` to `test_units.py`, `five_year_stats.py`, `JEVLiquidityScooper`, `banned_ticker`, `analyze_exit`, `time`, `BayesianConfidenceEngine`, `market_scanner.py`, `FactorDAG`, `argparse`, `hedging_engine.py`, `TestTechnicalIndicators`, `financial_modeling.py`, `pipeline.py`, `InstitutionalBenchmarkEngine`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Should `five_year_stats.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08416389811738649 - nodes in this community are weakly interconnected._
- **Why does `BayesianConfidenceEngine` connect `BayesianConfidenceEngine` to `pandas`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Should `AppDelegate` be split into smaller, more focused modules?**
  _Cohesion score 0.07743496672716274 - nodes in this community are weakly interconnected._