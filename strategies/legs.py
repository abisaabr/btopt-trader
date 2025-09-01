from dataclasses import dataclass
from typing import Literal

OptionType = Literal["call","put"]
Side = Literal["long","short"]

@dataclass
class Leg:
    opt_type: OptionType
    side: Side
    strike_rule: dict     # {"type":"delta","value":0.30} / {"type":"pct_otm","value":4}
    dte_rule: list[int]   # [20,30]
    qty: int = 1
