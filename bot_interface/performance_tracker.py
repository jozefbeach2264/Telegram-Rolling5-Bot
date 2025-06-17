from .config import STARTING_CAPITAL, LIQUIDATION_THRESHOLD

def update_balance(current, profit):
    new_balance = current + profit
    if new_balance <= LIQUIDATION_THRESHOLD:
        new_balance = STARTING_CAPITAL
    return new_balance

def get_balance(current):
    return current