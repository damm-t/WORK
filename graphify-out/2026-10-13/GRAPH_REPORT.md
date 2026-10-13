# Graph Report - WORK  (2026-10-13)

## Corpus Check
- 212 files · ~436,064 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 31 file(s) not represented in the graph (top: .csv 15, (none) 9, .ipynb 3)

## Summary
- 1550 nodes · 3401 edges · 80 communities (51 shown, 29 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 79 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `823365e0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- score_trade
- tunnel_manager.py
- app.py
- run_analyze
- scenario_small.sh
- get
- Any
- time
- manifest.json
- test_units.py
- run_autopilot.sh
- run_webapp.sh
- _is_request_authenticated
- post
- api_desks_status
- TechnicalIndicators
- watchdog.sh
- sentiment_hedged_vs_unhedged.py
- fundamentals.py
- alpha_client.py
- .filter_series
- ConvexTailEngine
- autonomous_checker.py
- AgentCouncil
- mirror_dispatcher.py
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
- days_to_target
- council.py
- run_ross_momentum_sim
- test_jev_scooper.py
- atomic_json_read
- os
- test_institutional_benchmark.py
- CryptoPerpStrategyEngine
- factor_dag.py
- CMEFuturesStrategyEngine
- market_scanner.py
- five_year_stats.py
- autopilot.py
- hedging_backtester.py
- numpy
- tp1_scale_plan
- TestArchitectureFixes
- daily_routine.py
- calculate_streak_compounding_factor
- low_float_scanner.py
- calculate_position_size
- TestProjectOmega
- test_project_omega.py
- log_purchase
- _start_port_8081_forwarder
- PairStrategySimulator
- TestTechnicalIndicators
- TwentyYearStrategyEngine
- api_flatten
- execute_ross_bracket_trade
- detect_intraday_shock
- execute_jev_scoop_trade
- evaluate_fundamental_quality
- banned_ticker
- TestArticleSelection
- reality_check.py
- walk_forward
- 20-Year Institutional Strategy & Swing-Shield Benchmark
- TestTimeDecay

## God Nodes (most connected - your core abstractions)
1. `fetch_prices()` - 31 edges
2. `TechnicalIndicators` - 30 edges
3. `atomic_json_read()` - 30 edges
4. `atomic_json_write()` - 28 edges
5. `TradeJournal` - 25 edges
6. `main()` - 20 edges
7. `AgentCouncil` - 20 edges
8. `Profile` - 19 edges
9. `_simulate_bars()` - 19 edges
10. `TestMultiDeskArchitecture` - 17 edges

## Surprising Connections (you probably didn't know these)
- `build_books()` --calls--> `calculate_exit_levels()`  [INFERRED]
  stock-signal-engine/backtest/sentiment_hedged_vs_unhedged.py → stock-signal-engine/risk/hedging_engine.py
- `build_books()` --calls--> `calculate_hedge_pair()`  [INFERRED]
  stock-signal-engine/backtest/sentiment_hedged_vs_unhedged.py → stock-signal-engine/risk/hedging_engine.py
- `_tunnel()` --calls--> `start_tunnel()`  [EXTRACTED]
  stock-signal-engine/webapp/app.py → stock-signal-engine/webapp/tunnel_manager.py
- `run_morning()` --calls--> `fetch_prices()`  [EXTRACTED]
  stock-signal-engine/backtest/daily_routine.py → stock-signal-engine/market/price_fetcher.py
- `run_morning()` --calls--> `without_banned()`  [EXTRACTED]
  stock-signal-engine/backtest/daily_routine.py → stock-signal-engine/risk/hedging_engine.py

## Import Cycles
- None detected.

## Communities (80 total, 29 thin omitted)

### Community 1 - "tunnel_manager.py"
Cohesion: 0.09
Nodes (14): api_remote_qr_svg(), get_active_tunnel_url(), get_local_ip(), get_qr_png_bytes(), get_qr_svg(), get_remote_status(), is_caffeinate_running(), is_tunnel_evicted() (+6 more)

### Community 3 - "app.py"
Cohesion: 0.07
Nodes (23): _account_snapshot(), AIReviewRequest, api_account(), api_compliance_ai_review(), api_equity_curve(), api_gateway_register_subscriber(), api_gateway_replicate(), api_health() (+15 more)

### Community 4 - "run_analyze"
Cohesion: 0.29
Nodes (3): run_analyze(), detect_market_regime(), _leaderboard()

### Community 5 - "scenario_small.sh"
Cohesion: 0.07
Nodes (26): BE_OFFSET_MULT, BE_TRIGGER_MULT, HF_HUB_OFFLINE, MAX_PORTFOLIO_HEAT, MAX_POSITION_NOTIONAL_PCT, MIN_AUTO_SCORE, MIN_TRADE_SCORE, NEWS_MEMORY (+18 more)

### Community 6 - "get"
Cohesion: 0.06
Nodes (21): api_advisor_exit(), api_book_allocation(), api_evaluate(), api_jev_opportunities(), api_journal_exits(), api_model_confidence(), api_model_learning_log(), api_model_stabilized_price() (+13 more)

### Community 7 - "Any"
Cohesion: 0.09
Nodes (11): api_benchmark_summary(), api_compliance_report(), api_confluence_evaluate(), api_council_recent(), api_council_status(), api_desks_benchmark(), api_desks_scan(), api_gateway_list_subscribers() (+3 more)

### Community 9 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 10 - "test_units.py"
Cohesion: 0.06
Nodes (13): calculate_compounder_size(), check_tail_risk(), TestAlpacaNews, TestDatasetGenerator, TestJournalV2, TestJournalV3, TestNewsMemory, TestPurchaseLogger (+5 more)

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
Cohesion: 0.12
Nodes (9): api_auth_logout(), api_council_convene(), api_council_decision(), api_purge_mock_trades(), api_reconcile_broker(), api_remote_restart(), api_verify_pin(), graph_tree_view() (+1 more)

### Community 15 - "api_desks_status"
Cohesion: 0.40
Nodes (4): api_desks_status(), _find_process_pid(), _is_pid_alive(), _read_pid()

### Community 16 - "TechnicalIndicators"
Cohesion: 0.11
Nodes (9): TechnicalIndicators, expected_move_pct(), analyze_stock(), _analyze_trend(), add(), _assess_entry(), _fmt_pct(), _project_1m() (+1 more)

### Community 17 - "watchdog.sh"
Cohesion: 0.80
Nodes (4): alive(), heal_via_terminal(), log(), watchdog.sh script

### Community 19 - "sentiment_hedged_vs_unhedged.py"
Cohesion: 0.08
Nodes (11): build_books(), main(), print_comparison(), run_signal_pipeline(), stress_test(), add_indicators(), get_latest(), get_market_features() (+3 more)

### Community 20 - "fundamentals.py"
Cohesion: 0.33
Nodes (5): _ensure_cache_dir(), fetch_fundamentals(), _load_cik_map(), _load_fundamentals_cache(), _save_fundamentals_cache()

### Community 21 - "alpha_client.py"
Cohesion: 0.22
Nodes (8): get_client(), get_current_exposure(), get_portfolio_value(), submit_market_order(), submit_order(), submit_pair_orders(), execute_hedged_trade(), execute_trade()

### Community 22 - ".filter_series"
Cohesion: 0.11
Nodes (3): AntiVolatilityModel, StabilizationResult, TestAntiVolatilityModel

### Community 24 - "autonomous_checker.py"
Cohesion: 0.06
Nodes (7): AIReviewResult, AIRevisionChecker, TradeReviewPacket, AuditFeedback, AutonomousComplianceChecker, ComplianceCertificate, TestAutonomousComplianceChecker

### Community 26 - "mirror_dispatcher.py"
Cohesion: 0.07
Nodes (7): BrokerClientFactory, MirrorDispatcher, MirrorTradeSignal, ReplicationSummary, SubscriberProfile, SubscriberRegistry, TestMirrorGateway

### Community 28 - "BayesianConfidenceEngine"
Cohesion: 0.07
Nodes (6): BayesianConfidenceEngine, DailyEvidenceBundle, InformationHarvester, LearnedRule, ThesisStatement, TestBayesianConfidence

### Community 29 - "FactorDAG"
Cohesion: 0.07
Nodes (5): FactorDAG, NewsSourceNode, Node, PriceSourceNode, TestFactorDAG

### Community 30 - "CryptoFuturesAutopilot"
Cohesion: 0.09
Nodes (3): CryptoFuturesAutopilot, main(), TestCryptoPerpFixes

### Community 33 - "shock_detector.py"
Cohesion: 0.22
Nodes (5): earnings_blackout(), _env_float(), fetch_prev_close(), gap_shock_threshold(), velocity_shock_threshold()

### Community 34 - "align_timestamp_point_in_time"
Cohesion: 0.11
Nodes (7): align_timestamp_point_in_time(), enrich_article_point_in_time(), get_next_trading_day(), is_trading_day(), parse_timestamp(), SessionInfo, TestPointInTimeAlignment

### Community 36 - "pandas"
Cohesion: 0.15
Nodes (13): get_sniper_setup(), main(), run_test(), run_mean_reversion(), run_diagnostic(), calculate_asset_beta(), fetch_latest_price(), fetch_prices() (+5 more)

### Community 37 - "hedging_engine.py"
Cohesion: 0.07
Nodes (12): calculate_dynamic_hedge_ratio(), calculate_exit_levels(), calculate_hedge_pair(), compute_book_exposure(), _env_float(), get_adaptive_exit_geometry(), get_exit_geometry(), is_hot_banned() (+4 more)

### Community 38 - "financial_modeling.py"
Cohesion: 0.07
Nodes (23): baseline_profile(), build_bundle(), Bundle, crisis_pool(), load_ohlcv(), main(), monte_carlo(), per_year_stats() (+15 more)

### Community 39 - "days_to_target"
Cohesion: 0.25
Nodes (3): days_to_target(), is_trade_viable(), TestCostModel

### Community 40 - "council.py"
Cohesion: 0.10
Nodes (7): convene_council_meeting(), CouncilMeetingResult, DeskAgent, get_floor_status(), get_recent_meetings(), resolve_council_decision(), TestAgentCouncilArchitecture

### Community 41 - "run_ross_momentum_sim"
Cohesion: 0.12
Nodes (7): Candle, generate_synthetic_candles(), mock_ross_session(), RossSessionManager, RossTrade, run_ross_momentum_sim(), TestRossMomentumStrategy

### Community 42 - "test_jev_scooper.py"
Cohesion: 0.15
Nodes (3): JEVLiquidityScooper, ScoopOpportunity, TestJEVLiquidityScooper

### Community 43 - "atomic_json_read"
Cohesion: 0.14
Nodes (6): check_liveness(), get_autopilot_heartbeat(), main(), run_daemon(), atomic_json_read(), atomic_json_write()

### Community 44 - "os"
Cohesion: 0.18
Nodes (5): classify_position_book(), get_book_allocations(), get_split_ratios(), evaluate_trade(), check_portfolio_heat()

### Community 45 - "test_institutional_benchmark.py"
Cohesion: 0.11
Nodes (4): ConfluenceDecision, TriConfluenceMatrix, TestTriConfluenceMatrix, TestInstitutionalBenchmarkEngine

### Community 47 - "factor_dag.py"
Cohesion: 0.15
Nodes (7): generate_realistic_news_stream(), run_experiment(), AlphaCompositeNode, PointInTimeAlignmentNode, SentimentAggregatorNode, TechnicalFeaturesNode, validate_anti_leakage()

### Community 49 - "market_scanner.py"
Cohesion: 0.23
Nodes (7): flat_universe(), main(), mass_backtest(), print_mass_report(), rank_market(), scan_dip_opportunities(), without_banned()

### Community 50 - "five_year_stats.py"
Cohesion: 0.16
Nodes (11): buy_and_hold_stats(), _console_summary(), _fmt(), _load(), main(), _report(), _row_str(), run() (+3 more)

### Community 51 - "autopilot.py"
Cohesion: 0.16
Nodes (11): auto_select(), _await_fill(), _day_guard(), load_state(), main(), manage_open_positions(), run_autopilot(), run_scan() (+3 more)

### Community 52 - "hedging_backtester.py"
Cohesion: 0.15
Nodes (12): main(), performance_metrics(), _print_report(), run_comparison(), simulate(), SimulationConfig, _strip_tz(), _trim() (+4 more)

### Community 54 - "numpy"
Cohesion: 0.19
Nodes (9): run_multi_asset_benchmark(), simulate_asset_trades(), growth_optimal_f(), main(), mc_time_to_goal(), oos_r_pool(), pool_stats(), savings_months() (+1 more)

### Community 55 - "tp1_scale_plan"
Cohesion: 0.15
Nodes (4): ratchet_trailing_stop(), tp1_scale_plan(), TestAdaptiveScaleOutAndTrail, TestTp1Automation

### Community 57 - "daily_routine.py"
Cohesion: 0.20
Nodes (8): _briefing_path(), load_today_briefing(), main(), _plan_path(), run_morning(), scrape_ticker(), collect_tickers(), get_universe()

### Community 59 - "low_float_scanner.py"
Cohesion: 0.23
Nodes (5): check_trading_window(), discover_market_universe(), evaluate_five_pillars(), evaluate_news_catalyst(), scan_momentum_market()

### Community 60 - "calculate_position_size"
Cohesion: 0.24
Nodes (3): calculate_position_size(), calculate_regime_risk_pct(), TestRegimeAdaptivePositionSizing

### Community 63 - "log_purchase"
Cohesion: 0.20
Nodes (5): backfill_historical_purchases(), format_purchase_log(), get_purchase_log_text(), get_purchase_logs(), log_purchase()

### Community 64 - "_start_port_8081_forwarder"
Cohesion: 0.28
Nodes (6): _start_port_8081_forwarder(), accept_loop(), forward_stream(), warm_cache(), _tunnel(), _warm()

### Community 67 - "TwentyYearStrategyEngine"
Cohesion: 0.39
Nodes (3): main(), save_report(), TwentyYearStrategyEngine

### Community 68 - "api_flatten"
Cohesion: 0.25
Nodes (4): post_market_belief_cycle(), unwind_paired_hedge(), api_flatten(), _cancel_open_orders()

### Community 77 - "20-Year Institutional Strategy & Swing-Shield Benchmark"
Cohesion: 0.40
Nodes (4): 20-Year Institutional Strategy & Swing-Shield Benchmark, Multi-Desk 30% YoY Synergy Architecture, Performance Comparison vs Market Benchmark, Year-by-Year Historical Breakdown (2007 - 2026)

## Knowledge Gaps
- **37 isolated node(s):** `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED`, `TOKENIZERS_PARALLELISM`, `TRANSFORMERS_OFFLINE` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 665 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TestMultiDeskArchitecture` connect `TestMultiDeskArchitecture` to `time`, `CMEFuturesAutopilot`, `CryptoFuturesAutopilot`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **What connects `HF_HUB_OFFLINE`, `OMP_NUM_THREADS`, `PYTHONUNBUFFERED` to the rest of the system?**
  _37 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tunnel_manager.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09269162210338681 - nodes in this community are weakly interconnected._
- **Why does `TradeJournal` connect `TradeJournal` to `time`, `run_ross_momentum_sim`, `os`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Should `quant` be split into smaller, more focused modules?**
  _Cohesion score 0.08669354838709678 - nodes in this community are weakly interconnected._
- **Why does `atomic_json_write()` connect `atomic_json_read` to `CMEFuturesAutopilot`, `council.py`, `time`, `os`, `autopilot.py`, `TestArchitectureFixes`, `AgentCouncil`, `daily_routine.py`, `CryptoFuturesAutopilot`, `TestMultiDeskArchitecture`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06755260243632337 - nodes in this community are weakly interconnected._