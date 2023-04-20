from collections import namedtuple

Ival = namedtuple('Ival', 'num off')

class IBReal:
    """
    IBReal represents a memory-limited, arbitrary precision, integer-based implementation of a real number.
    It offers addition, subtraction, powers, and multiplication only, which is OK for iteration exploration, albeit
    probably slow. All math operations are available in in-line mode (i.e. +=).

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
        tp = type(raw)
        if tp == Ival:
            self.ival = raw
        elif tp == tuple:
            self.ival = Ival(*raw)
        elif tp == type(self):
            self.ival = raw.ival
            self.prec = raw.prec #override arg
            self.trim_on = raw.trim_on
        elif tp == int:
            self.ival = Ival(raw, 0)
        else: #textify any numbers
            self.ival = self._from_txt(str(raw))
        self.trim()

    def trim(self, prec=None):
        if not self.trim_on:
            return self 
        prec = self.prec if prec is None else prec
        if not isinstance(prec, int) or prec <= 0:
            raise ValueError('Only positive integers allowed')
        if abs(self.ival.num) > 10**prec:
            neg = 1
            tval = str(self.ival.num)
            if tval[0] == '-':
                tval = tval[1:]
                neg = -1
            tlen = len(tval)
            self.ival = Ival(neg*int(tval[:prec]), self.ival.off-tlen+prec)
        return self

    @property
    def kwargs(self): #read-only kwargs
        return {'prec':self.prec, 'trim_on':self.trim_on}

    @property
    def _repr(self):
        neg = '-' if self.ival.num < 0 else ''
        txt = str(abs(self.ival.num))
        if len(txt) > self.ival.off:
            return '{}{}.{}'.format(neg, txt[:len(txt)-self.ival.off], txt[len(txt)-self.ival.off:] or '0')
        else:
            return '{}{}.{}e-{}'.format(neg, txt[0], txt[1:] or '0', self.ival.off-len(txt)+1)
            
    def _from_txt(self, val):
        if val[0] == '-':
            neg = -1
            val = val[1:]
        else:
            neg = 1
        exp = val.find('e-')
        if exp == -1:
            exp = None
            ev = 0
        else:
            ev = int(val[exp+2:])
        dot = val.find('.')
        if dot == -1:
            dot = len(val[:exp])
        val = val[:dot] + val[dot+1:exp]
        off = len(val) - dot + ev
        return Ival(neg*int(val), off)
        
    def _align(self, siv, oiv):
        if siv.off > oiv.off:
            pad = 10**(siv.off-oiv.off)
            oiv = Ival(pad*oiv.num, siv.off)
        else:
            pad = 10**(oiv.off-siv.off)
            siv = Ival(pad*siv.num, oiv.off)
        return (siv, oiv)

    def __mul__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        oiv = other.ival
        siv = self.ival
        ival = Ival(siv.num*oiv.num, siv.off+oiv.off)
        return type(self)(ival, prec=self.prec)

    def __rmul__(self, other):
        return self.__mul__(other) 

    def __imul__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs) 
        oiv = other.ival
        siv = self.ival
        self.ival = Ival(siv.num*oiv.num, siv.off+oiv.off)
        return self.trim()

    def __add__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = Ival(siv.num+oiv.num, siv.off)
        return type(self)(ival, prec=self.prec)

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        (siv, oiv) = self._align(self.ival, other.ival)
        self.ival = Ival(siv.num+oiv.num, siv.off)
        return self.trim()

    def __sub__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = Ival(siv.num-oiv.num, siv.off)
        return type(self)(ival, prec=self.prec)

    def __rsub__(self, other):
        return -self.__sub__(other)

    def __isub__(self, other):
        if not isinstance(other, type(self)):
            other = type(self)(other, **self.kwargs)
        (siv, oiv) = self._align(self.ival, other.ival)
        self.ival = Ival(siv.num-oiv.num, siv.off)
        return self.trim()

    def __pow__(self, oint):
        if not isinstance(oint, int) or oint < 0:
            raise ValueError('Only non-negative integers allowed')
        tmp = type(self)(self.ival, **self.kwargs)
        if oint == 0:
            tmp.ival = Ival(1,0)
        else:
            for _ in range(1, oint):
                tmp *= self
        return tmp 
        
    def __ipow__(self, oint):
        if not isinstance(oint, int) or oint < 0:
            raise ValueError('Only non-negative integers allowed')
        tmp = type(self)(self.ival, **self.kwargs)
        if oint == 0:
            self.ival = Ival(1,0)
        else:
            for _ in range(1, oint):
                self *= tmp
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

