# Graph Report - stock-signal-engine  (2026-10-19)

## Corpus Check
- 227 files · ~602,419 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: .csv 9, (none) 6, .bat 2)

## Summary
- 2340 nodes · 5132 edges · 133 communities (106 shown, 27 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 157 edges (avg confidence: 0.88)
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
- SubscriberProfile
- stock_analysis.py
- factor_dag.py
- app.py
- BayesianConfidenceEngine
- get
- quant
- get_book_allocations
- council.py
- core.py
- atomic_json_read
- argparse
- CryptoFuturesAutopilot
- tunnel_manager.py
- test_units.py
- FactorDAG
- os
- sentiment_hedged_vs_unhedged.py
- scenario_small.sh
- 🏗️ Stock Signal Engine — Full Project Visualization & Financial Model Improvement Plan
- .filter_series
- mcp_server.py
- scenario_sniper.sh
- daily_routine.py
- cost_model.py
- TestPhysicalRiskPipeline
- InstitutionalBenchmarkEngine
- package.json
- pipeline.py
- [...path]/route.ts
- dashboard/page.tsx
- hedging_engine.py
- market_scanner.py
- jev_execution.py
- compilerOptions
- TestProjectOmega
- analyze_exit
- external_alpha_bridge.py
- numpy
- pandas
- 📈 Stock Signal Engine — Personal Quant Desk
- tp1_scale_plan
- test_jev_scooper.py
- align_timestamp_point_in_time
- Any
- iOS Mobile App & Home Screen Widget Blueprint
- iOS Mobile App & Home Screen Widget Blueprint
- news_fetcher.py
- nlp/__init__.py
- dashboard.py
- FailureMemoryEngine
- process_trade_execution
- train.py
- types.ts
- api_verify_pin
- scenario_c.sh
- ForexStrategyEngine
- web_server.py
- model/__init__.py
- get_market_features
- calculate_exit_levels
- .test_defensive_scaling_on_losing_streak
- services.py
- news_memory.py
- pick_best_article
- manifest.json
- RiskPanel.tsx
- _leaderboard
- Win-Rate Optimization & Diagnostic Report
- ConvexTailEngine
- dependencies
- devDependencies
- store.ts
- TriConfluenceMatrix
- score_trade
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- Crisis-Tested Financial Model
- banned_ticker
- TestTechnicalIndicators
- run_multi_asset_benchmark
- time_to_goal.py
- check_trading_window
- Article
- run_autopilot.sh
- run_webapp.sh
- deadmans_switch.py
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- QuantDesk Project & Deployment Architecture
- detect_market_regime
- scanner.py
- CryptoPerpStrategyEngine
- autopilot_run_once
- scripts
- Five-Year Market Statistics
- Five-Year Market Statistics
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- CMEFuturesStrategyEngine
- watchdog.sh
- dashboard/README.md
- domain_not_found_handler
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
- time_to_goal_2026-09-21.md
- run_instagram_extractor.sh
- remote_setup.sh
- TestShockDetector

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 79 edges
2. `TechnicalIndicators` - 42 edges
3. `atomic_json_read()` - 38 edges
4. `atomic_json_write()` - 32 edges
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
- `TwentyYearStrategyEngine` --uses--> `TechnicalIndicators`  [INFERRED]
  backtest/twenty_year_strategy.py → market/technicals.py

## Import Cycles
- None detected.

## Communities (133 total, 27 thin omitted)

### Community 0 - "TradeJournal"
Cohesion: 0.06
Nodes (9): Candle, generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), TradeJournal, evaluate_five_pillars() (+1 more)

### Community 1 - "five_year_stats.py"
Cohesion: 0.08
Nodes (19): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+11 more)

### Community 2 - "TestMultiDeskArchitecture"
Cohesion: 0.05
Nodes (4): CMEFuturesAutopilot, main(), ForexAutopilot, TestMultiDeskArchitecture

### Community 3 - "time"
Cohesion: 0.11
Nodes (4): FailureEpisode, backfill_historical_purchases(), StrategyItem, ForexSignal

### Community 4 - "financial_modeling.py"
Cohesion: 0.05
Nodes (26): baseline_profile(), build_bundle(), Bundle, crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats() (+18 more)

### Community 5 - "AppDelegate"
Cohesion: 0.08
Nodes (20): Cocoa, Foundation, AccountResponse, AIReviewItem, AppDelegate, ComplianceReport, DeskItem, DesksResponse (+12 more)

### Community 6 - "TradeReviewPacket"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 7 - "SubscriberProfile"
Cohesion: 0.08
Nodes (7): BrokerClientFactory, MirrorDispatcher, MirrorTradeSignal, ReplicationSummary, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 8 - "stock_analysis.py"
Cohesion: 0.18
Nodes (7): analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _project_1m(), _verdict()

### Community 9 - "factor_dag.py"
Cohesion: 0.11
Nodes (9): generate_realistic_news_stream(), run_experiment(), AlphaCompositeNode, NewsSourceNode, Node, PointInTimeAlignmentNode, PriceSourceNode, SentimentAggregatorNode (+1 more)

### Community 10 - "app.py"
Cohesion: 0.07
Nodes (26): get_purchase_logs(), AIReviewRequest, api_compliance_ai_review(), api_council_decision(), api_farm_demote(), api_farm_promote(), api_flatten(), api_gateway_register_subscriber() (+18 more)

### Community 11 - "BayesianConfidenceEngine"
Cohesion: 0.08
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 12 - "get"
Cohesion: 0.06
Nodes (22): api_account(), api_advisor_exit(), api_book_allocation(), api_equity_curve(), api_evaluate(), api_health(), api_jev_opportunities(), api_journal_exits() (+14 more)

### Community 14 - "get_book_allocations"
Cohesion: 0.14
Nodes (6): get_settings(), Settings, execute_ross_bracket_trade(), get_book_allocations(), get_split_ratios(), TestBookSplitArchitecture

### Community 15 - "council.py"
Cohesion: 0.12
Nodes (7): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision(), TestAgentCouncilArchitecture

### Community 16 - "core.py"
Cohesion: 0.09
Nodes (14): cmd_demo(), cmd_extract(), cmd_process(), main(), abstract_quant_content(), download_file(), encrypt_url_token(), extract_audio_tracks() (+6 more)

### Community 17 - "atomic_json_read"
Cohesion: 0.05
Nodes (5): AgentCouncil, CouncilTurn, atomic_json_read(), StrategyFarmManager, TestArchitectureFixes

### Community 18 - "argparse"
Cohesion: 0.16
Nodes (11): main(), _print_report(), run_comparison(), _trim(), _window(), main(), month_folds(), _policy_summary() (+3 more)

### Community 19 - "CryptoFuturesAutopilot"
Cohesion: 0.09
Nodes (3): CryptoFuturesAutopilot, main(), TestCryptoPerpFixes

### Community 20 - "tunnel_manager.py"
Cohesion: 0.10
Nodes (15): api_remote_access(), api_remote_qr_svg(), get_active_tunnel_url(), get_local_ip(), get_qr_png_bytes(), get_qr_svg(), get_remote_status(), is_caffeinate_running() (+7 more)

### Community 21 - "test_units.py"
Cohesion: 0.07
Nodes (11): generate_triple_barrier_labels(), calculate_compounder_size(), check_tail_risk(), TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory, TestPurchaseLogger (+3 more)

### Community 22 - "FactorDAG"
Cohesion: 0.20
Nodes (3): FactorDAG, evaluate_factor_dag(), TestFactorDAG

### Community 23 - "os"
Cohesion: 0.12
Nodes (16): auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open(), post_market_belief_cycle() (+8 more)

### Community 24 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.18
Nodes (10): build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test(), add_label(), build_feature_vector(), build_features() (+2 more)

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
Cohesion: 0.11
Nodes (15): align_event_point_in_time(), analyze_financial_sentiment(), check_alpaca_account(), convene_agent_council_meeting(), fetch_stock_prices(), find_codebase_path(), get_codebase_graph_summary(), get_engine_health() (+7 more)

### Community 29 - "scenario_sniper.sh"
Cohesion: 0.08
Nodes (24): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+16 more)

### Community 30 - "daily_routine.py"
Cohesion: 0.20
Nodes (10): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker(), flat_universe() (+2 more)

### Community 31 - "cost_model.py"
Cohesion: 0.17
Nodes (6): breakeven_move_pct(), days_to_target(), expected_move_pct(), is_trade_viable(), round_trip_cost(), TestCostModel

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
Cohesion: 0.15
Nodes (10): submit_bracket_buy(), format_purchase_log(), log_purchase(), build_candidate(), composite_score(), main(), news_deep_dive(), phase_night() (+2 more)

### Community 36 - "[...path]/route.ts"
Cohesion: 0.12
Nodes (12): nextConfig, buildHeaders(), createBackendUrl(), DELETE(), GET(), POST(), proxy(), PUT() (+4 more)

### Community 37 - "dashboard/page.tsx"
Cohesion: 0.22
Nodes (14): DashboardPage(), IndicatorPanel(), PortfolioBar(), sentColor(), SentimentFeed(), SignalCard(), TickerSearch(), useMarket() (+6 more)

### Community 38 - "hedging_engine.py"
Cohesion: 0.10
Nodes (11): _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), is_hot_banned(), _latest_close(), resolve_hedge_instrument(), calculate_position_size(), calculate_regime_risk_pct() (+3 more)

### Community 39 - "market_scanner.py"
Cohesion: 0.27
Nodes (5): main(), mass_backtest(), print_mass_report(), rank_market(), scan_dip_opportunities()

### Community 40 - "jev_execution.py"
Cohesion: 0.25
Nodes (3): execute_jev_scoop_trade(), classify_position_book(), _account_snapshot()

### Community 41 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 44 - "external_alpha_bridge.py"
Cohesion: 0.52
Nodes (4): cross_reference_batch(), evaluate_ticker(), main(), print_alpha_report()

### Community 45 - "numpy"
Cohesion: 0.10
Nodes (5): main(), simulate_night(), run_test(), run_mean_reversion(), TechnicalIndicators

### Community 46 - "pandas"
Cohesion: 0.12
Nodes (15): get_sniper_setup(), main(), build_historical_dataset(), calculate_asset_beta(), fetch_latest_price(), fetch_prices(), _fetch_with_yahoo_chart(), _fetch_with_yfinance() (+7 more)

### Community 47 - "📈 Stock Signal Engine — Personal Quant Desk"
Cohesion: 0.12
Nodes (16): 🏗️ Architecture, Autopilot flags, 🧪 Backtesting Guide, 🧰 Command Reference, ⚙️ Configuration Knobs (env / .env — all optional), 📊 Dashboard, 📜 Disclaimer, 🖥️ Live Web App (`webapp/`) (+8 more)

### Community 48 - "tp1_scale_plan"
Cohesion: 0.15
Nodes (4): ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 49 - "test_jev_scooper.py"
Cohesion: 0.14
Nodes (3): JEVLiquidityScooper, ScoopOpportunity, TestJEVLiquidityScooper

### Community 50 - "align_timestamp_point_in_time"
Cohesion: 0.10
Nodes (8): align_timestamp_point_in_time(), enrich_article_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), SessionInfo, validate_anti_leakage(), TestPointInTimeAlignment

### Community 51 - "Any"
Cohesion: 0.07
Nodes (13): api_benchmark_summary(), api_compliance_report(), api_confluence_evaluate(), api_council_convene(), api_council_recent(), api_council_status(), api_desks_benchmark(), api_farm_status() (+5 more)

### Community 52 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 53 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 54 - "news_fetcher.py"
Cohesion: 0.07
Nodes (27): fetch_earnings(), _normalize(), fetch_all(), fetch_alpaca_news(), fetch_news(), _fetch_with_yahoo_search(), _fetch_with_yfinance(), fetch_yfinance_news() (+19 more)

### Community 55 - "nlp/__init__.py"
Cohesion: 0.18
Nodes (9): evaluate_news_catalyst(), analyze_sentiment(), _get_finbert(), analyze(), analyze_sentiment_only(), compute_time_decay(), extract_entities(), _get_nlp() (+1 more)

### Community 56 - "dashboard.py"
Cohesion: 0.18
Nodes (9): _esc(), _fmt_ts(), load_account(), load_journal(), load_leaderboard(), generate_once(), render_page(), seed_demo() (+1 more)

### Community 58 - "process_trade_execution"
Cohesion: 0.20
Nodes (7): process_trade_execution(), get_client(), submit_market_order(), submit_order(), submit_pair_orders(), execute_hedged_trade(), execute_trade()

### Community 59 - "train.py"
Cohesion: 0.21
Nodes (4): train(), build_bootstrap_dataframe(), load_or_build_training_dataframe(), main()

### Community 60 - "types.ts"
Cohesion: 0.33
Nodes (7): api, MarketFeatures, PortfolioResponse, RiskDecision, SignalResponse, SignalResult, swr

### Community 61 - "api_verify_pin"
Cohesion: 0.15
Nodes (8): api_auth_logout(), api_auth_status(), api_verify_pin(), graph_tree_view(), graph_view(), _is_request_authenticated(), pin_auth_middleware(), PinVerifyRequest

### Community 62 - "scenario_c.sh"
Cohesion: 0.14
Nodes (13): HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY, OMP_NUM_THREADS, PYTHONUNBUFFERED (+5 more)

### Community 64 - "web_server.py"
Cohesion: 0.18
Nodes (3): get_preset(), serve_index(), serve_media()

### Community 65 - "model/__init__.py"
Cohesion: 0.21
Nodes (5): ensemble_signal(), _fallback_prediction(), get_signal(), load_model(), predict()

### Community 66 - "get_market_features"
Cohesion: 0.31
Nodes (3): add_indicators(), get_latest(), get_market_features()

### Community 67 - "calculate_exit_levels"
Cohesion: 0.15
Nodes (4): calculate_exit_levels(), compute_book_exposure(), TestAdaptiveExitGeometry, TestExitEngine

### Community 69 - "services.py"
Cohesion: 0.17
Nodes (15): health(), market_endpoint(), portfolio_endpoint(), purchases_endpoint(), sentiment_endpoint(), signal_endpoint(), EngineException, MarketDataNotFoundError (+7 more)

### Community 70 - "news_memory.py"
Cohesion: 0.29
Nodes (7): _conn(), _main(), remember(), similar(), stats(), _tokens(), _vec()

### Community 71 - "pick_best_article"
Cohesion: 0.21
Nodes (4): directional_sentiment(), pick_best_article(), TestArticleSelection, TestTimeDecay

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

### Community 80 - "TriConfluenceMatrix"
Cohesion: 0.22
Nodes (3): ConfluenceDecision, TriConfluenceMatrix, TestTriConfluenceMatrix

### Community 81 - "score_trade"
Cohesion: 0.20
Nodes (4): hedge_evaluate_endpoint(), get_hedge_evaluation(), score_trade(), TestScorer

### Community 82 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 83 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 84 - "Crisis-Tested Financial Model"
Cohesion: 0.22
Nodes (8): Assumptions & limits, Crisis-Tested Financial Model, Per-year win rate (tuned), Stage 3 — Crisis stress tests, Stage 3 — Out-of-sample test (2024 → today), Stage 4 — Monte Carlo (one-year horizon), Stage 5 — Capital scenarios (out-of-sample), Validation (2021-2023) — candidate stability

### Community 85 - "banned_ticker"
Cohesion: 0.23
Nodes (4): main(), save_report(), TwentyYearStrategyEngine, banned_ticker()

### Community 88 - "time_to_goal.py"
Cohesion: 0.29
Nodes (7): growth_optimal_f(), main(), mc_time_to_goal(), oos_r_pool(), pool_stats(), savings_months(), tuned_profile()

### Community 89 - "check_trading_window"
Cohesion: 0.25
Nodes (5): check_trading_window(), discover_market_universe(), scan_momentum_market(), api_ross_runners(), api_ross_window()

### Community 90 - "Article"
Cohesion: 0.32
Nodes (4): ArticlesFeedProps, SentimentHeatmapProps, sources, Article

### Community 91 - "run_autopilot.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_autopilot.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 92 - "run_webapp.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_webapp.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 93 - "deadmans_switch.py"
Cohesion: 0.11
Nodes (5): check_liveness(), get_autopilot_heartbeat(), is_us_equity_market_open(), main(), run_daemon()

### Community 94 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.29
Nodes (6): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🔌 Universal MCP Server Setup Guide for All AI Builders

### Community 96 - "QuantDesk Project & Deployment Architecture"
Cohesion: 0.33
Nodes (5): 1. Executive Summary & Host Topography, 2. Remote Access & Tailscale Networking Rules, 3. Core Desks & Automation Components, Critical Infrastructure Topology, QuantDesk Project & Deployment Architecture

### Community 97 - "detect_market_regime"
Cohesion: 0.29
Nodes (3): regime_endpoint(), get_regime(), detect_market_regime()

### Community 98 - "scanner.py"
Cohesion: 0.53
Nodes (3): clamp(), main(), score_row()

### Community 100 - "autopilot_run_once"
Cohesion: 0.40
Nodes (3): autopilot_run_once(), execute_endpoint(), ExecuteRequest

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

### Community 108 - "domain_not_found_handler"
Cohesion: 0.53
Nodes (3): domain_not_found_handler(), engine_logic_handler(), global_crash_handler()

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
Cohesion: 0.40
Nodes (4): api_desks_status(), _find_process_pid(), _is_pid_alive(), _read_pid()

## Knowledge Gaps
- **83 isolated node(s):** `axios`, `react-dom`, `@tailwindcss/postcss`, `@types/node`, `@types/react` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1045 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_prices()` connect `pandas` to `TradeJournal`, `five_year_stats.py`, `TestMultiDeskArchitecture`, `time`, `financial_modeling.py`, `stock_analysis.py`, `factor_dag.py`, `app.py`, `BayesianConfidenceEngine`, `get`, `get_book_allocations`, `council.py`, `atomic_json_read`, `argparse`, `os`, `.filter_series`, `mcp_server.py`, `daily_routine.py`, `InstitutionalBenchmarkEngine`, `pipeline.py`, `hedging_engine.py`, `market_scanner.py`, `analyze_exit`, `external_alpha_bridge.py`, `numpy`, `get_market_features`, `_leaderboard`, `ConvexTailEngine`, `TriConfluenceMatrix`, `banned_ticker`, `run_multi_asset_benchmark`, `Any`, `detect_market_regime`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **What connects `axios`, `react-dom`, `@tailwindcss/postcss` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TradeJournal` be split into smaller, more focused modules?**
  _Cohesion score 0.05654761904761905 - nodes in this community are weakly interconnected._
- **Why does `TechnicalIndicators` connect `numpy` to `five_year_stats.py`, `time`, `financial_modeling.py`, `market_scanner.py`, `stock_analysis.py`, `factor_dag.py`, `BayesianConfidenceEngine`, `external_alpha_bridge.py`, `pandas`, `TriConfluenceMatrix`, `test_jev_scooper.py`, `argparse`, `banned_ticker`, `test_units.py`, `TestTechnicalIndicators`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Should `five_year_stats.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0797979797979798 - nodes in this community are weakly interconnected._
- **Why does `calculate_streak_compounding_factor()` connect `hedging_engine.py` to `.test_defensive_scaling_on_losing_streak`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `TestMultiDeskArchitecture` be split into smaller, more focused modules?**
  _Cohesion score 0.05182443151771549 - nodes in this community are weakly interconnected._