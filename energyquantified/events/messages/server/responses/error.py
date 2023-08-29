from .base_response import ServerResponse

class ServerResponseError(ServerResponse):

    @staticmethod
    def from_message(json):
        response_obj = ServerResponseError()
        response_obj._parse_message(json)

    def _set_data(self, _):
        raise ValueError(f"Data should not be set for message with type error")