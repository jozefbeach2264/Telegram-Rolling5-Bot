# module_dispatcher.py

import json
import importlib
import os

MODULE_DIR = "modules"
STATS_FILE = "data/r5_statistics.json"

# Command to module mapping
COMMAND_MAP = {
    "/scalpel": "trade_module_scalpel",
    "/trapx": "trade_module_trapx",
    "/defcon6": "trade_module_defcon6",
    "/rawstrike": "trade_module_rawstrike"
}

def load_statistics():
    if not os.path.exists(STATS_FILE):
        return {}
    with open(STATS_FILE, "r") as f:
        return json.load(f)

def record_failure(module_name, reason):
    stats = load_statistics()
    stats["module_failures"][module_name].append(reason)
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def dispatch(command, context):
    if command not in COMMAND_MAP:
        return {"status": "error", "message": "Unknown command"}

    module_name = COMMAND_MAP[command]
    try:
        module = importlib.import_module(f"{MODULE_DIR}.{module_name}")
        result = module.run(context)
        return {"status": "success", "result": result}
    except Exception as e:
        record_failure(module_name.replace("trade_module_", ""), str(e))
        return {"status": "failed", "error": str(e)}