# utility_earnings_tracker.py

import json
import os

STATS_FILE = "data/r5_statistics.json"

def record_trade_result(result):
    """
    Append new trade result to r5_statistics.json
    """
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump([], f)

    with open(STATS_FILE, "r") as f:
        data = json.load(f)

    data.append(result)

    with open(STATS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_session_summary():
    if not os.path.exists(STATS_FILE):
        return {"total_trades": 0, "roi_total": 0}

    with open(STATS_FILE, "r") as f:
        data = json.load(f)

    total_roi = sum(t.get("roi", 0) for t in data)
    return {
        "total_trades": len(data),
        "roi_total": round(total_roi, 2)
    }