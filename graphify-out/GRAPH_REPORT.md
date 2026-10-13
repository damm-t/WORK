# Graph Report - WORK  (2026-10-13)

## Corpus Check
- 212 files · ~436,064 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 31 file(s) not represented in the graph (top: .csv 15, (none) 9, .ipynb 3)

## Summary
- 1576 nodes · 3424 edges · 92 communities (57 shown, 35 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 79 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f9fd4439`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Profile
- tunnel_manager.py
- app.py
- test_project_omega.py
- scenario_small.sh
- FileResponse
- get
- time
- manifest.json
- test_units.py
- run_autopilot.sh
- run_webapp.sh
- _is_request_authenticated
- post
- api_desks_status
- analyze_stock
- watchdog.sh
- sentiment_hedged_vs_unhedged.py
- fundamentals.py
- ross_execution.py
- .filter_series
- ConvexTailEngine
- AutonomousComplianceChecker
- AgentCouncil
- SubscriberProfile
- TradeJournal
- BayesianConfidenceEngine
- FactorDAG
- CryptoFuturesAutopilot
- TestMultiDeskArchitecture
- CMEFuturesAutopilot
- shock_detector.py
- align_timestamp_point_in_time
- ForexStrategyEngine
- pandas
- hedging_engine.py
- financial_modeling.py
- cost_model.py
- council.py
- run_ross_momentum_sim
- iOS Mobile App & Home Screen Widget Blueprint
- deadmans_switch.py
- unittest
- test_institutional_benchmark.py
- CryptoPerpStrategyEngine
- Node
- CMEFuturesStrategyEngine
- market_scanner.py
- five_year_stats.py
- os
- walk_forward.py
- pathlib
- time_to_goal.py
- tp1_scale_plan
- TestArchitectureFixes
- daily_routine.py
- .test_defensive_scaling_on_losing_streak
- evaluate_five_pillars
- risk/__init__.py
- TestProjectOmega
- atomic_json_read
- argparse
- _start_port_8081_forwarder
- test_point_in_time.py
- TestTechnicalIndicators
- TwentyYearStrategyEngine
- api_remote_qr_svg
- TestAgentCouncilArchitecture
- detect_intraday_shock
- main
- _simulate_bars
- analyze_exit
- TestArticleSelection
- reality_check.py
- run_experiment
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- calculate_dynamic_hedge_ratio
- validate_anti_leakage
- 🔌 Universal MCP Server Setup Guide for All AI Builders
- Candle
- run_multi_asset_benchmark
- check_tail_risk
- TestJournalV3
- GEMINI.md

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 31 edges
2. `TechnicalIndicators` - 30 edges
3. `atomic_json_read()` - 30 edges
4. `atomic_json_write()` - 28 edges
5. `TradeJournal` - 25 edges
6. `AgentCouncil` - 20 edges
7. `main()` - 20 edges
8. `Profile` - 19 edges
9. `_simulate_bars()` - 19 edges
10. `CryptoFuturesAutopilot` - 17 edges

## Surprising Connections (you probably didn't know these)
- `analyze_stock()` --uses--> `TechnicalIndicators`  [INFERRED]
  stock-signal-engine/risk/stock_analysis.py → stock-signal-engine/market/technicals.py
- `_analyze_trend()` --uses--> `TechnicalIndicators`  [INFERRED]
  stock-signal-engine/risk/stock_analysis.py → stock-signal-engine/market/technicals.py
- `_assess_entry()` --uses--> `TechnicalIndicators`  [INFERRED]
  stock-signal-engine/risk/stock_analysis.py → stock-signal-engine/market/technicals.py
- `BrokerClientFactory` --uses--> `SubscriberProfile`  [INFERRED]
  stock-signal-engine/gateway/broker_client.py → stock-signal-engine/gateway/subscriber_registry.py
- `_tunnel()` --calls--> `start_tunnel()`  [EXTRACTED]
  stock-signal-engine/webapp/app.py → stock-signal-engine/webapp/tunnel_manager.py

## Import Cycles
- None detected.

## Communities (92 total, 35 thin omitted)

### Community 0 - "Profile"
Cohesion: 0.15
Nodes (5): baseline_profile(), Profile, profile_from_row(), sensitivity_grid(), TestFinancialModelingAdaptive

### Community 1 - "tunnel_manager.py"
Cohesion: 0.10
Nodes (13): api_remote_access(), get_active_tunnel_url(), get_local_ip(), get_qr_png_bytes(), get_remote_status(), is_caffeinate_running(), is_tunnel_evicted(), print_cli_summary() (+5 more)

### Community 3 - "app.py"
Cohesion: 0.09
Nodes (13): _account_snapshot(), api_account(), api_equity_curve(), api_health(), api_journal_summary(), api_journal_trades(), api_model_learning_log(), api_rescan() (+5 more)

### Community 4 - "test_project_omega.py"
Cohesion: 0.15
Nodes (6): build_books(), calculate_asset_beta(), detect_market_regime(), calculate_hedge_pair(), _latest_close(), resolve_hedge_instrument()

### Community 5 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 6 - "FileResponse"
Cohesion: 0.17
Nodes (6): index(), manifest(), office_view(), overview(), terminal(), widget()

### Community 7 - "get"
Cohesion: 0.06
Nodes (23): api_advisor_exit(), api_benchmark_summary(), api_book_allocation(), api_compliance_report(), api_confluence_evaluate(), api_council_recent(), api_council_status(), api_desks_benchmark() (+15 more)

### Community 9 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 10 - "test_units.py"
Cohesion: 0.07
Nodes (11): banned_ticker(), without_banned(), TestAlpacaNews, TestDatasetGenerator, TestJournalV2, TestNewsMemory, TestPurchaseLogger, TestScannerQualityGate (+3 more)

### Community 11 - "run_autopilot.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_autopilot.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 12 - "run_webapp.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_OFFLINE, OMP_NUM_THREADS, PYTHONUNBUFFERED, run_webapp.sh script, TOKENIZERS_PARALLELISM, TRANSFORMERS_OFFLINE, USE_LGBM_RUNTIME

### Community 13 - "_is_request_authenticated"
Cohesion: 0.38
Nodes (3): api_auth_status(), _is_request_authenticated(), pin_auth_middleware()

### Community 14 - "post"
Cohesion: 0.08
Nodes (18): AIReviewRequest, api_compliance_ai_review(), api_council_convene(), api_council_decision(), api_gateway_register_subscriber(), api_gateway_replicate(), api_jev_execute(), api_model_confidence_evaluate() (+10 more)

### Community 15 - "api_desks_status"
Cohesion: 0.40
Nodes (4): api_desks_status(), _find_process_pid(), _is_pid_alive(), _read_pid()

### Community 16 - "analyze_stock"
Cohesion: 0.10
Nodes (7): analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _project_1m(), _verdict()

### Community 17 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 19 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.13
Nodes (7): main(), print_comparison(), run_signal_pipeline(), stress_test(), add_indicators(), get_latest(), get_market_features()

### Community 20 - "fundamentals.py"
Cohesion: 0.19
Nodes (7): _ensure_cache_dir(), evaluate_fundamental_quality(), fetch_fundamentals(), _load_cik_map(), _load_fundamentals_cache(), _save_fundamentals_cache(), TestFundamentals

### Community 21 - "ross_execution.py"
Cohesion: 0.05
Nodes (17): get_client(), get_current_exposure(), get_portfolio_value(), submit_bracket_buy(), submit_market_order(), submit_order(), submit_pair_orders(), execute_hedged_trade() (+9 more)

### Community 24 - "AutonomousComplianceChecker"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 26 - "SubscriberProfile"
Cohesion: 0.08
Nodes (4): MirrorDispatcher, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 28 - "BayesianConfidenceEngine"
Cohesion: 0.07
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 30 - "CryptoFuturesAutopilot"
Cohesion: 0.09
Nodes (3): CryptoFuturesAutopilot, main(), TestCryptoPerpFixes

### Community 33 - "shock_detector.py"
Cohesion: 0.32
Nodes (4): _env_float(), fetch_prev_close(), gap_shock_threshold(), velocity_shock_threshold()

### Community 34 - "align_timestamp_point_in_time"
Cohesion: 0.27
Nodes (3): align_timestamp_point_in_time(), parse_timestamp(), TestPointInTimeAlignment

### Community 36 - "pandas"
Cohesion: 0.11
Nodes (15): main(), _print_report(), run_comparison(), _window(), run_test(), run_mean_reversion(), fetch_latest_price(), fetch_prices() (+7 more)

### Community 37 - "hedging_engine.py"
Cohesion: 0.11
Nodes (8): calculate_exit_levels(), compute_book_exposure(), _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), is_hot_banned(), TestAdaptiveExitGeometry, TestExitEngine

### Community 38 - "financial_modeling.py"
Cohesion: 0.15
Nodes (11): crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats(), pick_best(), rank_candidates(), refine_grid() (+3 more)

### Community 39 - "cost_model.py"
Cohesion: 0.22
Nodes (4): days_to_target(), expected_move_pct(), is_trade_viable(), TestCostModel

### Community 40 - "council.py"
Cohesion: 0.20
Nodes (6): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision()

### Community 41 - "run_ross_momentum_sim"
Cohesion: 0.20
Nodes (6): generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), TestRossMomentumStrategy

### Community 42 - "iOS Mobile App & Home Screen Widget Blueprint"
Cohesion: 0.12
Nodes (15): 1. Executive Summary & Value Proposition, 2. System Architecture & Connectivity, 3. Widget UI Specifications, 4. Implementation Pathways, 5. Security & Multi-Tenant Subscriber Protection, 6. Execution Roadmap (When Ready to Proceed), A. Small Widget (2×2 Home Screen Tile / Lock Screen Complication), B. Medium Widget (4×2 Home Screen Tile) (+7 more)

### Community 43 - "deadmans_switch.py"
Cohesion: 0.20
Nodes (5): check_liveness(), get_autopilot_heartbeat(), is_us_equity_market_open(), main(), run_daemon()

### Community 45 - "test_institutional_benchmark.py"
Cohesion: 0.11
Nodes (4): ConfluenceDecision, TriConfluenceMatrix, TestTriConfluenceMatrix, TestInstitutionalBenchmarkEngine

### Community 47 - "Node"
Cohesion: 0.15
Nodes (5): AlphaCompositeNode, Node, PriceSourceNode, SentimentAggregatorNode, TechnicalFeaturesNode

### Community 49 - "market_scanner.py"
Cohesion: 0.26
Nodes (6): flat_universe(), main(), mass_backtest(), print_mass_report(), rank_market(), scan_dip_opportunities()

### Community 50 - "five_year_stats.py"
Cohesion: 0.08
Nodes (20): buy_and_hold_stats(), collect_tickers(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str() (+12 more)

### Community 51 - "os"
Cohesion: 0.09
Nodes (18): auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), market_is_open(), post_market_belief_cycle() (+10 more)

### Community 52 - "walk_forward.py"
Cohesion: 0.25
Nodes (5): main(), month_folds(), _policy_summary(), _run_style(), walk_forward()

### Community 53 - "pathlib"
Cohesion: 0.14
Nodes (3): BrokerClientFactory, MirrorTradeSignal, ReplicationSummary

### Community 54 - "time_to_goal.py"
Cohesion: 0.29
Nodes (7): growth_optimal_f(), main(), mc_time_to_goal(), oos_r_pool(), pool_stats(), savings_months(), tuned_profile()

### Community 55 - "tp1_scale_plan"
Cohesion: 0.15
Nodes (4): ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 57 - "daily_routine.py"
Cohesion: 0.22
Nodes (7): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_analyze(), run_morning(), scrape_ticker()

### Community 59 - "evaluate_five_pillars"
Cohesion: 0.20
Nodes (4): discover_market_universe(), evaluate_five_pillars(), evaluate_news_catalyst(), scan_momentum_market()

### Community 60 - "risk/__init__.py"
Cohesion: 0.16
Nodes (7): evaluate_trade(), calculate_compounder_size(), calculate_position_size(), calculate_regime_risk_pct(), calculate_streak_compounding_factor(), check_portfolio_heat(), TestRegimeAdaptivePositionSizing

### Community 63 - "argparse"
Cohesion: 0.13
Nodes (6): main(), backfill_historical_purchases(), format_purchase_log(), get_purchase_log_text(), get_purchase_logs(), log_purchase()

### Community 64 - "_start_port_8081_forwarder"
Cohesion: 0.32
Nodes (5): _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel()

### Community 65 - "test_point_in_time.py"
Cohesion: 0.19
Nodes (4): PointInTimeAlignmentNode, enrich_article_point_in_time(), get_next_trading_day(), is_trading_day()

### Community 67 - "TwentyYearStrategyEngine"
Cohesion: 0.33
Nodes (3): main(), save_report(), TwentyYearStrategyEngine

### Community 68 - "api_remote_qr_svg"
Cohesion: 0.17
Nodes (7): api_auth_logout(), api_remote_qr_svg(), api_verify_pin(), graph_tree_view(), graph_view(), PinVerifyRequest, get_qr_svg()

### Community 70 - "detect_intraday_shock"
Cohesion: 0.23
Nodes (4): get_sniper_setup(), detect_intraday_shock(), earnings_blackout(), TestShockDetector

### Community 71 - "main"
Cohesion: 0.18
Nodes (4): build_bundle(), build_hunt_grid(), main(), run_diagnostic()

### Community 72 - "_simulate_bars"
Cohesion: 0.22
Nodes (5): Bundle, run_profile(), _simulate_bars(), window_run(), round_trip_cost()

### Community 73 - "analyze_exit"
Cohesion: 0.25
Nodes (3): breakeven_move_pct(), analyze_exit(), TestExitAdvisor

### Community 76 - "run_experiment"
Cohesion: 0.20
Nodes (3): generate_realistic_news_stream(), run_experiment(), NewsSourceNode

### Community 77 - "20-Year Institutional Strategy & Swing-Shield Benchmark"
Cohesion: 0.40
Nodes (4): 20-Year Institutional Strategy & Swing-Shield Benchmark, Multi-Desk 30% YoY Synergy Architecture, Performance Comparison vs Market Benchmark, Year-by-Year Historical Breakdown (2007 - 2026)

### Community 82 - "🔌 Universal MCP Server Setup Guide for All AI Builders"
Cohesion: 0.25
Nodes (7): 1. Claude Desktop (macOS), 2. Claude Code CLI, 3. Cursor IDE, 4. Windsurf / Codeium, 5. VS Code (Cline / Roo Code / Continue), 🛠️ The 9 Live MCP Tools Exposed, 🔌 Universal MCP Server Setup Guide for All AI Builders

## Knowledge Gaps
- **37 isolated node(s):** `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED`, `TOKENIZERS_PARALLELISM`, `TRANSFORMERS_OFFLINE` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 686 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TechnicalIndicators` connect `pandas` to `financial_modeling.py`, `time`, `test_units.py`, `analyze_stock`, `market_scanner.py`, `pathlib`, `argparse`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **What connects `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED` to the rest of the system?**
  _37 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tunnel_manager.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09879032258064516 - nodes in this community are weakly interconnected._
- **Why does `TradeJournal` connect `TradeJournal` to `time`, `run_ross_momentum_sim`, `.reconcile_with_broker`, `ross_execution.py`, `.__init__`, `.record_partial`, `argparse`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Should `quant` be split into smaller, more focused modules?**
  _Cohesion score 0.08669354838709678 - nodes in this community are weakly interconnected._
- **Why does `CMEFuturesAutopilot` connect `CMEFuturesAutopilot` to `time`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09113300492610837 - nodes in this community are weakly interconnected._