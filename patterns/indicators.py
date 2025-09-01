import pandas as pd
import pandas_ta as ta

def add_basic_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["rsi"] = ta.rsi(out["close"], length=14)
    macd = ta.macd(out["close"], fast=12, slow=26, signal=9)
    out["macd"] = macd["MACD_12_26_9"]
    out["macd_signal"] = macd["MACDs_12_26_9"]
    out["atr"] = ta.atr(out["high"], out["low"], out["close"], length=14)
    return out
