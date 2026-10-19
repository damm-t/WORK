# Graph Report - WORK  (2026-10-19)

## Corpus Check
- 230 files · ~613,750 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 33 file(s) not represented in the graph (top: .csv 15, (none) 9, .ipynb 3)

## Summary
- 2307 nodes · 4937 edges · 147 communities (99 shown, 48 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 117 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `660da670`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Any
- tunnel_manager.py
- quant
- app.py
- FailureMemoryEngine
- scenario_small.sh
- AppDelegate
- get
- time
- manifest.json
- test_units.py
- run_autopilot.sh
- run_webapp.sh
- types.ts
- post
- atomic_json_read
- Series
- watchdog.sh
- score_trade
- news_fetcher.py
- test_project_omega.py
- .filter_series
- ConvexTailEngine
- TradeReviewPacket
- core.py
- SubscriberProfile
- TradeJournal
- BayesianConfidenceEngine
- shock_detector.py
- CryptoFuturesAutopilot
- ForexAutopilot
- argparse
- dashboard.py
- AgentCouncil
- ForexStrategyEngine
- pandas
- hedging_engine.py
- financial_modeling.py
- json
- TestProjectOmega
- TestDynamicHedgeRatio
- iOS Mobile App & Home Screen Widget Blueprint
- daily_routine.py
- low_float_scanner.py
- align_timestamp_point_in_time
- CryptoPerpStrategyEngine
- FactorDAG
- CMEFuturesStrategyEngine
- run_diagnostic
- five_year_stats.py
- os
- mcp_server.py
- services.py
- unittest
- tp1_scale_plan
- web_server.py
- model/__init__.py
- .test_defensive_scaling_on_losing_streak
- validate_anti_leakage
- test_adaptive_hedging.py
- get_purchase_logs
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- numpy
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
- .evaluate_ticker
- daily_sniper.py
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- market_scanner.py
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- iOS Mobile App & Home Screen Widget Blueprint
- dataset_generator.py
- package.json
- GEMINI.md
- external_alpha_bridge.py
- analyze_exit
- scenario_c.sh
- next
- test_physical_risk_pipeline.py
- InstitutionalBenchmarkEngine
- store.ts
- Win-Rate Optimization & Diagnostic Report
- dependencies
- devDependencies
- factor_dag.py
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- TestAgentCouncilArchitecture
- scanner.py
- scripts
- Five-Year Market Statistics
- Five-Year Market Statistics
- TestInstitutionalBenchmarkEngine
- get_regime
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
- Request
- analyze_sentiment
- get_portfolio_summary
- QuantDesk Project & Deployment Architecture
- TestArticleSelection
- calculate_exit_levels
- api_remote_qr_svg
- walk_forward.py
- host_architecture.md
- remote_setup.sh

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 55 edges
2. `atomic_json_read()` - 38 edges
3. `atomic_json_write()` - 32 edges
4. `TechnicalIndicators` - 32 edges
5. `TradeJournal` - 25 edges
6. `AppDelegate` - 22 edges
7. `align_timestamp_point_in_time()` - 22 edges
8. `AgentCouncil` - 20 edges
9. `main()` - 20 edges
10. `get_book_allocations()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `unwind_paired_hedge()` --calls--> `submit_market_order()`  [INFERRED]
  stock-signal-engine/execution/autopilot.py → stock-signal-engine/execution/alpha_client.py
- `manage_open_positions()` --calls--> `submit_market_order()`  [INFERRED]
  stock-signal-engine/execution/autopilot.py → stock-signal-engine/execution/alpha_client.py
- `manage_open_positions()` --calls--> `ratchet_trailing_stop()`  [INFERRED]
  stock-signal-engine/execution/autopilot.py → stock-signal-engine/risk/hedging_engine.py
- `manage_open_positions()` --calls--> `tp1_scale_plan()`  [INFERRED]
  stock-signal-engine/execution/autopilot.py → stock-signal-engine/risk/hedging_engine.py
- `analyze_stock()` --uses--> `TechnicalIndicators`  [INFERRED]
  stock-signal-engine/risk/stock_analysis.py → stock-signal-engine/market/technicals.py

## Import Cycles
- None detected.

## Communities (147 total, 48 thin omitted)

### Community 0 - "Any"
Cohesion: 0.07
Nodes (13): api_benchmark_summary(), api_compliance_report(), api_confluence_evaluate(), api_council_recent(), api_council_status(), api_desks_benchmark(), api_desks_scan(), api_farm_status() (+5 more)

### Community 1 - "tunnel_manager.py"
Cohesion: 0.11
Nodes (13): api_remote_access(), get_active_tunnel_url(), get_local_ip(), get_qr_png_bytes(), get_remote_status(), is_caffeinate_running(), is_tunnel_evicted(), print_cli_summary() (+5 more)

### Community 3 - "app.py"
Cohesion: 0.11
Nodes (12): api_auth_status(), api_desks_status(), api_rescan(), api_ross_execute(), _cancel_open_orders(), _find_process_pid(), _is_pid_alive(), _is_request_authenticated() (+4 more)

### Community 5 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 6 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 7 - "get"
Cohesion: 0.06
Nodes (23): api_account(), api_advisor_exit(), api_book_allocation(), api_equity_curve(), api_evaluate(), api_health(), api_jev_opportunities(), api_journal_exits() (+15 more)

### Community 8 - "time"
Cohesion: 0.09
Nodes (4): main(), FailureEpisode, StrategyItem, ForexSignal

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

### Community 14 - "post"
Cohesion: 0.06
Nodes (22): autopilot_run_once(), execute_endpoint(), ExecuteRequest, AIReviewRequest, api_compliance_ai_review(), api_council_convene(), api_council_decision(), api_farm_demote() (+14 more)

### Community 15 - "atomic_json_read"
Cohesion: 0.06
Nodes (8): check_liveness(), get_autopilot_heartbeat(), main(), run_daemon(), atomic_json_read(), atomic_json_write(), StrategyFarmManager, TestArchitectureFixes

### Community 16 - "Series"
Cohesion: 0.12
Nodes (5): _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _verdict()

### Community 17 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 19 - "score_trade"
Cohesion: 0.24
Nodes (3): get_hedge_evaluation(), score_trade(), TestScorer

### Community 20 - "news_fetcher.py"
Cohesion: 0.08
Nodes (25): get_settings(), Settings, fetch_all(), fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news() (+17 more)

### Community 21 - "test_project_omega.py"
Cohesion: 0.15
Nodes (11): signal_endpoint(), process_trade_execution(), get_client(), get_current_exposure(), get_portfolio_value(), submit_market_order(), submit_order(), submit_pair_orders() (+3 more)

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
Cohesion: 0.07
Nodes (7): BrokerClientFactory, MirrorDispatcher, MirrorTradeSignal, ReplicationSummary, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 27 - "TradeJournal"
Cohesion: 0.05
Nodes (10): Candle, generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), TradeJournal, evaluate_five_pillars() (+2 more)

### Community 28 - "BayesianConfidenceEngine"
Cohesion: 0.07
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 29 - "shock_detector.py"
Cohesion: 0.19
Nodes (6): is_us_equity_market_open(), detect_intraday_shock(), _env_float(), gap_shock_threshold(), velocity_shock_threshold(), TestShockDetector

### Community 30 - "CryptoFuturesAutopilot"
Cohesion: 0.09
Nodes (3): CryptoFuturesAutopilot, main(), TestCryptoPerpFixes

### Community 31 - "ForexAutopilot"
Cohesion: 0.05
Nodes (3): CMEFuturesAutopilot, ForexAutopilot, TestMultiDeskArchitecture

### Community 32 - "argparse"
Cohesion: 0.14
Nodes (8): _conn(), _main(), remember(), similar(), stats(), _tokens(), _vec(), main()

### Community 33 - "dashboard.py"
Cohesion: 0.18
Nodes (9): _esc(), _fmt_ts(), load_account(), load_journal(), load_leaderboard(), generate_once(), render_page(), seed_demo() (+1 more)

### Community 36 - "pandas"
Cohesion: 0.14
Nodes (16): main(), _print_report(), run_comparison(), _window(), run_test(), run_mean_reversion(), fetch_latest_price(), fetch_prices() (+8 more)

### Community 37 - "hedging_engine.py"
Cohesion: 0.13
Nodes (9): banned_ticker(), calculate_hedge_pair(), compute_book_exposure(), _env_float(), get_exit_geometry(), is_hot_banned(), _latest_close(), ratchet_trailing_stop() (+1 more)

### Community 38 - "financial_modeling.py"
Cohesion: 0.07
Nodes (24): baseline_profile(), build_bundle(), Bundle, crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats() (+16 more)

### Community 39 - "json"
Cohesion: 0.12
Nodes (13): submit_bracket_buy(), backfill_historical_purchases(), format_purchase_log(), log_purchase(), earnings_blackout(), fetch_prev_close(), build_candidate(), composite_score() (+5 more)

### Community 42 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 43 - "daily_routine.py"
Cohesion: 0.19
Nodes (9): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), walk_forward() (+1 more)

### Community 44 - "low_float_scanner.py"
Cohesion: 0.08
Nodes (10): execute_ross_bracket_trade(), check_trading_window(), discover_market_universe(), scan_momentum_market(), classify_position_book(), get_book_allocations(), get_split_ratios(), TestBookSplitArchitecture (+2 more)

### Community 45 - "align_timestamp_point_in_time"
Cohesion: 0.16
Nodes (6): align_timestamp_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), SessionInfo, TestPointInTimeAlignment

### Community 47 - "FactorDAG"
Cohesion: 0.18
Nodes (4): run_experiment(), FactorDAG, evaluate_factor_dag(), TestFactorDAG

### Community 50 - "five_year_stats.py"
Cohesion: 0.08
Nodes (19): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+11 more)

### Community 51 - "os"
Cohesion: 0.11
Nodes (17): auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open(), post_market_belief_cycle() (+9 more)

### Community 52 - "mcp_server.py"
Cohesion: 0.12
Nodes (13): align_event_point_in_time(), analyze_financial_sentiment(), convene_agent_council_meeting(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health(), get_multi_desk_status() (+5 more)

### Community 53 - "services.py"
Cohesion: 0.20
Nodes (9): health(), hedge_evaluate_endpoint(), market_endpoint(), sentiment_endpoint(), EngineException, MarketDataNotFoundError, NLPAnalysisError, NoArticlesFoundError (+1 more)

### Community 55 - "tp1_scale_plan"
Cohesion: 0.16
Nodes (3): tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 56 - "web_server.py"
Cohesion: 0.13
Nodes (6): api_extract_only(), api_process(), ExtractRequest, get_preset(), serve_index(), serve_media()

### Community 57 - "model/__init__.py"
Cohesion: 0.23
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 60 - "test_adaptive_hedging.py"
Cohesion: 0.11
Nodes (7): get_adaptive_exit_geometry(), calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), TestAdaptiveExitGeometry, TestRegimeAdaptivePositionSizing

### Community 61 - "get_purchase_logs"
Cohesion: 0.40
Nodes (4): purchases_endpoint(), get_purchase_log_text(), get_purchase_logs(), api_purchases()

### Community 62 - "🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan"
Cohesion: 0.08
Nodes (25): 10. Quick-Start Commands, 1. Complete System Architecture Map, 2. Capital Architecture & Current State, 3. Financial Model Honest Audit, 3A. Closed Trade Performance (The Hard Truth), 3B. Bayesian Confidence Model — Current Assessment, 4. Root Cause Diagnosis: Why the System is Losing Money, 5. Improvement Plan: 8 Concrete Upgrades (+17 more)

### Community 63 - "numpy"
Cohesion: 0.14
Nodes (11): run_multi_asset_benchmark(), simulate_asset_trades(), main(), simulate_night(), growth_optimal_f(), main(), mc_time_to_goal(), oos_r_pool() (+3 more)

### Community 65 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 67 - "TwentyYearStrategyEngine"
Cohesion: 0.39
Nodes (3): main(), save_report(), TwentyYearStrategyEngine

### Community 68 - "_start_port_8081_forwarder"
Cohesion: 0.28
Nodes (6): _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel(), _warm()

### Community 69 - "nlp/__init__.py"
Cohesion: 0.24
Nodes (5): analyze(), analyze_sentiment_only(), compute_time_decay(), directional_sentiment(), pick_best_article()

### Community 71 - "dashboard/page.tsx"
Cohesion: 0.24
Nodes (13): DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch(), useMarket() (+5 more)

### Community 72 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 74 - "council.py"
Cohesion: 0.22
Nodes (6): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision()

### Community 76 - "daily_sniper.py"
Cohesion: 0.19
Nodes (5): get_sniper_setup(), main(), calculate_asset_beta(), detect_market_regime(), api_regime()

### Community 77 - "20-Year Institutional Strategy & Swing-Shield Benchmark"
Cohesion: 0.40
Nodes (4): 20-Year Institutional Strategy & Swing-Shield Benchmark, Multi-Desk 30% YoY Synergy Architecture, Performance Comparison vs Market Benchmark, Year-by-Year Historical Breakdown (2007 - 2026)

### Community 78 - "market_scanner.py"
Cohesion: 0.23
Nodes (7): flat_universe(), main(), mass_backtest(), print_mass_report(), rank_market(), scan_dip_opportunities(), without_banned()

### Community 82 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.25
Nodes (7): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🛠️ The 9 Live MCP Tools Exposed, 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 87 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 88 - "dataset_generator.py"
Cohesion: 0.10
Nodes (9): get_universe(), build_historical_dataset(), generate_triple_barrier_labels(), add_indicators(), get_latest(), train(), build_bootstrap_dataframe(), load_or_build_training_dataframe() (+1 more)

### Community 90 - "package.json"
Cohesion: 0.10
Nodes (18): axios, eslint, eslint-config-next, next-auth, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+10 more)

### Community 92 - "external_alpha_bridge.py"
Cohesion: 0.52
Nodes (4): cross_reference_batch(), evaluate_ticker(), main(), print_alpha_report()

### Community 93 - "analyze_exit"
Cohesion: 0.18
Nodes (4): analyze_exit(), analyze_stock(), _project_1m(), TestExitAdvisor

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
Cohesion: 0.24
Nodes (7): build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test(), evaluate_trade(), check_portfolio_heat()

### Community 126 - "RiskPanel.tsx"
Cohesion: 0.22
Nodes (5): recharts, PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps

### Community 134 - "Request"
Cohesion: 0.53
Nodes (3): domain_not_found_handler(), engine_logic_handler(), global_crash_handler()

### Community 137 - "QuantDesk Project & Deployment Architecture"
Cohesion: 0.33
Nodes (5): 1. Executive Summary & Host Topography, 2. Remote Access & Tailscale Networking Rules, 3. Core Desks & Automation Components, Critical Infrastructure Topology, QuantDesk Project & Deployment Architecture

### Community 139 - "calculate_exit_levels"
Cohesion: 0.14
Nodes (6): days_to_target(), expected_move_pct(), is_trade_viable(), calculate_exit_levels(), TestCostModel, TestExitEngine

### Community 142 - "api_remote_qr_svg"
Cohesion: 0.17
Nodes (7): api_auth_logout(), api_remote_qr_svg(), api_verify_pin(), graph_tree_view(), graph_view(), PinVerifyRequest, get_qr_svg()

### Community 144 - "walk_forward.py"
Cohesion: 0.25
Nodes (4): main(), month_folds(), _policy_summary(), _run_style()

## Knowledge Gaps
- **83 isolated node(s):** `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED`, `TOKENIZERS_PARALLELISM`, `TRANSFORMERS_OFFLINE` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1050 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `Any`, `app.py`, `get`, `time`, `ForexAutopilot`, `AgentCouncil`, `hedging_engine.py`, `financial_modeling.py`, `json`, `daily_routine.py`, `FactorDAG`, `five_year_stats.py`, `mcp_server.py`, `numpy`, `TwentyYearStrategyEngine`, `council.py`, `daily_sniper.py`, `market_scanner.py`, `dataset_generator.py`, `external_alpha_bridge.py`, `InstitutionalBenchmarkEngine`, `factor_dag.py`, `TriConfluenceMatrix`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **What connects `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Any` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._
- **Why does `TradeJournal` connect `TradeJournal` to `time`, `low_float_scanner.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Should `tunnel_manager.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11375661375661375 - nodes in this community are weakly interconnected._
- **Should `quant` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11 - nodes in this community are weakly interconnected._