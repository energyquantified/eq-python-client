from ..utils import Page, dict_to_str
from .base import BaseAPI

from ..parser.metadata import parse_curve, parse_place


class MetadataAPI(BaseAPI):
    """
    Operations for curve search and place lookups. It also includes
    operations for listing attributes on
    :py:class:`energyquantified.metadata.Curve` objects.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    def categories(self):
        """
        List all available categories.

        Results are cached on repeated calls.

        :return: A set of available categories (strings)
        :rtype: set
        """
        CACHE_KEY = "categories"
        if self._cache.get(CACHE_KEY):
            return self._cache[CACHE_KEY]
        response = self._get("/metadata/categories/")
        self._cache[CACHE_KEY] = set(response.json())
        return self._cache[CACHE_KEY]

    def exact_categories(self):
        """
        List available exact combinations of categories (meaning
        combinations that exists in curve names). You can use this response
        for filtering curves on the ``exact_category`` parameter in
        :py:meth:`MetadataAPI.curves`.

        Results are cached on repeated calls.

        :return: A set of category combinations (strings)
        :rtype: set
        """
        CACHE_KEY = "exact-categories"
        if self._cache.get(CACHE_KEY):
            return self._cache[CACHE_KEY]
        response = self._get("/metadata/exact-categories/")
        self._cache[CACHE_KEY] = set(response.json())
        return self._cache[CACHE_KEY]

    def curves(
            self,
            q=None,
            area=None,
            data_type=None,
            category=None,
            exact_category=None,
            frequency=None,
            has_place=None,
            page=1,
            page_size=50):
        """
        Search for curves. Supports paging.

        :param q: Freetext search, defaults to None
        :type q: str, optional
        :param area: Filter on an area, defaults to None
        :type area: Area, str, optional
        :param data_type: Filter on a DataType, defaults to None
        :type data_type: DataType, str, optional
        :param category: List of one or more categories that the curves\
            must have, defaults to None
        :type category: list[str], optional
        :param exact_category: An exact string of the category list for\
            a curve, defaults to None
        :type exact_category: str, optional
        :param frequency: Filter by frequency, defaults to None
        :type frequency: Frequency, str, optional
        :param has_place: True – only curves for places, False – only curves\
            without places, defaults to None
        :type has_place: bool, optional
        :param page: Set the page, defaults to 1
        :type page: int, optional
        :param page_size: Set the page size, defaults to 50
        :type page_size: int, optional
        :return: A page of :py:class:`energyquantified.metadata.Curve`
        :rtype: :py:class:`energyquantified.utils.Page` (subclass of list)
        """
        # Parameters
        params = {}
        self._add_str(params, "q", q)
        self._add_area(params, "area", area)
        self._add_data_type(params, "data-type", data_type)
        self._add_str_list(params, "category", category)
        self._add_str(params, "exact-category", exact_category)
        self._add_frequency(params, "frequency", frequency)
        self._add_bool(params, "has-place", has_place)
        self._add_int(params, "page", page)
        self._add_int(params, "page-size", page_size)
        # Load function
        def _load(page=None):
            # Override page if it is set
            if page:
                self._add_int(params, "page", page)
            # Check cache to see if we already have done this
            cache_key = dict_to_str(params, "curves")
            if self._cache.get(cache_key):
                return self._cache[cache_key]
            # Do the HTTP request, cache the result and return
            response = self._get("/metadata/curves/", params=params)
            items_gen = (parse_curve(c) for c in response.json())
            self._cache[cache_key] = (
                Page._response_to_page(items_gen, response, load_func=_load)
            )
            return self._cache[cache_key]
        # Invoke load
        return _load()

    def places(
            self,
            q=None,
            area=None,
            fuel=None,
            kind=None,
            tree=False,
            page=1,
            page_size=50):
        """
        Search for places. Supports places.

        :param q: Freetext search, defaults to None
        :type q: str, optional
        :param area: Filter on an area, defaults to None
        :type area: Area, str, optional
        :param fuel: Filter by fuel type, defaults to None
        :type fuel: str, optional
        :param kind: Type of place (producer, consumer, river, etc.),\
            defaults to None
        :type kind: str, optional
        :param tree: Enable to return as a hierachy, defaults to False
        :type tree: bool, optional
        :param page: Set the page, defaults to 1
        :type page: int, optional
        :param page_size: Set the page size, defaults to 50
        :type page_size: int, optional
        :return: A page of :py:class:`energyquantified.metadata.Place`
        :rtype: :py:class:`energyquantified.utils.Page` (subclass of list)
        """
        # Parameters
        params = {}
        self._add_str(params, "q", q)
        self._add_area(params, "area", area)
        self._add_str_list(params, "fuel", fuel)
        self._add_str_list(params, "kind", kind)
        self._add_bool(params, "tree", tree)
        self._add_int(params, "page", page)
        self._add_int(params, "page-size", page_size)
        # Load function
        def _load(page=None):
            # Override page if it is set
            if page:
                self._add_int(params, "page", page)
            # Check cache to see if we already have done this
            cache_key = dict_to_str(params, "places")
            if self._cache.get(cache_key):
                return self._cache[cache_key]
            # Do the HTTP request, cache the result and return
            response = self._get("/metadata/places/", params=params)
            items_gen = (parse_place(p) for p in response.json())
            self._cache[cache_key] = (
                Page._response_to_page(items_gen, response, load_func=_load)
            )
            return self._cache[cache_key]
        # Invoke load
        return _load()