import time
import signal
import sys
from bot_interface.strategy_engine import Rolling5Strategy

NETWORK_URL = "https://bac4d511-16b6-482e-8ccc-eb134f27ce6a-00-2fdyzur7p8drl.riker.replit.dev"

bot = Rolling5Strategy(network_url=NETWORK_URL)
running = True

def handle_shutdown(signum, frame):
    global running
    print("\n[SHUTDOWN] Interrupt received, stopping bot loop...")
    running = False

# Bind shutdown signals
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

def run_bot():
    print("[BOT] Rolling5 Strategy Bot Starting...")
    while running:
        try:
            bot.run_cycle()
            time.sleep(2.5)
        except Exception as e:
            print(f"[BOT ERROR] {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
