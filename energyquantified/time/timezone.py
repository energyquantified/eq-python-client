import pytz
import tzlocal

from ._timezone_gas import _build_europe_gas_day_tzinfo

# Look up the most used timezones in the European power markets
# from the pytz library

UTC = pytz.UTC
CET = pytz.timezone("CET")
WET = pytz.timezone("WET")
EET = pytz.timezone("EET")
TRT = pytz.timezone("Europe/Istanbul")
GAS_DAY = _build_europe_gas_day_tzinfo()


def local_tz():
    """
    Get the local timezone.

    :return: The timezone for this system.
    :rtype: TzInfo
    """
    return tzlocal.get_localzone()


def _is_valid_timezone(tz):
    """
    Check if a timezone is a valid timezone.

    :param tz: Timezone to check
    :type tz: str, pytz.tzinfo.BaseTzInfo, required
    :return: True if tz is a valid timezone, else False
    :rtype: bool
    """
    if tz is None:
        return False
    if isinstance(tz, str):
        try:
            tz = pytz.timezone(tz)
        except pytz.exceptions.UnknownTimeZoneError:
            return False
    if isinstance(tz, pytz.tzinfo.BaseTzInfo):
        return tz in (UTC, CET, WET, EET, TRT, GAS_DAY)
    return False


# Default timezone

DEFAULT_TZ = CET
LOCAL_TZ = local_tz()
