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
        try:
            if isinstance(raw, tuple):
                self.rcomp = raw[0] if isinstance(raw[0], IBReal) else IBReal(raw[0])
                self.icomp = raw[1] if isinstance(raw[1], IBReal) else IBReal(raw[1])
            elif isinstance(raw, type(self)):
                self.rcomp = raw.rcomp
                self.icomp = raw.icomp
            elif isinstance(raw, int):
                self.rcomp = IBReal(raw)
                self.icomp = IBReal((0, 0))
            elif isinstance(raw, IBReal):
                self.rcomp = raw
                self.icomp = IBReal((0, 0), **raw.kwargs)
            else:
                (self.rcomp, self.icomp) = self._from_raw(str(raw))
        except Exception as e:
            raise ValueError('Failed to coerce {}:{} to IBReal pair'.format(type(raw), raw)) from e 

    @property #still within our precision space. May be helpful for comparisons.
    def lengthsq(self):
        return self.rcomp**2 + self.icomp**2

    @property #Chops off to fit float precision
    def length(self):
        slen = self.rcomp**2 + self.icomp**2
        return IBReal(str(sqrt(float(slen))))

    @property
    def conj(self):
        return type(self)((self.rcomp, -self.icomp))

    def trim(self, prec):
        if not isinstance(prec, int) or prec <= 0:
            raise ValueError('Only positive integers allowed')
        self.rcomp.trim(prec)
        self.icomp.trim(prec)
        return self

    def _from_raw(self, val): #looking for a+bi
        val = val.replace(' ', '')
        plus = val.find('+')
        eye = val.find('i')
        if plus == -1 and eye == -1: #real number
            return (IBReal(val), IBReal((0, 0)))
        elif plus == -1 and eye != -1: #imag number
            if val in ('i', '-i'): #allow bare-i notation
                val = val.replace('i', '1')
            else:
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
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        return other.__mul__(self)

    def __imul__(self, other):
        other = self.__mul__(other)
        (self.rcomp, self.icomp) = (other.rcomp, other.icomp)
        return self

    def __truediv__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        numer = self * other.conj
        denom = (other * other.conj).rcomp
        rcmp = numer.rcomp / denom
        icmp = numer.icomp / denom
        return type(self)((rcmp, icmp))

    def __itruediv__(self, other):
        other = self.__truediv__(other)
        (self.rcomp, self.icomp) = (other.rcomp, other.icomp)
        return self

    def __rtruediv__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        return other.__truediv__(self)

    def __add__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        return type(self)((self.rcomp+other.rcomp, self.icomp+other.icomp))

    def __radd__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        return other.__add__(self)

    def __iadd__(self, other):
        other = self.__add__(other)
        (self.rcomp, self.icomp) = (other.rcomp, other.icomp)
        return self

    def __sub__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        return type(self)((self.rcomp-other.rcomp, self.icomp-other.icomp))

    def __rsub__(self, other):
        if not isinstance(other, type(self)):
            rcmp = IBReal(other, **self.rcomp.kwargs)
            icmp = IBReal((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp))
        return other.__sub__(self)

    def __isub__(self, other):
        other = self.__sub__(other)
        (self.rcomp, self.icomp) = (other.rcomp, other.icomp)
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
        other = self.__pow__(oint)
        (self.rcomp, self.icomp) = (other.rcomp, other.icomp)
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

