import websockets
import json

NETWORK_URL = "https://replit.com/@jozefbeach2264/NeuroSync?s=app"

async def send_to_network(message: str):
    try:
        async with websockets.connect(NETWORK_URL) as ws:
            await ws.send(message)
            response = await ws.recv()

            try:
                data = json.loads(response)
                print(f"[RESPONSE FROM NETWORK] {data}")
                return data
            except json.JSONDecodeError:
                print(f"[NETWORK BRIDGE ERROR] Invalid JSON: {response}")
                return None

    except Exception as e:
        print(f"[NETWORK BRIDGE ERROR] {e}")
        return None