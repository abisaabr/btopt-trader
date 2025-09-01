import pandas as pd

def is_bullish_engulfing(df: pd.DataFrame) -> pd.Series:
    open_, close = df["open"], df["close"]
    prev_open, prev_close = open_.shift(1), close.shift(1)
    return (close > open_) & (prev_close < prev_open) & (close >= prev_open) & (open_ <= prev_close)

def is_hammer(df: pd.DataFrame, body_thresh=0.3, lower_wick_mult=2.0) -> pd.Series:
    high, low, open_, close = df["high"], df["low"], df["open"], df["close"]
    body = (close - open_).abs()
    range_ = (high - low).replace(0, 1e-9)
    lower_wick = (open_.where(close >= open_, close) - low).abs()
    return (body / range_ < body_thresh) & (lower_wick > lower_wick_mult * body)
