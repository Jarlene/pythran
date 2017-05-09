""" Module with facilities to represent range values. """

from math import isinf
import gast as ast
import itertools

import numpy


class Interval(object):

    """ Representation for a range of values. """

    def __init__(self, low, high):
        """ Set initial bound of the range object. """
        self.low = low
        self.high = high

    def __repr__(self):
        """ Return a nicely formatted representation string. """
        return "Interval(low={low}, high={high})".format(low=self.low,
                                                         high=self.high)

    def bounds(self):
        return self.low, self.high

    def union_update(self, other):
        """ Intersect current range with other."""
        self.low = min(self.low, other.low)
        self.high = max(self.high, other.high)

    def union(self, other):
        """ Intersect current range with other."""
        res = self.copy()
        res.union_update(other)
        return res

    def copy(self):
        return Interval(self.low, self.high)

    def widen(self, other):
        """ Widen current range. """
        if self.low < other.low:
            self.low = -float("inf")
        if self.high > other.high:
            self.high = float("inf")

    def __sub__(self, other):
        """
        Combiner for Subtraction operation.

        >>> Interval(1, 5) - Interval(-5, -4)
        Interval(low=5, high=10)
        """
        return Interval(self.low - other.high, self.high - other.low)

    def __mul__(self, other):
        """
        Combiner for Multiplication operation.

        >>> Interval(1, 5) * Interval(-5, -4)
        Interval(low=-25, high=-4)
        >>> Interval(-1, 5) * Interval(-5, 3)
        Interval(low=-25, high=15)
        >>> Interval(1, 5) * Interval(3, 8)
        Interval(low=3, high=40)
        """
        res = [v1 * v2 for v1, v2 in
               itertools.product(self.bounds(), other.bounds())]
        return Interval(numpy.min(res), numpy.max(res))

    __mult__ = __mul__

    def __add__(self, other):
        """
        Combiner for Addition operation.

        >>> Interval(-12, 5) + Interval(-5, -3)
        Interval(low=-17, high=2)
        """
        return Interval(self.low + other.low, self.high + other.high)

    def __div__(self, other):
        """
        Combiner for Divide operation.

        >>> Interval(-1, 5) / Interval(3, 8)
        Interval(low=-1, high=1)
        >>> Interval(-1, 5) / Interval(-5, -4)
        Interval(low=-2, high=0)
        >>> Interval(-1, 5) / Interval(-5, 3)
        Interval(low=-inf, high=inf)
        """
        if other.low <= 0 and other.high >= 0:
            return UNKNOWN_RANGE
        if other.low == 0:
            return UNKNOWN_RANGE
        res = [v1 / v2 for v1, v2 in
               itertools.product(self.bounds(), other.bounds())]
        return Interval(numpy.min(res), numpy.max(res))

    def __rshift__(range1, range2):
        """
        Combiner for Right shift operation.

        >>> Interval(10, 100) >> Interval(3, 8)
        Interval(low=0, high=12)
        >>> Interval(10, float("inf")) >> Interval(3, 8)
        Interval(low=0, high=inf)
        >>> Interval(-float("inf"), 0) >> Interval(3, 8)
        Interval(low=-inf, high=0)
        >>> Interval(-30, 10) >> Interval(3, float('inf'))
        Interval(low=-4, high=1)
        """
        if range1.low <= 0:
            if isinf(range1.low):
                min_ = range1.low
            else:
                min_ = range1.low >> range2.low
        elif isinf(range2.high):
            min_ = 0
        else:
            min_ = range1.low >> range2.high
        if isinf(range1.high):
            max_ = range1.high
        elif isinf(range2.low):
            max_ = 0
        else:
            max_ = range1.high >> range2.low
        return Interval(min_, max_)

    def __mod__(range1, range2):
        """ Combiner for Modulo operation.

        >>> Interval(-1, 5) % Interval(1, 13)
        Interval(low=0, high=5)
        >>> Interval(-21, 5) % Interval(1, 13)
        Interval(low=0, high=13)
        """
        return Interval(0, min(range2.high,
                               max(abs(range1.high), abs(range1.low))))

    def __pow__(range1, range2):
        """
        Combiner for Power operation.

        >>> Interval(1, 5) ** Interval(-5, -4)
        Interval(low=1.0, high=1.0)
        >>> Interval(-1, 5) ** Interval(-5, 3)
        Interval(low=-1.0, high=125.0)
        >>> Interval(1, 5) ** Interval(3, 8)
        Interval(low=1.0, high=390625.0)
        """
        res = [v1 ** v2 for v1, v2 in
               itertools.product(range1.bounds(), range2.bounds())]
        return Interval(numpy.ceil(min(res)), numpy.floor(max(res)))

    def __lshift__(range1, range2):
        """
        Combiner for Left shift operation.

        >>> Interval(1, 5) << Interval(3, 8)
        Interval(low=8, high=1280)
        >>> Interval(1, float("inf")) << Interval(3, 8)
        Interval(low=8, high=inf)
        >>> Interval(-float("inf"), 0) << Interval(3, 8)
        Interval(low=-inf, high=0)
        >>> Interval(-3, 1) << Interval(3, float('inf'))
        Interval(low=-24, high=inf)
        """
        min_inf = isinf(range1.low) or isinf(range2.low)
        max_inf = isinf(range1.high) or isinf(range2.high)
        min_ = -float("inf") if min_inf else (range1.low << range2.low)
        max_ = float("inf") if max_inf else (range1.high << range2.high)
        return Interval(min_, max_)

    def __floordiv__(range1, range2):
        """
        Combiner for Floor divide operation.

        >>> Interval(-1, 5) // Interval(3, 8)
        Interval(low=-1, high=1)
        >>> Interval(-1, 5) // Interval(-5, -4)
        Interval(low=-2, high=0)
        >>> Interval(-1, 5) // Interval(-5, 3)
        Interval(low=-inf, high=inf)
        """
        if range2.low <= 0 and range2.high >= 0:
            return UNKNOWN_RANGE
        if range2.low == 0:
            return UNKNOWN_RANGE
        res = [v1 // v2 for v1, v2 in
               itertools.product(range1.bounds(), range2.bounds())]
        return Interval(min(res), max(res))

UNKNOWN_RANGE = Interval(-float("inf"), float("inf"))


def range_values(args):
    """ Function used to compute returned range value of [x]range function. """
    if len(args) == 1:
        return Interval(0, args[0].high)
    elif len(args) == 2:
        return Interval(args[0].low, args[1].high)
    elif len(args) == 3:
        is_neg = args[2].low < 0
        is_pos = args[2].high > 0
        if is_neg and is_pos:
            return UNKNOWN_RANGE
        elif is_neg:
            return Interval(args[1].low, args[0].high)
        else:
            return Interval(args[0].low, args[1].high)


def bool_values(_):
    """ Return the range of a boolean value, i.e. [0, 1]. """
    return Interval(0, 1)


def cmp_values(_):
    """ Return the range of a comparison value, i.e. [-1, 1]. """
    return Interval(-1, 1)


def positive_values(_):
    """ Return a positive range without upper bound. """
    return Interval(0, float("inf"))


def max_values(args):
    """ Return possible range for max function. """
    return Interval(max(x.low for x in args), max(x.high for x in args))


def min_values(args):
    """ Return possible range for min function. """
    return Interval(min(x.low for x in args), min(x.high for x in args))


def ord_values(_):
    """ Return possible range for ord function. """
    return Interval(0, 255)