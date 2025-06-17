import asyncio
import websockets

NETWORK_URL = "wss://bac4d511-16b6-482e-8ccc-eb134f27ce6a-00-2fdyzur7p8drl.riker.replit.dev/ws"

async def send_to_network(message: str):
    try:
        async with websockets.connect(NETWORK_URL) as ws:
            await ws.send(message)
            response = await ws.recv()
            print(f"[RESPONSE FROM NETWORK] {response}")
            return response
    except Exception as e:
        print(f"[NETWORK BRIDGE ERROR] {e}")
        return None