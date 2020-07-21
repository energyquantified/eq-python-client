import logging
import time

import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError


log = logging.getLogger(__name__)


class Retry:
    """
    Retry rules with max retries, number of seconds delay between the
    retries with a backoff factor (multiplies the delay for each missed
    retry).

    If you don't want any backoff, just leave the backoff factor at 1.
    """

    def __init__(self, max_tries=3, delay=7.5, backoff=2):
        self.max_tries = max_tries
        self.delay = delay
        self.backoff = backoff

    def __call__(self, func):
        """
        Retries decorator.
        """
        def _wrapper():
            # Local variables
            tries, delay, backoff = self.max_tries, self.delay, self.backoff
            error = None
            # Retry
            while tries > 1:
                # Perform operation
                try:
                    r = func()
                    # Check status versus 5xx (server errors)
                    if 500 <= r.status_code < 600:
                        log.error(
                            "HTTP %s %s for URL: %s"
                            % (r.status_code, r.reason, r.url)
                        )
                        raise HTTPError(
                            "HTTP %s %s for URL: %s"
                            % (r.status_code, r.reason, r.url)
                        )
                    # Return response if all was OK
                    return r
                except (ConnectionError, Timeout, HTTPError) as e:
                    error = e
                # Print info
                attempt = self.max_tries - tries + 1
                log.info(
                    "Attempt %d/%d failed. Retrying in %.1fs."
                    % (attempt, self.max_tries, delay)
                )
                # Sleep and update retrier
                time.sleep(delay)
                tries = tries - 1
                delay = delay * backoff
            # Last try
            return func()
        return _wrapper
