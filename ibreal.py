from collections import namedtuple
from math import log

FLOAT_PREC = 16
Ival = namedtuple('Ival', 'num off')

class IBReal:
    """
    IBReal represents a memory-limited, arbitrary precision, integer-based implementation of a real number.
    it is probably slow. All math operations are available in in-line mode (i.e. +=).

    Usage:
    realnum = IBReal(raw, prec=300, trim_on=True)

    raw: IBReal object, number, Ival object, ascii repr of a real number, or tuple (integer, offset) -- where integer 
         is the integer after multiplying the real number by 10^offset. If using an IBReal instance, the precision
         will always be inherited from the object argument in spite of passing a prec val.

    prec: precision -- length limit of internal integer (self.ival.num)

    trim_on: allow trimming or not

    """
    def __init__(self, raw, prec=300, trim_on=True):
        self.trim_on = trim_on
        self.prec = prec
        try:
            if isinstance(raw, Ival):
                self.ival = raw
            elif isinstance(raw, tuple):
                self.ival = Ival(*raw)
            elif isinstance(raw, type(self)):
                self.ival = raw.ival
                self.prec = raw.prec #override arg
                self.trim_on = raw.trim_on
            elif isinstance(raw, int):
                self.ival = Ival(raw, 0)
            else: # coerce text or numbers to IBReal
                self.ival = self._from_raw(raw)
            self.trim()
        except Exception as e:
            raise ValueError('Failed to coerce {}:{} to Ival'.format(type(raw), raw)) from e 

    def trim(self, prec=None):
        if not self.trim_on:
            return self 
        prec = self.prec if prec is None else prec
        if not isinstance(prec, int) or prec <= 0:
            raise ValueError('Only positive integers allowed')
        if  self._ilength > prec:
            neg = 1
            tval = str(self.ival.num)
            if tval[0] == '-':
                tval = tval[1:]
                neg = -1
            tlen = len(tval)
            self.ival = Ival(neg*int(tval[:prec]), self.ival.off-tlen+prec)
        return self

    @property
    def kwargs(self):
        return {'prec':self.prec, 'trim_on':self.trim_on}

    @property
    def _repr(self):
        neg = '-' if self.ival.num < 0 else ''
        txt = str(abs(self.ival.num))
        if len(txt) > self.ival.off:
            return '{}{}.{}'.format(neg, txt[:len(txt)-self.ival.off], txt[len(txt)-self.ival.off:] or '0')
        else:
            return '{}{}.{}e-{}'.format(neg, txt[0], txt[1:] or '0', self.ival.off-len(txt)+1)
 
    @property
    def _ilength(self):
        if self.ival.num == 0:
            return 1
        return int(log(abs(self.ival.num), 10)) + 1
            
    def _from_raw(self, raw):
        straw = str(raw)
        if hasattr(raw, 'rcomp'):
            straw = str(raw.rcomp)
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
        
    def _align(self, siv, oiv):
        if siv.off > oiv.off:
            pad = 10 ** (siv.off-oiv.off)
            oiv = Ival(pad*oiv.num, siv.off)
        else:
            pad = 10 ** (oiv.off-siv.off)
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
        return type(self)(ival, **self.kwargs)

    def __rmul__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        return other.__mul__(self) 

    def __imul__(self, other):
        self.ival = self.__mul__(other).ival
        return self.trim()

    def __truediv__(self, other):
        try:
            if not isinstance(other, type(self)):
                other = type(self)(other, **self.kwargs)
        except Exception:
            return other.__rtruediv__(self)
        siv = self.ival
        oiv = other.ival
        mlen = self.prec + other._ilength - self._ilength - FLOAT_PREC
        num = siv.num * 10 ** mlen  // oiv.num
        rem = siv.num * 10 ** mlen  % oiv.num
        off = mlen + siv.off - oiv.off
        flt = rem / oiv.num #less than one
        flt *= 10 ** FLOAT_PREC #digits in float result
        num *= 10 ** FLOAT_PREC
        num += int(flt)
        off += FLOAT_PREC
        return type(self)(Ival(num, off), **self.kwargs).trim()

    def __rtruediv__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        return other.__truediv__(self)

    def __itruediv__(self, other):
        self.ival = self.__truediv__(other).ival
        return self.trim()

    def __add__(self, other):
        try:
            if not isinstance(other, type(self)):
                other = type(self)(other, **self.kwargs)
        except Exception:
            return other.__radd__(self)
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = Ival(siv.num+oiv.num, siv.off)
        return type(self)(ival, **self.kwargs)

    def __radd__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        return other.__add__(self)

    def __iadd__(self, other):
        self.ival = self.__add__(other).ival
        return self.trim()

    def __sub__(self, other):
        try:
            if not isinstance(other, type(self)):
                other = type(self)(other, **self.kwargs)
        except Exception:
            return other.__rsub__(self)
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = Ival(siv.num-oiv.num, siv.off)
        return type(self)(ival, **self.kwargs)

    def __rsub__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        return other.__sub__(self)

    def __isub__(self, other):
        self.ival = self.__sub__(other).ival
        return self.trim()

    def __pow__(self, oint):
        if not isinstance(oint, int) or oint < 0:
            raise ValueError('Only non-negative integers allowed')
        tmp = type(self)(self.ival, **self.kwargs)
        if oint == 0:
            tmp.ival = Ival(1, 0)
        else:
            for _ in range(1, oint):
                tmp *= self
        return tmp 
        
    def __ipow__(self, oint):
        self.ival = self.__pow__(oint).ival
        return self.trim()

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

