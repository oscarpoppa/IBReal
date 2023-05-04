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
    def isint(num):
        return int(num) == num 
    if not isinstance(root, R): 
        root = R(root)
    (num, sl) = root.ival
    denom = 10 ** sl
    index = sorted([num, denom])[0] + 1
    tn = num 
    for a in range(1, int(index)):
        if isint(num/a):
            if isint(denom/a):
                tn = num/a
    return int(tn)

# prettifies output by zeroing out very low order numbers
# return chopped off values if effectivel zero.
# specified by limit of decimal places
def eff_0(val, limit=None):
    if limit is None:
        pt9 = R((9, 1))
        limit = pt9 * pt9.prec
    if not isinstance(limit, R):
        limit = R(limit)
    one = R((1, 0), **limit.kwargs)
    lowval = one / 10**limit
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val)
    def tform(num):
        return R((0, 0), **num.kwargs) if abs(num) < lowval else num
    if isinstance(val, C):
        return C((tform(val.rcomp), tform(val.icomp)), **val.kwargs)
    else:
        return tform(val)

# prettifies output by rounding up .99999999999999... numbers
# specified by limit of decimal places
def eff_int(val, limit=None):
    if not isinstance(val, R) and not isinstance(val, C):
        val = R(val)
    if limit is None:
        pt9 = R((9, 1))
        limit = pt9 * pt9.prec
    if not isinstance(limit, R):
        limit = R(limit)
    def getint(rval):
        st = str(abs(rval.ival.num))
        ln = len(st)
        one = R((1, 0), **rval.kwargs)
        zero = R((0, 0), **rval.kwargs)
        neg1 = R((-1, 0), **rval.kwargs)
        neg = one if rval.ival.num > zero else neg1 
        off = rval.ival.off
        dot = ln - off
        if dot < 0:
            return rval
        patt = '9'*int(limit)
        wh = st[:dot] or '0'
        fr = st[dot:] or ''
        idx = fr.find(patt)
        if idx == -1:
            return rval
        if idx == 0:
            return neg * (R(wh) + one)
        else:
            nu = str(int(fr[idx-1]) + 1)
            fr = fr[:idx-1] + nu
            return neg * R('{}.{}'.format(wh, fr))
    if isinstance(val, C):
        return C((getint(val.rcomp), getint(val.icomp)), **val.kwargs) 
    else:
        return getint(val) 

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

