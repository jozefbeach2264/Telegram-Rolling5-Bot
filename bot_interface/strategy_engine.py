import requests
import json
import os
import datetime

class Rolling5Strategy:
    def __init__(self, network_url, capital=10.0, leverage=250, fee_percent=0.34):
        self.network_url = network_url
        self.initial_capital = capital
        self.capital = capital
        self.leverage = leverage
        self.fee_percent = fee_percent
        self.liquidation_threshold = 4.00
        self.position = None  # {'entry': float, 'side': 'long'/'short'}
        self.trade_log = []
        self.data_file = "trades.json"
        self._load_existing_log()

    def _load_existing_log(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    self.trade_log = json.load(f)
                    if self.trade_log:
                        self.capital = self.trade_log[-1]["net"]
            except Exception as e:
                print(f"[WARNING] Could not load trade log: {e}")

    def _save_log(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.trade_log, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save trade log: {e}")

    def _is_trade_window_open(self):
        now = datetime.datetime.utcnow()
        est = now - datetime.timedelta(hours=4)  # UTC to EST
        time_str = est.strftime("%H:%M")
        windows = [
            ("02:00", "03:00"),  # Tokyo Apex
            ("06:00", "07:00"),  # London Build-Up
            ("09:30", "11:00"),  # US Open
            ("21:00", "22:00")   # Tokyo Prep
        ]
        return any(start <= time_str <= end for (start, end) in windows)

    def fetch_market_data(self):
        try:
            ob = requests.get(f"{self.network_url}/orderbook").json()
            ob_10s = requests.get(f"{self.network_url}/orderbook10s").json()
            vol = requests.get(f"{self.network_url}/volume_feed").json()
            spoof = requests.get(f"{self.network_url}/spoof_tracker").json()
            return {
                "orderbook": ob,
                "ob_10s": ob_10s,
                "volume": vol,
                "spoof": spoof
            }
        except Exception as e:
            print(f"[ERROR] Failed to fetch market data: {e}")
            return None

    def _analyze_orderbook(self, asks, bids):
        try:
            ask1 = float(asks[0][0])
            bid1 = float(bids[0][0])
            ask2 = float(asks[1][0]) if len(asks) > 1 else ask1
            bid2 = float(bids[1][0]) if len(bids) > 1 else bid1
            wall_gap = ask2 - ask1 if ask2 - ask1 > bid1 - bid2 else bid1 - bid2
            spread = ask1 - bid1
            return {
                "spread": spread,
                "wall_gap": wall_gap,
                "top_ask": ask1,
                "top_bid": bid1
            }
        except:
            return None

    def _conviction_index(self, vol_data):
        bull = vol_data.get("bull_volume", 0)
        bear = vol_data.get("bear_volume", 0)
        total = bull + bear
        if total == 0:
            return 0
        ratio = (bull - bear) / total
        return round(ratio, 3)

    def _spoof_alert(self, spoof_data):
        spoof_ratio = spoof_data.get("ask_spoof", 0) - spoof_data.get("bid_spoof", 0)
        return abs(spoof_ratio) > 0.2  # adjustable

    def decide_trade(self, data):
        if not data or not self._is_trade_window_open():
            return None

        ob = data["orderbook"]
        asks = ob.get("asks", [])
        bids = ob.get("bids", [])
        if not asks or not bids:
            return None

        ob_result = self._analyze_orderbook(asks, bids)
        conviction = self._conviction_index(data["volume"])
        spoof_threat = self._spoof_alert(data["spoof"])

        if not ob_result or spoof_threat or conviction < 0.2:
            return None

        spread = ob_result["spread"]
        wall_gap = ob_result["wall_gap"]
        top_ask = ob_result["top_ask"]

        if spread > 0.4 and wall_gap > 0.6:
            return {
                "side": "long",
                "entry": top_ask
            }
        return None

    def execute_trade(self, signal):
        if not signal:
            return
        entry = signal["entry"]
        fee = (self.capital * self.leverage) * (self.fee_percent / 100)
        self.position = {
            "entry": entry,
            "side": signal["side"],
            "fee": fee
        }
        print(f"[TRADE ENTERED] {signal['side']} at {entry} with fee {fee:.4f}")

    def close_trade(self, exit_price):
        if not self.position:
            return

        entry = self.position["entry"]
        side = self.position["side"]
        fee = self.position["fee"]
        move = (exit_price - entry) if side == "long" else (entry - exit_price)
        profit = move * self.leverage
        net = self.capital + profit - fee

        if abs(move) >= self.liquidation_threshold:
            print("[LIQUIDATED] Resetting capital.")
            self.capital = self.initial_capital
        else:
            self.capital = net

        self.trade_log.append({
            "entry": entry,
            "exit": exit_price,
            "side": side,
            "profit": profit,
            "net": self.capital
        })

        self._save_log()
        print(f"[TRADE CLOSED] Exit: {exit_price}, Profit: {profit:.2f}, Net Capital: {self.capital:.2f}")
        self.position = None

    def run_cycle(self):
        print("[CYCLE] Running bot cycle...")
        data = self.fetch_market_data()
        if not data:
            return

        if self.position:
            asks = data["orderbook"].get("asks", [])
            bids = data["orderbook"].get("bids", [])
            if not asks or not bids:
                return
            mark = (float(asks[0][0]) + float(bids[0][0])) / 2
            self.close_trade(mark)
        else:
            signal = self.decide_trade(data)
            self.execute_trade(signal)