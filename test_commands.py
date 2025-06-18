from module_dispatcher import dispatch

def handle_message(message):
    command = message.get("text", "").strip().lower()
    context = {
        "user": message.get("from"),
        "timestamp": message.get("date"),
        "chat_id": message.get("chat", {}).get("id"),
        "meta": message
    }
    response = dispatch(command, context)
    return response

test_messages = [
    {"text": "/scalpel", "from": "userA", "date": "2025-06-18T18:00:00Z", "chat": {"id": 123}},
    {"text": "/trapx", "from": "userB", "date": "2025-06-18T18:01:00Z", "chat": {"id": 124}},
    {"text": "/defcon6", "from": "userC", "date": "2025-06-18T18:02:00Z", "chat": {"id": 125}},
    {"text": "/rawstrike", "from": "userD", "date": "2025-06-18T18:03:00Z", "chat": {"id": 126}},
]

for msg in test_messages:
    result = handle_message(msg)
    print(f"Command: {msg['text']} → Result: {result}")