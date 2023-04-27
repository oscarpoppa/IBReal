def fact_gen():
    cnt = 0
    val = 1
    while True:
        yield val
        cnt += 1
        val *= cnt
    
def ibexp(val, prec=None):
    if not isinstance(val, R):
        val = R(val)
    prec = prec if prec else val.prec
    rsum = R((0, 0), prec=prec)
    fac = fact_gen()
    one = R((1, 0), prec=prec)
    small = one / 10**(prec+1)
    idx = 0
    while True:
        term = val**idx / next(fac)
        if abs(term) < small:
            break
        rsum += term
        idx += 1
    fac.close()
    return rsum

def iblog(val, prec=None):
    if not isinstance(val, R):
        val = R(val)
    if val <= 0:
        raise ValueError('Positive numbers only')
    prec = prec if prec else val.prec
    one = R((1, 0), prec=prec)
    neg = R((1, 0), prec=prec)
    neg1 = R((-1,0), prec=prec)
    rsum = R((0, 0), prec=prec)
    if val > 1:
        neg = R((-1, 0), prec=prec)
        val = one / val
    val = one - val
    small = one / 10**(prec+1)
    idx = 1 
    while True:
        term = neg1 * (val)**idx / idx
        if abs(term) < small:
            break
        rsum += term
        idx += 1
    return neg * rsum

def ibsqrt(val, prec=None):
    if not isinstance(val, R):
        val = R(val)
    if val <= 0:
        raise ValueError('Positive numbers only')
    prec = prec if prec else val.prec
    lv = iblog(val, prec=prec)
    half = R((5, 1), prec=prec)
    return ibexp(half*lv, prec=prec)

from .ibreal import IBReal as R

