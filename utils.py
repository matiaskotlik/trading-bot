import itertools
import math
from functools import wraps

import diskcache


def clamp(n: float, min_val: float = 0, max_val: float = 1) -> float:
    """Clamp a value in the range [min_val, max_val)"""
    assert min_val < max_val
    if n < min_val: return min_val
    if n >= max_val: return math.nextafter(max_val, min_val)
    return n


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def sign(n: float):
    if n < 0:
        return '-'
    return '+'


def memoize_diskcache(cache: diskcache.Cache):
    def decorator(func):
        """
        Memoizing cache decorator.
        Decorator to wrap callable with memoizing function using cache.
        Repeated calls with the same arguments will lookup result in cache and
        avoid function evaluation.
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            "Wrapper for callable to cache arguments and return values."
            key = wrapper.__cache_key__(*args, **kwargs)
            result = cache.get(key, default=diskcache.ENOVAL, retry=True)

            if result is diskcache.ENOVAL:
                result = func(self, *args, **kwargs)
                cache.set(key, result, retry=True)

            return result

        def __cache_key__(*args, **kwargs):
            "Make key for cache given function arguments."
            key = (func.__module__ + '.' + func.__qualname__, ) + args
            if kwargs:
                key += (diskcache.ENOVAL, )
                for item in sorted(kwargs.items()):
                    key += item
            return key

        wrapper.__cache_key__ = __cache_key__
        return wrapper

    return decorator
