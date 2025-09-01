class Rails:
    def __init__(self, max_daily_dd_pct=2.0, max_positions=10):
        self.max_daily_dd_pct = max_daily_dd_pct
        self.max_positions = max_positions
    def ok_to_trade(self, portfolio, vix=None):
        return True
