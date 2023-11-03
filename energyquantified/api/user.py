from .base import BaseAPI

from ..parser.user import parse_user


class UserAPI(BaseAPI):
    """
    User API operations.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    def user(self):
        """
        Get details about the current user.

        :return: The current user
        :rtype: :py:class:`energyquantified.user.User`
        """
        # HTTP request
        response = self._get("/user/")
        return parse_user(response.json())
