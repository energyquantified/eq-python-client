from energyquantified.metadata import CurveType
from . import EventType


class CurveUpdateEvent:
    def __init__(
        self,
        event_id,
        curve,
        event_type,
        begin = None,
        end = None,
        instance = None,
        num_values = None,
    ):
        self.event_id = event_id
        self.curve = curve
        self.event_type = event_type
        self.begin = begin
        self.end = end
        self.instance = instance
        self.num_values = num_values
    
    def __str__(self):
        begin_str = self.begin.isoformat(sep=" ") if self.begin is not None else None
        end_str = self.end.isoformat(sep=" ") if self.end is not None else None
        return (
            f"<CurveUpdateEvent: "
            f"event_id={self.event_id}, "
            f"curve={self.curve}, "
            f"event_type={self.event_type}, "
            f"begin={begin_str}, "
            f"end={end_str}, "
            f"instance={self.instance}, "
            f"num_values:{self.num_values}"
            f">"
        )

    def __repr__(self):
        return self.__str__()

    def load_data(self, eq):
        """
        Load data in the range described by the event. Returns 'None' if the
        event type is either ``EventType.TRUNCATE`` or ``EventType.DELETE``.

        :param eq: Instance of the api client
        :type eq: :py:class:`energyquantified.EnergyQuantified`
        :return: The range of data the event describes
        :rtype: :py:class:`energyquantified.data.TimeSeries`\
            | :py:class:`energyquantified.data.Periodseries`\
            | :py:class:`energyquantified.data.OHLCList`\
            | None
        :raises APIError: If there were any network- or server-related \
            issues while loading the data
        """
        if self.event_type in [EventType.TRUNCATE, EventType.DELETE]:
            return None
        # Timeseries and scenarios
        if self.curve.curve_type in [CurveType.TIMESERIES, CurveType.SCENARIO_TIMESERIES]:
            return eq.timeseries.load(
                self.curve,
                begin=self.begin,
                end=self.end,
                )
        # Instance
        if self.curve.curve_type == CurveType.INSTANCE:
            return eq.instances.get(
                self.curve,
                issued=self.instance.issued,
                tag=self.instance.tag,
                )
        # Periods
        if self.curve.curve_type == CurveType.PERIOD:
            assert not self.curve.frequency.is_iterable
            # Periods
            return eq.periods.load(
                self.curve,
                begin=self.begin,
                end=self.end,
                )
        # Instance periods
        if self.curve.curve_type == CurveType.INSTANCE_PERIOD:
            assert self.instance is not None
            assert not self.curve.frequency.is_iterable
            # InstancePeriod
            return eq.period_instances.get(
                self.curve,
                begin=self.begin,
                end=self.end,
                issued=self.instance.issued,
                tag=self.instance.tag,
                )
        # OHLC
        if self.curve.curve_type == CurveType.OHLC:
            return eq.ohlc.load(
                self.curve, 
                begin=self.begin, 
                end=self.end,
                )
