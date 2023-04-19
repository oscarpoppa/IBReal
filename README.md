# IBReal
Messing with extended precision using Python integers.

IBReal represents a memory-limited, arbitrary precision, integer-based implementation of a real number.
It offers addition, subtraction, powers, and multiplication only, which is OK for iteration exploration, albeit
probably slow. All math operations are available in in-line mode (i.e. +=).

Usage:
realnum = IBReal(raw, prec)

raw: IBReal object, number, Ival object, ascii repr of a real number, or tuple (integer, offset) -- where integer 
     is the integer after multiplying the real number by 10^offset. If using an IBReal instance, the precision
     will always be inherited from the object argument in spite of passing a prec val.

prec: precision -- length limit of internal integer (self.ival.num)


    >>> from ibreal import IBReal, Ival
    >>>
    >>> st = IBReal(-1.778243238)
    >>> st
    -1.778243238
    >>> 
    >>> sc = IBReal(-1.23123e-12)
    >>> sc
    -1.23123e-12
    >>>
    >>> tu = IBReal((123,2))
    >>> tu
    1.23
    >>> tu * 3
    3.69
    >>> 
    >>> iv = Ival(40889978788,17)
    >>> iv
    Ival(num=40889978788, off=17)
    >>> ivr = IBReal(iv)
    >>> ivr
    4.0889978788e-7
    >>> 
    >>> ivr + tu
    1.57000040889978788
    >>> 
    >>> ivr+=5
    >>> ivr
    5.00000040889978788
    >>> ivr**2
    25.0000040889980459990365283089948944
    >>>
    >>> small = IBReal((16757657654, 78))
    >>> small
    1.6757657654e-68
    >>> small**2
    2.80819090048664783716e-136
    >>>
