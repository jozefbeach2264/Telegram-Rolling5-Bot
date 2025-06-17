import asyncio
from .decision_engine import analyze_market
from .trade_executor import execute_trade

async def main_bot_loop():
    while True:
        signal = await analyze_market()
        result = execute_trade(signal)
        print("[BOT EXECUTION RESULT]", result)
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main_bot_loop())