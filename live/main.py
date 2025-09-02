import os
from typing import List
import time
import yfinance as yf
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass

# Indicators
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

# Alpaca Trading (paper)
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

app = FastAPI()

def get_env_list(key: str, default: str = "") -> List[str]:
    raw = os.getenv(key, default)
    return [s.strip().upper() for s in raw.split(",") if s.strip()]

def fetch_last_price(sym: str) -> float | None:
    try:
        df = yf.download(sym, period="5d", interval=os.getenv("INTERVAL", "5m"), progress=False)
        if df is None or df.empty:
            return None
        return float(df["Close"].iloc[-1])
    except Exception:
        return None

@app.get("/paper")
def paper():
    """
    Dry-run paper trading pass.
    - Reads universe from UNIVERSE env var
    - Pulls last price via yfinance (no paid data needed)
    - If PLACE_ORDERS=true, places a tiny market order in Alpaca paper (1 share) for the first symbol only
      (kept intentionally small/safe). Otherwise just returns a summary.
    """
    universe = get_env_list("UNIVERSE", "SPY,QQQ,AAPL,MSFT")
    place_orders = os.getenv("PLACE_ORDERS", "false").lower() == "true"

    # Pull prices
    results = []
    t0 = time.time()
    for sym in universe:
        px = fetch_last_price(sym)
        results.append({"symbol": sym, "last": px})

    placed = []
    msg = "dry-run"
    if place_orders:
        # Alpaca auth (paper keys are provided via secrets)
        key = os.getenv("ALPACA_KEY")
        secret = os.getenv("ALPACA_SECRET")
        if not key or not secret:
            return {"ok": False, "error": "Missing ALPACA_KEY/ALPACA_SECRET env"}

        client = TradingClient(api_key=key, secret_key=secret, paper=True)

        # Sanity check account status
        try:
            acct = client.get_account()
            # OPTIONAL: ensure we're in paper mode / active
            _ = acct.status
        except Exception as e:
            return {"ok": False, "error": f"Alpaca auth/account failed: {e!r}"}

        # Safety: place **one** tiny test order on the first symbol only
        sym0 = universe[0]
        try:
            order = client.submit_order(
                order_data=MarketOrderRequest(
                    symbol=sym0,
                    qty=1,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY,
                    order_class=OrderClass.SIMPLE,
                )
            )
            placed.append({"symbol": sym0, "id": getattr(order, "id", None)})
            msg = "1 test order placed"
        except Exception as e:
            return {"ok": False, "error": f"submit_order failed: {e!r}"}

    return {
        "ok": True,
        "mode": "live-service",
        "place_orders": place_orders,
        "universe": universe,
        "prices": results,
        "placed": placed,
        "elapsed_s": round(time.time() - t0, 3),
        "msg": msg,
    }

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
    ema_now = df["EMA"].iloc[-1]

    buy = (rsi_prev1 <= 30 and rsi_now > 30) and (price_now > ema_now)
    sell = (rsi_prev1 >= 70 and rsi_now < 70) and (price_now < ema_now)

    if buy:
        return "BUY"
    if sell:
        return "SELL"
    return "HOLD"

def alpaca_client_or_none() -> TradingClient | None:
    key = os.getenv("ALPACA_KEY")
    sec = os.getenv("ALPACA_SECRET")
    if not key or not sec:
        return None
    # paper=True ensures we hit paper trading
    return TradingClient(api_key=key, secret_key=sec, paper=True)

def calc_qty(price: float, equity: float, risk_pct: float) -> int:
    if price <= 0:
        return 0
    dollar_risk = equity * max(min(risk_pct, 0.05), 0.0001)  # clamp to [0.01%, 5%]
    qty = math.floor(max(dollar_risk / price, 0))
    return int(qty)

def maybe_place_order(client: TradingClient, symbol: str, side: str, qty: int) -> Dict[str, Any]:
    side_enum = OrderSide.BUY if side == "BUY" else OrderSide.SELL
    req = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side_enum,
        time_in_force=TimeInForce.DAY,
    )
    o = client.submit_order(order_data=req)
    return {"id": o.id, "symbol": o.symbol, "side": o.side.value, "qty": o.qty, "status": str(o.status)}

@app.get("/paper")
def paper():
    """
    Pulls data with yfinance, computes RSI/EMA, emits signals,
    and (if enabled) places paper market orders on Alpaca.
    """
    uni = get_universe()
    interval = os.getenv("INTERVAL", "5m")
    lookback = int(os.getenv("LOOKBACK_DAYS", "30"))
    rsi_len = int(os.getenv("RSI", "14"))
    ema_len = int(os.getenv("EMA", "50"))

    # trading controls
    place_orders = os.getenv("PLACE_ORDERS", "false").lower() == "true"
    paper_equity = env_float("PAPER_EQUITY", 100000.0)
    risk_pct = env_float("RISK_PCT", 0.005)  # 0.5% default

    results: Dict[str, Any] = {"ok": True, "interval": interval, "lookback_days": lookback, "signals": {}}

    client = alpaca_client_or_none() if place_orders else None
    if place_orders and client is None:
        results["warning"] = "PLACE_ORDERS=true but ALPACA_KEY/ALPACA_SECRET not set; skipping orders."

    for sym in uni:
        try:
            df = get_ohlcv(sym, interval, lookback)
            if df.empty:
                results["signals"][sym] = {"error": "no data"}
                continue
            df = compute_indicators(df, rsi_len, ema_len)
            sig = generate_signal(df)
            price = float(df["Close"].iloc[-1])
            rsi_now = float(df["RSI"].iloc[-1])
            ema_now = float(df["EMA"].iloc[-1])

            sig_result: Dict[str, Any] = {"signal": sig, "price": price, "rsi": rsi_now, "ema": ema_now}

            if place_orders and sig in ("BUY", "SELL") and client is not None:
                qty = calc_qty(price, paper_equity, risk_pct)
                if qty > 0:
                    order_info = maybe_place_order(client, sym, sig, qty)
                    sig_result["order"] = order_info
                else:
                    sig_result["order_skipped"] = "qty=0 based on risk/equity/price"
            results["signals"][sym] = sig_result
        except Exception as e:
            results["signals"][sym] = {"error": str(e)}

    results["ts"] = time.time()
    return results
