"""
The European "Gas Day", as specified by ACER
--------------------------------------------

​​​​​​​​The Gas Day establishes the trading window for exchanging day-ahead
and daily gas products on the EU trading platforms. The Gas Day has
a harmonised start and end from 5.00 to 5.00 UTC the following day
for winter time, and from 4.00 to 4.00 UTC the following day when
daylight saving is applied. The harmonised Gas Day promotes
cross-border trading and underpins capacity bundling.​

Source:
https://documents.acer.europa.eu/en/Gas/Framework%20guidelines_and_network%20codes/Pages/Gas-Day.aspx


How to generate the zone in this file
-------------------------------------

 - Open the CET zonefile
   >>> fp = open('<path-to-python-site-packages>/pytz/zoneinfo/CET', 'rb')

 - Copy and modify the latest build_tzinfo file from pytz:
   https://github.com/stub42/pytz/blob/master/src/pytz/tzfile.py

 - Extract variables "zone", "transitions" and "transition_info".

 - Replace offsets and names.
"""

import datetime

from pytz import _tzinfo_cache
from pytz.tzinfo import DstTzInfo


def _build_europe_gas_day_tzinfo():
    """
    Build the Europe/Gas_Day based on the CET time.

    :raises ValueError: When something is wrong with the CET/CEST definition
    """
    zone = 'Europe/Gas_Day'
    transitions = _get_transitions()
    transition_info_cet = _get_transition_info_cet()

    difference_sec = 3600 * 6
    transition_info_gas_day = []
    for dt1, dt2, name in transition_info_cet:
        sec1 = dt1.seconds - difference_sec
        hours1 = sec1 / (60 * 60)
        gas_dt1 = datetime.timedelta(hours=hours1)
        sec2 = dt2.seconds - difference_sec
        hours2 = sec2 / (60 * 60)
        gas_dt2 = datetime.timedelta(hours=hours2)
        if name == 'CET':
            name = 'CET'
        elif name == 'CEST':
            name = 'CEST'
        else:
            raise ValueError("tz name not CET or CEST")
        transition_info_gas_day.append((gas_dt1, gas_dt2, name))

    gas_day_cls = type('Europe/Gas_Day', (DstTzInfo,), dict(
        zone=zone,
        _utc_transition_times=transitions,
        _transition_info=transition_info_gas_day
    ))

    _tzinfo_cache[zone] = gas_day_cls()
    return _tzinfo_cache[zone]


def _get_transition_info_cet():
    """
    Get all transition info for CET.
    """
    return [
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET'),
        (datetime.timedelta(seconds=7200), datetime.timedelta(seconds=3600),
         'CEST'),
        (datetime.timedelta(seconds=3600), datetime.timedelta(0), 'CET')
    ]


def _get_transitions():
    """
    All transitions for the CET timezone.
    """
    return [
        datetime.datetime(1, 1, 1, 0, 0),
        datetime.datetime(1916, 4, 30, 22, 0),
        datetime.datetime(1916, 9, 30, 23, 0),
        datetime.datetime(1917, 4, 16, 1, 0),
        datetime.datetime(1917, 9, 17, 1, 0),
        datetime.datetime(1918, 4, 15, 1, 0),
        datetime.datetime(1918, 9, 16, 1, 0),
        datetime.datetime(1940, 4, 1, 1, 0),
        datetime.datetime(1942, 11, 2, 1, 0),
        datetime.datetime(1943, 3, 29, 1, 0),
        datetime.datetime(1943, 10, 4, 1, 0),
        datetime.datetime(1944, 4, 3, 1, 0),
        datetime.datetime(1944, 10, 2, 1, 0),
        datetime.datetime(1945, 4, 2, 1, 0),
        datetime.datetime(1945, 9, 16, 1, 0),
        datetime.datetime(1977, 4, 3, 1, 0),
        datetime.datetime(1977, 9, 25, 1, 0),
        datetime.datetime(1978, 4, 2, 1, 0),
        datetime.datetime(1978, 10, 1, 1, 0),
        datetime.datetime(1979, 4, 1, 1, 0),
        datetime.datetime(1979, 9, 30, 1, 0),
        datetime.datetime(1980, 4, 6, 1, 0),
        datetime.datetime(1980, 9, 28, 1, 0),
        datetime.datetime(1981, 3, 29, 1, 0),
        datetime.datetime(1981, 9, 27, 1, 0),
        datetime.datetime(1982, 3, 28, 1, 0),
        datetime.datetime(1982, 9, 26, 1, 0),
        datetime.datetime(1983, 3, 27, 1, 0),
        datetime.datetime(1983, 9, 25, 1, 0),
        datetime.datetime(1984, 3, 25, 1, 0),
        datetime.datetime(1984, 9, 30, 1, 0),
        datetime.datetime(1985, 3, 31, 1, 0),
        datetime.datetime(1985, 9, 29, 1, 0),
        datetime.datetime(1986, 3, 30, 1, 0),
        datetime.datetime(1986, 9, 28, 1, 0),
        datetime.datetime(1987, 3, 29, 1, 0),
        datetime.datetime(1987, 9, 27, 1, 0),
        datetime.datetime(1988, 3, 27, 1, 0),
        datetime.datetime(1988, 9, 25, 1, 0),
        datetime.datetime(1989, 3, 26, 1, 0),
        datetime.datetime(1989, 9, 24, 1, 0),
        datetime.datetime(1990, 3, 25, 1, 0),
        datetime.datetime(1990, 9, 30, 1, 0),
        datetime.datetime(1991, 3, 31, 1, 0),
        datetime.datetime(1991, 9, 29, 1, 0),
        datetime.datetime(1992, 3, 29, 1, 0),
        datetime.datetime(1992, 9, 27, 1, 0),
        datetime.datetime(1993, 3, 28, 1, 0),
        datetime.datetime(1993, 9, 26, 1, 0),
        datetime.datetime(1994, 3, 27, 1, 0),
        datetime.datetime(1994, 9, 25, 1, 0),
        datetime.datetime(1995, 3, 26, 1, 0),
        datetime.datetime(1995, 9, 24, 1, 0),
        datetime.datetime(1996, 3, 31, 1, 0),
        datetime.datetime(1996, 10, 27, 1, 0),
        datetime.datetime(1997, 3, 30, 1, 0),
        datetime.datetime(1997, 10, 26, 1, 0),
        datetime.datetime(1998, 3, 29, 1, 0),
        datetime.datetime(1998, 10, 25, 1, 0),
        datetime.datetime(1999, 3, 28, 1, 0),
        datetime.datetime(1999, 10, 31, 1, 0),
        datetime.datetime(2000, 3, 26, 1, 0),
        datetime.datetime(2000, 10, 29, 1, 0),
        datetime.datetime(2001, 3, 25, 1, 0),
        datetime.datetime(2001, 10, 28, 1, 0),
        datetime.datetime(2002, 3, 31, 1, 0),
        datetime.datetime(2002, 10, 27, 1, 0),
        datetime.datetime(2003, 3, 30, 1, 0),
        datetime.datetime(2003, 10, 26, 1, 0),
        datetime.datetime(2004, 3, 28, 1, 0),
        datetime.datetime(2004, 10, 31, 1, 0),
        datetime.datetime(2005, 3, 27, 1, 0),
        datetime.datetime(2005, 10, 30, 1, 0),
        datetime.datetime(2006, 3, 26, 1, 0),
        datetime.datetime(2006, 10, 29, 1, 0),
        datetime.datetime(2007, 3, 25, 1, 0),
        datetime.datetime(2007, 10, 28, 1, 0),
        datetime.datetime(2008, 3, 30, 1, 0),
        datetime.datetime(2008, 10, 26, 1, 0),
        datetime.datetime(2009, 3, 29, 1, 0),
        datetime.datetime(2009, 10, 25, 1, 0),
        datetime.datetime(2010, 3, 28, 1, 0),
        datetime.datetime(2010, 10, 31, 1, 0),
        datetime.datetime(2011, 3, 27, 1, 0),
        datetime.datetime(2011, 10, 30, 1, 0),
        datetime.datetime(2012, 3, 25, 1, 0),
        datetime.datetime(2012, 10, 28, 1, 0),
        datetime.datetime(2013, 3, 31, 1, 0),
        datetime.datetime(2013, 10, 27, 1, 0),
        datetime.datetime(2014, 3, 30, 1, 0),
        datetime.datetime(2014, 10, 26, 1, 0),
        datetime.datetime(2015, 3, 29, 1, 0),
        datetime.datetime(2015, 10, 25, 1, 0),
        datetime.datetime(2016, 3, 27, 1, 0),
        datetime.datetime(2016, 10, 30, 1, 0),
        datetime.datetime(2017, 3, 26, 1, 0),
        datetime.datetime(2017, 10, 29, 1, 0),
        datetime.datetime(2018, 3, 25, 1, 0),
        datetime.datetime(2018, 10, 28, 1, 0),
        datetime.datetime(2019, 3, 31, 1, 0),
        datetime.datetime(2019, 10, 27, 1, 0),
        datetime.datetime(2020, 3, 29, 1, 0),
        datetime.datetime(2020, 10, 25, 1, 0),
        datetime.datetime(2021, 3, 28, 1, 0),
        datetime.datetime(2021, 10, 31, 1, 0),
        datetime.datetime(2022, 3, 27, 1, 0),
        datetime.datetime(2022, 10, 30, 1, 0),
        datetime.datetime(2023, 3, 26, 1, 0),
        datetime.datetime(2023, 10, 29, 1, 0),
        datetime.datetime(2024, 3, 31, 1, 0),
        datetime.datetime(2024, 10, 27, 1, 0),
        datetime.datetime(2025, 3, 30, 1, 0),
        datetime.datetime(2025, 10, 26, 1, 0),
        datetime.datetime(2026, 3, 29, 1, 0),
        datetime.datetime(2026, 10, 25, 1, 0),
        datetime.datetime(2027, 3, 28, 1, 0),
        datetime.datetime(2027, 10, 31, 1, 0),
        datetime.datetime(2028, 3, 26, 1, 0),
        datetime.datetime(2028, 10, 29, 1, 0),
        datetime.datetime(2029, 3, 25, 1, 0),
        datetime.datetime(2029, 10, 28, 1, 0),
        datetime.datetime(2030, 3, 31, 1, 0),
        datetime.datetime(2030, 10, 27, 1, 0),
        datetime.datetime(2031, 3, 30, 1, 0),
        datetime.datetime(2031, 10, 26, 1, 0),
        datetime.datetime(2032, 3, 28, 1, 0),
        datetime.datetime(2032, 10, 31, 1, 0),
        datetime.datetime(2033, 3, 27, 1, 0),
        datetime.datetime(2033, 10, 30, 1, 0),
        datetime.datetime(2034, 3, 26, 1, 0),
        datetime.datetime(2034, 10, 29, 1, 0),
        datetime.datetime(2035, 3, 25, 1, 0),
        datetime.datetime(2035, 10, 28, 1, 0),
        datetime.datetime(2036, 3, 30, 1, 0),
        datetime.datetime(2036, 10, 26, 1, 0),
        datetime.datetime(2037, 3, 29, 1, 0),
        datetime.datetime(2037, 10, 25, 1, 0)
    ]
