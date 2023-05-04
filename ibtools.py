from .ibreal import IBReal as R
from .ibcomp import IBComp as C
from os import environ
from functools import wraps

# set global percision (internal integer length)
def set_global_prec(num):
    environ['IBR_DEF_PREC'] = str(num)

# tool to check out number of
# expected roots given degree of real root
# effectively, just makes a reduced fraction
def num_roots(root):
    def _isint(num):
        return int(num) == num 
    if not isinstance(root, R): 
        root = R(root)
    (num, sl) = root.ival
    denom = 10 ** sl
    index = sorted([num, denom])[0] + 1
    tn = num 
    for a in range(1, int(index)):
        if _isint(num/a):
            if _isint(denom/a):
                tn = num/a
    return int(tn)

# prettifies output by zeroing out very low order numbers
# return chopped off values if effectivel zero.
# specified by limit of decimal places
def eff_0(val, limit=None):
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val)
    if limit is None:
        pt9 = R((9, 1), **val.kwargs)
        limit = pt9 * val.prec
    if not isinstance(limit, R):
        limit = R(limit, **val.kwargs)
    one = R((1, 0), **val.kwargs)
    lowval = one / 10**limit
    def _tform(num):
        return R((0, 0), **num.kwargs) if abs(num) < lowval else num
    if isinstance(val, C):
        return C((_tform(val.rcomp), _tform(val.icomp)), **val.kwargs)
    else:
        return _tform(val)

# prettifies output by rounding off .XYZ99999999999999... 
# numbers and .XYZ000000000000000... numbers specified 
# by limit of decimal places
# text-based :(
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
        neg = one if rval.ival.num > zero else neg1 
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
            return neg * (R(wh, **rval.kwargs) + add)
        else:
            nu = str(int(fr[idx-1]) + int(add))
            fr = fr[:idx-1] + nu
            return neg * R('{}.{}'.format(wh, fr), **rval.kwargs)
    if isinstance(val, C):
        return C((_getint(val.rcomp), _getint(val.icomp)), **val.kwargs) 
    else:
        return _getint(val) 

# applies both eff_int and eff_0
# specified by limit of decimal places
def clean(val, limit=None):
    return eff_int(eff_0(val, limit), limit)

# decorator to return clean numbers
def ret_clean(limit=None):
    def inner1(func):
        @wraps(func)
        def inner2(*args, **kwargs):
            ret = func(*args, **kwargs)
            return clean(ret, limit)
        return inner2
    return inner1

