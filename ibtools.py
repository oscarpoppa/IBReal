from .ibreal import IBReal as R
from .ibcomp import IBComp as C
from .ibfuncs import ib_pi, ib_sgn, MemoizeIBRCall as M
from os import environ
from functools import wraps

# set global precision (internal integer length)
def set_global_prec(num):
    environ['IBR_DEF_PREC'] = str(num)

# clear all caches
def clear_caches():
    M.clearall()

# prettifies output by zeroing out very low order numbers
# return chopped off values if effectively zero.
# specified by limit of decimal places
# not for "production"
def eff_0(val, limit=None):
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val)
    if limit is None:
        pt9 = R((9, 1), **val.kwargs)
        limit = pt9 * val.prec
    if not isinstance(limit, R):
        limit = R(limit, **val.kwargs)
    zero = R((0, 0), **val.kwargs)
    one = R((1, 0), **val.kwargs)
    lowval = one / 10**limit
    def _tform(num):
        return zero if abs(num) < lowval else num
    if isinstance(val, C):
        return C((_tform(val.rcomp), _tform(val.icomp)), **val.kwargs)
    else:
        return _tform(val)

# prettifies output by rounding off .XYZ99999999999999... 
# numbers and .XYZ000000000000000... numbers specified 
# by limit of decimal places
# text-based :(
# not for "production"
def eff_int(val, limit=None):
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val)
    if limit is None:
        pt9 = R((9, 1), **val.kwargs)
        limit = pt9 * val.prec
    if not isinstance(limit, R):
        limit = R(limit, **val.kwargs)
    def _getint(rval):
        st = str(abs(rval.ival.num))
        ln = len(st)
        one = R((1, 0), **rval.kwargs)
        zero = R((0, 0), **rval.kwargs)
        neg1 = R((-1, 0), **rval.kwargs)
        off = rval.ival.off
        dot = ln - off
        if dot < 0:
            st = '0'*abs(dot) + st
            dot = 0
        patt9 = '9'*int(limit)
        patt0 = '0'*int(limit)
        wh = st[:dot] or '0'
        fr = st[dot:] or ''
        add = one
        idx = fr.find(patt9)
        if idx == -1:
            add = zero
            idx = fr.find(patt0)
            if idx == -1:
                return rval
        if idx == 0:
            return ib_sgn(rval.ival.num) * (R(wh, **rval.kwargs) + add)
        else:
            nu = str(int(fr[idx-1]) + int(add))
            fr = fr[:idx-1] + nu
            return ib_sgn(rval.ival.num) * R('{}.{}'.format(wh, fr), **rval.kwargs)
    if isinstance(val, C):
        return C((_getint(val.rcomp), _getint(val.icomp)), **val.kwargs) 
    else:
        return _getint(val) 

# more presentation tidiness...
# looks for numbers that are an integer multiple of pi and 
# creates a special __repr__ for the result -- eye candy ;)
# not for "production"
def eff_pi(num):
    if not isinstance(num, R) and not isinstance(num, C):
        num = R(num)
    def _tform(val):
        zero = R((0, 0), **val.kwargs)
        one = R((1, 0), **val.kwargs)
        ten = R((10, 0), **val.kwargs)
        overshoot = one
        pi = ib_pi(**val.kwargs)
        pt9 = R((9, 1), **val.kwargs)
        limit = pt9 * val.prec
        lowval = one / 10**limit
        cnt = 0
        tmp = R(val)
        while (abs(tmp) >= pi):
            tmp -= ib_sgn(tmp)*pi
            cnt += 1 
            if abs(tmp) < lowval:
                neg = '' if val > zero else '-'
                # special __repr__
                rep = '{}{}\u03c0'.format(neg, cnt)
                return R(val, rep=rep, **val.kwargs)
        return val
    if isinstance(num, C):
        return C((_tform(num.rcomp), _tform(num.icomp)), **num.kwargs) 
    else:
        return _tform(num) 

# applies eff_pi, eff_int and eff_0
# specified by limit of decimal places
# not for "production"
def clean(val, limit=None):
    return eff_pi(eff_int(eff_0(val, limit), limit))

# decorator to return "clean" numbers
# not for "production"
def ret_clean(limit=None):
    def inner1(func):
        @wraps(func)
        def inner2(*args, **kwargs):
            ret = func(*args, **kwargs)
            return clean(ret, limit)
        return inner2
    return inner1

