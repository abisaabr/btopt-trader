# PLAN.md – Backtester & Trade Picker Build

## Phase 1: Core Backtester
- [ ] Implement base engine for loading historical OHLCV + options chain
- [ ] Define ContextKey format (`SYMBOL|TF|Pattern|MACDsign|RSIstate|Trend|VolRegime`)
- [ ] Support both calls and puts (long & short); multi-leg containers
- [ ] Triple-barrier exits (TP/SL/time)
- [ ] Log win%, profit factor, Sharpe, avg P&L, drawdown

## Phase 2: Realism
- [ ] Liquidity gates (max spread %, min OI/vol)
- [ ] Actual quotes when available; fallback to model + conservative slippage
- [ ] Assignment heuristics for short ITM near ex-div
- [ ] Cache indicators per-symbol

## Phase 3: Smarter Testing
- [ ] Regime classifier (trend/chop × vol)
- [ ] Coarse grid → zoom
- [ ] Symbol archetypes (mega-cap, high beta…)
- [ ] Walk-forward CV with purge/embargo
- [ ] Multiple-testing penalty (higher sample min or Sharpe haircut)

## Phase 4: Strategy Promotion
- [ ] Stress test at base/+1×/+2× slippage
- [ ] Top-K keys per regime; sample size threshold
- [ ] Export whitelist for live

## Phase 5: Live Readiness
- [ ] Equity-aware sizing; daily DD stop; max positions; kill-switch
- [ ] Monitoring: realized vs simulated fills; drift checks
- [ ] Daily summary

## Phase 6: Continuous Improvement
- [ ] Bandit weighting for capital allocation
- [ ] Why-enter / why-exit logging
- [ ] Prune/quarantine underperformers
