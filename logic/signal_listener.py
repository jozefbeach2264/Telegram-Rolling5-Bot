import asyncio
import websockets
import json

class SignalListener:
    def __init__(self, engine):
        self.engine = engine
        self.ws_url = "wss://<neurosync-url>.replit.dev/ws"

    async def listen(self):
        print("[LISTENER] Connecting to core signal network...")
        try:
            async with websockets.connect(self.ws_url) as ws:
                while True:
                    msg = await ws.recv()
                    print(f"[LISTENER] Signal received: {msg}")
                    await self.engine.handle_signal(msg)
        except Exception as e:
            print(f"[LISTENER ERROR] {e}")
