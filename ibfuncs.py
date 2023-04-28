def fact_gen():
    cnt = 0
    val = 1
    while True:
        yield val
        cnt += 1
        val *= cnt

def pi(**kwargs):
    one = R((1, 0), **kwargs)
    two = R((2, 0), **kwargs)
    four = R((4, 0), **kwargs)
    five = R((5, 0), **kwargs)
    six = R((6, 0), **kwargs)
    eight = R((8, 0), **kwargs)
    sixteen = R((16, 0), **kwargs)
    rsum = R((0, 0), **kwargs)
    small = one / 10**(one.prec+1)
    idx = 0
    while True:
        a = one / (sixteen**idx)
        b = four / (eight * idx + one)
        c = two / (eight * idx + four)
        d = one / (eight * idx + five)
        e = one / (eight * idx + six)
        term = a * (b - c - d - e)
        if abs(term) < small:
            break
        rsum += term
        idx += 1
    return rsum
    
def ibexp(val):
    if not isinstance(val, R):
        val = R(val)
    rsum = R((0, 0), **val.kwargs)
    one = R((1, 0), **val.kwargs)
    small = one / 10**(val.prec+1)
    fac = fact_gen()
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
        neg = -neg
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
    if val < 0:
        raise ValueError('Non-negative numbers only')
    if val == 0:
        return val
    lv = iblog(val)
    half = R((5, 1), **val.kwargs)
    return ibexp(half*lv)

from .ibreal import IBReal as R

