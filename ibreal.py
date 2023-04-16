#!/usr/bin/env python

class IBReal:
    """
    IBReal represents a memory-limited, arbitrary precision, integer-based implementation of a real number.
    It offers addition, subtraction, and multiplication only, which is OK for iteration exploration, albeit
    probably slow. All math operations are available in in-line mode (i.e. +=).

    Usage:
    realnum = IBReal(raw, prec, fast_ivs)

    raw: ascii real number in decimal notation OR tuple (integer, offset), where integer is the integer after multiplying the real
         number by 10^offset.

    prec: precision   

    fast_ivs: exclude text generation overhead. SB faster for extended calculation.
    """
    def __init__(self, raw, prec=500, fast_ivs=False):
        self.fast_ivs = fast_ivs
        self.prec = prec
        if type(raw) == str:
            self.tval = raw
        else:
            self.ival = raw #tuple

    @property
    def ival(self):
        return self._ival

    @ival.setter
    def ival(self, val): #val SB a tuple
        self._ival = val
        if not self.fast_ivs:
            offs = self._ival[1]
            tval = str(self._ival[0])
            tlen = len(tval)
            if tlen > offs:
                self._tval = '{}.{}'.format(tval[:tlen-offs], tval[tlen-offs:] or '0')
            else:
                self._tval = '0.{}{}'.format('0'*(offs-tlen), tval)
            self._tval = self._tval[:self.prec] #trim
        
    @property
    def tval(self):
        return self._tval

    @tval.setter
    def tval(self, val):
        self._tval = val[:self.prec] #trim
        dot = self._tval.find('.')
        if dot == 0: #no zero
            self._tval = '0{}'.format(self._tval)
        elif dot == -1: #no point
            if self._tval[0] == '0': #leading zero
                self._tval = '0.{}'.format(self._tval)
            else:
                self._tval = '{}.0'.format(self._tval)
        offset = len(self._tval) - self._tval.find('.') - 1
        ival = int(self._tval.replace('.',''))
        self._ival = (ival, offset)
        
    def _align(self, siv, oiv):
        if siv[1] > oiv[1]:
            pad = 10 ** (siv[1]-oiv[1])
            oiv = (pad * oiv[0], siv[1])
        else:
            pad = 10 ** (oiv[1]-siv[1])
            siv = (pad * siv[0], oiv[1])
        return (siv, oiv)

    def __mul__(self, other):
        oiv = other.ival
        siv = self.ival
        ival = (siv[0]*oiv[0], siv[1]+oiv[1])
        return type(self)(ival, prec=self.prec, fast_ivs=self.fast_ivs)

    def __imul__(self, other):
        oiv = other.ival
        siv = self.ival
        self.ival = (siv[0]*oiv[0], siv[1]+oiv[1])
        return self

    def __add__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = (siv[0]+oiv[0], siv[1])
        return type(self)(ival, prec=self.prec, fast_ivs=self.fast_ivs)

    def __iadd__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        self.ival = (siv[0]+oiv[0], siv[1])
        return self

    def __sub__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = (siv[0]-oiv[0], siv[1])
        return type(self)(ival, prec=self.prec, fast_ivs=self.fast_ivs)

    def __isub__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        self.ival = (siv[0]-oiv[0], siv[1])
        return self

    def __pow__(self, oint): #integer power only
        tmp = type(self)(self.ival, prec=self.prec, fast_ivs=self.fast_ivs)
        if type(oint) == int:
            if oint == 0:
                tmp.ival = (1,0)
            else:
                for i in range(1, oint):
                    tmp *= self
        return tmp 
        
    def __ipow__(self, oint): #integer power only
        tmp = type(self)(self.ival, prec=self.prec, fast_ivs=self.fast_ivs)
        if type(oint) == int:
            if oint == 0:
                self.ival = (1,0)
            else:
                for i in range(1, oint):
                    self *= tmp
        return self 
        
    def __str__(self):
        return '<FAST:{}>'.format(self.ival) if self.fast_ivs else self.tval

    def __repr__(self):
        return '<FAST:{}>'.format(self.ival) if self.fast_ivs else self.tval

