from .http import Session

from .api import (
    InstancesAPI,
    MetadataAPI,
    RealtoMetadataAPI,
    TimeseriesAPI,
    PeriodsAPI,
    PeriodInstancesAPI,
    OhlcAPI,
    SrmcAPI,
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
                       each HTTP request, defaults to 0.125 seconds (8 req/s)
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
            http_delay=0.125,
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
        assert http_delay >= 0.0667, (
            "http_delay must be 0.0667s or slower (15 req/s)"
        )
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
        #: See :py:class:`energyquantified.api.OhlcAPI`. For loading
        #: OHLC data in various ways
        self.ohlc = OhlcAPI(self)
        #: See :py:class:`energyquantified.api.SrmcAPI`. For loading and
        #: calculating short-run marginal costs (SRMC) from OHLC data.
        self.srmc = SrmcAPI(self)

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


class RealtoConnection:
    """
    The Time Series API client for customers subscribing via Realto.

    Wraps a Energy Quantified Time Series API on Realto. Handles validation,
    network errors, rate limiting, and parsing of the API responses.

    You must specify the **api_url**. There are

    Exactly one of **api_key** and **api_key_file** must be set at
    the same time. **api_key_file** shall be the file path to a file
    that contains just the API key (blank lines a stripped when read).

    :param api_url: The root URL for the API, such as
    :type api_url: string, optional
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
                       each HTTP request, defaults to 0.125 seconds (8 req/s)
    :type http_delay: float, optional

    **Basic usage:**

       >>> from energyquantified import RealtoConnection
       >>> eq = RealtoConnection(
       >>>     api_url=RealtoConnection.API_URL_GERMANY,
       >>>     api_key="aaaa-bbbb-cccc-dddd"
       >>> )
       >>> eq.metadata.curves(q="de wind power actual")

    """

    #: The base URL for the German data API on Realto.
    API_URL_GERMANY = 'https://api.realto.io/energyquantified-germany'

    #: The base URL for the French data API on Realto.
    API_URL_FRANCE = 'https://api.realto.io/energyquantified-france'

    #: The base URL for the Netherlands data API on Realto.
    API_URL_NETHERLANDS = 'https://api.realto.io/energyquantified-netherlands'

    #: The base URL for the UK data API on Realto.
    API_URL_UK = 'https://api.realto.io/energyquantified-greatbritain'

    #: The base URL for the Belgium data API on Realto.
    API_URL_BELGIUM = 'https://api.realto.io/energyquantified-belgium'

    def __init__(
            self,
            api_url=None,
            api_key=None,
            api_key_file=None,
            ssl_verify=True,
            timeout=15.0,
            http_delay=0.125
        ):
        # Simple validations
        assert api_url, "api_url is missing"
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
        assert http_delay >= 0.0667, (
            "http_delay must be 0.0667s or slower (15 req/s)"
        )
        # Attributes
        self._api_url = api_url
        self._api_key = _find_api_key(api_key, api_key_file)
        # HTTP client
        self._session = Session(
            timeout=timeout,
            verify=ssl_verify,
            base_url=self._api_url,
            headers={
                "Ocp-Apim-Subscription-Key": self._api_key,
            },
            delay=http_delay
        )
        # --- Public members ---
        #: See :py:class:`energyquantified.api.MetadataAPI`. For metadata
        #: queries (such as curve search and place lookups).
        self.metadata = RealtoMetadataAPI(self)
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
            self.metadata.curves(page_size=10)
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
