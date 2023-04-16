# IBReal
Messing with extended precision using Python integers.

IBReal represents a memory-limited, arbitrary precision, integer-based implementation of a real number.
It offers addition, subtraction, and multiplication only, which is OK for iteration exploration. I'm not expecting
it to be fast. All math operations (+-*) are also available in in-line mode (i.e. +=).

Usage:
realnum = IBReal(raw, prec, fast_ivs)
raw: ascii real number in decimal notation OR tuple (integer, offset), where integer is the integer after multiplying the real
     number by 10^offset.
prec: precision   
fast_ivs: exclude text generation overhead. SB faster for extended calculation.

    >>> one = IBReal('1')
    >>> one
    1.0
    >>>
    >>> small = IBReal('0.0000000000000000000000000000000000000000000000000000000000000000000055')
    >>> small
    0.0000000000000000000000000000000000000000000000000000000000000000000055
    >>>
    >>> one + small
    1.0000000000000000000000000000000000000000000000000000000000000000000055
    >>>
    >>> prec = small * small
    >>> prec
    0.00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003025
    >>>
    >>> prec += one
    >>> prec
    1.00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003025
    >>> 
    >>> byival = IBReal((188899882228898, 17))
    >>> byival
    0.00188899882228898
    >>>
