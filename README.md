# IBReal
Messing with extended precision using Python integers.

IBReal represents a memory-only-limited, arbitrary precision, integer-based implementation of a real number.
It offers addition, subtraction, powers (integer), and multiplication only, which is OK for iteration exploration. I'm not expecting
it to be fast. All math operations (**,+,-,*) are also available in in-line mode (i.e. +=).

Usage:

realnum = IBReal(raw, prec=300)

raw: Ival instance (defined in same file), ascii real number in decimal notation or tuple (integer, offset), 
where integer is the integer after multiplying the real number by 10^offset.
     
prec: precision

    >>> from ibreal import IBReal, Ival
    >>>
    >>> st = IBReal('-1.778243238')
    >>> st
    -1.778243238
    >>> 
    >>> sc = IBReal('-1.23123e-12')
    >>> sc
    -1.23123e-12
    >>>
    >>> tu = IBReal((123,2))
    >>> tu
    1.23
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
    >>> five = IBReal('5')
    >>> five
    5.0
    >>> ivr+=five
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
