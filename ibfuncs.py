from collections import namedtuple
from functools import wraps
from os import environ

Memo = namedtuple('Memo','id prec trim_on')

def set_global_prec(num):
    environ['IBR_DEF_PREC'] = str(num)

class MemoizeIBRCall:
    def __init__(self):
        self.tbl = dict()

    def __call__(self, func):
        @wraps(func)
        def inner(*args):
            if isinstance(args[0], C) or isinstance(args[0], R):
                tmp = args[0]
            else:
                tmp = R(args[0])
            key = Memo(repr(tmp), **tmp.kwargs)
            if key in self.tbl:
                return self.tbl[key]
            ret = func(tmp)
            self.tbl[key] = ret
            return ret
        return inner

#parity = off, odd, even
def _fact_gen(parity='off'):
    # 1,1,2,6,...
    cnt = 0
    def mparity():
        if parity == 'off':
            return True
        elif parity == 'even':
            return False if cnt%2 else True
        else:
            return True if cnt%2 else False
    val = 1
    while True:
        if mparity():
            yield R(val)
        cnt += 1
        val *= cnt

class IBArcTan:
    #!! Very slow to converge near 1
    def __call__(self, tan):
        if not isinstance(tan, R):
            tan = R(tan)
        neg = R((1, 0), **tan.kwargs)
        if tan < 0:
            tan = abs(tan)
            neg = -neg
        if abs(tan) < 1:
            return neg*self._arctan_lt1(tan)
        else:
            return neg*self._arctan_gt1(tan)
    
    def _arctan_gt1(self, tan):
        # for tan >= 1 or <= -1
        one = R((1, 0), **tan.kwargs)
        two = R((2, 0), **tan.kwargs)
        ten = R((10, 0), **tan.kwargs)
        neg1 = R((-1, 0), **tan.kwargs)
        rsum = R((0, 0), **tan.kwargs)
        idx = R((0, 0), **tan.kwargs)
        small = one / ten**(tan.prec+one)
        halfpi = pi(**tan.kwargs) / two
        while True:
            a = neg1**idx
            b = one / ((two*idx+one)*(tan**(two*idx+one)))
            term = a * b
            if abs(term) < small:
                break
            rsum += term
            idx += one
        return halfpi-rsum if tan > 0 else -halfpi-rsum
        
    def _arctan_lt1(self, tan):
        # for -1 <= tan <= 1
        one = R((1, 0), **tan.kwargs)
        two = R((2, 0), **tan.kwargs)
        ten = R((10, 0), **tan.kwargs)
        neg1 = R((-1, 0), **tan.kwargs)
        rsum = R((0, 0), **tan.kwargs)
        idx = R((0, 0), **tan.kwargs)
        small = one / ten**(tan.prec+one)
        while True:
            a = neg1**idx
            b = (tan**(two*idx+one))/(two*idx+one)
            term = a * b
            if abs(term) < small:
                break
            rsum += term
            idx += one
        return rsum

ibarctanmemo = MemoizeIBRCall()
# memoized callable
ibarctan = ibarctanmemo(IBArcTan())

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
    ten = R((10, 0), **kwargs)
    sixteen = R((16, 0), **kwargs)
    idx = R((0, 0), **kwargs)
    rsum = R((0, 0), **kwargs)
    small = one / ten**(one.prec+one)
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

class IBExp:
    def __call__(self, val):
        if isinstance(val, C):
            return self._exp_comp(val)
        else:
             if not isinstance(val, R):
                 val = R(val, **self.kwargs)
             return self._exp_real(val)
    
    def _exp_real(self, val):
        rsum = R((0, 0), **val.kwargs)
        one = R((1, 0), **val.kwargs)
        ten = R((10, 0), **val.kwargs)
        idx = R((0, 0), **val.kwargs)
        small = one / ten**(val.prec+one)
        fac = _fact_gen()
        while True:
            term = val**idx / next(fac)
            if abs(term) < small:
                break
            rsum += term
            idx += one 
        fac.close()
        return rsum
    
    def _exp_comp(self, val):
        rsum = C((0, 0), **val.kwargs)
        one = R((1, 0), **val.kwargs)
        ten = R((10, 0), **val.kwargs)
        idx = R((0, 0), **val.kwargs)
        small = one / ten**(val.prec+one)
        fac = _fact_gen()
        while True:
            term = val**idx / next(fac)
            if abs(term.rcomp) < small and abs(term.icomp) < small:
                break
            rsum += term
            idx += one 
        fac.close()
        return rsum

ibexpmemo = MemoizeIBRCall()
# memoized callable
ibexp = ibexpmemo(IBExp())

class IBLog:
    def __init__(self):
        self._log2 = None

    def _log_comp(self, val):
        zero = R((0, 0), **val.kwargs)
        two = R((2, 0), **val.kwargs)
        mypi = pi()
        my2pi = two * mypi
        lr = iblog(val.length)
        cm = C((0, val.theta), **val.kwargs) + lr
        # get principal value
        sub = abs(cm.icomp) // mypi
        cm.icomp += sub * (my2pi if cm.icomp < zero else -my2pi)
        return cm

    def _log_real(self, val):
        # can be SLOW
        one = R((1, 0), **val.kwargs)
        ten = R((10, 0), **val.kwargs)
        neg = R((1, 0), **val.kwargs)
        neg1 = R((-1, 0), **val.kwargs)
        rsum = R((0, 0), **val.kwargs)
        small = one / ten**(val.prec+one)
        idx = R((1, 0), **val.kwargs) 
        if val > 1:
            neg = -neg
            val = one / val
        val = one - val
        while True:
            term = neg1 * (val)**idx / idx
            if abs(term) < small:
                break
            rsum += term
            idx += one 
        return neg * rsum

    def __call__(self, val):
        if isinstance(val, C):
            return self._log_comp(val)
        if not isinstance(val, R):
            val = R(val)
        if val < R((0, 0), **val.kwargs):
            val = C(val)
            return self._log_comp(val)
        zero = R((0, 0), **val.kwargs)
        two = R((2, 0), **val.kwargs)
        cnt = R((0, 0), **val.kwargs)
        one = R((1, 0), **val.kwargs)
        if self._log2 is None or self._log2.prec < val.prec:
            self._log2 = self._log_real(two)
        if val > 1:
            while True:
                if val <= two:
                    break
                val /= two
                cnt += one
            return self._log_real(val) + (cnt * self._log2)
        else:
            while True:
                if val >= one:
                    break
                val *= two
                cnt += one
            return self._log_real(val) - (cnt * self._log2)

iblogmemo = MemoizeIBRCall()
# memoized callable
iblog = iblogmemo(IBLog())

ibsqrtmemo = MemoizeIBRCall()
@ibsqrtmemo
def ibsqrt(val):
    two = R((2, 0), **val.kwargs)
    return ibgenrt(val, two)

def ibgenrt(val, root):
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val)
    if not isinstance(root, R) and not isinstance(root, C):
        root = R(root)
    if val == 0:
        return val
    lv = iblog(val)
    return ibexp(lv/root)

ibsinmemo = MemoizeIBRCall()
@ibsinmemo
def ibsin(theta):
    if not isinstance(theta, R):
        theta = R(theta)
    neg1 = R((-1, 0), **theta.kwargs)
    one = R((1, 0), **theta.kwargs)
    two = R((2, 0), **theta.kwargs)
    ten = R((10, 0), **theta.kwargs)
    rsum = R((0, 0), **theta.kwargs)
    idx = R((1, 0), **theta.kwargs)
    seq = R((0, 0), **theta.kwargs)
    small = one / ten**(theta.prec+one)
    fac = _fact_gen('odd')
    while True:
        term = neg1**(seq) * theta**idx / next(fac)
        if abs(term) < small:
            break
        rsum += term
        idx += two
        seq += one
    fac.close()
    return rsum

ibcosmemo = MemoizeIBRCall()
@ibcosmemo
def ibcos(theta):
    if not isinstance(theta, R):
        theta = R(theta)
    neg1 = R((-1, 0), **theta.kwargs)
    one = R((1, 0), **theta.kwargs)
    two = R((2, 0), **theta.kwargs)
    ten = R((10, 0), **theta.kwargs)
    rsum = R((0, 0), **theta.kwargs)
    idx = R((0, 0), **theta.kwargs)
    seq = R((0, 0), **theta.kwargs)
    small = one / ten**(theta.prec+one)
    fac = _fact_gen('even')
    while True:
        term = neg1**(seq) * theta**idx / next(fac)
        if abs(term) < small:
            break
        rsum += term
        idx += two
        seq += one
    fac.close()
    return rsum

from .ibreal import Ival, IBReal as R
from .ibcomp import IBComp as C
