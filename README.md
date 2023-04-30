# IBReal
Exploring extended precision using Python 3 integers in a 100% Python library.

IBReal represents a fully functional, memory-only-limited, arbitrary precision real number. Under the hood,
it is 100% integer-based. It is naturally slow. All math operations are available in in-line mode (i.e. +=).

its counterpart, IBComp, is an equally robust complex formulation based on IBReal.

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
    >>> cm * 0.00000000000000000000000000000000000000000012212
    -1.34332e-43 + 1.34439331268e-55i
    >>>

