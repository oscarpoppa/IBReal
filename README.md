# IBReal
Exploring extended precision using Python 3 integers in a 100% Python library. 

Using regular or double precision C math is fast, but lacks the precision to explore such things as fractals, 
which can benefit from arbitrarily precise math. Python integers have no size-limit, so an arbitrary precision 
decimal can be created by using a python3 integer paired with an offset value to locate the decimal point within 
the integer. i.e. 13276887645 offset 3 is equivalent to 132.76887645.

Class IBReal represents a fully functional, memory-only-limited, arbitrary precision real number. Under the hood,
it is 100% integer-based. It is naturally slow, although caching is used throughout.

its counterpart class, IBComp, is an equally robust complex formulation based on IBReal.

    >>> from ibreal import IBReal, Ival
    >>> 
    >>> ## Instantiate in several ways
    >>>
    >>> sa = IBReal('-1.778243238') #string
    >>> sa
    -1.778243238
    >>>
    >>> st = IBReal(-1.778243238) #raw number
    >>> st
    -1.778243238
    >>>
    >>> tu = IBReal((123,2)) #2-tuple
    >>> tu
    1.23
    >>> 
    >>> tu = IBReal(Ival(123,2)) #Ival instance
    >>> tu
    1.23
    >>> 
    >>> cp = IBReal(tu) #another IBReal instance
    >>> cp
    1.23
    >>> 
    >>> ## watch out for implicit truncation. When in doubt, use quotes
    >>> 
    >>> lf = IBReal(1.13322288732987384930949090349093477378764e-43) #float literal gets truncated before passage
    >>> sf = IBReal('1.13322288732987384930949090349093477378764e-43')
    >>> lf
    1.1332228873298739e-43
    >>> sf
    1.13322288732987384930949090349093477378764e-43
    >>> lf == sf
    False 
    >>>
    >>> small = IBReal((16757657654, 78))
    >>> small
    1.6757657654e-68
    >>> small**2
    2.80819090048664783716e-136
    >>>
    >>> ## IBComp is the complex extension of IBReal
    >>>
    >>> from ibcomp import IBComp
    >>> cm = IBComp(-1.1, 1.1008789e-12)
    >>> cm
    -1.1 + 1.1008789e-12i
    >>> 
    >>> cm**2
    1.20999999999999999999999878806564753479 + 1.21096678999999999999998665807043185887326931e-13i
    >>> 
    >>> cm + IBReal(4)
    2.9 + 1.1008789e-12i
    >>> 
    >>> cm * 6
    -6.6000000000000000000 + 6.6052734e-12i
    >>> 
    >>> cm * IBReal('0.00000000000000000000000000000000000000000012212')
    -1.34332e-43 + 1.34439331268e-55i
    >>>
    >>> # functions and utilities to support IBReal and IBComp types
    >>> from ibfuncs import ib_roots
    >>> from ibtools import clean, ret_clean
    >>>
    >>> # "clean" twelfth root of one
    >>> one = IBReal(1)
    >>> root = ret_clean()(ib_roots(one, 12))
    >>>
    >>> examine any of the roots
    >>> root(0)
    1.0 + 0.0i
    >>> root(1)
    8.660254037844386467637231707529361834714026269051903140279034897259665084544000185405730933786242898e-1 + 5.0e-1i
    >>> root(2)
    5.0e-1 + 8.660254037844386467637231707529361834714026269051903140279034897259665084544000185405730933786242787e-1i
    >>> _**12
    9.999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999041e-1 + -5.505e-98i
    >>> clean(_)
    1.0 + 0.0i
    >>> root(9)
    0.0 + -1.0i
    >>> root(11)
    8.660254037844386467637231707529361834714026269051903140279034897259665084544000185405730933786242177e-1 + -5.0e-1i
    >>>
    >>> _.dtrim(20)
    8.6602540378443864676e-1 + -5.0e-1i
    >>> 
