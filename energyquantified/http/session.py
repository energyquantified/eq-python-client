import logging
import time

import requests

from ..__version__ import __version__

from .rate_limiter import RateLimiter
from .retry import Retry


# Identify the API client
USER_AGENT = f"Python/EQ-API-Client {__version__}"

# Suppress SSL certificate warnings
# TODO This should probably not be handled here
requests.packages.urllib3.disable_warnings()

# Logging
log = logging.getLogger(__name__)


class Session:
    """
    An HTTP session object wrapper around requests. Enhancements:

     * Configurable rate limiting
     * Configurable retries on server errors
    """

    def __init__(self, timeout=30, max_redirects=5, verify=True, headers={},
            auth=None, base_url=None, delay=None, retry=None):
        # Rate limit and retry
        self.rate_limiter = RateLimiter(delay) if delay else RateLimiter()
        self.retry = retry if retry else Retry()
        # Default arguments
        self.verify = verify
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.headers = headers
        self.auth = auth
        self.base_url = base_url
        # Requests
        self._requests = 0
        # Session
        self.session = requests.Session()
        self.session.max_redirects = max_redirects
        self.session.headers.update({"User-agent": USER_AGENT})
        self.session.headers.update(self.headers)
        self.session.hooks["response"] = [self._request_inc]

    def _request_inc(self, response, *args, **kwargs):
        self._requests += 1

    @property
    def requests(self):
        return self._requests

    def _prepare_args(self, **kwargs):
        return {
            "timeout": kwargs.get("timeout", self.timeout),
            "verify": kwargs.get("verify", self.verify),
            "auth": kwargs.get("auth", self.auth),
            "headers": kwargs.get("headers"),
            "params": kwargs.get("params"),
            "data": kwargs.get("data"),
            "json": kwargs.get("json"),
        }

    def get(self, url, retry=True, **kwargs):
        """
        Perform a HTTP GET request.
        """
        return self.request("get", url, retry=retry, **kwargs)

    def post(self, url, retry=False, **kwargs):
        """
        Perform a HTTP POST request.
        """
        return self.request("post", url, retry=retry, **kwargs)

    def request(self, method, url, retry=False, **kwargs):
        """
        Perform a request using a HTTP verb of your choice.
        """
        # Prepare arguments
        args = self._prepare_args(**kwargs)

        # Append base url
        if self.base_url:
            url = f"{self.base_url}{url}"

        # Make the function that does the work
        def _func():
            self.rate_limiter()
            log.debug(
                "HTTP %s %s %s"
                % (method.upper(), url, args.get("params") or "")
            )
            return self.session.request(method, url, **args)

        # Attach retry logic, if any
        func = self.retry(_func) if retry and self.retry else _func

        # Perform request
        return func()
