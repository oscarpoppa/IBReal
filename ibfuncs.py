from collections import namedtuple
from functools import wraps

Memo = namedtuple('Memo','id prec trim_on')

class MemoizeIBRCall:
    def __init__(self):
        self.tbl = dict()

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            # must call with positional primary arg
            if len(args):
                if isinstance(args[0], C) or isinstance(args[0], R):
                    tmp = args[0]
                else:
                    tmp = R(args[0])
            else:
                tmp = None
            skw = R((0, 0)).kwargs if tmp is None else tmp.kwargs
            key = Memo(repr(tmp)+repr(args[1:])+repr(kwargs), **skw)
            if key in self.tbl:
                return self.tbl[key]
            ret = func(*args, **kwargs)
            self.tbl[key] = ret
            return ret
        return inner

#parity = off, odd, even
def _fact_gen(parity='off'):
    # 1,1,2,6,...
    cnt = 0
    def _mparity():
        if parity == 'off':
            return True
        elif parity == 'even':
            return False if cnt%2 else True
        else:
            return True if cnt%2 else False
    val = 1
    while True:
        if _mparity():
            yield R(val)
        cnt += 1
        val *= cnt

# i times val
def ib_i(val=None, **kwargs):
    if val is None:
        val = C((1, 0), **kwargs)
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val, **kwargs)
    return val * C((0, 1), **val.kwargs) 

# pi times val
ibpimemo = MemoizeIBRCall()
@ibpimemo
def ib_pi(val=None, **kwargs):
    if val is None:
        val = R((1, 0), **kwargs)
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val, **kwargs)
    one = R((1, 0), **val.kwargs)
    two = R((2, 0), **val.kwargs)
    four = R((4, 0), **val.kwargs)
    five = R((5, 0), **val.kwargs)
    six = R((6, 0), **val.kwargs)
    eight = R((8, 0), **val.kwargs)
    ten = R((10, 0), **val.kwargs)
    sixteen = R((16, 0), **val.kwargs)
    overshoot = one
    idx = R((0, 0), **val.kwargs)
    rsum = R((0, 0), **val.kwargs)
    small = one / ten**(one.prec+overshoot)
    while True:
        a = one / sixteen**idx
        b = four / (eight*idx+one)
        c = two / (eight*idx+four)
        d = one / (eight*idx+five)
        e = one / (eight*idx+six)
        term = a * (b - c - d - e)
        if abs(term) < small:
            break
        rsum += term
        idx += one
    return val * rsum

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
        neg1 = R((-1, 0), **tan.kwargs)
        one = R((1, 0), **tan.kwargs)
        two = R((2, 0), **tan.kwargs)
        ten = R((10, 0), **tan.kwargs)
        overshoot = one
        idx = R((0, 0), **tan.kwargs)
        rsum = R((0, 0), **tan.kwargs)
        small = one / ten**(tan.prec+overshoot)
        halfpi = ib_pi(**tan.kwargs) / two
        while True:
            a = neg1**idx
            b = one / (two*idx+one) / tan**(two*idx+one)
            term = a * b
            if abs(term) < small:
                break
            rsum += term
            idx += one
        return halfpi-rsum if tan > 0 else -halfpi-rsum
        
    def _arctan_lt1(self, tan):
        # for -1 <= tan <= 1
        neg1 = R((-1, 0), **tan.kwargs)
        one = R((1, 0), **tan.kwargs)
        two = R((2, 0), **tan.kwargs)
        ten = R((10, 0), **tan.kwargs)
        overshoot = one
        idx = R((0, 0), **tan.kwargs)
        rsum = R((0, 0), **tan.kwargs)
        small = one / ten**(tan.prec+overshoot)
        while True:
            a = neg1**idx
            b = tan**(two*idx+one) / (two*idx+one)
            term = a * b
            if abs(term) < small:
                break
            rsum += term
            idx += one
        return rsum

# singleton and memoized callable
_arctan_sing = IBArcTan()
ibarctanmemo = MemoizeIBRCall()
@ibarctanmemo
def ib_arctan(tan):
    return _arctan_sing(tan)

class IBExp:
    def __call__(self, val):
        if isinstance(val, C):
            return self._exp_comp(val)
        else:
             if not isinstance(val, R):
                 val = R(val)
             return self._exp_real(val)
    
    def _exp_real(self, val):
        one = R((1, 0), **val.kwargs)
        ten = R((10, 0), **val.kwargs)
        overshoot = one
        idx = R((0, 0), **val.kwargs)
        rsum = R((0, 0), **val.kwargs)
        small = one / ten**(val.prec+overshoot)
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
        one = R((1, 0), **val.kwargs)
        ten = R((10, 0), **val.kwargs)
        overshoot = one
        idx = R((0, 0), **val.kwargs)
        rsum = C((0, 0), **val.kwargs)
        small = one / ten**(val.prec+overshoot)
        fac = _fact_gen()
        while True:
            term = val**idx / next(fac)
            if abs(term.rcomp) < small and abs(term.icomp) < small:
                break
            rsum += term
            idx += one 
        fac.close()
        return rsum

# singleton and memoized callable
_ibexp_sing = IBExp()
ibexpmemo = MemoizeIBRCall()
@ibexpmemo
def ib_exp(val, base='e'):
    if base == 'e':
        return _ibexp_sing(val)
    else:
        return _ibexp_sing(val*ib_log(base))

class IBLog:
    def __init__(self):
        self._log2 = None

    def __call__(self, val):
        if isinstance(val, C):
            return self._log_comp(val)
        if not isinstance(val, R):
            val = R(val)
        zero = R((0, 0), **val.kwargs)
        if val < zero:
            val = C(val)
            return self._log_comp(val)
        zero = R((0, 0), **val.kwargs)
        two = R((2, 0), **val.kwargs)
        cnt = R((0, 0), **val.kwargs)
        one = R((1, 0), **val.kwargs)
        if self._log2 is None or self._log2.prec < val.prec:
            self._log2 = self._log_real(two)
        if val > one:
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

    def _log_comp(self, val):
        zero = R((0, 0), **val.kwargs)
        two = R((2, 0), **val.kwargs)
        mypi = ib_pi(**val.kwargs)
        my2pi = two * mypi
        lr = ib_log(val.length)
        cm = C((0, val.theta), **val.kwargs) + lr
        # get principal value
        while abs(cm.icomp) > mypi:
            cm.icomp += (my2pi if cm.icomp < zero else -my2pi)
        return cm

    def _log_real(self, val):
        # can be SLOW
        neg1 = R((-1, 0), **val.kwargs)
        one = R((1, 0), **val.kwargs)
        ten = R((10, 0), **val.kwargs)
        overshoot = one
        neg = R((1, 0), **val.kwargs)
        idx = R((1, 0), **val.kwargs) 
        rsum = R((0, 0), **val.kwargs)
        small = one / ten**(val.prec+overshoot)
        if val > one:
            neg = -neg
            val = one / val
        val = one - val
        while True:
            term = neg1 * val**idx / idx
            if abs(term) < small:
                break
            rsum += term
            idx += one 
        return neg * rsum

# singleton and memoized callable
_iblog_sing = IBLog()
iblogmemo = MemoizeIBRCall()
@iblogmemo
def ib_log(val, base='e'):
    if base == 'e':
        return _iblog_sing(val)
    else:
        return _iblog_sing(val) / _iblog_sing(base)

# returns a closure to allow access to any branch 
# (i.e. ib_logs(C('1+2i'))(3) for third branch)
def ib_logs(val, base='e'):
    val = C(val)
    one = R((1, 0), **val.kwargs)
    two = R((2, 0), **val.kwargs)
    my2pi = ib_pi(two, **val.kwargs)
    princ_log = ib_log(val, base)
    if base == 'e':
        lnb = one
    else:
        lnb = ib_log(base)
    @wraps(ib_logs)
    def inner(branch):
        branch = R(branch)
        if not branch.isint:
            raise ValueError('Integers only')
        return princ_log + ib_i(branch*my2pi/lnb)
    return inner

ibsqrtmemo = MemoizeIBRCall()
@ibsqrtmemo
def ib_sqrt(val):
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val)
    two = R((2, 0), **val.kwargs)
    return ib_root(val, two)

# uses principal branch of log for a single root
ibrootmemo = MemoizeIBRCall()
@ibrootmemo
def ib_root(val, root):
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val)
    if not isinstance(root, R) and not isinstance(root, C):
        root = R(root)
    zero = R((0, 0), **val.kwargs)
    if val == zero:
        return val
    lv = ib_log(val)
    return ib_exp(lv/root)

# returns a closure to allow access to any root, specified by corresponding 
# log branch (i.e. ib_roots(C('1+2i'),5)(3) for root corresponding to third branch)
def ib_roots(val, root):
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val)
    if not isinstance(root, R) and not isinstance(root, C):
        root = R(root)
    zero = R((0, 0), **val.kwargs)
    if val == zero:
        @wraps(ib_roots)
        def inner(num):
            return zero
        return inner
    lv = ib_logs(val)
    @wraps(ib_roots)
    def inner(branch):
        branch = R(branch)
        if not branch.isint:
            raise ValueError('Integers only')
        return ib_exp(lv(branch)/root)
    return inner

# reals only
ibsinmemo = MemoizeIBRCall()
@ibsinmemo
def ib_sin(theta):
    if not isinstance(theta, R):
        theta = R(theta)
    neg1 = R((-1, 0), **theta.kwargs)
    one = R((1, 0), **theta.kwargs)
    two = R((2, 0), **theta.kwargs)
    ten = R((10, 0), **theta.kwargs)
    overshoot = one
    idx = R((1, 0), **theta.kwargs)
    rsum = R((0, 0), **theta.kwargs)
    seq = R((0, 0), **theta.kwargs)
    small = one / ten**(theta.prec+overshoot)
    fac = _fact_gen(parity='odd')
    while True:
        term = neg1**seq * theta**idx / next(fac)
        if abs(term) < small:
            break
        rsum += term
        idx += two
        seq += one
    fac.close()
    return rsum

# reals only
ibcosmemo = MemoizeIBRCall()
@ibcosmemo
def ib_cos(theta):
    if not isinstance(theta, R):
        theta = R(theta)
    neg1 = R((-1, 0), **theta.kwargs)
    one = R((1, 0), **theta.kwargs)
    two = R((2, 0), **theta.kwargs)
    ten = R((10, 0), **theta.kwargs)
    overshoot = one
    rsum = R((0, 0), **theta.kwargs)
    idx = R((0, 0), **theta.kwargs)
    seq = R((0, 0), **theta.kwargs)
    small = one / ten**(theta.prec+overshoot)
    fac = _fact_gen(parity='even')
    while True:
        term = neg1**seq * theta**idx / next(fac)
        if abs(term) < small:
            break
        rsum += term
        idx += two
        seq += one
    fac.close()
    return rsum

# here to prevent circular import
from .ibreal import Ival, IBReal as R
from .ibcomp import IBComp as C
