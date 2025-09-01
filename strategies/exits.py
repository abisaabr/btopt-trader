from dataclasses import dataclass

@dataclass
class ExitRules:
    profit_target_pct: float
    max_loss_mult_credit: float
    time_stop_days_before_expiry: int
