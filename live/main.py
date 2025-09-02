from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/readyz")
def readyz():
    """Readiness probe endpoint."""
    return {"status": "ready"}

@app.get("/healthz")
def healthz():
    """Liveness probe endpoint."""
    return {"status": "healthy"}

async def trading_loop():
    """A background task that simulates trading logic."""
    while True:
        # TODO: replace this stub with real market data fetch and strategy execution
        print("Simulating a trading iteration...")
        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    """Start the trading loop when the app starts."""
    asyncio.create_task(trading_loop())
