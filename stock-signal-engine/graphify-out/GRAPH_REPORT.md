# Graph Report - stock-signal-engine  (2026-10-20)

## Corpus Check
- 234 files · ~773,025 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: .csv 9, (none) 6, .bat 2)

## Summary
- 2388 nodes · 5255 edges · 131 communities (97 shown, 34 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 167 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2814822f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TradeJournal
- five_year_stats.py
- TestMultiDeskArchitecture
- pathlib
- financial_modeling.py
- AppDelegate
- TradeReviewPacket
- mirror_dispatcher.py
- analyze_exit
- factor_dag.py
- post
- BayesianConfidenceEngine
- get
- quant
- os
- council.py
- core.py
- AgentCouncil
- atomic_json_read
- CryptoFuturesAutopilot
- tunnel_manager.py
- test_units.py
- FactorDAG
- autopilot.py
- TechnicalIndicators
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
- layout.tsx
- dashboard/page.tsx
- test_adaptive_hedging.py
- json
- daily_routine.py
- compilerOptions
- TestProjectOmega
- news_memory.py
- daily_sniper.py
- TestArchitectureFixes
- pandas
- 📈 Stock Signal Engine — Personal Quant Desk
- SelfImprovingExpectancyTracker
- JEVLiquidityScooper
- align_timestamp_point_in_time
- Any
- iOS Mobile App & Home Screen Widget Blueprint
- iOS Mobile App & Home Screen Widget Blueprint
- news_fetcher.py
- analyze_sentiment
- dashboard.py
- FailureMemoryEngine
- alpha_client.py
- train.py
- types.ts
- _is_request_authenticated
- scenario_c.sh
- ForexStrategyEngine
- market_scanner.py
- model/__init__.py
- add_indicators
- services.py
- nlp/__init__.py
- main.py
- unified_four_desk_simulation.py
- wr_hunt.py
- manifest.json
- RiskPanel.tsx
- _start_port_8081_forwarder
- Win-Rate Optimization & Diagnostic Report
- ConvexTailEngine
- dependencies
- devDependencies
- store.ts
- api_remote_qr_svg
- TwentyYearStrategyEngine
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- validate_anti_leakage
- calculate_dynamic_hedge_ratio
- TestCryptoPerpFixes
- TestTechnicalIndicators
- [...path]/route.ts
- scanner.py
- run_autopilot.sh
- run_webapp.sh
- time
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- AlphaCompositeNode
- QuantDesk Project & Deployment Architecture
- TestSMCCryptoStrategy
- numpy
- scripts
- Five-Year Market Statistics
- Five-Year Market Statistics
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- CMEFuturesStrategyEngine
- watchdog.sh
- dashboard/README.md
- Pre-Market Plan — 2026-08-26
- Pre-Market Plan — 2026-08-27
- Pre-Market Plan — 2026-09-05
- Pre-Market Plan — 2026-09-07
- Pre-Market Plan — 2026-09-08
- Pre-Market Plan — 2026-09-14
- Pre-Market Plan — 2026-09-19
- Pre-Market Plan — 2026-09-21
- app.py
- host_architecture.md
- AGENTS.md
- postcss.config.mjs
- GEMINI.md
- time_to_goal_2026-09-21.md
- run_instagram_extractor.sh
- remote_setup.sh
- TestShockDetector

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 81 edges
2. `TechnicalIndicators` - 42 edges
3. `atomic_json_read()` - 38 edges
4. `atomic_json_write()` - 32 edges
5. `TradeJournal` - 27 edges
6. `CryptoFuturesAutopilot` - 23 edges
7. `align_timestamp_point_in_time()` - 22 edges
8. `AppDelegate` - 22 edges
9. `detect_intraday_shock()` - 21 edges
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
- `TwentyYearStrategyEngine` --uses--> `TechnicalIndicators`  [INFERRED]
  backtest/twenty_year_strategy.py → market/technicals.py

## Import Cycles
- None detected.

## Communities (131 total, 34 thin omitted)

### Community 0 - "TradeJournal"
Cohesion: 0.06
Nodes (9): Candle, generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), TradeJournal, evaluate_five_pillars() (+1 more)

### Community 1 - "five_year_stats.py"
Cohesion: 0.06
Nodes (28): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+20 more)

### Community 2 - "TestMultiDeskArchitecture"
Cohesion: 0.05
Nodes (4): CMEFuturesAutopilot, main(), ForexAutopilot, TestMultiDeskArchitecture

### Community 3 - "pathlib"
Cohesion: 0.10
Nodes (4): FailureEpisode, StrategyItem, CryptoFuturesSignal, ForexSignal

### Community 4 - "financial_modeling.py"
Cohesion: 0.05
Nodes (33): baseline_profile(), build_bundle(), Bundle, crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats() (+25 more)

### Community 5 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 6 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 7 - "mirror_dispatcher.py"
Cohesion: 0.08
Nodes (7): BrokerClientFactory, MirrorDispatcher, MirrorTradeSignal, ReplicationSummary, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 8 - "analyze_exit"
Cohesion: 0.07
Nodes (11): breakeven_move_pct(), expected_move_pct(), analyze_exit(), analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct() (+3 more)

### Community 9 - "factor_dag.py"
Cohesion: 0.11
Nodes (7): generate_realistic_news_stream(), NewsSourceNode, Node, PointInTimeAlignmentNode, PriceSourceNode, SentimentAggregatorNode, TechnicalFeaturesNode

### Community 10 - "post"
Cohesion: 0.08
Nodes (18): api_council_decision(), api_farm_promote(), api_gateway_register_subscriber(), api_gateway_replicate(), api_jev_execute(), api_model_confidence_evaluate(), api_purge_mock_trades(), api_reconcile_broker() (+10 more)

### Community 11 - "BayesianConfidenceEngine"
Cohesion: 0.08
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 12 - "get"
Cohesion: 0.06
Nodes (22): api_advisor_exit(), api_book_allocation(), api_equity_curve(), api_evaluate(), api_health(), api_jev_opportunities(), api_journal_exits(), api_journal_summary() (+14 more)

### Community 14 - "os"
Cohesion: 0.12
Nodes (6): get_settings(), Settings, execute_ross_bracket_trade(), get_book_allocations(), get_split_ratios(), TestBookSplitArchitecture

### Community 15 - "council.py"
Cohesion: 0.09
Nodes (10): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision(), convene_agent_council_meeting(), get_virtual_office_status() (+2 more)

### Community 16 - "core.py"
Cohesion: 0.06
Nodes (17): cmd_demo(), cmd_extract(), cmd_process(), main(), abstract_quant_content(), download_file(), encrypt_url_token(), extract_audio_tracks() (+9 more)

### Community 18 - "atomic_json_read"
Cohesion: 0.13
Nodes (3): atomic_json_read(), atomic_json_write(), StrategyFarmManager

### Community 20 - "tunnel_manager.py"
Cohesion: 0.11
Nodes (13): api_remote_access(), get_active_tunnel_url(), get_local_ip(), get_qr_png_bytes(), get_remote_status(), is_caffeinate_running(), is_tunnel_evicted(), print_cli_summary() (+5 more)

### Community 21 - "test_units.py"
Cohesion: 0.06
Nodes (12): ratchet_trailing_stop(), tp1_scale_plan(), check_tail_risk(), TestAdaptiveScaleOutAndTrail, TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory (+4 more)

### Community 22 - "FactorDAG"
Cohesion: 0.18
Nodes (4): run_experiment(), FactorDAG, evaluate_factor_dag(), TestFactorDAG

### Community 23 - "autopilot.py"
Cohesion: 0.08
Nodes (23): submit_market_order(), auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open() (+15 more)

### Community 24 - "TechnicalIndicators"
Cohesion: 0.19
Nodes (5): cross_reference_batch(), evaluate_ticker(), main(), print_alpha_report(), TechnicalIndicators

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
Cohesion: 0.14
Nodes (13): get_client(), align_event_point_in_time(), analyze_financial_sentiment(), check_alpaca_account(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health() (+5 more)

### Community 29 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 30 - "pick_best_article"
Cohesion: 0.16
Nodes (5): run_signal_pipeline(), directional_sentiment(), pick_best_article(), TestArticleSelection, TestTimeDecay

### Community 31 - "hedging_engine.py"
Cohesion: 0.12
Nodes (7): detect_market_regime(), days_to_target(), _env_float(), get_exit_geometry(), is_hot_banned(), _latest_close(), resolve_hedge_instrument()

### Community 32 - "TestPhysicalRiskPipeline"
Cohesion: 0.22
Nodes (3): PhysicalRiskPipeline, RiskPipelineVerdict, TestPhysicalRiskPipeline

### Community 33 - "InstitutionalBenchmarkEngine"
Cohesion: 0.08
Nodes (6): BenchmarkMetrics, InstitutionalBenchmarkEngine, ConfluenceDecision, TriConfluenceMatrix, TestTriConfluenceMatrix, TestInstitutionalBenchmarkEngine

### Community 34 - "package.json"
Cohesion: 0.10
Nodes (18): eslintConfig, name, private, version, auth, authOptions, config, axios (+10 more)

### Community 35 - "pipeline.py"
Cohesion: 0.14
Nodes (10): submit_bracket_buy(), get_market_features(), earnings_blackout(), build_candidate(), composite_score(), main(), news_deep_dive(), phase_night() (+2 more)

### Community 36 - "layout.tsx"
Cohesion: 0.15
Nodes (5): nextConfig, geistMono, geistSans, metadata, next

### Community 37 - "dashboard/page.tsx"
Cohesion: 0.24
Nodes (13): DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch(), useMarket() (+5 more)

### Community 38 - "test_adaptive_hedging.py"
Cohesion: 0.07
Nodes (8): get_adaptive_exit_geometry(), calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), TestAdaptiveExitGeometry, TestRegimeAdaptivePositionSizing, TestStreakCompounding

### Community 39 - "json"
Cohesion: 0.19
Nodes (5): backfill_historical_purchases(), format_purchase_log(), get_purchase_logs(), log_purchase(), _main()

### Community 40 - "daily_routine.py"
Cohesion: 0.20
Nodes (9): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), get_universe() (+1 more)

### Community 41 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "news_memory.py"
Cohesion: 0.20
Nodes (7): _conn(), remember(), similar(), stats(), _tokens(), _vec(), _seen_titles()

### Community 44 - "daily_sniper.py"
Cohesion: 0.15
Nodes (8): get_sniper_setup(), main(), is_us_equity_market_open(), calculate_asset_beta(), detect_intraday_shock(), _env_float(), gap_shock_threshold(), velocity_shock_threshold()

### Community 46 - "pandas"
Cohesion: 0.18
Nodes (9): run_test(), run_mean_reversion(), fetch_latest_price(), fetch_prices(), _fetch_with_yahoo_chart(), _fetch_with_yfinance(), _get_cache_path(), _load_cache() (+1 more)

### Community 47 - "📈 Stock Signal Engine — Personal Quant Desk"
Cohesion: 0.12
Nodes (16): 🏗️ Architecture, Autopilot flags, 🧪 Backtesting Guide, 🧰 Command Reference, ⚙️ Configuration Knobs (env / .env — all optional), 📊 Dashboard, 📜 Disclaimer, 🖥️ Live Web App (`webapp/`) (+8 more)

### Community 49 - "JEVLiquidityScooper"
Cohesion: 0.15
Nodes (3): JEVLiquidityScooper, ScoopOpportunity, TestJEVLiquidityScooper

### Community 50 - "align_timestamp_point_in_time"
Cohesion: 0.18
Nodes (5): align_timestamp_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), TestPointInTimeAlignment

### Community 51 - "Any"
Cohesion: 0.06
Nodes (15): api_benchmark_summary(), api_compliance_report(), api_confluence_evaluate(), api_council_convene(), api_council_recent(), api_council_status(), api_desks_benchmark(), api_farm_demote() (+7 more)

### Community 52 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 53 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 54 - "news_fetcher.py"
Cohesion: 0.07
Nodes (26): fetch_earnings(), _normalize(), fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news(), _get_alpaca_news_client() (+18 more)

### Community 56 - "dashboard.py"
Cohesion: 0.21
Nodes (9): _esc(), _fmt_ts(), load_account(), load_journal(), main(), generate_once(), render_page(), seed_demo() (+1 more)

### Community 58 - "alpha_client.py"
Cohesion: 0.22
Nodes (7): get_portfolio_summary(), get_current_exposure(), get_portfolio_value(), submit_order(), submit_pair_orders(), execute_hedged_trade(), execute_trade()

### Community 59 - "train.py"
Cohesion: 0.21
Nodes (4): train(), build_bootstrap_dataframe(), load_or_build_training_dataframe(), main()

### Community 60 - "types.ts"
Cohesion: 0.19
Nodes (11): ArticlesFeedProps, SentimentHeatmapProps, sources, api, Article, MarketFeatures, PortfolioResponse, RiskDecision (+3 more)

### Community 61 - "_is_request_authenticated"
Cohesion: 0.38
Nodes (3): api_auth_status(), _is_request_authenticated(), pin_auth_middleware()

### Community 62 - "scenario_c.sh"
Cohesion: 0.14
Nodes (13): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+5 more)

### Community 64 - "market_scanner.py"
Cohesion: 0.23
Nodes (7): flat_universe(), main(), mass_backtest(), print_mass_report(), rank_market(), scan_dip_opportunities(), without_banned()

### Community 65 - "model/__init__.py"
Cohesion: 0.21
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 67 - "services.py"
Cohesion: 0.09
Nodes (18): get_hedge_evaluation(), process_trade_execution(), build_books(), main(), print_comparison(), stress_test(), add_label(), build_feature_vector() (+10 more)

### Community 68 - "nlp/__init__.py"
Cohesion: 0.24
Nodes (7): evaluate_news_catalyst(), analyze(), analyze_sentiment_only(), compute_time_decay(), extract_entities(), _get_nlp(), preprocess()

### Community 69 - "main.py"
Cohesion: 0.10
Nodes (20): autopilot_run_once(), domain_not_found_handler(), engine_logic_handler(), execute_endpoint(), global_crash_handler(), health(), hedge_evaluate_endpoint(), market_endpoint() (+12 more)

### Community 70 - "unified_four_desk_simulation.py"
Cohesion: 0.24
Nodes (6): run_comprehensive_simulation(), simulate_crypto_desk(), simulate_forex_desk(), simulate_futures_desk(), simulate_stock_desk(), TradeRecord

### Community 72 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 73 - "RiskPanel.tsx"
Cohesion: 0.22
Nodes (5): PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps, recharts

### Community 74 - "_start_port_8081_forwarder"
Cohesion: 0.32
Nodes (5): _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel()

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
Cohesion: 0.24
Nodes (8): MessagePayload, useWebSocket(), AppState, Article, Signal, useAppStore, react, zustand

### Community 80 - "api_remote_qr_svg"
Cohesion: 0.20
Nodes (5): api_auth_logout(), api_remote_qr_svg(), graph_tree_view(), graph_view(), get_qr_svg()

### Community 81 - "TwentyYearStrategyEngine"
Cohesion: 0.33
Nodes (3): main(), save_report(), TwentyYearStrategyEngine

### Community 82 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 83 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 84 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 85 - "validate_anti_leakage"
Cohesion: 0.18
Nodes (3): enrich_article_point_in_time(), SessionInfo, validate_anti_leakage()

### Community 89 - "[...path]/route.ts"
Cohesion: 0.46
Nodes (7): buildHeaders(), createBackendUrl(), DELETE(), GET(), POST(), proxy(), PUT()

### Community 90 - "scanner.py"
Cohesion: 0.53
Nodes (3): clamp(), main(), score_row()

### Community 91 - "run_autopilot.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_autopilot.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 92 - "run_webapp.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_webapp.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 93 - "time"
Cohesion: 0.36
Nodes (4): check_liveness(), get_autopilot_heartbeat(), main(), run_daemon()

### Community 94 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.29
Nodes (6): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 96 - "QuantDesk Project & Deployment Architecture"
Cohesion: 0.33
Nodes (5): 1. Executive Summary & Host Topography, 2. Remote Access & Tailscale Networking Rules, 3. Core Desks & Automation Components, Critical Infrastructure Topology, QuantDesk Project & Deployment Architecture

### Community 100 - "numpy"
Cohesion: 0.12
Nodes (7): run_multi_asset_benchmark(), simulate_asset_trades(), main(), simulate_night(), build_historical_dataset(), generate_triple_barrier_labels(), TestTripleBarrier

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

### Community 117 - "app.py"
Cohesion: 0.10
Nodes (17): get_purchase_log_text(), _account_snapshot(), AIReviewRequest, api_account(), api_compliance_ai_review(), api_desks_scan(), api_desks_status(), api_purchases() (+9 more)

## Knowledge Gaps
- **83 isolated node(s):** `axios`, `react-dom`, `@tailwindcss/postcss`, `@types/node`, `@types/react` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1060 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `TradeJournal`, `five_year_stats.py`, `TestMultiDeskArchitecture`, `pathlib`, `financial_modeling.py`, `analyze_exit`, `factor_dag.py`, `BayesianConfidenceEngine`, `get`, `os`, `council.py`, `AgentCouncil`, `FactorDAG`, `autopilot.py`, `TechnicalIndicators`, `.filter_series`, `mcp_server.py`, `hedging_engine.py`, `InstitutionalBenchmarkEngine`, `pipeline.py`, `json`, `daily_routine.py`, `daily_sniper.py`, `market_scanner.py`, `add_indicators`, `unified_four_desk_simulation.py`, `ConvexTailEngine`, `TwentyYearStrategyEngine`, `AlphaCompositeNode`, `numpy`, `app.py`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **What connects `axios`, `react-dom`, `@tailwindcss/postcss` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TradeJournal` be split into smaller, more focused modules?**
  _Cohesion score 0.05654761904761905 - nodes in this community are weakly interconnected._
- **Why does `TechnicalIndicators` connect `TechnicalIndicators` to `market_scanner.py`, `five_year_stats.py`, `InstitutionalBenchmarkEngine`, `financial_modeling.py`, `analyze_exit`, `factor_dag.py`, `BayesianConfidenceEngine`, `daily_sniper.py`, `pandas`, `TwentyYearStrategyEngine`, `JEVLiquidityScooper`, `test_units.py`, `TestTechnicalIndicators`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Should `five_year_stats.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06174863387978142 - nodes in this community are weakly interconnected._
- **Why does `TradeJournal` connect `TradeJournal` to `os`, `pandas`, `json`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `TestMultiDeskArchitecture` be split into smaller, more focused modules?**
  _Cohesion score 0.05182443151771549 - nodes in this community are weakly interconnected._