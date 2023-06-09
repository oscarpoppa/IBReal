from collections import namedtuple
from functools import wraps

# key for memoizing -- may be over-specifying key
Memo = namedtuple('Memo','id prec trim_on')

# memoize a decorated function's output by input
# clear all with ibtools.clear_caches()
class MemoizeIBRCall:
    _instances = list()

    # wipe all caches
    @classmethod
    def clearall(cls):
        for i in cls._instances:
            print('{}: removing {}'.format(repr(i), len(i.tbl)))
            i.tbl.clear()

    def __init__(self):
        self.tbl = dict()
        self._repr = None
        type(self)._instances.append(self)

    def __call__(self, func):
        self._repr = 'Memoizer for {}'.format(func.__name__)
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

    def __repr__(self):
        return self._repr

# factorial generator with parity
class FactGen:
    def __init__(self, parity='off'):
        if parity not in ('off', 'even', 'odd'):
            raise ValueError('Only (off, odd, even) allowed')
        self.parity = parity
        self.gen = self._gen()

    def close(self):
        self.gen.close()

    def _mparity(self, cnt):
        if self.parity == 'off':
            return True
        elif self.parity == 'even':
            return False if cnt%2 else True
        else:
            return True if cnt%2 else False

    def _gen(self):
        cnt = 0
        val = R(1, trim_on=False)
        while True:
            if self._mparity(cnt):
                yield val
            cnt += 1
            val *= cnt

    def __next__(self):
        return next(self.gen)

    # context management
    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

class IBArcTan:
    #!! Very slow to converge near one
    # need a good algorithm for near one
    def __call__(self, tan):
        if not isinstance(tan, R):
            tan = R(tan)
        sgn = ib_sgn(tan)
        if tan < 0:
            tan = abs(tan)
        if abs(tan) < 1:
            return sgn*self._arctan_lt1(tan)
        else:
            return sgn*self._arctan_gt1(tan)
    
    # for abs(tan) greater than or equal to one
    def _arctan_gt1(self, tan):
        # for tan >= 1 or <= -1
        neg1 = R((-1, 0), **tan.kwargs)
        one = R((1, 0), **tan.kwargs)
        two = R((2, 0), **tan.kwargs)
        ten = R((10, 0), **tan.kwargs)
        idx = R((0, 0), **tan.kwargs)
        rsum = R((0, 0), **tan.kwargs)
        overshoot = one
        small = one / ten**(tan.prec+overshoot)
        halfpi = ib_pi(**tan.kwargs) / two
        while True:
            a = neg1**idx
            b = one / (two*idx+one) / tan**(two*idx+one)
            term = a * b
            rsum += term
            if abs(term) < small:
                break
            idx += one
        return ib_sgn(tan)*halfpi-rsum
        
    # for abs(tan) less than one    
    def _arctan_lt1(self, tan):
        # for -1 <= tan <= 1
        neg1 = R((-1, 0), **tan.kwargs)
        one = R((1, 0), **tan.kwargs)
        two = R((2, 0), **tan.kwargs)
        ten = R((10, 0), **tan.kwargs)
        idx = R((0, 0), **tan.kwargs)
        rsum = R((0, 0), **tan.kwargs)
        overshoot = one
        small = one / ten**(tan.prec+overshoot)
        while True:
            a = neg1**idx
            b = tan**(two*idx+one) / (two*idx+one)
            term = a * b
            rsum += term
            if abs(term) < small:
                break
            idx += one
        return rsum

# arctangent
# singleton and memoized callable
_arctan_sing = IBArcTan()
ibarctanmemo = MemoizeIBRCall()
@ibarctanmemo
def ib_arctan(tan):
    return _arctan_sing(tan)

# only base e for now
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
        idx = R((0, 0), **val.kwargs)
        rsum = R((0, 0), **val.kwargs)
        overshoot = one
        small = one / ten**(val.prec+overshoot)
        with FactGen() as fac:
            while True:
                term = val**idx / next(fac)
                rsum += term
                if abs(term) < small:
                    break
                idx += one 
        return rsum
    
    def _exp_comp(self, val):
        one = R((1, 0), **val.kwargs)
        ten = R((10, 0), **val.kwargs)
        idx = R((0, 0), **val.kwargs)
        rsum = C((0, 0), **val.kwargs)
        overshoot = one
        small = one / ten**(val.prec+overshoot)
        with FactGen() as fac:
            while True:
                term = val**idx / next(fac)
                rsum += term
                # right way to do this??
                if abs(term.rcomp) < small and abs(term.icomp) < small:
                    break
                idx += one 
        return rsum

# exponential base e
# singleton and memoized callable
_ibexp_sing = IBExp()
ibexpmemo = MemoizeIBRCall()
@ibexpmemo
def ib_exp(val):
    return _ibexp_sing(val)

# only base e for now
class IBLog:
    def __init__(self):
        self._log2 = None

    def __call__(self, val):
        if isinstance(val, C):
            return self._log_comp(val)
        if not isinstance(val, R):
            val = R(val)
        zero = R((0, 0), **val.kwargs)
        if val < zero: # need to use complex
            val = C(val)
            return self._log_comp(val)
        zero = R((0, 0), **val.kwargs)
        two = R((2, 0), **val.kwargs)
        cnt = R((0, 0), **val.kwargs)
        one = R((1, 0), **val.kwargs)
        if self._log2 is None or self._log2.prec < val.prec:
            self._log2 = self._log_real(two)
        # nudge value towards one by successively dividing by two
        if val > one:
            while True:
                if val <= two:
                    break
                val /= two
                cnt += one
            return self._log_real(val) + (cnt * self._log2)
        # nudge value towards one by successively multiplying by two
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
            cm.icomp -= ib_sgn(cm.icomp)*my2pi
        return cm

    def _log_real(self, val):
        # can be SLOW
        neg1 = R((-1, 0), **val.kwargs)
        one = R((1, 0), **val.kwargs)
        ten = R((10, 0), **val.kwargs)
        idx = R((1, 0), **val.kwargs) 
        rsum = R((0, 0), **val.kwargs)
        overshoot = one
        small = one / ten**(val.prec+overshoot)
        neg = ib_sgn(one-val)
        if val > one:
            # log(1/x) = -log(x)
            val = one / val
        val = one - val
        while True:
            term = neg1 * val**idx / idx
            rsum += term
            if abs(term) < small:
                break
            idx += one 
        return neg * rsum

# log base e
# singleton and memoized callable
_iblog_sing = IBLog()
iblogmemo = MemoizeIBRCall()
@iblogmemo
def ib_log(val):
    return _iblog_sing(val)

# multi-branch complex log
# returns a closure to allow access to any branch 
# (i.e. ib_logs(C('1+2i'))(3) for third branch)
def ib_logs(val):
    val = C(val)
    one = R((1, 0), **val.kwargs)
    two = R((2, 0), **val.kwargs)
    my2pi = ib_pi(two, **val.kwargs)
    princ_log = ib_log(val)
    @wraps(ib_logs)
    def inner(branch):
        branch = R(branch)
        if not branch.isint:
            raise TypeError('Only integers allowed')
        return princ_log + ib_i(branch*my2pi)
    return inner

# i times val
def ib_i(val=None, **kwargs):
    if val is None:
        return C((0, 1), **kwargs)
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val, **kwargs)
    return val * C((0, 1), **val.kwargs) 

# pi times val
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
    idx = R((0, 0), **val.kwargs)
    rsum = R((0, 0), **val.kwargs)
    overshoot = one
    small = one / ten**(one.prec+overshoot)
    while True:
        a = one / sixteen**idx
        b = four / (eight*idx+one)
        c = two / (eight*idx+four)
        d = one / (eight*idx+five)
        e = one / (eight*idx+six)
        term = a * (b - c - d - e)
        rsum += term
        if abs(term) < small:
            break
        idx += one
    return val * rsum

# regular square root
def ib_sqrt(val):
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val)
    two = R((2, 0), **val.kwargs)
    return ib_root(val, two)

# single, arbitrary root
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

# multiple arbitrary roots
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
            raise TypeError('Only integers allowed')
        return ib_exp(lv(branch)/root)
    return inner

# sine
# real arguments only
ibsinmemo = MemoizeIBRCall()
@ibsinmemo
def ib_sin(theta):
    if not isinstance(theta, R):
        theta = R(theta)
    neg1 = R((-1, 0), **theta.kwargs)
    one = R((1, 0), **theta.kwargs)
    two = R((2, 0), **theta.kwargs)
    ten = R((10, 0), **theta.kwargs)
    idx = R((1, 0), **theta.kwargs)
    rsum = R((0, 0), **theta.kwargs)
    seq = R((0, 0), **theta.kwargs)
    overshoot = one
    small = one / ten**(theta.prec+overshoot)
    with FactGen('odd') as fac:
        while True:
            term = neg1**seq * theta**idx / next(fac)
            rsum += term
            if abs(term) < small:
                break
            idx += two
            seq += one
    return rsum

# cosine
# real arguments only
ibcosmemo = MemoizeIBRCall()
@ibcosmemo
def ib_cos(theta):
    if not isinstance(theta, R):
        theta = R(theta)
    neg1 = R((-1, 0), **theta.kwargs)
    one = R((1, 0), **theta.kwargs)
    two = R((2, 0), **theta.kwargs)
    ten = R((10, 0), **theta.kwargs)
    rsum = R((0, 0), **theta.kwargs)
    idx = R((0, 0), **theta.kwargs)
    seq = R((0, 0), **theta.kwargs)
    overshoot = one
    small = one / ten**(theta.prec+overshoot)
    with FactGen('even') as fac:
        while True:
            term = neg1**seq * theta**idx / next(fac)
            rsum += term
            if abs(term) < small:
                break
            idx += two
            seq += one
    return rsum

# return sign of arg
# (needs to be able to handle python ints too)
def ib_sgn(num=1):
    if num < 0:
        return type(num)(-1)
    return type(num)(1)

# here to prevent circular import
from .ibreal import Ival, IBReal as R
from .ibcomp import IBComp as C
