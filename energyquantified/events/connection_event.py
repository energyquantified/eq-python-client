from dataclasses import dataclass
from typing import Optional
from enum import Enum

NETWORK_ERROR = "NETWORK ERROR"
# 1000
CLOSE_NORMAL = "CLOSE_NORMAL"
CLOSE_GOING_AWAY = "CLOSE_GOING_AWAY"
CLOSE_PROTOCOL_ERROR = "CLOSE_PROTOCOL_ERROR"
CLOSE_UNSUPPORTED = "CLOSE_UNSUPPORTED"
CLOSED_NO_STATUS = "CLOSED_NO_STATUS"
CLOSE_ABNORMAL = "CLOSE_ABNORMAL"
UNSUPPORTED_PAYLOAD = "UNSUPPORTED_PAYLOAD"
POLICY_VIOLATION = "POLICY_VIOLATION"
CLOSE_TOO_LARGE = "CLOSE_TOO_LARGE"
MANDATORY_EXTENSION = "MANDATORY_EXTENSION"
SERVER_ERROR = "SERVER_ERROR"
SERVICE_RESTART = "SERVICE_RESTART"
TRY_AGAIN_LATER = "TRY_AGAIN_LATER"
BAD_GATEWAY = "BAD_GATEWAY"
TLS_HANDSHAKE_FAIL = "TLS_HANDSHAKE_FAIL"
# 100
CONNECTION_REFUSED = "CONNECTION_REFUSED"
# 400 errors
BAD_REQUEST = "BAD_REQUEST"
UNAUTHORIZED = "UNAUTHORIZED"
FORBIDDEN = "FORBIDDEN"
NOT_FOUND = "NOT_FOUND"
METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
NOT_ACCEPTABLE = "NOT_ACCEPTABLE"
PROXY_AUTHENTICATION_REQUIRED = "PROXY_AUTHENTICATION_REQUIRED"
REQUEST_TIMEOUT = "REQUEST_TIMEOUT"
CONFLICT = "CONFLICT"
GONE = "GONE"
LENGTH_REQUIRED = "LENGTH_REQUIRED"
PRECONDITION_FAILED = "PRECONDITION_FAILED"
PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
URI_TOO_LONG = "URI_TOO_LONG"
UNSUPPORTED_MEDIA_TYPE = "UNSUPPORTED_MEDIA_TYPE"
RANGE_NOT_SATISFIABLE = "RANGE_NOT_SATISFIABLE"
EXPECTATION_FAILED = "EXPECTATION_FAILED"
MISDIRECTION_REQUEST = "MISDIRECTION_REQUEST"
UNPROCESSABLE_ENTITY = "UNPROCESSABLE_ENTITY"
LOCKED = "LOCKED"
FAILED_DEPENDENCY = "FAILED_DEPENDENCY"
TOO_EARLY = "TOO_EARLY"
UPGRADE_REQUIRED = "UPGRADE_REQUIRED"
PRECONDITION_REQUIRED = "PRECONDITION_REQUIRED"
TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
REQUEST_HEADER_FIELD_TOO_LARGE = "REQUEST_HEADER_FIELD_TOO_LARGE"
UNAVAILABLE_FOR_LEGAL_REASONS = "UNAVAILABLE_FOR_LEGAL_REASONS"
# 500 errors
INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
GATEWAY_TIMEOUT = "GATEWAY_TIMEOUT"
HTTP_VERSION_NOT_SUPPORTED = "HTTP_VERSION_NOT_SUPPORTED"
VARIANT_ALSO_NEGOTIATES = "VARIANT_ALSO_NEGOTIATES"
INSUFFICIENT_STORAGE = "INSUFFICIENT_STORAGE"
LOOP_DETECTED = "LOPP_DETECTED"
NOT_EXTENDED = "NOT_EXTENDED"
NETWORK_AUTHENTICATION_REQUIRED = "NETWORK_AUTHENTICATION_REQUIRED"
# Undefined
TIMEOUT = "TIMEOUT"
CONNECTION_ERROR = "CONNECTION_ERROR"
UNKNOWN_ERROR = "UNKNOWN_ERROR"

CONNECTION_ERROR_LOOKUP = {
    #: NETWORK_ERROR,
    # WebSocket close codes
    1000: CLOSE_NORMAL,
    1001: CLOSE_GOING_AWAY,
    1002: CLOSE_PROTOCOL_ERROR,
    1003: CLOSE_UNSUPPORTED,
    1005: CLOSED_NO_STATUS,
    1006: CLOSE_ABNORMAL,
    1007: UNSUPPORTED_PAYLOAD,
    1008: POLICY_VIOLATION,
    1009: CLOSE_TOO_LARGE,
    1010: MANDATORY_EXTENSION,
    1011: SERVER_ERROR,
    1012: SERVICE_RESTART,
    1013: TRY_AGAIN_LATER,
    1014: BAD_GATEWAY,
    1015: TLS_HANDSHAKE_FAIL,
    #111: CONNECTION_REFUSED,
    # Http status codes
    400: BAD_REQUEST,
    401: UNAUTHORIZED,
    403: FORBIDDEN,
    404: NOT_FOUND,
    405: METHOD_NOT_ALLOWED,
    406: NOT_ACCEPTABLE,
    407: PROXY_AUTHENTICATION_REQUIRED,
    408: REQUEST_TIMEOUT,
    409: CONFLICT,
    410: GONE,
    411: LENGTH_REQUIRED,
    412: PRECONDITION_FAILED,
    413: PAYLOAD_TOO_LARGE,
    414: URI_TOO_LONG,
    415: UNSUPPORTED_MEDIA_TYPE,
    416: RANGE_NOT_SATISFIABLE,
    417: EXPECTATION_FAILED,
    421: MISDIRECTION_REQUEST,
    422: UNPROCESSABLE_ENTITY,
    423: LOCKED,
    424: FAILED_DEPENDENCY,
    425: TOO_EARLY,
    426: UPGRADE_REQUIRED,
    428: PRECONDITION_REQUIRED,
    429: TOO_MANY_REQUESTS,
    431: REQUEST_HEADER_FIELD_TOO_LARGE,
    451: UNAVAILABLE_FOR_LEGAL_REASONS,
    500: INTERNAL_SERVER_ERROR,
    501: NOT_IMPLEMENTED,
    502: BAD_GATEWAY,
    503: SERVICE_UNAVAILABLE,
    504: GATEWAY_TIMEOUT,
    505: HTTP_VERSION_NOT_SUPPORTED,
    506: VARIANT_ALSO_NEGOTIATES,
    507: INSUFFICIENT_STORAGE,
    508: LOOP_DETECTED,
    510: NOT_EXTENDED,
    511: NETWORK_AUTHENTICATION_REQUIRED,
}

class ConnectionEvent:

    def __init__(self, status=None, status_code=None, message=None):
        if status is None:
            if status_code is not None:
                status = CONNECTION_ERROR_LOOKUP.get(status_code, CONNECTION_ERROR)
        self.status = status
        self.status_code = status_code
        self.message = message

    def __str__(self):
        """
        Represent this object as a string.

        :return: String representation of this object
        :rtype: str
        """
        return (f"<ConnectionEvent: "
                f"status={self.status}, "
                f"status_code={self.status_code}, "
                f"message={self.message}>")

    def __repr__(self):
        return str(self)
