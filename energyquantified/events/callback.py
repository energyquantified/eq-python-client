SUBSCRIBE_CURVES = "subscribe_curves"

CALLBACK_TYPES = (SUBSCRIBE_CURVES)

class Callback:
    def __init__(self, callback, callback_type, latest=True):
        self.callback = callback
        assert callback_type in CALLBACK_TYPES, (
            f"callback_type: {callback_type} not in {CALLBACK_TYPES}"
        )
        self.callback_type = callback_type
        self.latest = latest