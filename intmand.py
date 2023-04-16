#!/usr/bin/env python

class IBReal:
    def __init__(self, raw, prec=500):
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
        tval = str(self._ival[0])
        tlen = len(tval)
        offs = self._ival[1]
        if tlen > offs:
            self._tval = '{}.{}'.format(tval[:tlen-offs], tval[tlen-offs:])
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
        if dot == -1: #no point
            self._tval += '.0'
        offset = len(self._tval) - self._tval.find('.') - 1
        ival = int(self._tval.replace('.',''))
        self._ival = (ival, offset)
        
    def _align(self, siv, oiv):
        if siv[1] > oiv[1]:
            pad = 10 ** (siv[1]-oiv[1])
            nuival = pad * oiv[0]
            oiv = (nuival, siv[1])
        else:
            pad = 10 ** (oiv[1]-siv[1])
            nuival = pad * siv[0]
            siv = (nuival, oiv[1])
        return (siv, oiv)

    def __mul__(self, other):
        oiv = other.ival
        siv = self.ival
        ival = (siv[0]*oiv[0], siv[1]+oiv[1])
        return IBReal(ival)

    def __imul__(self, other):
        oiv = other.ival
        siv = self.ival
        self.ival = (siv[0]*oiv[0], siv[1]+oiv[1])
        return self

    def __add__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = (siv[0]+oiv[0], siv[1])
        return IBReal(ival)

    def __iadd__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        self.ival = (siv[0]+oiv[0], siv[1])
        return self

    def __sub__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        ival = (siv[0]-oiv[0], siv[1])
        return IBReal(ival)

    def __isub__(self, other):
        (siv, oiv) = self._align(self.ival, other.ival)
        self.ival = (siv[0]-oiv[0], siv[1])
        return self

    def __str__(self):
        return self.tval

    def __repr__(self):
        return self.tval

