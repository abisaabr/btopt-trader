# scripts/run_backtests.py
import os, json, math, time, pathlib
from datetime import timedelta
import pandas as pd

# ENV expected
BUCKET = os.getenv("GCS_BUCKET")
RESULTS_PREFIX = os.getenv("RESULTS_PREFIX", "nightly")
TIMEFRAME = os.getenv("TIMEFRAME", "5m")
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "30"))
TP_GRID = os.getenv("TP_GRID", "0.01,0.015,0.02").split(",")
SL_GRID = os.getenv("SL_GRID", "0.005,0.01").split(",")
MAXBARS_GRID = os.getenv("MAXBARS_GRID", "20,30").split(",")
MIN_TRADES = int(os.getenv("MIN_TRADES", "1"))
BATCH_SLEEP_S = int(os.getenv("BATCH_SLEEP_S", "0"))  # optional throttle
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# Shard info from Cloud Run Jobs
TASK_INDEX = int(os.getenv("CLOUD_RUN_TASK_INDEX", "0"))
TASK_COUNT = int(os.getenv("CLOUD_RUN_TASK_COUNT", "1"))

# Optional: limit symbols for smoke-tests: "AAPL,MSFT,SPY"
LIMIT_SYMBOLS = [s for s in os.getenv("LIMIT_SYMBOLS","").split(",") if s]

# Your existing util to compute top-500 by 30d median dollar volume
# If you already have a parquet/csv for that, just load it here.
def load_universe():
    p = pathlib.Path("data/universe/top500_30d_mdv.parquet")
    if p.exists():
        df = pd.read_parquet(p)
        syms = df["symbol"].tolist()
    else:
        # fallback: load from csv or a function you already have
        df = pd.read_csv("data/universe/top500_30d_mdv.csv")
        syms = df["symbol"].tolist()
    if LIMIT_SYMBOLS:
        syms = [s for s in syms if s in LIMIT_SYMBOLS]
    return syms

def shard_slice(items, idx, total):
    n = len(items)
    base = n // total
    extra = n % total
    start = idx * base + min(idx, extra)
    end = start + base + (1 if idx < extra else 0)
    return items[start:end]

def run_one_symbol(symbol):
    # === call your existing backtest runner here ===
    # should return a dataframe of trades OR save parquet to local disk
    # Example:
    # df = backtest(symbol, timeframe=TIMEFRAME, tp_list=TP_GRID, sl_list=SL_GRID, maxbars_list=MAXBARS_GRID, lookback_days=LOOKBACK_DAYS)
    # df.to_parquet(f"data/parquet/{symbol}_{TIMEFRAME}.parquet")
    return True

def upload_results():
    # Mirror local parquet to GCS prefix
    # (requires gsutil in container or python GCS client; gsutil is simplest)
    os.system(f'gsutil -m rsync -r data/parquet gs://{BUCKET}/{RESULTS_PREFIX}/')

def main():
    symbols = load_universe()
    my_slice = shard_slice(symbols, TASK_INDEX, TASK_COUNT)
    print(f"[shard] index={TASK_INDEX}/{TASK_COUNT} symbols={len(my_slice)}")

    for i, sym in enumerate(my_slice, 1):
        print(f"[{i}/{len(my_slice)}] backtesting {sym}")
        if not DRY_RUN:
            run_one_symbol(sym)
        if BATCH_SLEEP_S:
            time.sleep(BATCH_SLEEP_S)

    if not DRY_RUN:
        upload_results()
    print("[done] shard complete")

if __name__ == "__main__":
    main()
