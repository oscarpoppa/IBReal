from os import environ

class IBComp:
    """
    IBComp is a complex number that uses the precision of IBReal numbers. The math interface offers the 
    same ioperations IBReal offers.

    Usage:
    comp = IBComp(raw, prec=None, trim_on=True, rep=None)

    raw: tuple of rcomp & icomp, IBReal object, Ival object, number, string, or 2-tuple

    rep: any special name for this number

    $export IBR_DEF_PREC=450 :: set environment var to pick up global precision
    """
    def __init__(self, raw, prec=None, trim_on=True, rep=None):
        if prec is not None:
            self.prec = prec
        elif 'IBR_DEF_PREC' in environ:
            self.prec = int(environ['IBR_DEF_PREC'])
        else:
            self.prec = 100 
        self.trim_on = trim_on
        self.rep = rep
        try:
            if isinstance(raw, tuple):
                self.rcomp = raw[0] if isinstance(raw[0], R) else R(raw[0], **self.kwargs)
                self.icomp = raw[1] if isinstance(raw[1], R) else R(raw[1], **self.kwargs)
            elif isinstance(raw, type(self)):
                self.rcomp = raw.rcomp
                self.icomp = raw.icomp
            elif isinstance(raw, int):
                self.rcomp = R(raw, **self.kwargs)
                self.icomp = R((0, 0), **self.kwargs)
            elif isinstance(raw, R):
                self.rcomp = raw
                self.icomp = R((0, 0), **raw.kwargs)
            else:
                (self.rcomp, self.icomp) = self._from_raw(str(raw))
        except Exception as e:
            raise ValueError('Failed to coerce {}:{} to IBReal pair'.format(type(raw), raw)) from e

    @property
    def kwargs(self):
        return {'prec':self.prec, 'trim_on':self.trim_on}

    @property
    def length(self):
        two = R((2, 0), **self.kwargs)
        slen = self.rcomp**two + self.icomp**two
        return ib_sqrt(slen)

    @property
    def theta(self):
        zero = R((0, 0), **self.kwargs)
        two = R((2, 0), **self.kwargs)
        mypi = ib_pi(**self.kwargs)
        my2pi = two * mypi
        if self.rcomp == zero:
            return mypi/two if self.icomp > zero else -mypi/two
        th = ib_arctan(self.icomp/self.rcomp)
        if self.rcomp < zero:
            th = th + mypi
        while abs(th) > mypi:
            # return canonical form
            th += (my2pi if th < 0 else -my2pi)
        return th

    @property
    def conj(self):
        return type(self)((self.rcomp, -self.icomp), **self.kwargs)

    def dtrim(self, prec):
        if not isinstance(prec, int) or prec <= 0:
            raise ValueError('Only positive integers allowed')
        rcmp = self.rcomp.dtrim(prec)
        icmp = self.icomp.dtrim(prec)
        return type(self)((rcmp, icmp), **self.kwargs)

    def trim(self, prec):
        trm = self.dtrim(prec=prec)
        (self.rcomp, self.icomp) = (trm.rcomp, trm.icomp)
        return self

    def _repr(self):
        if self.rep is not None:
            return self.rep
        return '{} + {}i'.format(self.rcomp, self.icomp)

    def _from_raw(self, val): #looking for a+bi
        val = val.replace(' ', '')
        plus = val.find('+')
        eye = val.find('i')
        if plus == -1 and eye == -1: #real number
            return (R(val, **self.kwargs), R((0, 0), **self.kwargs))
        elif plus == -1 and eye != -1: #imag number
            if val in ('i', '-i'): #allow bare-i notation
                val = val.replace('i', '1')
            else:
                val = val[:eye]
            return (R((0, 0), **self.kwargs), R(val, **self.kwargs))
        elif plus != -1 and eye != -1: #comp number
            return (R(val[:plus], **self.kwargs), R(val[plus+1:eye], **self.kwargs))

    def __mul__(self, other):
        if not isinstance(other, type(self)):
            rcmp = R(other, **self.rcomp.kwargs)
            icmp = R((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp), **self.kwargs)
        rcmp = R(self.rcomp*other.rcomp-self.icomp*other.icomp, **self.rcomp.kwargs)
        icmp = R(self.rcomp*other.icomp+self.icomp*other.rcomp, **self.icomp.kwargs)
        return type(self)((rcmp, icmp), **self.kwargs)

    def __rmul__(self, other):
        if not isinstance(other, type(self)):
            rcmp = R(other, **self.rcomp.kwargs)
            icmp = R((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp), **self.kwargs)
        return other.__mul__(self)

    def __imul__(self, other):
        other = self.__mul__(other)
        (self.rcomp, self.icomp) = (other.rcomp, other.icomp)
        return self

    def __truediv__(self, other):
        if not isinstance(other, type(self)):
            rcmp = R(other, **self.rcomp.kwargs)
            icmp = R((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp), **self.kwargs)
        numer = self * other.conj
        denom = (other * other.conj).rcomp
        rcmp = numer.rcomp / denom
        icmp = numer.icomp / denom
        return type(self)((rcmp, icmp), **self.kwargs)

    def __itruediv__(self, other):
        other = self.__truediv__(other)
        (self.rcomp, self.icomp) = (other.rcomp, other.icomp)
        return self

    def __rtruediv__(self, other):
        if not isinstance(other, type(self)):
            rcmp = R(other, **self.rcomp.kwargs)
            icmp = R((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp), **self.kwargs)
        return other.__truediv__(self)

    def __add__(self, other):
        if not isinstance(other, type(self)):
            rcmp = R(other, **self.rcomp.kwargs)
            icmp = R((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp), **self.kwargs)
        return type(self)((self.rcomp+other.rcomp, self.icomp+other.icomp), **self.kwargs)

    def __radd__(self, other):
        if not isinstance(other, type(self)):
            rcmp = R(other, **self.rcomp.kwargs)
            icmp = R((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp), **self.kwargs)
        return other.__add__(self)

    def __iadd__(self, other):
        other = self.__add__(other)
        (self.rcomp, self.icomp) = (other.rcomp, other.icomp)
        return self

    def __sub__(self, other):
        if not isinstance(other, type(self)):
            rcmp = R(other, **self.rcomp.kwargs)
            icmp = R((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp), **self.kwargs)
        return type(self)((self.rcomp-other.rcomp, self.icomp-other.icomp), **self.kwargs)

    def __rsub__(self, other):
        if not isinstance(other, type(self)):
            rcmp = R(other, **self.rcomp.kwargs)
            icmp = R((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp), **self.kwargs)
        return other.__sub__(self)

    def __isub__(self, other):
        other = self.__sub__(other)
        (self.rcomp, self.icomp) = (other.rcomp, other.icomp)
        return self

    def __pow__(self, other):
        if not isinstance(other, type(self)) and not isinstance(other, R):
            other = R(other, **self.kwargs)
        tmp = type(self)((self.rcomp, self.icomp))
        if other == 0:
            tmp.rcomp = R((1, 0), **self.rcomp.kwargs)
            tmp.icomp = R((0, 0), **self.icomp.kwargs)
            return tmp
        if isinstance(other, R) and other.isint:
            # !! Leave int section alone -- needed for series expansions
            for _ in range(1, abs(int(other))):
                tmp *= self
            if other < 0:
                rcmp = R((1, 0), **self.rcomp.kwargs)
                icmp = R((0, 0), **self.icomp.kwargs)
                return type(self)((rcmp, icmp), **self.kwargs).__truediv__(tmp)
        else:
            sl = ib_log(tmp)
            tmp = ib_exp(sl*other)
        return tmp

    def __rpow__(self, val):
        if not isinstance(val, type(self)):
            val = type(self)(val, **self.kwargs)
        return val.__pow__(self)

    def __ipow__(self, val):
        other = self.__pow__(val)
        (self.rcomp, self.icomp) = (other.rcomp, other.icomp)
        return self

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            rcmp = R(other, **self.rcomp.kwargs)
            icmp = R((0, 0), **self.icomp.kwargs)
            other = type(self)((rcmp, icmp), **self.kwargs)
        return self.rcomp == other.rcomp and self.icomp == other.icomp

    def __neg__(self):
        return type(self)((-self.rcomp, -self.icomp), **self.kwargs)

    def __str__(self):
        return  self._repr()

    def __repr__(self):
        return  self._repr()

# here to prevent circular import
from .ibreal import IBReal as R
from .ibfuncs import ib_sqrt, ib_arctan, ib_pi, ib_sin, ib_cos, ib_log, ib_exp
