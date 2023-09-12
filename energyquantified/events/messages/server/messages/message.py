from energyquantified.events.messages.server.base import _BaseServerMessage

class ServerMessageMessage(_BaseServerMessage):
    MESSAGE_KEY = "message"

    def __init__(self, message):
        self.message = message

    @staticmethod
    def from_message(json):
        msg = json.get(ServerMessageMessage.MESSAGE_KEY)
        if msg is None:
            raise ValueError(
                f"Failed to parse StreamMessageMessage because "
                f"field '{ServerMessageMessage.MESSAGE_KEY}' is missing"
            )
        return ServerMessageMessage(msg)
