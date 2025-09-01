# 📈 btopt-trader
Backtesting & live options trading with pattern recognition.

## What is this?
- Backtests intraday options strategies (calls, puts, spreads, condors, straddles)
- Ranks strategies by win%/Sharpe per **pattern + context** (“ContextKey”)
- Live picker places **paper trades** only when historical stats look strong
- Two workstations: one heavy (backtests), one light (trading)

## Quick start
1) Create a Python 3.11+ env
2) `pip install -r requirements.txt`
3) Read `PLAN.md` and start with `configs/*` then `backtests/runner.py`

## Config you must set
- GCS bucket for results: **replace** `<YOUR_GCS_BUCKET>` in `utils/io.py`
- Alpaca keys in environment (paper trading):
  - `APCA_API_KEY_ID` **replace value**
  - `APCA_API_SECRET_KEY` **replace value**
  - `APCA_PAPER` = `true` (paper), `PLACE_ORDERS` = `false` to start

## Repo map
See `PLAN.md` and the folder layout in this repo.

## Disclaimer
Research only. Not investment advice. Use at your own risk.
