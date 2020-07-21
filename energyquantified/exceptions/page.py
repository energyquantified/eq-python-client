
class PageError(Exception):
    """
    A page error.
    """

    def __init__(self, reason=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason = reason or ""

    def __str__(self):
        return self.reason