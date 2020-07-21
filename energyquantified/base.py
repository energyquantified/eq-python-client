from .http import Session

from .api import (
    InstancesAPI, MetadataAPI, TimeseriesAPI,
    PeriodsAPI, PeriodInstancesAPI
)
from .exceptions import UnauthorizedError, InitializationError


# Defaults

BASE_PATH = "https://app.energyquantified.com/api"


class EnergyQuantified:
    """
    The Time Series API client.

    Wraps the Energy Quantified Time Series API. Handles validation, network
    errors, rate limiting, and parsing of the API responses.

    Exactly one of **api_key** and **api_key_file** must be set at
    the same time. **api_key_file** shall be the file path to a file
    that contains just the API key (blank lines a stripped when read).

    :param api_key: The API key for your user account
    :type api_key: string, optional
    :param api_key_file: A file path to a file that contains the API key
    :type api_key_file: string, file, optional
    :param ssl_verify: Whether or not to verify the server certificate,\
                       defaults to True
    :type ssl_verify: bool, optional
    :param timeout: Maximum timeout per HTTP request, defaults to 15.0
    :type timeout: float, optional
    :param http_delay: The minimum number of seconds between the start of\
                       each HTTP request, defaults to 0.33 seconds
    :type http_delay: float, optional

    **Basic usage:**

       >>> from energyquantified import EnergyQuantified
       >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd")
       >>> eq.metadata.curves(q="de wind power actual")

    """

    def __init__(
            self,
            api_key=None,
            api_key_file=None,
            ssl_verify=True,
            timeout=15.0,
            http_delay=0.33,
            api_url=BASE_PATH
        ):
        # Simple validations
        assert api_key or api_key_file, "api_key is missing"
        if api_key:
            assert not api_key_file, (
                "Exactly one of 'api_key' and 'api_key_file' "
                "must be set at the same time, but both were given"
            )
        if api_key_file:
            assert not api_key, (
                "Exactly one of 'api_key' and 'api_key_file' "
                "must be set at the same time, but both were given"
            )
        assert timeout >= 0, "timeout must be larger than 0s"
        assert http_delay >= 0.125, "http_delay must be 0.125s or slower"
        assert api_url, "api_url is missing"
        # Attributes
        self._api_key = _find_api_key(api_key, api_key_file)
        self._api_url = api_url
        # HTTP client
        self._session = Session(
            timeout=timeout,
            verify=ssl_verify,
            base_url=self._api_url,
            headers={
                "X-API-Key": self._api_key,
            },
            delay=http_delay
        )
        # --- Public members ---
        #: See :py:class:`energyquantified.api.MetadataAPI`. For metadata
        #: queries (such as curve search and place lookups).
        self.metadata = MetadataAPI(self)
        #: See :py:class:`energyquantified.api.TimeseriesAPI`. For loading
        #: time series data.
        self.timeseries = TimeseriesAPI(self)
        #: See :py:class:`energyquantified.api.InstancesAPI`. For loading
        #: time series instances.
        self.instances = InstancesAPI(self)
        #: See :py:class:`energyquantified.api.PeriodsAPI`. For
        #: loading period-based series.
        self.periods = PeriodsAPI(self)
        #: See :py:class:`energyquantified.api.PeriodInstancesAPI`. For
        #: loading instances of period-based series.
        self.period_instances = PeriodInstancesAPI(self)

    def is_api_key_valid(self):
        """
        Check if the supplied API key is valid/user account can sign in.

        Does so by trying to load the categories list. If it succeeds, then
        the user has supplied a valid API key.

        :return: True if API key is valid, otherwise False
        :rtype: bool
        :raises APIError: If there were any network- or server-related \
            issues while check the API key
        """
        try:
            self.metadata.categories()
            return True
        except UnauthorizedError:
            return False


def _find_api_key(api_key, api_key_file):
    # With the API key, it's easy
    if api_key:
        return api_key
    # Open the file and read the key
    try:
        with open(api_key_file, mode='r', encoding='utf-8') as f:
            api_key = f.read().strip()
            if not api_key:
                raise InitializationError(
                    f"Could not read API key from file '{api_key_file}' "
                    "because it was empty"
                )
            return api_key
    except IOError as e:
        raise InitializationError(
            f"Could not read API key from file '{api_key_file}'. "
            f"Reason: {e}"
        ) from e
