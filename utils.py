import itertools
import math


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