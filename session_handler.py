import json
import os

class SessionHandler:
    def __init__(self, session_path="session_store.json", capital=10.0):
        self.session_path = session_path
        self.capital = capital
        self.session = {"active_module": None, "capital": capital}
        self._load()

    def _load(self):
        if os.path.exists(self.session_path):
            try:
                with open(self.session_path, "r") as f:
                    self.session = json.load(f)
            except Exception:
                pass

    def _save(self):
        with open(self.session_path, "w") as f:
            json.dump(self.session, f, indent=2)

    def update_capital(self, new_amount):
        self.session["capital"] = new_amount
        self._save()

    def restrict_modules(self):
        cap = self.session.get("capital", 0)
        restricted = []
        if cap < 10:
            restricted = ["scalpel", "defcon6"]
        return restricted

    def set_module(self, name):
        self.session["active_module"] = name
        self._save()

    def get_status(self):
        return self.session