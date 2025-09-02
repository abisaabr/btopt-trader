import os, time, math
from typing import List, Dict, Any
from fastapi import FastAPI
import pandas as pd

# Free market data
import yfinance as yf

# Indicators
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

# Alpaca Trading (paper)
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

app = FastAPI()

def env_list(name: str, default_csv: str) -> List[str]:
    return [s.strip().upper() for s in os.getenv(name, default_csv).split(",") if s.strip()]

def env_float(name: str, default_val: float) -> float:
    try:
        return float(os.getenv(name, str(default_val)))
    except Exception:
        return default_val

def get_universe() -> List[str]:
    return env_list("UNIVERSE", "SPY,QQQ")

@app.get("/readyz")
def readyz():
    return {"ok": True}

@app.get("/healthz")
def healthz():
    must_have = ["UNIVERSE"]
    env_ok = all(k in os.environ for k in must_have)
    return {"ok": env_ok, "time": time.time(), "missing": [k for k in must_have if k not in os.environ]}

@app.get("/run")
def run_once():
    return {"ok": True, "universe": get_universe(), "ts": time.time()}

# ---------- strategy helpers ----------

def get_ohlcv(symbol: str, interval: str, lookback_days: int) -> pd.DataFrame:
    # yfinance period must align with interval; use generous buffer
    period = f"{max(lookback_days, 5)}d"
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
    # normalize column names
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()
    df = df.rename(columns={c: c.capitalize() for c in df.columns})
    return df

def compute_indicators(df: pd.DataFrame, rsi_len=14, ema_len=50) -> pd.DataFrame:
    if df.empty:
        return df
    rsi = RSIIndicator(close=df["Close"], window=rsi_len).rsi()
    ema = EMAIndicator(close=df["Close"], window=ema_len).ema_indicator()
    df["RSI"] = rsi
    df["EMA"] = ema
    return df

def generate_signal(df: pd.DataFrame) -> str:
    """
    Super-simple demo rules:
      - BUY if RSI crosses above 30 and price > EMA
      - SELL if RSI crosses below 70 and price < EMA
      - else HOLD
    """
    if len(df) < 3:
        return "HOLD"
    rsi_prev2, rsi_prev1, rsi_now = df["RSI"].iloc[-3], df["RSI"].iloc[-2], df["RSI"].iloc[-1]
    price_now = df["Close"].iloc[-1]
