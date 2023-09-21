class WebSocketsError(Exception):

    def __init__(
            self,
            message,
            status_code=None,
            status=None,
            description=None,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.message = message
        self.status_code = status_code or ""
        self.status = status or ""
        self.description = description or ""

    def __str__(self):
        return (
            f"{self.message} "
            f"{self.status_code} "
            f"{self.status} "
            f"{self.description}"
        )