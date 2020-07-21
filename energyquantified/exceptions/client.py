
class InitializationError(Exception):
    """
    Initialization error for the Energy Quantified Python client.
    """

    def __init__(self, reason=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason = reason or ""

    def __str__(self):
        return self.reason