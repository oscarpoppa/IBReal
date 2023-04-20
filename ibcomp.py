from ibreal import IBReal
from math import sqrt

class IBComp:
    """
    IBComp is a complex number that uses the precision of IBReal numbers. The math interface offers the 
    same ioperations IBReal offers.
  
    Usage:
    comp = IBComp(rcomp, icomp)

    rcomp & icomp: IBReal object, Ival object, number, string, or 2-tuple
    """
    def __init__(self, raw):
        if isinstance(raw, tuple):
            self.rcomp = raw[0] if isinstance(raw[0], IBReal) else IBReal(raw[0])
            self.icomp = raw[1] if isinstance(raw[1], IBReal) else IBReal(raw[1])
        elif isinstance(raw, type(self)):
            self.rcomp = raw.rcomp
            self.icomp = raw.icomp
        elif isinstance(raw, IBReal):
            self.rcomp = raw
            self.icomp = IBReal((0, 0), **raw.kwargs)
        else:
            (self.rcomp, self.icomp) = self._from_txt(str(raw))

    @property #still within our precision space. May be helpful for comparisons.
    def lengthsq(self):
        return self.rcomp**2 + self.icomp**2

    @property #Chops off to fit float precision
    def length(self):
        slen = self.rcomp**2 + self.icomp**2
        return sqrt(float(slen))

    @property
    def conj(self):
        return type(self)((self.rcomp, -self.icomp))

    def trim(self, prec):
        if not isinstance(prec, int) or prec <= 0:
            raise ValueError('Only positive integers allowed')
        self.rcomp.trim(prec)
        self.icomp.trim(prec)
        return self

    def _from_txt(self, val): #looking for a+bi
        val = val.replace(' ', '')
        plus = val.find('+')
        eye = val.find('i')
        if plus == -1 and eye == -1: #real number
            return (IBReal(val), IBReal((0, 0)))
        elif plus == -1 and eye != -1: #imag number
            val = val[:eye]
            return (IBReal((0, 0)), IBReal(val))
        elif plus != -1 and eye != -1: #comp number
            return (IBReal(val[:plus]), IBReal(val[plus+1:eye]))

    def __mul__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        rcmp = IBReal(self.rcomp*other.rcomp-self.icomp*other.icomp, **self.rcomp.kwargs)
        icmp = IBReal(self.rcomp*other.icomp+self.icomp*other.rcomp, **self.icomp.kwargs)
        return type(self)((rcmp, icmp))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        rcmp = IBReal(self.rcomp*other.rcomp-self.icomp*other.icomp, **self.rcomp.kwargs)
        icmp = IBReal(self.rcomp*other.icomp+self.icomp*other.rcomp, **self.icomp.kwargs)
        (self.rcomp, self.icomp) = (rcmp, icmp)
        return self

    def __add__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        return type(self)((self.rcomp+other.rcomp, self.icomp+other.icomp))

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        self.rcomp = self.rcomp+other.rcomp
        self.icomp = self.icomp+other.icomp
        return self

    def __sub__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        return type(self)((self.rcomp-other.rcomp, self.icomp-other.icomp))

    def __rsub__(self, other):
        return -self.__sub__(other)

    def __isub__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        self.rcomp = self.rcomp-other.rcomp
        self.icomp = self.icomp-other.icomp
        return self

    def __pow__(self, oint):
        if not isinstance(oint, int) or oint < 0:
            raise ValueError('Only non-negative integers allowed')
        tmp = type(self)((self.rcomp, self.icomp))
        if oint == 0:
            tmp.rcomp = IBReal((1, 0), **self.rcomp.kwargs)
            tmp.icomp = IBReal((0, 0), **self.icomp.kwargs)
        else: 
            for _ in range(1, oint):
                tmp *= self 
        return tmp 

    def __ipow__(self, oint):
        if not isinstance(oint, int) or oint < 0:
            raise ValueError('Only non-negative integers allowed')
        tmp = type(self)((self.rcomp, self.icomp))
        if oint == 0:
            self.rcomp = IBReal((1, 0), **self.rcomp.kwargs)
            self.icomp = IBReal((0, 0), **self.icomp.kwargs)
        else: 
            for _ in range(1, oint):
                self *= tmp 
        return self 

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        return self.rcomp == other.rcomp and self.icomp == other.icomp

    def __neg__(self):
        return type(self)((-self.rcomp, -self.icomp))

    def __str__(self):
        return '{} + {}i'.format(self.rcomp, self.icomp)

    def __repr__(self):
        return '{} + {}i'.format(self.rcomp, self.icomp)

