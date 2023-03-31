from dataclasses import dataclass
from typing import Optional
from enum import Enum

# CLOSE_NORMAL = "CLOSE NORMAL"
# CLOSE_GOING_AWAY = "CLOSE_GOING_AWAY"
# CLOSE_PROTOCOL_ERROR = "CLOSE_PROTOCOL_ERROR"
# CLOSE_UNSUPPORTED = "CLOSE_UNSUPPORTED"
# NETWORK_ERROR = "NETWORK ERROR"
# WS_ERRORS = {
#     1000: CLOSE_NORMAL,
#     1001: ,
#     1002: ,
#     1003: ,
#     1004: ,
#     1005: ,
#     1006: ,
#     1007: ,
#     1009: ,
#     1010: ,
#     1011: ,
#     1015: ,
# }

_ws_status_lookup = {}
class WebSocketError(Enum):

    CLOSE_NORMAL = (1000, "CLOSE_NORMAL")
    CLOSE_GOING_AWAY = (1001, "CLOSE_GOING_AWAY")
    CLOSE_PROTOCOL_ERROR = (1002, "CLOSE_PROTOCOL_ERROR")
    CLOSE_UNSUPPORTED = (1003, "CLOSE_UNSUPPORTED")
    #_ = (1004, "")
    CLOSED_NO_STATUS = (1005, "CLOSED_NO_STATUS")
    CLOSE_ABNORMAL = (1006, "CLOSE_ABNORMAL")
    UNSUPPORTED_PAYLOAD = (1007, "UNSUPPORTED_PAYLOAD")
    POLICY_VIOLATION = (1008, "POLICY_VIOLATION")
    CLOSE_TOO_LARGE = (1009, "CLOSE_TOO_LARGE")
    MANDATORY_EXTENSION = (1010, "MANDATORY_EXTENSION")
    SERVER_ERROR = (1011, "SERVER_ERROR")
    SERVICE_RESTART = (1012, "SERVICE_RESTART")
    TRY_AGAIN_LATER = (1013, "TRY_AGAIN_LATER")
    BAD_GATEWAY = (1014, "BAD_GATEWAY")
    TLS_HANDSHAKE_FAIL = (1015, "TLS_HANDSHAKE_FAIL")

    def __init__(self, status_code, status):
        self.status_code = status_code
        self.status = status
        _ws_status_lookup[status_code] = self

    @staticmethod
    def is_valid_code(code):
        return code in _ws_status_lookup

    @staticmethod
    def by_code(code):
        return _ws_status_lookup[code]


class ConnectionEvent:
    def __init__(self, status_code, message):
        if WebSocketError.is_valid_code(status_code):
            self.status = WebSocketError.by_code(status_code).status
        else:
            self.status = "NETWORK_ERROR?"
        self.ws_status_code = status_code
        self.message = message

# @dataclass(frozen=True)
# class ConnectionEvent:
#     status: str
#     message: Optional[str] = None
#     ws_status_code: Optional[int] = None