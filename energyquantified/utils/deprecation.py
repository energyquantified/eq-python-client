import functools
import warnings
from typing import Optional


def deprecated(
        _func=None,
        *,
        alt: Optional[str] = None,
        msg: Optional[str] = None,
    ):
    """
    Decorator to mark a function or method as deprecated.
    To use this decorator, simply add ``@deprecated`` above the
    function or method definition. For classes, mark the __init__
    and method as deprecated. To work for inheritance, the __new__
    method must be marked. However, this will not work  for all
    cases of inheritance. For python3.13 and onwards, the ``warnings.deprecated``
    can be used instead, providing said functionality.

    :param _func: Needed for calling the decorator with optional arguments.
        (Otherwise, the function would not be passed to the decorator.)
    :type _func: function
    :param alt: Alternative function/method to use.
    :type alt: str
    :param msg: Custom deprecation warning message. Providing this will ignore the
        ``alt`` argument.
    :type msg: str
    :return: The decorated function/method
    :rtype: function
    """

    def decorator_deprecated(func):
        @functools.wraps(func)
        def wrapper_deprecated(*args, **kwargs):
            nonlocal msg
            nonlocal alt
            nonlocal _func
            funcname = func.__name__ if _func is None else _func.__name__
            if msg is None:
                if alt is None:
                    alt = "???"
                msg = f"The `{funcname}` method is deprecated; use `{alt}` instead."
            warnings.warn(
                msg,
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper_deprecated

    if _func is None:
        return decorator_deprecated
    else:
        return decorator_deprecated(_func)
