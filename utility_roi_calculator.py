# utility_roi_calculator.py

def calculate_roi(entry_price, exit_price, leverage, capital, fees=0.34):
    """
    Calculate ROI for a leveraged trade after fees.
    """
    raw_return = ((exit_price - entry_price) / entry_price) * leverage * 100
    net_return = raw_return - fees
    profit = (net_return / 100) * capital
    return {
        "entry": entry_price,
        "exit": exit_price,
        "leverage": leverage,
        "capital": capital,
        "roi": round(net_return, 2),
        "net_profit": round(profit, 2)
    }