class CommandRegistry:
    def __init__(self):
        self.commands = {
            "/status": self._status,
            "/syncdump": self._syncdump,
            "/retry_last": self._retry_last
        }

    def route(self, cmd, context):
        return self.commands.get(cmd, self._unknown)(context)

    def _status(self, ctx):
        return {
            "type": "status",
            "module": ctx.get("active_module"),
            "capital": ctx.get("capital"),
            "restricted": ctx.get("restricted", [])
        }

    def _syncdump(self, ctx):
        return {
            "type": "sync",
            "heartbeat": ctx.get("heartbeat", {}),
            "last_error": ctx.get("last_error"),
            "fail_trace": ctx.get("fail_trace", [])
        }

    def _retry_last(self, ctx):
        return {
            "type": "retry_request",
            "action": "resend_last_signal"
        }

    def _unknown(self, ctx):
        return {
            "type": "error",
            "message": "Unknown command"
        }