def fact_gen():
    cnt = 0
    val = 1
    while True:
        yield val
        cnt += 1
        val *= cnt
    
def ibexp(val):
    if not isinstance(val, R):
        val = R(val)
    rsum = R((0, 0), **val.kwargs)
    fac = fact_gen()
    one = R((1, 0), **val.kwargs)
    small = one / 10**(val.prec+1)
    idx = 0
    while True:
        term = val**idx / next(fac)
        if abs(term) < small:
            break
        rsum += term
        idx += 1
    fac.close()
    return rsum

def iblog(val):
    if not isinstance(val, R):
        val = R(val)
    if val <= 0:
        raise ValueError('Positive numbers only')
    one = R((1, 0), **val.kwargs)
    neg = R((1, 0), **val.kwargs)
    neg1 = R((-1, 0), **val.kwargs)
    rsum = R((0, 0), **val.kwargs)
    if val > 1:
        neg = R((-1, 0), **val.kwargs)
        val = one / val
    val = one - val
    small = one / 10**(val.prec+1)
    idx = 1 
    while True:
        term = neg1 * (val)**idx / idx
        if abs(term) < small:
            break
        rsum += term
        idx += 1
    return neg * rsum

def ibsqrt(val):
    if not isinstance(val, R):
        val = R(val)
    if val <= 0:
        raise ValueError('Positive numbers only')
    lv = iblog(val)
    half = R((5, 1), **val.kwargs)
    return ibexp(half*lv)

from .ibreal import IBReal as R

