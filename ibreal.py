class IBReal:
    """
    IBReal represents a memory-limited, arbitrary precision, integer-based implementation of a real number.
    It offers addition, subtraction, powers, and multiplication only, which is OK for iteration exploration, albeit
    probably slow. All math operations are available in in-line mode (i.e. +=).

    Usage:
    realnum = IBReal(raw)

    raw: ascii real number in decimal notation OR tuple (integer, offset), where integer is the integer after multiplying the real
         number by 10^offset.

    prec: precision (bit_length) assumed to be roughly 3 times char length

    """
    def __init__(self, raw, prec=3000):
        self.prec = prec
        self.ival = self._from_txt(raw) if type(raw) == str else raw
        self.trim()

    @property
    def tval(self):
        neg = '-' if self.ival[0] < 0 else ''
        txt = str(abs(self.ival[0]))
        if len(txt) > self.ival[1]:
            return '{}{}.{}'.format(neg, txt[:len(txt)-self.ival[1]], txt[len(txt)-self.ival[1]:] or '0')
        else:
            return '{}0.{}{}'.format(neg, '0'*(self.ival[1]-len(txt)), txt)

    def trim(self):
        if self.ival[0].bit_length() > self.prec:
            tval = str(self.ival[0])
            tlen = len(tval)
            cprec = int(self.prec/3) #need to check out bl vs cl
            if cprec < tlen:
                self.ival = (int(tval[:cprec]), self.ival[1] - tlen + cprec)
        return self
            
    def _from_txt(self, val):
        neg = 1
        if val[0] == '-':
            neg = -1
            val = val[1:]
        dot = val.find('.')
        if dot == -1:
            dot = len(val)
        val = val[:dot] + val[dot+1:]
        off = len(val) - dot
        return (neg*int(val), off)
        
    def _align(self, siv, oiv):
        if siv[1] > oiv[1]:
            pad = 10 ** (siv[1]-oiv[1])
            oiv = (pad * oiv[0], siv[1])
        else:
            pad = 10 ** (oiv[1]-siv[1])
            siv = (pad * siv[0], oiv[1])
        return (siv, oiv)

    def __float__(self):
        return self.ival[0]/10**self.ival[1]

    def __mul__(self, other):
        oiv = other.ival
        siv = self.ival
        ival = (siv[0]*oiv[0], siv[1]+oiv[1])
        return type(self)(ival, self.prec)

    def __imul__(self, other):
        oiv = other.ival
        siv = self.ival
        self.ival = (siv[0]*oiv[0], siv[1]+oiv[1])
        return self.trim()

    def __add__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = (siv[0]+oiv[0], siv[1])
        return type(self)(ival, self.prec)

    def __iadd__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        self.ival = (siv[0]+oiv[0], siv[1])
        return self.trim()

    def __sub__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = (siv[0]-oiv[0], siv[1])
        return type(self)(ival, self.prec)

    def __isub__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        self.ival = (siv[0]-oiv[0], siv[1])
        return self.trim()

    def __pow__(self, oint): #integer power only
        tmp = type(self)(self.ival, self.prec)
        if type(oint) == int:
            if oint == 0:
                tmp.ival = (1,0)
            else:
                for i in range(1, oint):
                    tmp *= self
        return tmp 
        
    def __ipow__(self, oint): #integer power only
        tmp = type(self)(self.ival, self.prec)
        if type(oint) == int:
            if oint == 0:
                self.ival = (1,0)
            else:
                for i in range(1, oint):
                    self *= tmp
        return self.trim()
        
    def __str__(self):
        return self.trim().tval

    def __repr__(self):
        return self.trim().tval

