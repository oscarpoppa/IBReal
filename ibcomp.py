from ibreal import IBReal
from math import sqrt

class IBComp:
    """
    IBComp is a complex number that uses the precision of IBReal numbers. The math interface offers the 
    same ioperations IBReal offers.
  
    Usage:
    comp = IBComp(rcomp, icomp)

    rcomp & icomp: IBReal object, Ival object, string, or 2-tuple
    """
    def __init__(self, rcomp, icomp):
        #string, tuple or IBReal
        self.rcomp = IBReal(rcomp) if type(rcomp) != IBReal else rcomp
        self.icomp = IBReal(icomp) if type(icomp) != IBReal else icomp

    @property #still within our precision space. May be helpful for comparisons.
    def lengthsq(self):
        return self.rcomp**2 + self.icomp**2

    @property #Chops off to fit float precision
    def length(self):
        slen = self.rcomp**2 + self.icomp**2
        return sqrt(float(slen))

    def trim(self, prec):
        if type(prec) != int:
            raise ValueError('Only positive integers allowed')
        if prec <= 0:
            raise ValueError('Only positive integers allowed')
        self.rcomp.trim(prec)
        self.icomp.trim(prec)

    def conj(self):
        return type(self)(self.rcomp, -self.icomp)

    def __mul__(self, other):
        if type(other) not in (type(self), IBReal):
            raise ValueError('Only {} and IBReal instances allowed'.format(type(self).__name__))
        if type(other) == IBReal:
            other = type(self)(other, IBReal((0,0), prec=self.rcomp.prec))
        return type(self)(self.rcomp*other.rcomp-self.icomp*other.icomp, self.rcomp*other.icomp+self.icomp*other.rcomp)

    def __imul__(self, other):
        if type(other) not in (type(self), type(self.rcomp)):
            raise ValueError('Only {} and IBReal instances allowed'.format(type(self).__name__))
        if type(other) == IBReal:
            other = type(self)(other, IBReal((0,0), prec=self.rcomp.prec))
        self.rcomp = self.rcomp*other.rcomp-self.icomp*other.icomp
        self.icomp = self.rcomp*other.icomp+self.icomp*other.rcomp
        return self

    def __add__(self, other):
        if type(other) not in (type(self), type(self.rcomp)):
            raise ValueError('Only {} and IBReal instances allowed'.format(type(self).__name__))
        if type(other) == IBReal:
            other = type(self)(other, IBReal((0,0), prec=self.rcomp.prec))
        return type(self)(self.rcomp+other.rcomp, self.icomp+other.icomp)

    def __iadd__(self, other):
        if type(other) not in (type(self), type(self.rcomp)):
            raise ValueError('Only {} and IBReal instances allowed'.format(type(self).__name__))
        if type(other) == IBReal:
            other = type(self)(other, IBReal((0,0), prec=self.rcomp.prec))
        self.rcomp = self.rcomp+other.rcomp
        self.icomp = self.icomp+other.icomp
        return self

    def __sub__(self, other):
        if type(other) not in (type(self), type(self.rcomp)):
            raise ValueError('Only {} and IBReal instances allowed'.format(type(self).__name__))
        if type(other) == IBReal:
            other = type(self)(other, IBReal((0,0), prec=self.rcomp.prec))
        return type(self)(self.rcomp-other.rcomp, self.icomp-other.icomp)

    def __isub__(self, other):
        if type(other) not in (type(self), type(self.rcomp)):
            raise ValueError('Only {} and IBReal instances allowed'.format(type(self).__name__))
        if type(other) == IBReal:
            other = type(self)(other, IBReal((0,0), prec=self.rcomp.prec))
        self.rcomp = self.rcomp-other.rcomp
        self.icomp = self.icomp-other.icomp
        return self

    def __pow__(self, oint):
        if type(oint) != int:
            raise ValueError('Only non-negative integers allowed')
        if oint < 0:
            raise ValueError('Only non-negative integers allowed')
        tmp = type(self)(self.rcomp, self.icomp)
        if oint == 0:
            tmp.rcomp = IBReal((1,0), prec=self.rcomp.prec)
            tmp.icomp = IBReal((0,0), prec=self.rcomp.prec)
        else: 
            for _ in range(1, oint):
                tmp *= self 
        return tmp 

    def __ipow__(self, oint):
        if type(oint) != int:
            raise ValueError('Only non-negative integers allowed')
        if oint < 0:
            raise ValueError('Only non-negative integers allowed')
        tmp = type(self)(self.rcomp, self.icomp)
        if oint == 0:
            self.rcomp = IBReal((1,0), prec=self.rcomp.prec)
            self.icomp = IBReal((0,0), prec=self.rcomp.prec)
        else: 
            for _ in range(1, oint):
                self *= tmp 
        return self 

    def __eq__(self, other):
        if type(other) != type(self):
            raise ValueError('Only {} instances allowed'.format(type(self).__name__))
        return self.rcomp == other.rcomp and self.icomp == other.icomp

    def __neg__(self):
        return type(self)(-self.rcomp, -self.icomp)

    def __str__(self):
        return '{} + {}i'.format(self.rcomp, self.icomp)

    def __repr__(self):
        return '{} + {}i'.format(self.rcomp, self.icomp)

