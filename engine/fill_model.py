from dataclasses import dataclass

@dataclass
class LiquidityGates:
    max_spread_pct: float = 0.05
    min_oi: int = 100
    min_volume: int = 20

def price_with_slippage(mid: float, spread: float, side: str, slip_frac_of_half=0.3) -> float:
    half = spread / 2.0
    slip = slip_frac_of_half * half
    return mid + slip if side == "buy" else mid - slip
