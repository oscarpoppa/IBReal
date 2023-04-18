from collections import namedtuple

Ival = namedtuple('Ival', 'num off')

class IBReal:
    """
    IBReal represents a memory-limited, arbitrary precision, integer-based implementation of a real number.
    It offers addition, subtraction, powers, and multiplication only, which is OK for iteration exploration, albeit
    probably slow. All math operations are available in in-line mode (i.e. +=).

    Usage:
    realnum = IBReal(raw, prec)

    raw: Ival object, ascii real number in decimal notation or tuple (integer, offset), where integer is the integer after multiplying the real
         number by 10^offset.

    prec: precision -- length limit of digits to right of decimal

    """
    def __init__(self, raw, prec=300):
        self.prec = prec
        self.ival = raw if type(raw) == Ival else Ival(*raw) if type(raw) == tuple else self._from_txt(raw)
        self.trim()

    @property
    def tval(self):
        neg = '-' if self.ival.num < 0 else ''
        txt = str(abs(self.ival.num))
        if len(txt) > self.ival.off:
            return '{}{}.{}'.format(neg, txt[:len(txt)-self.ival.off], txt[len(txt)-self.ival.off:] or '0')
        else:
            return '{}{}.{}e-{}'.format(neg, txt[0], txt[1:] or '0', self.ival.off-len(txt)+1)

    def trim(self, prec=None):
        prec = self.prec if not prec else abs(prec)
        if self.ival.off > prec:
            tval = str(self.ival.num)
            tlen = len(tval)
            if prec < tlen:
                self.ival = Ival(int(tval[:prec]), self.ival.off-tlen+prec)
        return self
            
    def _from_txt(self, val):
        neg = 1
        if val[0] == '-':
            neg = -1
            val = val[1:]
        dot = val.find('.')
        if dot == -1:
            dot = len(val)
        exp = val.find('e-')
        if exp == -1:
            exp = None
            ev = 0
        else:
            ev = int(val[exp+2:])
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

    def __float__(self):
        return self.ival.num/10**self.ival.off

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
                for i in range(1, oint):
                    tmp *= self
        return tmp 
        
    def __ipow__(self, oint): #integer power only
        tmp = type(self)(self.ival, self.prec)
        if type(oint) == int:
            if oint <= 0:
                self.ival = Ival(1,0)
            else:
                for i in range(1, oint):
                    self *= tmp
        return self.trim()
        
    def __str__(self):
        return self.trim().tval

    def __repr__(self):
        return self.trim().tval

