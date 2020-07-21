import sys

from ..exceptions import PageError


class Page(list):
    """
    A Page is a subclass of the standard `list` type in Python
    with additional attributes for paging.

    It also has methods for loading the next/previous page, and to
    print the page to stdout.
    """

    def __init__(
            self,
            elements,
            page=None,
            page_size=None,
            total_items=None,
            first_page=None,
            last_page=None,
            page_load_func=None,
        ):
        super().__init__(elements)
        # --- Public members ---
        #: The current page
        self.page = page
        #: The page size
        self.page_size = page_size
        #: Total number of items found in search across all pages
        self.total_items = total_items
        #: The first page (is always 1)
        self.first_page = first_page
        #: The last page in the search
        self.last_page = last_page
        #: The total number of pages
        self.total_pages = last_page
        self._page_load_func = page_load_func

    def has_next_page(self):
        """
        Check if there is a next page.

        :return: True when there is a next page
        :rtype: bool
        """
        return self.page is not None and self.page < self.last_page

    def has_previous_page(self):
        """
        Check if there is a previous page.

        :return: True when there is a previous page
        :rtype: bool
        """
        return self.page is not None and self.page > self.first_page

    def get_next_page(self):
        """
        Get the next page. Will perform an HTTP request if data is not
        already in local cache.

        :raises PageError: When there is no next page
        :raises PageError: There is no support for loading the next page
        :return: The next page
        :rtype: Page
        """
        if not self.has_next_page():
            raise PageError("No more pages available")
        if not self._page_load_func:
            raise PageError("Cannot load more pages")
        return self._page_load_func(page=self.page + 1)

    def get_previous_page(self):
        """
        Get the previous page. Will perform an HTTP request if data is not
        already in local cache.

        :raises PageError: When there is no previous page
        :raises PageError: There is no support for loading the previous page
        :return: The previous page
        :rtype: Page
        """
        if not self.has_previous_page():
            raise PageError("No previous page available")
        if not self._page_load_func:
            raise PageError("Cannot load more pages")
        return self._page_load_func(page=self.page - 1)

    def print(self, file=sys.stdout):
        """
        Print the page with all its attributes.

        :param file: A file descriptor, defaults to sys.stdout
        :type file: file descriptor, optional
        """
        print(
            f"Page:\n"
            f"   current = {self.page}\n"
            f"   page-size = {self.page_size}\n"
            f"   total-items = {self.total_items}\n"
            f"   total-pages = {self.total_pages}\n"
            f"   items:\n",
            file=file
        )
        for item in self:
            print("    –", item, file=file)

    @staticmethod
    def _response_to_page(items, response, load_func=None):
        """
        Private utility method to convert an HTTP response and a list of
        items to a Page object.
        """
        # Parse pagination from response headers
        headers = response.headers
        page = int(headers.get("X-Current-Page"))
        page_size = int(headers.get("X-Page-Size"))
        first_page = int(headers.get("X-First-Page"))
        last_page = int(headers.get("X-Last-Page"))
        total_items = int(headers.get("X-Total-Items"))
        # To a page instance
        return Page(
            items,
            page=page,
            page_size=page_size,
            first_page=first_page,
            last_page=last_page,
            total_items=total_items,
            page_load_func=load_func
        )
