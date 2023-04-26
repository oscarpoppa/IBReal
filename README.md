# IBReal
Messing with extended precision using Python integers.

IBReal represents a memory-limited, arbitrary precision, integer-based implementation of a real number.
It is naturally slow. All math operations are available in in-line mode (i.e. +=).

Usage:
realnum = IBReal(raw, prec)

raw: IBReal object, number, Ival object, ascii repr of a real number, or tuple (integer, offset) -- where integer 
     is the integer after multiplying the real number by 10^offset. If using an IBReal instance, the precision
     will always be inherited from the object argument in spite of passing a prec val.

prec: precision -- length limit of internal integer (self.ival.num)


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

