from collections import namedtuple
from functools import wraps

Memo = namedtuple('Memo','ival prec trim_on')

class MemoizeIBRCall:
    def __init__(self):
        self.tbl = dict()

    def __call__(self, func):
        @wraps(func)
        def inner(*args):
            tmp = args[0] if isinstance(args[0], R) else R(args[0])
            key = Memo(tmp.ival, **tmp.kwargs)
            if key in self.tbl:
                return self.tbl[key]
            ret = func(tmp)
            self.tbl[key] = ret
            return ret
        return inner

#par = off, odd, even
def _fact_gen(par='off'):
    # 1,1,2,6,...
    cnt = 0
    def mpar():
        if par == 'off':
            return True
        elif par == 'even':
            return False if cnt%2 else True
        else:
            return True if cnt%2 else False
    val = 1
    while True:
        if mpar():
            yield R(val)
        cnt += 1
        val *= cnt

class IBArcTan:
    def __call__(self, val):
        if not isinstance(val, R):
            val = R(val)
        neg = R((1, 0), **val.kwargs)
        if val < 0:
            val = abs(val)
            neg = -neg
        if abs(val) < 1:
            return neg*self._arctan_i(val)
        else:
            return neg*self._arctan_o(val)
    
    def _arctan_o(self, val):
        # for val >= 1 or <= -1
        one = R((1, 0), **val.kwargs)
        two = R((2, 0), **val.kwargs)
        halfpi = pi(**val.kwargs) / two
        neg1 = R((-1, 0), **val.kwargs)
        small = one / 10**(val.prec+1)
        rsum = R((0, 0), **val.kwargs)
        idx = R((0, 0), **val.kwargs)
        while True:
            a = neg1**idx
            b = one / ((two*idx+one)*(val**(two*idx+one)))
            term = a * b
            if abs(term) < small:
                break
            rsum += term
            idx += one
        return halfpi-rsum if val > 0 else -halfpi-rsum
        
    def _arctan_i(self, val):
        # for -1 <= val <= 1
        one = R((1, 0), **val.kwargs)
        two = R((2, 0), **val.kwargs)
        neg1 = R((-1, 0), **val.kwargs)
        small = one / 10**(val.prec+1)
        rsum = R((0, 0), **val.kwargs)
        idx = R((0, 0), **val.kwargs)
        while True:
            a = neg1**idx
            b = (val**(two*idx+one))/(two*idx+one)
            term = a * b
            if abs(term) < small:
                break
            rsum += term
            idx += one
        return rsum

# quick memoize
_pitbl = dict()

def pi(**kwargs):
    kwargs = kwargs if kwargs else R(0).kwargs
    if kwargs['prec'] in _pitbl:
        return _pitbl[kwargs['prec']]
    one = R((1, 0), **kwargs)
    two = R((2, 0), **kwargs)
    four = R((4, 0), **kwargs)
    five = R((5, 0), **kwargs)
    six = R((6, 0), **kwargs)
    eight = R((8, 0), **kwargs)
    sixteen = R((16, 0), **kwargs)
    rsum = R((0, 0), **kwargs)
    small = one / 10**(one.prec+1)
    idx = R((0, 0), **kwargs)
    while True:
        a = one/(sixteen**idx)
        b = four/(eight*idx+one)
        c = two/(eight*idx+four)
        d = one/(eight*idx+five)
        e = one/(eight*idx+six)
        term = a * (b - c - d - e)
        if abs(term) < small:
            break
        rsum += term
        idx += one 
    _pitbl[kwargs['prec']] = rsum
    return rsum

ibarctanmemo = MemoizeIBRCall()

# memoized callable
ibarctan = ibarctanmemo(IBArcTan())

ibexpmemo = MemoizeIBRCall()

@ibexpmemo
def ibexp(val):
    if not isinstance(val, R):
        val = R(val)
    rsum = R((0, 0), **val.kwargs)
    one = R((1, 0), **val.kwargs)
    small = one / 10**(val.prec+1)
    fac = _fact_gen()
    idx = R((0, 0), **val.kwargs)
    while True:
        term = val**idx / next(fac)
        if abs(term) < small:
            break
        rsum += term
        idx += one 
    fac.close()
    return rsum

iblogmemo = MemoizeIBRCall()

class IBLog:
    def __init__(self):
        self._log2 = None

    def __call__(self, val):
        if not isinstance(val, R):
            val = R(val)
        zero = R((0, 0), **val.kwargs)
        two = R((2, 0), **val.kwargs)
        if val <= zero:
            raise ValueError('Positive numbers only')
        if self._log2 is None or self._log2.prec < val.prec:
            self._log2 = self._iblog(two)
        cnt = R((0, 0), **val.kwargs)
        one = R((1, 0), **val.kwargs)
        while True:
            if val <= two:
                break
            val /= two
            cnt += one
        return self._iblog(val) + (cnt * self._log2)

    def _iblog(self, val):
        # can be SLOW
        one = R((1, 0), **val.kwargs)
        neg = R((1, 0), **val.kwargs)
        neg1 = R((-1, 0), **val.kwargs)
        rsum = R((0, 0), **val.kwargs)
        small = one / 10**(val.prec+1)
        if val > 1:
            neg = -neg
            val = one / val
        val = one - val
        idx = R((1, 0), **val.kwargs) 
        while True:
            term = neg1 * (val)**idx / idx
            if abs(term) < small:
                break
            rsum += term
            idx += one 
        return neg * rsum

iblogmemo = MemoizeIBRCall()

# memoized callable
iblog = iblogmemo(IBLog())

ibsqrtmemo = MemoizeIBRCall()

@ibsqrtmemo
def ibsqrt(val):
    # can be SLOW
    if not isinstance(val, R):
        val = R(val)
    if val < 0:
        raise ValueError('Non-negative numbers only')
    if val == 0:
        return val
    lv = iblog(val)
    half = R((5, 1), **val.kwargs)
    return ibexp(half*lv)

ibsinmemo = MemoizeIBRCall()

@ibsinmemo
def ibsin(val):
    #x-x3/3!+x5/5!
    if not isinstance(val, R):
        val = R(val)
    neg1 = R((-1, 0), **val.kwargs)
    one = R((1, 0), **val.kwargs)
    two = R((2, 0), **val.kwargs)
    small = one / 10**(val.prec+1)
    fac = _fact_gen('odd')
    rsum = R((0, 0), **val.kwargs)
    idx = R((1, 0), **val.kwargs)
    seq = R((0, 0), **val.kwargs)
    while True:
        term = neg1**(seq) * val**idx / next(fac)
        if abs(term) < small:
            break
        rsum += term
        idx += two
        seq += one
    fac.close()
    return rsum

ibcosmemo = MemoizeIBRCall()

@ibcosmemo
def ibcos(val):
    #1-x2/2!+x4/4!
    if not isinstance(val, R):
        val = R(val)
    neg1 = R((-1, 0), **val.kwargs)
    one = R((1, 0), **val.kwargs)
    two = R((2, 0), **val.kwargs)
    small = one / 10**(val.prec+1)
    fac = _fact_gen('even')
    rsum = R((0, 0), **val.kwargs)
    idx = R((0, 0), **val.kwargs)
    seq = R((0, 0), **val.kwargs)
    while True:
        term = neg1**(seq) * val**idx / next(fac)
        if abs(term) < small:
            break
        rsum += term
        idx += two
        seq += one
    fac.close()
    return rsum

from .ibreal import Ival, IBReal as R
