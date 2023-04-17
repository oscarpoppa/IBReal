from ibreal import IBReal
from math import sqrt

class IBComp:
    """
    IBComp is a complex number that uses the precision of IBReal numbers. The math interface offers the same ioperations as IBReal offers.
  
    Usage:
    comp = IBComp(rcomp, icomp)

    rcomp & icomp: IBReal object, string, or tuple(IBReal style)
    """
    def __init__(self, rcomp, icomp):
        #string, tuple or IBReal
        self.rcomp = IBReal(rcomp) if type(rcomp) != IBReal else rcomp
        self.icomp = IBReal(icomp) if type(icomp) != IBReal else icomp

    @property
    def length(self):
        slen = self.rcomp**2 + self.icomp**2
        return sqrt(float(slen))

    def trim(self, prec):
        for ibr in (self.rcomp, self.icomp):
            tval = str(ibr.ival[0])
            tlen = len(tval)
            if prec < tlen:
                ibr.ival = (int(tval[:prec]), ibr.ival[1] - tlen + prec)

    def __mul__(self, other):
        if type(other) == IBReal:
            other = type(self)(other, IBReal((0,0)))
        return type(self)(self.rcomp*other.rcomp-self.icomp*other.icomp, self.rcomp*other.icomp+self.icomp*other.rcomp)

    def __imul__(self, other):
        if type(other) == IBReal:
            other = type(self)(other, IBReal((0,0)))
        self.rcomp = self.rcomp*other.rcomp-self.icomp*other.icomp
        self.icomp = self.rcomp*other.icomp+self.icomp*other.rcomp
        return self

    def __add__(self, other):
        if type(other) == IBReal:
            other = type(self)(other, IBReal((0,0)))
        return type(self)(self.rcomp+other.rcomp, self.icomp+other.icomp)

    def __iadd__(self, other):
        if type(other) == IBReal:
            other = type(self)(other, IBReal((0,0)))
        self.rcomp = self.rcomp+other.rcomp
        self.icomp = self.icomp+other.icomp
        return self

    def __sub__(self, other):
        if type(other) == IBReal:
            other = type(self)(other, IBReal((0,0)))
        return type(self)(self.rcomp-other.rcomp, self.icomp-other.icomp)

    def __isub__(self, other):
        if type(other) == IBReal:
            other = type(self)(other, IBReal((0,0)))
        self.rcomp = self.rcomp-other.rcomp
        self.icomp = self.icomp-other.icomp
        return self

    def __pow__(self, oint):
        tmp = type(self)(self.rcomp, self.icomp)
        if type(oint) == int:
            if oint == 0:
                tmp.rcomp = IBReal((1,0))
                tmp.icomp = IBReal((0,0))
            else: 
                for i in range(1, oint):
                    tmp *= self 
        return tmp 

    def __ipow__(self, oint):
        tmp = type(self)(self.rcomp, self.icomp)
        if type(oint) == int:
            if oint == 0:
                self.rcomp = IBReal((1,0))
                self.icomp = IBReal((0,0))
            else: 
                for i in range(1, oint):
                    self *= tmp 
        return self 

    def __str__(self):
        self.trim(self.rcomp.prec)
        return '{} + {}i'.format(self.rcomp, self.icomp)

    def __repr__(self):
        self.trim(self.rcomp.prec)
        return '{} + {}i'.format(self.rcomp, self.icomp)

