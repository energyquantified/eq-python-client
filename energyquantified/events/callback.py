SUBSCRIBE_CURVES = "subscribe_curves"
GET_CURVE_FILTERS = "curve_filters"

CALLBACK_TYPES = (SUBSCRIBE_CURVES, GET_CURVE_FILTERS)

class Callback:
    def __init__(self, callback_type, latest=True):
        assert callback_type in CALLBACK_TYPES, (
            f"callback_type: {callback_type} not in {CALLBACK_TYPES}"
        )
        self.callback_type = callback_type
        self.latest = latest
