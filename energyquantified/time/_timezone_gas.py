from datetime import datetime

from pytz.tzinfo import DstTzInfo, memorized_datetime, memorized_timedelta


# TODO The Europe/Gas_Day time-zone is not implemented.


GAS_DAY = type('Europe/Gas_Day', (DstTzInfo,), dict(
    zone='Europe/Gas_Day',
    _utc_transition_times=[
        datetime.min,
    ],
    _transition_info=None
))
