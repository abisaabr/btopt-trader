from dataclasses import dataclass

@dataclass
class TradeStats:
    pnl: float
    win: bool
    ret_on_risk: float
    mae: float
    mfe: float
    fees: float
    slippage: float
