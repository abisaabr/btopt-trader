from typing import Literal

def build_context_key(
    symbol: str,
    timeframe: str,
    candle: str,
    macd_sign: Literal["pos","neg","flat"],
    rsi_state: Literal["overbought","oversold","neutral"],
    trend: Literal["up","down","flat"],
    vol_regime: Literal["low","mid","high"],
) -> str:
    return "|".join([symbol, timeframe, candle, macd_sign, rsi_state, trend, vol_regime])
