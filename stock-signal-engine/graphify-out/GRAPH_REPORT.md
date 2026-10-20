# Graph Report - stock-signal-engine  (2026-10-20)

## Corpus Check
- 244 files · ~783,606 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: .csv 9, (none) 6, .bat 2)

## Summary
- 2484 nodes · 5473 edges · 146 communities (101 shown, 45 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 189 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0242414c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TradeJournal
- five_year_stats.py
- CMEFuturesAutopilot
- time
- financial_modeling.py
- AppDelegate
- TradeReviewPacket
- SubscriberProfile
- stock_analysis.py
- align_timestamp_point_in_time
- app.py
- BayesianConfidenceEngine
- get
- quant
- os
- factor_dag.py
- core.py
- AgentCouncil
- atomic_json_read
- CryptoFuturesAutopilot
- tunnel_manager.py
- test_units.py
- EquitiesSelfLearningTracker
- autopilot.py
- FactorDAG
- scenario_small.sh
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- .filter_series
- mcp_server.py
- scenario_sniper.sh
- pick_best_article
- hedging_engine.py
- TestPhysicalRiskPipeline
- InstitutionalBenchmarkEngine
- package.json
- pipeline.py
- [...path]/route.ts
- dashboard/page.tsx
- test_adaptive_hedging.py
- test_agent_council.py
- model/__init__.py
- compilerOptions
- shock_detector.py
- news_memory.py
- sentiment_hedged_vs_unhedged.py
- TestArchitectureFixes
- pandas
- 📈 Stock Signal Engine — Personal Quant Desk
- SelfImprovingExpectancyTracker
- JEVLiquidityScooper
- .test_defensive_scaling_on_losing_streak
- Any
- iOS Mobile App & Home Screen Widget Blueprint
- iOS Mobile App & Home Screen Widget Blueprint
- news_fetcher.py
- run_ross_momentum_sim
- dashboard.py
- FailureMemoryEngine
- alpha_client.py
- tp1_scale_plan
- types.ts
- ForexAutopilot
- scenario_c.sh
- ForexStrategyEngine
- daily_routine.py
- train.py
- web_server.py
- check_trading_window
- nlp/__init__.py
- services.py
- run_comprehensive_simulation
- banned_ticker
- manifest.json
- RiskPanel.tsx
- _leaderboard
- Win-Rate Optimization & Diagnostic Report
- ConvexTailEngine
- dependencies
- devDependencies
- store.ts
- StrategyFarmManager
- check_liveness
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- ForexSelfLearningTracker
- score_trade
- TestCryptoPerpFixes
- TestTechnicalIndicators
- api_verify_pin
- scanner.py
- run_autopilot.sh
- run_webapp.sh
- analyze_exit
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- get_purchase_logs
- QuantDesk Project & Deployment Architecture
- generate_triple_barrier_labels
- TestSMCCryptoStrategy
- argparse
- scripts
- Five-Year Market Statistics
- Five-Year Market Statistics
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- TestMultiDeskArchitecture
- watchdog.sh
- dashboard/README.md
- TriConfluenceMatrix
- Pre-Market Plan — 2026-08-26
- Pre-Market Plan — 2026-08-27
- Pre-Market Plan — 2026-09-05
- Pre-Market Plan — 2026-09-07
- Pre-Market Plan — 2026-09-08
- Pre-Market Plan — 2026-09-14
- Pre-Market Plan — 2026-09-19
- Pre-Market Plan — 2026-09-21
- api_desks_status
- host_architecture.md
- AGENTS.md
- postcss.config.mjs
- GEMINI.md
- calculate_dynamic_hedge_ratio
- time_to_goal_2026-09-21.md
- run_instagram_extractor.sh
- remote_setup.sh
- council.py
- domain_not_found_handler
- unittest
- numpy
- daily_sniper.py
- Article
- Candle
- is_trade_viable
- api_self_learning
- archive_pre_upgrade_trades.py
- ReplicationSummary

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

## Communities (146 total, 45 thin omitted)

### Community 1 - "five_year_stats.py"
Cohesion: 0.08
Nodes (19): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+11 more)

### Community 2 - "CMEFuturesAutopilot"
Cohesion: 0.06
Nodes (6): CMEFuturesAutopilot, main(), CMEFuturesSelfLearningTracker, CMEFuturesSignal, CMEFuturesStrategyEngine, TestCMEFuturesDeskFixes

### Community 3 - "time"
Cohesion: 0.09
Nodes (5): run_daemon(), FailureEpisode, StrategyItem, CryptoFuturesSignal, ForexSignal

### Community 4 - "financial_modeling.py"
Cohesion: 0.07
Nodes (23): baseline_profile(), build_bundle(), Bundle, crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats() (+15 more)

### Community 5 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 6 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 7 - "SubscriberProfile"
Cohesion: 0.09
Nodes (5): BrokerClientFactory, MirrorDispatcher, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 8 - "stock_analysis.py"
Cohesion: 0.10
Nodes (8): expected_move_pct(), analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _project_1m(), _verdict()

### Community 9 - "align_timestamp_point_in_time"
Cohesion: 0.11
Nodes (8): align_timestamp_point_in_time(), enrich_article_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), SessionInfo, validate_anti_leakage(), TestPointInTimeAlignment

### Community 10 - "app.py"
Cohesion: 0.07
Nodes (25): AIReviewRequest, api_compliance_ai_review(), api_council_convene(), api_council_decision(), api_farm_demote(), api_farm_promote(), api_flatten(), api_gateway_register_subscriber() (+17 more)

### Community 11 - "BayesianConfidenceEngine"
Cohesion: 0.08
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 12 - "get"
Cohesion: 0.06
Nodes (22): api_account(), api_advisor_exit(), api_book_allocation(), api_equity_curve(), api_evaluate(), api_health(), api_jev_opportunities(), api_journal_exits() (+14 more)

### Community 14 - "os"
Cohesion: 0.11
Nodes (10): get_settings(), Settings, submit_bracket_buy(), execute_jev_scoop_trade(), execute_ross_bracket_trade(), classify_position_book(), get_book_allocations(), get_split_ratios() (+2 more)

### Community 15 - "factor_dag.py"
Cohesion: 0.11
Nodes (9): generate_realistic_news_stream(), run_experiment(), AlphaCompositeNode, NewsSourceNode, Node, PointInTimeAlignmentNode, PriceSourceNode, SentimentAggregatorNode (+1 more)

### Community 16 - "core.py"
Cohesion: 0.09
Nodes (14): cmd_demo(), cmd_extract(), cmd_process(), main(), abstract_quant_content(), download_file(), encrypt_url_token(), extract_audio_tracks() (+6 more)

### Community 18 - "atomic_json_read"
Cohesion: 0.15
Nodes (3): atomic_json_read(), atomic_json_write(), main()

### Community 20 - "tunnel_manager.py"
Cohesion: 0.10
Nodes (15): api_remote_access(), api_remote_qr_svg(), get_active_tunnel_url(), get_local_ip(), get_qr_png_bytes(), get_qr_svg(), get_remote_status(), is_caffeinate_running() (+7 more)

### Community 21 - "test_units.py"
Cohesion: 0.08
Nodes (9): evaluate_five_pillars(), check_tail_risk(), TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory, TestPurchaseLogger, TestRiskManager (+1 more)

### Community 22 - "EquitiesSelfLearningTracker"
Cohesion: 0.09
Nodes (3): EquitiesSelfLearningTracker, InstitutionalEquitiesStrategy, TestEquitiesDesk1Fixes

### Community 23 - "autopilot.py"
Cohesion: 0.10
Nodes (16): auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open(), post_market_belief_cycle() (+8 more)

### Community 24 - "FactorDAG"
Cohesion: 0.20
Nodes (3): FactorDAG, evaluate_factor_dag(), TestFactorDAG

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
Cohesion: 0.12
Nodes (14): align_event_point_in_time(), analyze_financial_sentiment(), check_alpaca_account(), convene_agent_council_meeting(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health() (+6 more)

### Community 29 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 30 - "pick_best_article"
Cohesion: 0.21
Nodes (4): directional_sentiment(), pick_best_article(), TestArticleSelection, TestTimeDecay

### Community 31 - "hedging_engine.py"
Cohesion: 0.09
Nodes (10): days_to_target(), calculate_exit_levels(), compute_book_exposure(), _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), _latest_close(), resolve_hedge_instrument() (+2 more)

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
Cohesion: 0.13
Nodes (12): get_universe(), format_purchase_log(), log_purchase(), fetch_all(), build_candidate(), composite_score(), main(), news_deep_dive() (+4 more)

### Community 36 - "[...path]/route.ts"
Cohesion: 0.12
Nodes (12): nextConfig, buildHeaders(), createBackendUrl(), DELETE(), GET(), POST(), proxy(), PUT() (+4 more)

### Community 37 - "dashboard/page.tsx"
Cohesion: 0.22
Nodes (14): DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch(), useMarket() (+6 more)

### Community 38 - "test_adaptive_hedging.py"
Cohesion: 0.16
Nodes (6): calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), TestRegimeAdaptivePositionSizing

### Community 39 - "test_agent_council.py"
Cohesion: 0.12
Nodes (5): convene_council_meeting(), get_floor_status(), resolve_council_decision(), get_virtual_office_status(), TestAgentCouncilArchitecture

### Community 40 - "model/__init__.py"
Cohesion: 0.22
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 41 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 42 - "shock_detector.py"
Cohesion: 0.08
Nodes (7): is_us_equity_market_open(), detect_intraday_shock(), _env_float(), gap_shock_threshold(), velocity_shock_threshold(), TestProjectOmega, TestShockDetector

### Community 43 - "news_memory.py"
Cohesion: 0.29
Nodes (7): _conn(), _main(), remember(), similar(), stats(), _tokens(), _vec()

### Community 44 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.12
Nodes (12): build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test(), add_label(), build_feature_vector(), build_features() (+4 more)

### Community 46 - "pandas"
Cohesion: 0.13
Nodes (11): run_test(), run_mean_reversion(), calculate_asset_beta(), fetch_latest_price(), fetch_prices(), _fetch_with_yahoo_chart(), _fetch_with_yfinance(), _get_cache_path() (+3 more)

### Community 47 - "📈 Stock Signal Engine — Personal Quant Desk"
Cohesion: 0.12
Nodes (16): 🏗️ Architecture, Autopilot flags, 🧪 Backtesting Guide, 🧰 Command Reference, ⚙️ Configuration Knobs (env / .env — all optional), 📊 Dashboard, 📜 Disclaimer, 🖥️ Live Web App (`webapp/`) (+8 more)

### Community 49 - "JEVLiquidityScooper"
Cohesion: 0.15
Nodes (3): JEVLiquidityScooper, ScoopOpportunity, TestJEVLiquidityScooper

### Community 51 - "Any"
Cohesion: 0.08
Nodes (12): api_benchmark_summary(), api_compliance_report(), api_confluence_evaluate(), api_council_recent(), api_council_status(), api_desks_benchmark(), api_farm_status(), api_gateway_list_subscribers() (+4 more)

### Community 52 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 53 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 54 - "news_fetcher.py"
Cohesion: 0.07
Nodes (26): fetch_earnings(), _normalize(), fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news(), _get_alpaca_news_client() (+18 more)

### Community 55 - "run_ross_momentum_sim"
Cohesion: 0.22
Nodes (6): generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), TestRossMomentumStrategy

### Community 56 - "dashboard.py"
Cohesion: 0.21
Nodes (9): _esc(), _fmt_ts(), load_account(), load_journal(), main(), generate_once(), render_page(), seed_demo() (+1 more)

### Community 58 - "alpha_client.py"
Cohesion: 0.20
Nodes (9): process_trade_execution(), get_client(), get_portfolio_value(), submit_market_order(), submit_order(), submit_pair_orders(), execute_hedged_trade(), execute_trade() (+1 more)

### Community 59 - "tp1_scale_plan"
Cohesion: 0.15
Nodes (4): ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 60 - "types.ts"
Cohesion: 0.33
Nodes (7): api, MarketFeatures, PortfolioResponse, RiskDecision, SignalResponse, SignalResult, swr

### Community 62 - "scenario_c.sh"
Cohesion: 0.14
Nodes (13): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+5 more)

### Community 64 - "daily_routine.py"
Cohesion: 0.14
Nodes (13): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), flat_universe() (+5 more)

### Community 65 - "train.py"
Cohesion: 0.18
Nodes (5): build_historical_dataset(), train(), build_bootstrap_dataframe(), load_or_build_training_dataframe(), main()

### Community 66 - "web_server.py"
Cohesion: 0.18
Nodes (3): get_preset(), serve_index(), serve_media()

### Community 67 - "check_trading_window"
Cohesion: 0.25
Nodes (5): check_trading_window(), discover_market_universe(), scan_momentum_market(), api_ross_runners(), api_ross_window()

### Community 68 - "nlp/__init__.py"
Cohesion: 0.18
Nodes (9): evaluate_news_catalyst(), analyze_sentiment(), _get_finbert(), analyze(), analyze_sentiment_only(), compute_time_decay(), extract_entities(), _get_nlp() (+1 more)

### Community 69 - "services.py"
Cohesion: 0.11
Nodes (21): autopilot_run_once(), execute_endpoint(), health(), hedge_evaluate_endpoint(), market_endpoint(), portfolio_endpoint(), purchases_endpoint(), regime_endpoint() (+13 more)

### Community 70 - "run_comprehensive_simulation"
Cohesion: 0.24
Nodes (6): run_comprehensive_simulation(), simulate_crypto_desk(), simulate_forex_desk(), simulate_futures_desk(), simulate_stock_desk(), TradeRecord

### Community 71 - "banned_ticker"
Cohesion: 0.23
Nodes (4): main(), save_report(), TwentyYearStrategyEngine, banned_ticker()

### Community 72 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 73 - "RiskPanel.tsx"
Cohesion: 0.22
Nodes (5): PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps, recharts

### Community 74 - "_leaderboard"
Cohesion: 0.18
Nodes (9): api_desks_scan(), api_scan(), _leaderboard(), _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel() (+1 more)

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
Cohesion: 0.28
Nodes (7): MessagePayload, useWebSocket(), AppState, Article, Signal, useAppStore, react

### Community 82 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 83 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 84 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 89 - "api_verify_pin"
Cohesion: 0.15
Nodes (8): api_auth_logout(), api_auth_status(), api_verify_pin(), graph_tree_view(), graph_view(), _is_request_authenticated(), pin_auth_middleware(), PinVerifyRequest

### Community 90 - "scanner.py"
Cohesion: 0.53
Nodes (3): clamp(), main(), score_row()

### Community 91 - "run_autopilot.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_autopilot.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 92 - "run_webapp.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_webapp.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 94 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.29
Nodes (6): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 95 - "get_purchase_logs"
Cohesion: 0.33
Nodes (4): backfill_historical_purchases(), get_purchase_log_text(), get_purchase_logs(), api_purchases()

### Community 96 - "QuantDesk Project & Deployment Architecture"
Cohesion: 0.33
Nodes (5): 1. Executive Summary & Host Topography, 2. Remote Access & Tailscale Networking Rules, 3. Core Desks & Automation Components, Critical Infrastructure Topology, QuantDesk Project & Deployment Architecture

### Community 100 - "argparse"
Cohesion: 0.10
Nodes (13): main(), _print_report(), run_comparison(), _window(), _run_style(), run_diagnostic(), main(), cross_reference_batch() (+5 more)

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

### Community 108 - "TriConfluenceMatrix"
Cohesion: 0.25
Nodes (3): ConfluenceDecision, TriConfluenceMatrix, TestTriConfluenceMatrix

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

### Community 117 - "api_desks_status"
Cohesion: 0.33
Nodes (4): api_desks_status(), _find_process_pid(), _is_pid_alive(), _read_pid()

### Community 132 - "council.py"
Cohesion: 0.31
Nodes (3): CouncilMeetingResult, DeskAgent, get_recent_meetings()

### Community 133 - "domain_not_found_handler"
Cohesion: 0.53
Nodes (3): domain_not_found_handler(), engine_logic_handler(), global_crash_handler()

### Community 135 - "numpy"
Cohesion: 0.14
Nodes (11): run_multi_asset_benchmark(), simulate_asset_trades(), main(), simulate_night(), growth_optimal_f(), main(), mc_time_to_goal(), oos_r_pool() (+3 more)

### Community 136 - "daily_sniper.py"
Cohesion: 0.14
Nodes (9): get_sniper_setup(), main(), main(), mass_backtest(), print_mass_report(), rank_market(), scan_dip_opportunities(), detect_market_regime() (+1 more)

### Community 137 - "Article"
Cohesion: 0.32
Nodes (4): ArticlesFeedProps, SentimentHeatmapProps, sources, Article

## Knowledge Gaps
- **83 isolated node(s):** `axios`, `react-dom`, `@tailwindcss/postcss`, `@types/node`, `@types/react` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1093 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **45 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `five_year_stats.py`, `CMEFuturesAutopilot`, `time`, `financial_modeling.py`, `council.py`, `numpy`, `daily_sniper.py`, `stock_analysis.py`, `.fetch_live_bars`, `Any`, `BayesianConfidenceEngine`, `app.py`, `os`, `factor_dag.py`, `get`, `AgentCouncil`, `test_units.py`, `autopilot.py`, `.filter_series`, `mcp_server.py`, `hedging_engine.py`, `InstitutionalBenchmarkEngine`, `pipeline.py`, `shock_detector.py`, `sentiment_hedged_vs_unhedged.py`, `daily_routine.py`, `train.py`, `run_comprehensive_simulation`, `banned_ticker`, `_leaderboard`, `ConvexTailEngine`, `analyze_exit`, `argparse`, `TriConfluenceMatrix`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **What connects `axios`, `react-dom`, `@tailwindcss/postcss` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TradeJournal` be split into smaller, more focused modules?**
  _Cohesion score 0.10873440285204991 - nodes in this community are weakly interconnected._
- **Why does `SelfImprovingExpectancyTracker` connect `SelfImprovingExpectancyTracker` to `TestSMCCryptoStrategy`, `time`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `five_year_stats.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08416389811738649 - nodes in this community are weakly interconnected._
- **Why does `TechnicalIndicators` connect `pandas` to `five_year_stats.py`, `time`, `argparse`, `financial_modeling.py`, `banned_ticker`, `daily_sniper.py`, `stock_analysis.py`, `BayesianConfidenceEngine`, `TriConfluenceMatrix`, `factor_dag.py`, `JEVLiquidityScooper`, `test_units.py`, `TestTechnicalIndicators`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `CMEFuturesAutopilot` be split into smaller, more focused modules?**
  _Cohesion score 0.0636734693877551 - nodes in this community are weakly interconnected._