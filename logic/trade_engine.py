import json

class TradeEngine:
    def __init__(self, balance_tracker):
        self.balance_tracker = balance_tracker

    async def handle_signal(self, msg):
        try:
            signal = json.loads(msg)
            direction = signal.get("direction")
            entry_price = float(signal.get("entry"))
            exit_price = float(signal.get("exit"))

            if direction not in ("long", "short"):
                print("[ENGINE] Invalid direction")
                return

            self.execute_trade(entry_price, exit_price, direction)

        except Exception as e:
            print(f"[ENGINE ERROR] {e}")

    def execute_trade(self, entry, exit, direction):
        capital_used = self.balance_tracker.get_current_balance()
        pnl = self.balance_tracker.calculate_pnl(entry, exit, direction)
        self.balance_tracker.update_balance(pnl)
        print(f"[TRADE] {direction.upper()} | Entry: {entry} Exit: {exit} | New Balance: ${self.balance_tracker.get_current_balance():.2f}")
