

class ParseException(Exception):
    """
    Failed to parse an API response.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
