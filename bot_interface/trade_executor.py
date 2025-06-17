from .config import SIMULATION_MODE, STARTING_CAPITAL, TAKER_FEE, LEVERAGE
from .performance_tracker import update_balance, get_balance

capital = STARTING_CAPITAL

def execute_trade(signal):
    if not signal or not signal.get("direction"):
        return "No trade executed"

    global capital
    fee_rate = TAKER_FEE
    direction = signal["direction"]
    entry_price = 2500  # Simulated entry
    exit_price = 2525 if direction == "long" else 2475  # Simulated exit

    move = abs(exit_price - entry_price)
    roi = (move / entry_price) * LEVERAGE
    fee_cost = capital * fee_rate * 2
    profit = (capital * roi) - fee_cost
    capital = update_balance(capital, profit)

    return {
        "entry": entry_price,
        "exit": exit_price,
        "roi": roi,
        "fees": fee_cost,
        "profit": profit,
        "new_balance": capital
    }