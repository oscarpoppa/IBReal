def fact_gen():
    cnt = 0
    val = 1
    while True:
        yield val
        cnt += 1
        val *= cnt
    
def ibexp(val, base='e', prec=None):
    if not isinstance(val, R):
        val = R(iblog(base)*val)
    rsum = R((0, 0))
    fac = fact_gen()
    one = R((1, 0))
    prec = prec if prec else val.prec
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
    one = R((1, 0))
    neg = R((1, 0))
    neg1 = R((-1,0))
    rsum = R((0, 0))
    if val > 1:
        neg = R((-1, 0))
        val = one / val
    val = one - val
    prec = prec if prec else val.prec
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
    lv = iblog(val, prec=prec)
    half = R((5, 1))
    return ibexp(half*lv)



from .ibreal import IBReal as R
