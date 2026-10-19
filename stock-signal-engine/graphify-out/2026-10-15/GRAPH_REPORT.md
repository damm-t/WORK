# Graph Report - stock-signal-engine  (2026-10-15)

## Corpus Check
- 220 files · ~488,679 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: .csv 9, (none) 6, .bat 2)

## Summary
- 2276 nodes · 5003 edges · 132 communities (100 shown, 32 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 156 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2ec6d8a5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TradeJournal
- five_year_stats.py
- TestMultiDeskArchitecture
- time
- financial_modeling.py
- AppDelegate
- TradeReviewPacket
- mirror_dispatcher.py
- TechnicalIndicators
- FactorDAG
- app.py
- BayesianConfidenceEngine
- get
- quant
- get_book_allocations
- mcp_server.py
- core.py
- atomic_json_read
- pandas
- CryptoFuturesAutopilot
- tunnel_manager.py
- test_units.py
- align_timestamp_point_in_time
- os
- hedging_engine.py
- scenario_small.sh
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- .filter_series
- Any
- scenario_sniper.sh
- Any
- numpy
- shock_detector.py
- InstitutionalBenchmarkEngine
- package.json
- pipeline.py
- [...path]/route.ts
- dashboard/page.tsx
- risk/__init__.py
- news_fetcher.py
- alpha_client.py
- compilerOptions
- TestProjectOmega
- calculate_hedge_pair
- main.py
- argparse
- daily_sniper.py
- 📈 Stock Signal Engine — Personal Quant Desk
- tp1_scale_plan
- JEVLiquidityScooper
- TestArchitectureFixes
- sys
- iOS Mobile App & Home Screen Widget Blueprint
- iOS Mobile App & Home Screen Widget Blueprint
- fundamentals.py
- sentiment_hedged_vs_unhedged.py
- dashboard.py
- model/__init__.py
- nlp/__init__.py
- daily_routine.py
- types.ts
- fetch_all
- scenario_c.sh
- ForexStrategyEngine
- web_server.py
- pick_best_article
- _leaderboard
- TestPhysicalRiskPipeline
- .test_defensive_scaling_on_losing_streak
- services.py
- news_memory.py
- unittest
- manifest.json
- RiskPanel.tsx
- get_market_features
- Win-Rate Optimization & Diagnostic Report
- ConvexTailEngine
- dependencies
- devDependencies
- store.ts
- json
- check_trading_window
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- analyze_exit
- TestTechnicalIndicators
- process_trade_execution
- Article
- generate_triple_barrier_labels
- score_trade
- run_autopilot.sh
- run_webapp.sh
- _is_request_authenticated
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- domain_not_found_handler
- main
- without_banned
- scanner.py
- CryptoPerpStrategyEngine
- api_desks_status
- scripts
- Five-Year Market Statistics
- Five-Year Market Statistics
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- CMEFuturesStrategyEngine
- watchdog.sh
- dashboard/README.md
- analyze_sentiment
- Pre-Market Plan — 2026-08-26
- Pre-Market Plan — 2026-08-27
- Pre-Market Plan — 2026-09-05
- Pre-Market Plan — 2026-09-07
- Pre-Market Plan — 2026-09-08
- Pre-Market Plan — 2026-09-14
- Pre-Market Plan — 2026-09-19
- Pre-Market Plan — 2026-09-21
- generate_realistic_news_stream
- get_purchase_log_text
- AGENTS.md
- postcss.config.mjs
- GEMINI.md
- time_to_goal_2026-09-21.md
- run_instagram_extractor.sh
- remote_setup.sh

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 77 edges
2. `TechnicalIndicators` - 40 edges
3. `atomic_json_read()` - 32 edges
4. `atomic_json_write()` - 27 edges
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
- `api_compliance_ai_review()` --uses--> `TradeReviewPacket`  [INFERRED]
  webapp/app.py → compliance/ai_revision_checker.py

## Import Cycles
- None detected.

## Communities (132 total, 32 thin omitted)

### Community 0 - "TradeJournal"
Cohesion: 0.06
Nodes (9): Candle, generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), TradeJournal, evaluate_five_pillars() (+1 more)

### Community 1 - "five_year_stats.py"
Cohesion: 0.06
Nodes (29): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+21 more)

### Community 2 - "TestMultiDeskArchitecture"
Cohesion: 0.05
Nodes (4): CMEFuturesAutopilot, main(), ForexAutopilot, TestMultiDeskArchitecture

### Community 4 - "financial_modeling.py"
Cohesion: 0.07
Nodes (23): baseline_profile(), build_bundle(), Bundle, crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats() (+15 more)

### Community 5 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 6 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 7 - "mirror_dispatcher.py"
Cohesion: 0.08
Nodes (7): BrokerClientFactory, MirrorDispatcher, MirrorTradeSignal, ReplicationSummary, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 8 - "TechnicalIndicators"
Cohesion: 0.07
Nodes (14): main(), save_report(), TwentyYearStrategyEngine, TechnicalIndicators, analyze_stock(), _analyze_trend(), add(), _assess_entry() (+6 more)

### Community 9 - "FactorDAG"
Cohesion: 0.08
Nodes (11): run_experiment(), AlphaCompositeNode, FactorDAG, NewsSourceNode, Node, PointInTimeAlignmentNode, PriceSourceNode, SentimentAggregatorNode (+3 more)

### Community 10 - "app.py"
Cohesion: 0.08
Nodes (27): AIReviewRequest, api_compliance_ai_review(), api_equity_curve(), api_flatten(), api_gateway_register_subscriber(), api_gateway_replicate(), api_health(), api_jev_execute() (+19 more)

### Community 11 - "BayesianConfidenceEngine"
Cohesion: 0.08
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 12 - "get"
Cohesion: 0.06
Nodes (21): api_account(), api_advisor_exit(), api_auth_logout(), api_book_allocation(), api_evaluate(), api_jev_opportunities(), api_journal_exits(), api_model_confidence() (+13 more)

### Community 14 - "get_book_allocations"
Cohesion: 0.11
Nodes (10): get_settings(), Settings, submit_bracket_buy(), execute_jev_scoop_trade(), execute_ross_bracket_trade(), classify_position_book(), get_book_allocations(), get_split_ratios() (+2 more)

### Community 15 - "mcp_server.py"
Cohesion: 0.09
Nodes (10): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision(), convene_agent_council_meeting(), get_virtual_office_status() (+2 more)

### Community 16 - "core.py"
Cohesion: 0.09
Nodes (14): cmd_demo(), cmd_extract(), cmd_process(), main(), abstract_quant_content(), download_file(), encrypt_url_token(), extract_audio_tracks() (+6 more)

### Community 17 - "atomic_json_read"
Cohesion: 0.12
Nodes (4): AgentCouncil, CouncilTurn, atomic_json_read(), atomic_json_write()

### Community 18 - "pandas"
Cohesion: 0.14
Nodes (11): run_test(), run_mean_reversion(), build_historical_dataset(), fetch_prices(), _fetch_with_yahoo_chart(), _fetch_with_yfinance(), _get_cache_path(), _load_cache() (+3 more)

### Community 19 - "CryptoFuturesAutopilot"
Cohesion: 0.09
Nodes (3): CryptoFuturesAutopilot, main(), TestCryptoPerpFixes

### Community 20 - "tunnel_manager.py"
Cohesion: 0.10
Nodes (14): api_remote_access(), get_active_tunnel_url(), get_local_ip(), get_qr_png_bytes(), get_qr_svg(), get_remote_status(), is_caffeinate_running(), is_tunnel_evicted() (+6 more)

### Community 21 - "test_units.py"
Cohesion: 0.07
Nodes (11): days_to_target(), is_trade_viable(), check_tail_risk(), TestCostModel, TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory (+3 more)

### Community 22 - "align_timestamp_point_in_time"
Cohesion: 0.10
Nodes (8): align_timestamp_point_in_time(), enrich_article_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), SessionInfo, validate_anti_leakage(), TestPointInTimeAlignment

### Community 23 - "os"
Cohesion: 0.13
Nodes (14): auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), post_market_belief_cycle(), run_autopilot() (+6 more)

### Community 24 - "hedging_engine.py"
Cohesion: 0.11
Nodes (8): expected_move_pct(), calculate_exit_levels(), _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), is_hot_banned(), TestAdaptiveExitGeometry, TestExitEngine

### Community 25 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 26 - "🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan"
Cohesion: 0.08
Nodes (25): 10. Quick-Start Commands, 1. Complete System Architecture Map, 2. Capital Architecture & Current State, 3. Financial Model Honest Audit, 3A. Closed Trade Performance (The Hard Truth), 3B. Bayesian Confidence Model — Current Assessment, 4. Root Cause Diagnosis: Why the System is Losing Money, 5. Improvement Plan: 8 Concrete Upgrades (+17 more)

### Community 27 - ".filter_series"
Cohesion: 0.11
Nodes (3): AntiVolatilityModel, StabilizationResult, TestAntiVolatilityModel

### Community 28 - "Any"
Cohesion: 0.14
Nodes (12): align_event_point_in_time(), analyze_financial_sentiment(), check_alpaca_account(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health(), get_multi_desk_status() (+4 more)

### Community 29 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 30 - "Any"
Cohesion: 0.08
Nodes (12): api_benchmark_summary(), api_compliance_report(), api_confluence_evaluate(), api_council_convene(), api_council_decision(), api_council_recent(), api_council_status(), api_desks_benchmark() (+4 more)

### Community 31 - "numpy"
Cohesion: 0.14
Nodes (11): run_multi_asset_benchmark(), simulate_asset_trades(), main(), simulate_night(), growth_optimal_f(), main(), mc_time_to_goal(), oos_r_pool() (+3 more)

### Community 32 - "shock_detector.py"
Cohesion: 0.14
Nodes (8): is_us_equity_market_open(), fetch_latest_price(), detect_intraday_shock(), earnings_blackout(), _env_float(), gap_shock_threshold(), velocity_shock_threshold(), TestShockDetector

### Community 33 - "InstitutionalBenchmarkEngine"
Cohesion: 0.13
Nodes (3): BenchmarkMetrics, InstitutionalBenchmarkEngine, TestInstitutionalBenchmarkEngine

### Community 34 - "package.json"
Cohesion: 0.10
Nodes (18): eslintConfig, name, private, version, auth, authOptions, config, axios (+10 more)

### Community 35 - "pipeline.py"
Cohesion: 0.15
Nodes (9): rank_market(), build_candidate(), composite_score(), main(), news_deep_dive(), phase_night(), premarket_snapshot(), _seen_titles() (+1 more)

### Community 36 - "[...path]/route.ts"
Cohesion: 0.12
Nodes (12): nextConfig, buildHeaders(), createBackendUrl(), DELETE(), GET(), POST(), proxy(), PUT() (+4 more)

### Community 37 - "dashboard/page.tsx"
Cohesion: 0.22
Nodes (14): DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch(), useMarket() (+6 more)

### Community 38 - "risk/__init__.py"
Cohesion: 0.17
Nodes (6): calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), TestRegimeAdaptivePositionSizing

### Community 39 - "news_fetcher.py"
Cohesion: 0.18
Nodes (13): fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news(), _get_alpaca_news_client(), _get_cache_path(), _load_cache() (+5 more)

### Community 40 - "alpha_client.py"
Cohesion: 0.19
Nodes (9): get_portfolio_summary(), get_client(), get_current_exposure(), get_portfolio_value(), submit_market_order(), submit_order(), submit_pair_orders(), execute_hedged_trade() (+1 more)

### Community 41 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "calculate_hedge_pair"
Cohesion: 0.12
Nodes (6): calculate_dynamic_hedge_ratio(), calculate_hedge_pair(), compute_book_exposure(), _latest_close(), resolve_hedge_instrument(), TestDynamicHedgeRatio

### Community 44 - "main.py"
Cohesion: 0.18
Nodes (10): health(), hedge_evaluate_endpoint(), market_endpoint(), portfolio_endpoint(), purchases_endpoint(), regime_endpoint(), sentiment_endpoint(), signal_endpoint() (+2 more)

### Community 45 - "argparse"
Cohesion: 0.17
Nodes (4): train(), build_bootstrap_dataframe(), load_or_build_training_dataframe(), main()

### Community 46 - "daily_sniper.py"
Cohesion: 0.17
Nodes (4): get_sniper_setup(), main(), calculate_asset_beta(), detect_market_regime()

### Community 47 - "📈 Stock Signal Engine — Personal Quant Desk"
Cohesion: 0.12
Nodes (16): 🏗️ Architecture, Autopilot flags, 🧪 Backtesting Guide, 🧰 Command Reference, ⚙️ Configuration Knobs (env / .env — all optional), 📊 Dashboard, 📜 Disclaimer, 🖥️ Live Web App (`webapp/`) (+8 more)

### Community 48 - "tp1_scale_plan"
Cohesion: 0.15
Nodes (4): ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 51 - "sys"
Cohesion: 0.17
Nodes (5): run_diagnostic(), check_liveness(), get_autopilot_heartbeat(), main(), run_daemon()

### Community 52 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 53 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 54 - "fundamentals.py"
Cohesion: 0.21
Nodes (7): _ensure_cache_dir(), evaluate_fundamental_quality(), fetch_fundamentals(), _load_cik_map(), _load_fundamentals_cache(), _save_fundamentals_cache(), TestFundamentals

### Community 55 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.22
Nodes (8): build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test(), add_label(), build_feature_vector(), build_features()

### Community 56 - "dashboard.py"
Cohesion: 0.21
Nodes (9): _esc(), _fmt_ts(), load_account(), load_journal(), main(), generate_once(), render_page(), seed_demo() (+1 more)

### Community 57 - "model/__init__.py"
Cohesion: 0.21
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 58 - "nlp/__init__.py"
Cohesion: 0.22
Nodes (7): evaluate_news_catalyst(), analyze(), analyze_sentiment_only(), compute_time_decay(), extract_entities(), _get_nlp(), preprocess()

### Community 59 - "daily_routine.py"
Cohesion: 0.24
Nodes (8): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), flat_universe()

### Community 60 - "types.ts"
Cohesion: 0.33
Nodes (7): api, MarketFeatures, PortfolioResponse, RiskDecision, SignalResponse, SignalResult, swr

### Community 61 - "fetch_all"
Cohesion: 0.25
Nodes (7): fetch_earnings(), _normalize(), fetch_all(), fetch_tweets(), _is_valid_token(), _normalize(), TestTwitterSuppression

### Community 62 - "scenario_c.sh"
Cohesion: 0.14
Nodes (13): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+5 more)

### Community 64 - "web_server.py"
Cohesion: 0.18
Nodes (3): get_preset(), serve_index(), serve_media()

### Community 65 - "pick_best_article"
Cohesion: 0.21
Nodes (4): directional_sentiment(), pick_best_article(), TestArticleSelection, TestTimeDecay

### Community 66 - "_leaderboard"
Cohesion: 0.18
Nodes (9): api_desks_scan(), api_scan(), _leaderboard(), _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel() (+1 more)

### Community 67 - "TestPhysicalRiskPipeline"
Cohesion: 0.22
Nodes (3): PhysicalRiskPipeline, RiskPipelineVerdict, TestPhysicalRiskPipeline

### Community 69 - "services.py"
Cohesion: 0.32
Nodes (6): EngineException, MarketDataNotFoundError, NLPAnalysisError, NoArticlesFoundError, get_processed_signal(), get_regime()

### Community 70 - "news_memory.py"
Cohesion: 0.29
Nodes (7): _conn(), _main(), remember(), similar(), stats(), _tokens(), _vec()

### Community 72 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 73 - "RiskPanel.tsx"
Cohesion: 0.22
Nodes (5): PriceChartProps, formatValue(), RiskPanel(), RiskPanelProps, recharts

### Community 74 - "get_market_features"
Cohesion: 0.31
Nodes (3): add_indicators(), get_latest(), get_market_features()

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

### Community 80 - "json"
Cohesion: 0.28
Nodes (4): backfill_historical_purchases(), format_purchase_log(), get_purchase_logs(), log_purchase()

### Community 81 - "check_trading_window"
Cohesion: 0.25
Nodes (5): check_trading_window(), discover_market_universe(), scan_momentum_market(), api_ross_runners(), api_ross_window()

### Community 82 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 83 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 84 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 87 - "process_trade_execution"
Cohesion: 0.29
Nodes (4): autopilot_run_once(), execute_endpoint(), ExecuteRequest, process_trade_execution()

### Community 88 - "Article"
Cohesion: 0.32
Nodes (4): ArticlesFeedProps, SentimentHeatmapProps, sources, Article

### Community 91 - "run_autopilot.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_autopilot.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 92 - "run_webapp.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_webapp.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 93 - "_is_request_authenticated"
Cohesion: 0.38
Nodes (3): api_auth_status(), _is_request_authenticated(), pin_auth_middleware()

### Community 94 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.29
Nodes (6): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 95 - "domain_not_found_handler"
Cohesion: 0.53
Nodes (3): domain_not_found_handler(), engine_logic_handler(), global_crash_handler()

### Community 96 - "main"
Cohesion: 0.33
Nodes (4): main(), mass_backtest(), print_mass_report(), scan_dip_opportunities()

### Community 98 - "scanner.py"
Cohesion: 0.53
Nodes (3): clamp(), main(), score_row()

### Community 100 - "api_desks_status"
Cohesion: 0.40
Nodes (4): api_desks_status(), _find_process_pid(), _is_pid_alive(), _read_pid()

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

## Knowledge Gaps
- **83 isolated node(s):** `axios`, `react-dom`, `@tailwindcss/postcss`, `@types/node`, `@types/react` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1016 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `TradeJournal`, `five_year_stats.py`, `TestMultiDeskArchitecture`, `time`, `financial_modeling.py`, `TechnicalIndicators`, `FactorDAG`, `app.py`, `BayesianConfidenceEngine`, `get`, `get_book_allocations`, `mcp_server.py`, `atomic_json_read`, `os`, `hedging_engine.py`, `.filter_series`, `Any`, `numpy`, `shock_detector.py`, `InstitutionalBenchmarkEngine`, `pipeline.py`, `calculate_hedge_pair`, `argparse`, `daily_sniper.py`, `daily_routine.py`, `_leaderboard`, `get_market_features`, `ConvexTailEngine`, `analyze_exit`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **What connects `axios`, `react-dom`, `@tailwindcss/postcss` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TradeJournal` be split into smaller, more focused modules?**
  _Cohesion score 0.05654761904761905 - nodes in this community are weakly interconnected._
- **Why does `TechnicalIndicators` connect `TechnicalIndicators` to `five_year_stats.py`, `pipeline.py`, `financial_modeling.py`, `time`, `FactorDAG`, `BayesianConfidenceEngine`, `daily_sniper.py`, `JEVLiquidityScooper`, `pandas`, `test_units.py`, `TestTechnicalIndicators`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Should `five_year_stats.py` be split into smaller, more focused modules?**
  _Cohesion score 0.060814383923849816 - nodes in this community are weakly interconnected._
- **Why does `TradeJournal` connect `TradeJournal` to `time`, `get_book_allocations`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `TestMultiDeskArchitecture` be split into smaller, more focused modules?**
  _Cohesion score 0.05182443151771549 - nodes in this community are weakly interconnected._