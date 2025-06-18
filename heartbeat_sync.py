import time
import threading

class HeartbeatSync:
    def __init__(self, pulse_interval=15):
        self.pulse_interval = pulse_interval
        self.last_heartbeat = time.time()
        self.latency_log = []
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._pulse_loop, daemon=True).start()

    def _pulse_loop(self):
        while self.running:
            now = time.time()
            delta = now - self.last_heartbeat
            self.latency_log.append(round(delta, 4))
            if len(self.latency_log) > 20:
                self.latency_log.pop(0)
            self.last_heartbeat = now
            time.sleep(self.pulse_interval)

    def get_status(self):
        return {
            "last_ping": round(time.time() - self.last_heartbeat, 4),
            "average_ping": round(sum(self.latency_log) / len(self.latency_log), 4) if self.latency_log else 0.0
        }

    def stop(self):
        self.running = False