import pytz
import tzlocal


# Look up the most used time zones in the European power markets
# from the pytz library

UTC = pytz.UTC
CET = pytz.timezone("CET")
WET = pytz.timezone("WET")
EET = pytz.timezone("EET")
TRT = pytz.timezone("Europe/Istanbul")


def local_tz():
    """
    Get the local time-zone.

    :return: The time-zone for this system.
    :rtype: TzInfo
    """
    return tzlocal.get_localzone()


# Default time zone

DEFAULT_TZ = CET
LOCAL_TZ = local_tz()
