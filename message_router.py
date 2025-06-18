from module_dispatcher import dispatch

def handle_message(message):
    """
    Routes Telegram messages to the appropriate strategy module.
    """
    command = message.get("text", "").strip().lower()
    context = {
        "user": message.get("from"),
        "timestamp": message.get("date"),
        "chat_id": message.get("chat", {}).get("id"),
        "meta": message
    }

    response = dispatch(command, context)
    return response