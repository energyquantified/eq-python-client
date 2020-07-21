import logging
import time
import threading

from ..time import now


log = logging.getLogger(__name__)


class RateLimiter:
    """
    A rate limit that sleeps until a new call is allowed. Rate limiting
    will ensure that there is always a minimum delay between each call.

    Defaults to a delay of 1.0 second per call. The rate limiter is thread-safe.

    Example usage:

        # Create a rate limit with a delay of 2.5 second per call
        rate_limiter = RateLimit(rate_per_second=2.5)

        # Rate limit
        for foo in bar:
            rate_limiter()
            ...
    """

    def __init__(self, delay=1.0):
        assert delay is not None, "delay cannot be None"
        self.delay = delay
        self._previous = None
        self._lock = threading.RLock()

    def __call__(self):
        """
        Waits and returns when
        """
        if not self.delay:
            return # Dont impose delay
        else:
            self._lock.acquire()
            try:
                self._rate_limited()
            finally:
                self._lock.release()

    def _rate_limited(self):
        """
        Perform rate limiting and let thread sleep if necessary.
        """
        # Check if we must sleep, except for the first time
        if self._previous:
            diff = (now() - self._previous).total_seconds()
            if diff < self.delay:
                wait_for = (self.delay - diff) + 0.0001
                self._sleep(wait_for)
        # Set previous pass-through time end time
        self._previous = now()

    def _sleep(self, seconds):
        log.debug("Sleep for %.2fs" % seconds)
        time.sleep(seconds)
