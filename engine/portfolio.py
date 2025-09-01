class Portfolio:
    def __init__(self, starting_cash: float = 100000.0, max_positions: int = 10):
        self.cash = starting_cash
        self.max_positions = max_positions
        self.positions = []
