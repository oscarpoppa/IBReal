from collections import namedtuple
from math import log
from os import environ

# the internal integer pair representing a real by (number, offset)
# where number is an integer representing all the digits in a real
# and offset is the number of places from the right where the decimal
# point should be i.e (12345, 2) represents 123.45
Ival = namedtuple('Ival', 'num off')

# arbitrary-precision real number
class IBReal:
    """
    IBReal represents a memory-limited, arbitrary precision, integer-based implementation of a real number.
    it is probably slow. All math operations are available in in-line mode (i.e. +=).

    Usage:
    realnum = IBReal(raw, prec=300, trim_on=True, rep=None)

    raw: IBReal object, number, Ival object, ascii repr of a real number, or tuple (integer, offset) -- where integer 
         is the integer after multiplying the real number by 10^offset. If using an IBReal instance, the precision
         will always be inherited from the object argument in spite of passing a prec val.

    prec: precision -- length limit of internal integer (self.ival.num)

    trim_on: allow trimming or not

    rep: any special name for this number

    $export IBR_DEF_PREC=450 :: set environment var to pick up global precision
    """
    def __init__(self, raw, prec=None, trim_on=True, rep=None):
        if prec is not None:
            self.prec = prec
        elif 'IBR_DEF_PREC' in environ:
            # precision from environment
            self.prec = int(environ['IBR_DEF_PREC'])
        else:
            # default without environment var
            self.prec = 50 
        self.trim_on = trim_on
        self.rep = rep
        try:
            # Ival instance
            if isinstance(raw, Ival):
                self.ival = raw
            # 2-tuple representing ival members
            elif isinstance(raw, tuple):
                self.ival = Ival(*raw)
            # another IBReal instance
            elif isinstance(raw, type(self)):
                self.ival = raw.ival
                self.prec = prec or raw.prec
            # an integer
            elif isinstance(raw, int):
                self.ival = Ival(raw, 0)
            # something else -- text or float
            else:
                self.ival = self._from_raw(raw)
            self.trim()
        except Exception as e:
            raise ValueError('Failed to coerce {}:{} to Ival'.format(type(raw), raw)) from e

    # display trim -- no side effects on self
    def dtrim(self, prec=None):
        prec = self.prec if prec is None else prec
        if not isinstance(prec, int) or prec <= 0:
            raise TypeError('Only positive integers allowed')
        if  self.ilength > prec+1:
            tval = str(self.ival.num)
            if tval[0] == '-':
                tval = tval[1:]
            tlen = len(tval)
            return type(self)(Ival(ib_sgn(self.ival.num)*int(tval[:prec]), self.ival.off-tlen+prec), **self.kwargs)
        return self

    # in-place trim to precision -- side effects
    def trim(self, prec=None):
        if not self.trim_on:
            return self
        prec = self.prec if prec is None else prec
        self.ival = self.dtrim(prec=prec).ival
        return self

    @property
    def kwargs(self):
        return {'prec':self.prec, 'trim_on':self.trim_on}

    # true if self's value is effectively an integer (i.e 2.0000000000000000000)
    # concerned about int roundoff
    @property
    def isint(self):
        return self == int(self)

    @property
    def _repr(self):
        if self.rep is not None:
            return self.rep
        neg = '-' if self.ival.num < 0 else ''
        txt = str(abs(self.ival.num))
        if len(txt) > self.ival.off:
            return '{}{}.{}'.format(neg, txt[:len(txt)-self.ival.off], txt[len(txt)-self.ival.off:] or '0')
        else:
            return '{}{}.{}e-{}'.format(neg, txt[0], txt[1:] or '0', self.ival.off-len(txt)+1)

    # length of internal integer
    @property
    def ilength(self):
        if self.ival.num == 0:
            return 1
        return int(log(abs(self.ival.num), 10)) + 1

    # coercion engine
    def _from_raw(self, raw):
        straw = str(raw)
        straw = straw.replace(' ', '')
        if straw[0] == '-':
            neg = -1
            straw = straw[1:]
        else:
            neg = 1
        exp = straw.find('e-')
        if exp == -1:
            exp = None
            ev = 0
        else:
            ev = int(straw[exp+2:])
        dot = straw.find('.')
        if dot == -1:
            dot = len(straw[:exp])
        straw = straw[:dot] + straw[dot+1:exp]
        off = len(straw) - dot + ev
        return Ival(neg*int(straw), off)

    # ensure decimal alignment for addition and subtraction
    def _align(self, siv, oiv):
        if siv.off > oiv.off:
            pad = 10**(siv.off-oiv.off)
            oiv = Ival(pad*oiv.num, siv.off)
        else:
            pad = 10**(oiv.off-siv.off)
            siv = Ival(pad*siv.num, oiv.off)
        return (siv, oiv)

    def __mul__(self, other):
        try:
            if not isinstance(other, type(self)):
                other = type(self)(other, **self.kwargs)
        except Exception:
            return other.__rmul__(self)
        oiv = other.ival
        siv = self.ival
        ival = Ival(siv.num*oiv.num, siv.off+oiv.off)
        return type(self)(ival, **self.kwargs).trim()

    def __rmul__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        return other.__mul__(self)

    def __imul__(self, other):
        self.ival = self.__mul__(other).ival
        return self

    def __truediv__(self, other):
        try:
            if not isinstance(other, type(self)):
                other = type(self)(other, **self.kwargs)
        except Exception:
            return other.__rtruediv__(self)
        siv = self.ival
        oiv = other.ival
        mlen = self.prec + other.ilength - self.ilength
        num = siv.num * 10**mlen  // oiv.num
        off = mlen + siv.off - oiv.off
        return type(self)(Ival(num, off), **self.kwargs).trim()

    def __rtruediv__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        return other.__truediv__(self)

    def __itruediv__(self, other):
        self.ival = self.__truediv__(other).ival
        return self

    def __floordiv__(self, other):
        return type(self)(int(self.__truediv__(other)))

    def __rfloordiv__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        return other.__floordiv__(self)

    def __ifloordiv__(self, other):
        self.ival = self.__floordiv__(other).ival
        return self

    def __add__(self, other):
        try:
            if not isinstance(other, type(self)):
                other = type(self)(other, **self.kwargs)
        except Exception:
            return other.__radd__(self)
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = Ival(siv.num+oiv.num, siv.off)
        return type(self)(ival, **self.kwargs).trim()

    def __radd__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        return other.__add__(self)

    def __iadd__(self, other):
        self.ival = self.__add__(other).ival
        return self

    def __sub__(self, other):
        try:
            if not isinstance(other, type(self)):
                other = type(self)(other, **self.kwargs)
        except Exception:
            return other.__rsub__(self)
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = Ival(siv.num-oiv.num, siv.off)
        return type(self)(ival, **self.kwargs).trim()

    def __rsub__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        return other.__sub__(self)

    def __isub__(self, other):
        self.ival = self.__sub__(other).ival
        return self

    def __pow__(self, other):
        try:
            if not isinstance(other, type(self)):
                other = type(self)(other, **self.kwargs)
        except Exception:
            return other.__rpow__(self)
        tmp = type(self)(self.ival, **self.kwargs)
        if other == 0:
            tmp.ival = Ival(1, 0)
            return tmp.trim()
        if isinstance(other, type(self)) and other.isint:
            # !! Leave int section alone -- needed for series expansions
            for _ in range(1, abs(int(other))):
                tmp *= self
            if other < 0:
                tmp = type(self)(Ival(1, 0), **self.kwargs).__truediv__(tmp)
        else:
            sl = ib_log(self)
            tmp = ib_exp(sl*other)
        return tmp.trim(other.prec)

    def __rpow__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        return other.__pow__(self)

    def __ipow__(self, other):
        self.ival = self.__pow__(other).ival
        return self

    def __int__(self):
        return int(self.__float__())

    def __float__(self):
        return self.ival.num/10**self.ival.off

    def __neg__(self):
        return type(self)(Ival(-self.ival.num, self.ival.off), **self.kwargs)

    def __abs__(self):
        return type(self)(Ival(abs(self.ival.num), self.ival.off), **self.kwargs)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        (siv, oiv) = self._align(self.ival, other.ival)
        return siv.num == oiv.num

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        (siv, oiv) = self._align(self.ival, other.ival)
        return siv.num < oiv.num

    def __gt__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        (siv, oiv) = self._align(self.ival, other.ival)
        return siv.num > oiv.num

    def __le__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        (siv, oiv) = self._align(self.ival, other.ival)
        return siv.num <= oiv.num

    def __ge__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        (siv, oiv) = self._align(self.ival, other.ival)
        return siv.num >= oiv.num

    def __ne__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        (siv, oiv) = self._align(self.ival, other.ival)
        return siv.num != oiv.num

    def __str__(self):
        return self.trim()._repr

    def __repr__(self):
        return self.trim()._repr

# here to prevent circular import
from .ibfuncs import ib_exp, ib_log, ib_sgn
