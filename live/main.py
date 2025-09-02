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
    # readiness should NOT hit external APIs
    return {"ok": True}

@app.get("/healthz")
def healthz():
    # healthy if the loop (or /run) executed recently
    return {"ok": (time.time() - _last_loop_ts) < 600}

# quiet the noisy 404s in logs
@app.post("/guardrail")
def guardrail_hook():
    # accept and ignore
    return Response(status_code=204)

@app.get("/run")
def run_once():
    """
    Minimal 'do a loop' endpoint.
    For now it just reads the universe from env to prove the app is healthy.
    Wire your trading logic here later.
    """
    global _last_loop_ts
    symbols = get_most_active_symbols()
    # TODO: call your indicator calc + order logic here (no external Screener calls)
    _last_loop_ts = time.time()
    return {"ok": True, "universe": symbols, "ts": _last_loop_ts}
