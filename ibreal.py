from collections import namedtuple

Ival = namedtuple('Ival', 'num off')

class IBReal:
    """
    IBReal represents a memory-limited, arbitrary precision, integer-based implementation of a real number.
    It offers addition, subtraction, powers, and multiplication only, which is OK for iteration exploration, albeit
    probably slow. All math operations are available in in-line mode (i.e. +=).

    Usage:
    realnum = IBReal(raw, prec)

    raw: IBReal object, Ival object, ascii repr of a real number, or tuple (integer, offset) -- where integer 
         is the integer after multiplying the real number by 10^offset. If using an IBReal instance, the precision
         will always be inherited from the object argument in spite of passing a prec val.

    prec: precision -- length limit of internal integer (self.ival.num)

    """
    def __init__(self, raw, prec=300):
        self.prec = prec
        tp = type(raw)
        if tp == Ival:
            self.ival = raw
        elif tp == tuple:
            self.ival = Ival(*raw)
        elif tp == type(self):
            self.ival = raw.ival
            self.prec = raw.prec #override arg
        else: #assume text
            self.ival = self._from_txt(raw)
        self.trim()

    def trim(self, prec=None):
        prec = self.prec if not prec else abs(prec)
        if self.ival.num > 10**(prec+10): #+10 gives some wiggle room--change if too much trimming
            tval = str(self.ival.num)
            tlen = len(tval)
            self.ival = Ival(int(tval[:prec]), self.ival.off-tlen+prec)
        return self

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
            pad = 10 ** (siv.off-oiv.off)
            oiv = Ival(pad*oiv.num, siv.off)
        else:
            pad = 10 ** (oiv.off-siv.off)
            siv = Ival(pad*siv.num, oiv.off)
        return (siv, oiv)

    def __mul__(self, other):
        oiv = other.ival
        siv = self.ival
        ival = Ival(siv.num*oiv.num, siv.off+oiv.off)
        return type(self)(ival, self.prec)

    def __imul__(self, other):
        oiv = other.ival
        siv = self.ival
        self.ival = Ival(siv.num*oiv.num, siv.off+oiv.off)
        return self.trim()

    def __add__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = Ival(siv.num+oiv.num, siv.off)
        return type(self)(ival, self.prec)

    def __iadd__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        self.ival = Ival(siv.num+oiv.num, siv.off)
        return self.trim()

    def __sub__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = Ival(siv.num-oiv.num, siv.off)
        return type(self)(ival, self.prec)

    def __isub__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        self.ival = Ival(siv.num-oiv.num, siv.off)
        return self.trim()

    def __pow__(self, oint): #integer power only
        tmp = type(self)(self.ival, self.prec)
        if type(oint) == int:
            if oint <= 0:
                tmp.ival = Ival(1,0)
            else:
                for _ in range(1, oint):
                    tmp *= self
        return tmp 
        
    def __ipow__(self, oint): #integer power only
        tmp = type(self)(self.ival, self.prec)
        if type(oint) == int:
            if oint <= 0:
                self.ival = Ival(1,0)
            else:
                for _ in range(1, oint):
                    self *= tmp
        return self.trim()

    def __float__(self):
        return self.ival.num/10**self.ival.off

    def __neg__(self):
        return type(self)(Ival(-self.ival.num, self.ival.off), self.prec)

    def __abs__(self):
        return type(self)(Ival(abs(self.ival.num), self.ival.off), self.prec)
        
    def __eq__(self, other): #won't differentiate between (100,2) and (1000, 3)
        (siv, oiv) = self._align(self.ival, other.ival)
        return siv.num == oiv.num

    def __lt__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        return siv.num < oiv.num

    def __gt__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        return siv.num > oiv.num

    def __le__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        return siv.num <= oiv.num
    
    def __ge__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        return siv.num >= oiv.num

    def __ne__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        return siv.num != oiv.num

    def __str__(self):
        return self.trim()._repr

    def __repr__(self):
        return self.trim()._repr

