class BalanceTracker:
    def __init__(self, start_balance=10.0, leverage=250, fee_rate=0.0034):
        self.balance = start_balance
        self.start_balance = start_balance
        self.leverage = leverage
        self.fee_rate = fee_rate

    def get_current_balance(self):
        return self.balance

    def calculate_pnl(self, entry, exit, direction):
        position_size = self.balance * self.leverage
        move = (exit - entry) if direction == "long" else (entry - exit)
        raw_profit = position_size * (move / entry)
        fees = abs(position_size * self.fee_rate * 2)
        net = raw_profit - fees
        return net

    def update_balance(self, pnl):
        self.balance += pnl
        if self.balance <= 0:
            print("[BALANCE] Liquidation triggered. Resetting...")
            self.balance = self.start_balance
