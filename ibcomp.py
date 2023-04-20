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
    def __init__(self, rcomp, icomp):
        #string, tuple or IBReal
        self.rcomp = IBReal(rcomp) if not isinstance(rcomp, IBReal) else rcomp
        self.icomp = IBReal(icomp) if not isinstance(icomp, IBReal) else icomp

    @property #still within our precision space. May be helpful for comparisons.
    def lengthsq(self):
        return self.rcomp**2 + self.icomp**2

    @property #Chops off to fit float precision
    def length(self):
        slen = self.rcomp**2 + self.icomp**2
        return sqrt(float(slen))

    @property
    def conj(self):
        return type(self)(self.rcomp, -self.icomp)

    def trim(self, prec):
        if not isinstance(prec, int) or prec <= 0:
            raise ValueError('Only positive integers allowed')
        self.rcomp.trim(prec)
        self.icomp.trim(prec)

    def __mul__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0,0), **self.icomp.kwargs)
            other = type(self)(rcmp, icmp)
        return type(self)(self.rcomp*other.rcomp-self.icomp*other.icomp, self.rcomp*other.icomp+self.icomp*other.rcomp)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0,0), **self.icomp.kwargs)
            other = type(self)(rcmp, icmp)
        self.rcomp = self.rcomp*other.rcomp-self.icomp*other.icomp
        self.icomp = self.rcomp*other.icomp+self.icomp*other.rcomp
        return self

    def __add__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0,0), **self.icomp.kwargs)
            other = type(self)(rcmp, icmp)
        return type(self)(self.rcomp+other.rcomp, self.icomp+other.icomp)

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0,0), **self.icomp.kwargs)
            other = type(self)(rcmp, icmp)
        self.rcomp = self.rcomp+other.rcomp
        self.icomp = self.icomp+other.icomp
        return self

    def __sub__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0,0), **self.icomp.kwargs)
            other = type(self)(rcmp, icmp)
        return type(self)(self.rcomp-other.rcomp, self.icomp-other.icomp)

    def __rsub__(self, other):
        return -self.__sub__(other)

    def __isub__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0,0), **self.icomp.kwargs)
            other = type(self)(rcmp, icmp)
        self.rcomp = self.rcomp-other.rcomp
        self.icomp = self.icomp-other.icomp
        return self

    def __pow__(self, oint):
        if not isinstance(oint, int) or oint < 0:
            raise ValueError('Only non-negative integers allowed')
        tmp = type(self)(self.rcomp, self.icomp)
        if oint == 0:
            tmp.rcomp = IBReal((1,0), **self.rcomp.kwargs)
            tmp.icomp = IBReal((0,0), **self.icomp.kwargs)
        else: 
            for _ in range(1, oint):
                tmp *= self 
        return tmp 

    def __ipow__(self, oint):
        if not isinstance(oint, int) or oint < 0:
            raise ValueError('Only non-negative integers allowed')
        tmp = type(self)(self.rcomp, self.icomp)
        if oint == 0:
            self.rcomp = IBReal((1,0), **self.rcomp.kwargs)
            self.icomp = IBReal((0,0), **self.icomp.kwargs)
        else: 
            for _ in range(1, oint):
                self *= tmp 
        return self 

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0,0), **self.icomp.kwargs)
            other = type(self)(rcmp, icmp)
        return self.rcomp == other.rcomp and self.icomp == other.icomp

    def __neg__(self):
        return type(self)(-self.rcomp, -self.icomp)

    def __str__(self):
        return '{} + {}i'.format(self.rcomp, self.icomp)

    def __repr__(self):
        return '{} + {}i'.format(self.rcomp, self.icomp)

