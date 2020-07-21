import urllib
from datetime import date, datetime, time

from requests import exceptions

from ..metadata import Area, Curve, DataType, Aggregation, Filter
from ..time import Frequency

from ..exceptions import (
    ForbiddenError,
    HTTPError,
    InternalServerError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


class BaseAPI:

    def __init__(self, client):
        self._client = client
        self._session = client._session

    def _get(self, url, params=None, ignore403=False, ignore404=False):
        # Perform HTTP request and check for any IO errors
        try:
            response = self._session.get(url, params=params)
        except exceptions.RequestException as e:
            raise HTTPError(e)

        # Check response for common errors
        if response.status_code == 400:
            # Parameters validation error
            json = response.json()
            raise ValidationError(
                reason=json.get("message"),
                parameter=json.get("field")
            )
        if response.status_code == 401:
            # Authentication error
            json = response.json()
            raise UnauthorizedError(reason=json.get("message"))
        if response.status_code == 403 and not ignore403:
            # Forbidden error
            json = response.json()
            raise ForbiddenError(reason=json.get("message"))
        if response.status_code == 404 and not ignore404:
            # Not found
            json = response.json()
            raise NotFoundError(reason=json.get("message"))
        if 500 <= response.status_code < 600:
            # Some internal server error
            raise InternalServerError()

        # Most likely OK at this point
        return response

    def _post(self, url, params, body):
        raise NotImplementedError

    @staticmethod
    def _urlencode_curve_name(curve, curve_types=None):
        if curve is None:
            raise ValidationError(
                reason="Provide a Curve or a curve name",
                parameter="curve"
            )
        curve_name = None
        if isinstance(curve, str):
            curve_name = curve
        elif isinstance(curve, Curve):
            if curve_types and curve.curve_type not in curve_types:
                raise ValidationError(
                    reason=(
                        f"Curve.curve_type must be any of {curve_types}, "
                        f"but was {curve.curve_type}"
                    ),
                    parameter="curve"
                )
            curve_name = curve.name
        else:
            raise ValidationError(
                reason="Provide either a string or a Curve instance",
                parameter="curve"
            )
        return urllib.parse.quote(curve_name)

    @staticmethod
    def _urlencode_datetime(datetime_obj, name):
        if datetime_obj is None:
            raise ValidationError(
                reason="Provide a date or datetime",
                parameter=name
            )
        date_string = None
        # Check for different types. IMPORTANT:
        # The isinstance(datetime) check must come before isinstance(date),
        # as a datetime is also an instance of date...
        if isinstance(datetime_obj, str):
            date_string = datetime_obj
        elif isinstance(datetime_obj, datetime):
            date_string = datetime_obj.isoformat(sep=" ")
        elif isinstance(datetime_obj, date):
            date_string = datetime_obj.isoformat()
        else:
            raise ValidationError(reason="Provide a datetime", parameter=name)
        return urllib.parse.quote(date_string)

    @staticmethod
    def _urlencode_string(text, name, transform_func=None):
        if text is None or not isinstance(text, str):
            raise ValidationError(
                reason="Provide a string",
                parameter=name
            )
        if transform_func:
            text = transform_func(text)
        return urllib.parse.quote(text)

    @staticmethod
    def _add_datetime(params, name, var, required=False):
        if var is None and not required:
            return
        if isinstance(var, str):
            params[name] = var
        elif isinstance(var, (date, datetime)):
            params[name] = var
        else:
            raise ValidationError(reason="Provide a datetime", parameter=name)

    @staticmethod
    def _add_date(params, name, var, required=False):
        if var is None and not required:
            return
        if isinstance(var, str):
            params[name] = var
        elif isinstance(var, date):
            params[name] = var
        else:
            raise ValidationError(reason="Provide a date", parameter=name)

    @staticmethod
    def _add_time(params, name, var, required=False):
        if var is None and not required:
            return
        if isinstance(var, str):
            params[name] = var
        elif isinstance(var, time):
            params[name] = var.isoformat(timespec='milliseconds')
        else:
            raise ValidationError(reason="Provide a time", parameter=name)

    @staticmethod
    def _add_str(params, name, var, allowed_values=None, required=False):
        if var is None and not required:
            return
        if isinstance(var, str):
            if allowed_values and not var in allowed_values:
                raise ValidationError(
                    reason=f"Allowed values are {allowed_values}",
                    parameter=name
                )
            params[name] = var
        else:
            raise ValidationError(reason="Provide a string", parameter=name)

    @staticmethod
    def _add_str_list(params, name, var, required=False):
        if (var is None or var == []) and not required:
            return
        if isinstance(var, str):
            params[name] = [var]
        elif isinstance(var, (list, tuple)):
            for element in var:
                if not isinstance(element, str):
                    raise ValidationError(
                        reason=(
                            f"All element in list must be "
                            f"strings, but found: {type(element)}"
                        ),
                        parameter=name
                    )
            params[name] = list(var)
        else:
            raise ValidationError(
                reason="Provide a string or a list of strings",
                parameter=name
            )

    @staticmethod
    def _add_int(params, name, var, required=False, min=None, max=None):
        if var is None and not required:
            return
        if isinstance(var, int):
            if min is not None and var < min:
                raise ValidationError(
                    reason=f"Must be higher than {min}, was {var}",
                    parameter=name
                )
            if max is not None and var > max:
                raise ValidationError(
                    reason=f"Must be lower than {max}, was {var}",
                    parameter=name
                )
            params[name] = var
        else:
            raise ValidationError(reason="Provide an integer", parameter=name)

    @staticmethod
    def _add_bool(params, name, var, required=False):
        if var is None and not required:
            return
        if isinstance(var, bool):
            params[name] = 'true' if var else 'false'
        else:
            raise ValidationError(
                reason="Provide a boolean (True or False)",
                parameter=name
            )

    @staticmethod
    def _add_area(params, name, var, required=False):
        if var is None and not required:
            return
        if isinstance(var, str):
            if not Area.is_valid_tag(var):
                raise ValidationError(
                    reason=f"Not a valid Area: '{var}'",
                    parameter=name
                )
            params[name] = var
        elif isinstance(var, Area):
            params[name] = var.tag
        else:
            raise ValidationError(
                reason=f"Not a valid Area: '{var}'",
                parameter=name
            )

    @staticmethod
    def _add_data_type(params, name, var, required=False):
        if var is None and not required:
            return
        if isinstance(var, str):
            if not DataType.is_valid_tag(var):
                raise ValidationError(
                    reason=f"Not a valid DataType: '{var}'",
                    parameter=name
                )
            params[name] = var
        elif isinstance(var, DataType):
            params[name] = var.tag
        else:
            raise ValidationError(
                reason=f"Not a valid DataType: '{var}'",
                parameter=name
            )

    @staticmethod
    def _add_frequency(params, name, var, required=False):
        if var is None and not required:
            return
        if isinstance(var, str):
            if not Frequency.is_valid_tag(var):
                raise ValidationError(
                    reason=f"Not a valid Frequency: '{var}'",
                    parameter=name
                )
            params[name] = var
        elif isinstance(var, Frequency):
            params[name] = var.tag
        else:
            raise ValidationError(
                reason=f"Not a valid Frequency: '{var}'",
                parameter=name
            )

    @staticmethod
    def _add_aggregation(params, name, var, required=False):
        if var is None and not required:
            return
        if isinstance(var, str):
            if not Aggregation.is_valid_tag(var):
                raise ValidationError(
                    reason=f"Not a valid Aggregation: '{var}'",
                    parameter=name
                )
            params[name] = var
        elif isinstance(var, Aggregation):
            params[name] = var.tag
        else:
            raise ValidationError(
                reason=f"Not a valid Aggregation: '{var}'",
                parameter=name
            )

    @staticmethod
    def _add_filter(params, name, var, required=False):
        if var is None and not required:
            return
        if isinstance(var, str):
            if not Filter.is_valid_tag(var):
                raise ValidationError(
                    reason=f"Not a valid Filter: '{var}'",
                    parameter=name
                )
            params[name] = var
        elif isinstance(var, Filter):
            params[name] = var.tag
        else:
            raise ValidationError(
                reason=f"Not a valid Filter: '{var}'",
                parameter=name
            )
