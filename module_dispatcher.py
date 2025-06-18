import time

class ModuleDispatcher:
    def __init__(self):
        self.module_failures = {}
        self.last_dispatch = {}

    def record_failure(self, module_name):
        now = time.time()
        self.module_failures.setdefault(module_name, []).append(now)
        # Keep only last 60 minutes
        self.module_failures[module_name] = [
            t for t in self.module_failures[module_name] if now - t < 3600
        ]

    def needs_rotation(self, module_name):
        fails = self.module_failures.get(module_name, [])
        return len(fails) >= 2

    def dispatch(self, module_name, module_obj, signal):
        self.last_dispatch[module_name] = time.time()
        if self.needs_rotation(module_name):
            return {
                "fallback": "rawstrike",
                "reason": "Module unstable, fallback injected"
            }
        try:
            result = module_obj.evaluate(signal)
            return result
        except Exception as e:
            self.record_failure(module_name)
            return {
                "fallback": "rawstrike",
                "error": str(e)
            }