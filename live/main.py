# live/main.py
from fastapi import FastAPI, Response
import os, time, sys

app = FastAPI()

# --- heartbeat for /healthz ---
_last_loop_ts = 0

def get_universe_from_env() -> list[str]:
    raw = os.getenv("UNIVERSE", "SPY,QQQ,AAPL,MSFT,NVDA,AMD")
    return [s.strip().upper() for s in raw.split(",") if s.strip()]

# ✅ replace any old screener-based function with this
def get_most_active_symbols() -> list[str]:
    # NOTE: avoid Alpaca Screener (403 on free plans). Use env-provided universe for MVP.
    return get_universe_from_env()

# ---- endpoints ----

@app.get("/readyz")
def readyz():
    return {"ok": True}

@app.get("/healthz")
def healthz():
    return {"ok": "UNIVERSE" in os.environ, "time": time.time()}



# quiet the noisy 404s in logs
@app.post("/guardrail")
def guardrail_hook():
    # accept and ignore
    return Response(status_code=204)

@app.get("/run")
def run_once():
    uni = os.getenv("UNIVERSE", "SPY,QQQ").split(",")
    return {"ok": True, "universe": uni, "ts": time.time()}
